# MNE-CPP has no formal releases since v0.1.9 (2021).
# Use a recent git snapshot from main branch.
%global commit 1daca518d5375aa40be156ef5f9b1f4396a8bee5
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260304

%define debug_package %{nil}

Name:           mne-cpp
Version:        0.1.9^%{snapdate}git%{shortcommit}
Release:        1%{?dist}
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
%autosetup -n mne-cpp-%{commit}

# Remove bundled Eigen — use system copy
rm -rf src/external/eigen-3.4.0

# The upstream cmake outputs everything to out/Release/ and has no install()
# targets. We override the output directories to use the cmake binary dir,
# and add install() calls for libraries, headers, and applications.

# 1. Override BINARY_OUTPUT_DIRECTORY to use CMAKE_BINARY_DIR
sed -i 's|set(BINARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../out/${CMAKE_BUILD_TYPE})|set(BINARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/out)|' \
    src/CMakeLists.txt

# 2. Fix the git hash commands that fail on non-git source dirs
sed -i '/execute_process.*COMMAND git log/,/OUTPUT_STRIP_TRAILING_WHITESPACE)/d' \
    src/CMakeLists.txt

# 3. Remove the symlink to resources (uses source dir paths)
sed -i '/Add symbolic links to project resources/,$ { /execute_process/d; /cmake_path/d; /message.*RESOURCES/d; /set.*RESOURCES/d }' \
    src/CMakeLists.txt

# 4. Inject SOVERSION into each library CMakeLists.txt
for libcml in src/libraries/*/CMakeLists.txt; do
    libname=$(basename $(dirname "$libcml"))
    # Add VERSION/SOVERSION after the add_library call
    if grep -q 'add_library' "$libcml"; then
        sed -i "/^[[:space:]]*target_compile_definitions/i\\
set_target_properties(\${TARGET_NAME} PROPERTIES VERSION 0.1.9 SOVERSION 0)" \
            "$libcml"
    fi
done

# 5. Inject install() targets for libraries
cat >> src/libraries/CMakeLists.txt << 'INSTALL_EOF'

# Fedora: install all MNE-CPP libraries
foreach(tgt IN ITEMS
    mne_utils mne_lsl mne_fiff mne_fs mne_mri mne_mne mne_fwd mne_inverse
    mne_communication mne_rtprocessing mne_connectivity
    mne_events mne_disp mne_disp3D_rhi)
    if(TARGET ${tgt})
        install(TARGETS ${tgt}
            LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
            ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        )
    endif()
endforeach()
INSTALL_EOF

# 6. Inject install() for headers
cat >> src/libraries/CMakeLists.txt << 'HEADERS_EOF'

# Fedora: install headers
set(_mne_lib_dirs utils lsl fiff fs mri mne fwd inverse communication
    rtprocessing connectivity events disp disp3D_rhi)
foreach(libdir IN LISTS _mne_lib_dirs)
    file(GLOB_RECURSE _hdrs
        "${CMAKE_CURRENT_SOURCE_DIR}/${libdir}/*.h"
    )
    foreach(_hdr IN LISTS _hdrs)
        file(RELATIVE_PATH _rel "${CMAKE_CURRENT_SOURCE_DIR}/${libdir}" "${_hdr}")
        get_filename_component(_dest "include/mne-cpp/${libdir}/${_rel}" DIRECTORY)
        install(FILES "${_hdr}" DESTINATION "${_dest}")
    endforeach()
endforeach()
HEADERS_EOF

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
export CXXFLAGS="%{optflags} -Wno-error -fpermissive -include cstdint"
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

# Install resources needed at runtime
mkdir -p %{buildroot}%{_datadir}/%{name}
if [ -d resources ]; then
    cp -a resources/* %{buildroot}%{_datadir}/%{name}/
fi

%ldconfig_scriptlets

%files
%license LICENSE
%doc README.md
%{_bindir}/mne_*
%{_libdir}/libmne_*.so.0*
%{_datadir}/%{name}/

%files devel
%{_libdir}/libmne_*.so
%{_includedir}/mne-cpp/

%changelog
* Wed Mar 04 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.9^20260304git1daca51-1
- Rewrite spec from git snapshot (no releases since v0.1.9 in 2021)
- Use system Eigen3 instead of bundled copy
- Inject SOVERSION 0 on all shared libraries
- Inject cmake install targets (upstream lacks install rules)
- Upgrade C++ standard to C++17 for GCC 15 compatibility
- Split into main and devel subpackages

* Tue Jan 06 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.0-1
- Initial RPM build attempt
