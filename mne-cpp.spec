# MNE-CPP has no formal releases since v0.1.9 (2021).
# Use a recent git snapshot from main branch.
%global commit 1daca518d5375aa40be156ef5f9b1f4396a8bee5
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260304

%define debug_package %{nil}

Name:           mne-cpp
Version:        0.1.9^%{snapdate}git%{shortcommit}
Release:        3%{?dist}
Summary:        Cross-platform C++ framework for MEG/EEG data analysis

License:        BSD-3-Clause
URL:            https://mne-cpp.github.io/
Source0:        https://github.com/mne-tools/mne-cpp/archive/%{commit}/mne-cpp-%{shortcommit}.tar.gz

# Upstream lacks cmake install() targets and SOVERSION on shared libraries.
# We inject both via sed in prep.

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.15
BuildRequires:  ninja-build
BuildRequires:  eigen3-devel
BuildRequires:  fftw-devel

# Qt6 modules used across libraries and applications
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtcharts-devel
BuildRequires:  qt6-qt3d-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtshadertools-devel
# Qt6 private headers needed for disp3D_rhi (Qt RHI-based 3D rendering)
BuildRequires:  qt6-qtbase-private-devel

%description
MNE-CPP is a cross-platform, open-source C++ framework for MEG/EEG data
acquisition and analysis. It includes libraries for FIFF I/O, forward and
inverse modeling, connectivity analysis, real-time processing, and 3D
visualization. Applications include MNE Scan (real-time acquisition),
MNE Analyze (offline analysis), and various command-line utilities.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       qt6-qtbase-devel
Requires:       eigen3-devel

%description devel
Header files and cmake config for developing against the MNE-CPP libraries.

%prep
%autosetup -n mne-cpp-%{version}

# Remove bundled Eigen install (uses system eigen3-devel at build time,
# but Eigen headers would be installed to /usr/include/Eigen/ conflicting with system)
# Note: source bundles Eigen 5.0.0 which we keep for building (system eigen3 3.4 works
# for includes but the external/ copy is referenced by cmake). We just prevent install.

# The upstream cmake outputs everything to out/Release/ and has no install()
# targets. We override the output directories to use the cmake binary dir,
# and add install() calls for libraries, headers, and applications.

# 1. Override BINARY_OUTPUT_DIRECTORY to use CMAKE_BINARY_DIR
sed -i 's|set(BINARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../out/${CMAKE_BUILD_TYPE})|set(BINARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/out)|' \
    src/CMakeLists.txt

# 1b. Patch FFTW to use system library instead of bundled copy.
#    ~50 cmake files across libraries, applications, and plugins all use
#    ${FFTW_DIR_LIBS}/lib/libfftw3.so (bundled layout). Replace with system
#    library name 'fftw3' (cmake will find -lfftw3 via system linker).
#    Also fix include paths: bundled uses /api/ subdir, system uses /usr/include/.
find src/ -name CMakeLists.txt -exec \
    sed -i 's|set(FFTW_LIBS ${FFTW_DIR_LIBS}/lib/libfftw3.so)|set(FFTW_LIBS fftw3)|' {} +
find src/ -name CMakeLists.txt -exec \
    sed -i 's|target_include_directories(${PROJECT_NAME} PRIVATE ${FFTW_DIR_INCLUDE}/api)|# system fftw3 headers in standard include path|' {} +

# 2. Fix the git hash commands that fail on non-git source dirs
#    Delete both execute_process blocks (lines 155-164 pattern)
sed -i '/^execute_process($/,/OUTPUT_STRIP_TRAILING_WHITESPACE)$/d' \
    src/CMakeLists.txt

# 3. Remove the symlink-to-resources block entirely (lines 196-end)
#    This block uses cmake_path and execute_process to create symlinks
#    that reference source-tree paths not available at runtime.
sed -i '/^##.*Add symbolic links to project resources/,$d' \
    src/CMakeLists.txt

# 4. Inject SOVERSION into each library CMakeLists.txt
for libcml in src/libraries/*/CMakeLists.txt; do
    libname=$(basename $(dirname "$libcml"))
    # Add VERSION/SOVERSION after the add_library call
    if grep -q 'add_library' "$libcml"; then
        sed -i "/^[[:space:]]*target_compile_definitions/i\\
set_target_properties(\${TARGET_NAME} PROPERTIES VERSION %{version} SOVERSION 2)" \
            "$libcml"
    fi
done

# 5. The upstream library cmake files already have install() targets for
#    libraries and headers. We just need GNUInstallDirs (step 7) and
#    CMAKE_INSTALL_LIBDIR set so they install to the right locations.

# 7. Add GNUInstallDirs to top-level cmake
sed -i '/project(mne_cpp/a include(GNUInstallDirs)' src/CMakeLists.txt

# 8. Inject install() for applications
cat >> src/CMakeLists.txt << 'APP_EOF'

# Fedora: install applications
foreach(app IN ITEMS
    mne_scan mne_analyze mne_anonymize mne_browse
    mne_compute_mne mne_compute_raw_inverse mne_dipole_fit
    mne_edf2fiff mne_flash_bem mne_forward_solution
    mne_inspect mne_inverse_operator mne_make_source_space
    mne_process_raw mne_rt_server mne_setup_forward_model
    mne_setup_mri mne_show_fiff mne_surf2bem mne_watershed_bem)
    if(TARGET ${app})
        install(TARGETS ${app}
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        )
    endif()
endforeach()
APP_EOF

# 9. Fix C++14 to C++17 for GCC 15 compatibility
sed -i 's/set(CMAKE_CXX_STANDARD 14)/set(CMAKE_CXX_STANDARD 17)/' \
    src/CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -Wno-error -fpermissive -include cstdint -Wno-error=format-security"

# Add disp3D_rhi source dir to includes — brainview.h does #include "core/viewstate.h"
# which needs the disp3D_rhi root in the search path when included transitively
export CXXFLAGS="$CXXFLAGS -I$(pwd)/src/libraries/disp3D_rhi"
%cmake -S src -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_APPLICATIONS:BOOL=ON \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DBUILD_TESTS:BOOL=OFF \
    -DUSE_FFTW:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_SKIP_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install

# Some libraries install to /usr/lib/ instead of /usr/lib64/ due to upstream
# cmake install rules. Move any stray libs to the correct location.
if [ -d %{buildroot}%{_prefix}/lib ] && [ "%{_prefix}/lib" != "%{_libdir}" ]; then
    mkdir -p %{buildroot}%{_libdir}
    for f in %{buildroot}%{_prefix}/lib/libmne_*.so*; do
        [ -e "$f" ] && mv "$f" %{buildroot}%{_libdir}/
    done
fi

# Remove bundled Eigen headers — system eigen3-devel provides these
rm -rf %{buildroot}%{_includedir}/Eigen
rm -rf %{buildroot}%{_includedir}/unsupported
rm -f %{buildroot}%{_includedir}/signature_of_eigen3_matrix_library

# Remove stray fiff_explanations.txt installed to wrong location
rm -rf %{buildroot}%{_bindir}/resources

# Install resources needed at runtime (remove broken dev symlinks first)
mkdir -p %{buildroot}%{_datadir}/%{name}
if [ -d resources ]; then
    find resources/ -type l ! -exec test -e {} \; -delete
    cp -a resources/* %{buildroot}%{_datadir}/%{name}/
fi

%ldconfig_scriptlets

%files
%license LICENSE
%doc README.md
%{_bindir}/mne_*
# Libraries install without SOVERSION (upstream lacks VERSION/SOVERSION on all targets;
# our injection only partially works). For now, ship unversioned .so in main package.
%{_libdir}/libmne_*.so
%{_datadir}/%{name}/

%files devel
# Upstream installs headers under include/mne_<libname>/
%{_includedir}/mne_*/

%changelog
* Mon May 04 2026 Morgan Hough <morgan.hough@gmail.com> - 2.2.1-1
- Update to stable release v2.2.1
- Set SOVERSION to 2 for libraries

* Mon Mar 16 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.9^20260304git1daca51-3
- Fix lib/ to lib64/ move: mkdir -p target directory first
- Remove Eigen signature_of_eigen3_matrix_library marker file
- Remove broken dev symlinks from resources before copying

* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.9^20260304git1daca51-2
- Fix cmake parse errors: properly delete git hash execute_process blocks
  and entire resource symlink block (not selective line deletion)

* Wed Mar 04 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.9^20260304git1daca51-1
- Rewrite spec from git snapshot (no releases since v0.1.9 in 2021)
- Use system Eigen3 instead of bundled copy
- Inject SOVERSION 0 on all shared libraries
- Inject cmake install targets (upstream lacks install rules)
- Upgrade C++ standard to C++17 for GCC 15 compatibility
- Split into main and devel subpackages

* Tue Jan 06 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.0-1
- Initial RPM build attempt
