%define debug_package %{nil}

# Half the cores of a 16-core system for mock builds
%global _smp_mflags -j8

Name:           freesurfer
Version:        8.2.0
Release:        1%{?dist}
Summary:        Neuroimaging analysis and visualization suite (CLI tools)

# FreeSurfer Software License Agreement v1.0 — custom permissive license from MGH
# Allows redistribution with conditions; not OSI-approved
License:        FreeSurfer
URL:            https://surfer.nmr.mgh.harvard.edu/
Source0:        https://github.com/freesurfer/freesurfer/archive/refs/tags/v%{version}.tar.gz#/freesurfer-%{version}.tar.gz

# Recognize Fedora in host_os(), set system library flags, VTK/ITK paths
Patch0:         freesurfer-fedora-host-os.patch

BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  libX11-devel
BuildRequires:  libXmu-devel
BuildRequires:  libXt-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  expat-devel
BuildRequires:  libxml2-devel
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  freeglut-devel
BuildRequires:  libXi-devel
BuildRequires:  vtk-devel
BuildRequires:  InsightToolkit5-devel
BuildRequires:  xxd

# Bundled libraries — these have FreeSurfer-specific modifications or are not
# separately packaged in Fedora. Unbundle as Fedora packages become available.
Provides:       bundled(minc)
Provides:       bundled(netcdf)
Provides:       bundled(nifti)
Provides:       bundled(gifti)
Provides:       bundled(dicom)
Provides:       bundled(dcm2niix)
Provides:       bundled(cephes)
Provides:       bundled(tetgen)
Provides:       bundled(nrrdio)
Provides:       bundled(svm-light)
Provides:       bundled(glut)

%description
FreeSurfer is an open source software suite for processing and analyzing
human brain MRI images. This package provides the core command-line tools
used in the recon-all processing stream.

This is a minimal CLI-only build (no freeview or other GUI tools).

%prep
%autosetup -p0 -n freesurfer-%{version}

# GCC 15: fix K&R-style empty parameter lists in bundled CTN DICOM
sed -i 's/COND_ExtractConditions(CTNBOOLEAN(\*callback) ())/COND_ExtractConditions(CTNBOOLEAN(*callback) (CONDITION, const char*))/' \
    packages/dicom/condition.h
sed -i 's/COND_EstablishCallback(void (\*callback) ())/COND_EstablishCallback(void (*callback) (CONDITION, const char*))/' \
    packages/dicom/condition.h
sed -i 's/LST_Sort(LST_HEAD \*\* list, size_t nodeSize, int (\*compare) ())/LST_Sort(LST_HEAD ** list, size_t nodeSize, int (*compare) (LST_NODE*, LST_NODE*))/' \
    packages/dicom/lst.h

# GCC 15 defaults to -std=gnu23 which rejects K&R-style empty parameter lists
# and implicit function declarations throughout the bundled C libraries.
# Add -std=gnu89 to the bundled packages build to allow old-style C code.
sed -i 's/add_compile_options(-w -fPIC)/add_compile_options(-w -fPIC -std=gnu89)/' \
    packages/CMakeLists.txt

# Remove bundled glut from build — we use system freeglut via GLUT_SYSLIBS=ON
sed -i '/^  glut$/d' packages/CMakeLists.txt

# vtkutils uses legacy VTK_INCLUDE_DIRS which is empty in VTK 9.5+.
# Use modern VTK cmake targets instead.
sed -i 's/target_link_libraries(vtkutils tiff)/target_link_libraries(vtkutils tiff VTK::CommonCore VTK::CommonDataModel VTK::RenderingCore VTK::RenderingOpenGL2 VTK::FiltersCore VTK::FiltersSources VTK::ImagingCore)/' \
    vtkutils/CMakeLists.txt

# VTK 9.5: VTK_LEGACY(SetColorSpaceToHSVNoWrap) removed in modern VTK;
# comment out both the declaration in .h and the definition in .cxx
sed -i 's/VTK_LEGACY(void SetColorSpaceToHSVNoWrap())/\/\/ VTK_LEGACY removed/' \
    vtkutils/vtkRGBATransferFunction.h
sed -i '/^void vtkRGBATransferFunction::SetColorSpaceToHSVNoWrap/,/^}/s/^/\/\//' \
    vtkutils/vtkRGBATransferFunction.cxx

# Remove install(CODE) blocks that hardcode CMAKE_INSTALL_PREFIX:
# 1. build-stamp.txt (single line in top-level CMakeLists.txt)
sed -i '/^install(CODE.*build-stamp/d' CMakeLists.txt
# 2. Python symlink calls in top-level CMakeLists.txt
sed -i '/symlink(.*python.*bin.*python3)/d' CMakeLists.txt
# 3. Python subdir: gut the entire file — we don't distribute fspython
echo "# Disabled for RPM build — no fspython" > python/CMakeLists.txt
# 4. Fix install_configured() to respect DESTDIR
sed -i 's|\${CMAKE_INSTALL_PREFIX}/\${INSTALL_DESTINATION}|$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/\${INSTALL_DESTINATION}|g' cmake/functions.cmake
# 5. Replace install_append_help() with a version that doesn't run cmake --build
#    at install time. Just install the configured script and the helptext XML.
sed -i '/^function(install_append_help/,/^endfunction()/c\
function(install_append_help SCRIPT HELPTEXT DESTINATION)\
  install_configured(${SCRIPT} DESTINATION ${DESTINATION})\
  install(FILES ${HELPTEXT} DESTINATION docs/xml)\
  add_test(${SCRIPT}_help_test bash -c "xmllint --noout ${CMAKE_CURRENT_SOURCE_DIR}/${HELPTEXT}")\
endfunction()' cmake/functions.cmake

%build
export CFLAGS="%{optflags} -Wno-error"
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error -include cstdint -fpermissive"
export FFLAGS="%{optflags} -fallow-invalid-boz -fallow-argument-mismatch"

%cmake -GNinja \
    -DMINIMAL=ON \
    -DBUILD_GUIS=OFF \
    -DDISTRIBUTE_FSPYTHON=OFF \
    -DINSTALL_PYTHON_DEPENDENCIES=OFF \
    -DTIFF_SYSLIBS=ON \
    -DGLUT_SYSLIBS=ON \
    -DMARTINOS_BUILD=OFF \
    -DWARNING_AS_ERROR=OFF \
    -DBUILD_FORTRAN=ON \
    -DINTEGRATE_SAMSEG=ON \
    -DLINK_SHARED_AS_NEEDED=ON \
    -DVTK_DIR=%{_libdir}/cmake/vtk \
    -DITK_DIR=%{_libdir}/cmake/ITK-5.4 \
    -DCMAKE_INSTALL_PREFIX=%{_prefix}/lib/freesurfer

%cmake_build

%install
# Skip atlas/average data extraction — not included in GitHub source tarball
rm -f %{__cmake_builddir}/distribution/average/cmake_install.cmake
touch %{__cmake_builddir}/distribution/average/cmake_install.cmake

# Empty the python cmake_install — we don't distribute fspython
echo "" > %{__cmake_builddir}/python/cmake_install.cmake

# Remove ALL cmake install files that try to run pip or reference fspython.
# Empty them entirely — these subdirs only install python packages we don't need.
find %{__cmake_builddir} -name cmake_install.cmake -exec \
    grep -l 'fspython\|pip install\|python3\.8' {} + | \
    while read f; do echo "# Cleared for RPM build" > "$f"; done

# Fix generated cmake_install files: install(CODE) blocks baked the literal prefix
# into file(MAKE_DIRECTORY), configure_file(), execute_process, and message() calls.
# Add DESTDIR prefix to all bare /usr/lib/freesurfer references in these cmake commands.
find %{__cmake_builddir} -name cmake_install.cmake \
    -exec sed -i '/file(MAKE_DIRECTORY\|configure_file\|execute_process\|message(STATUS/s|/usr/lib/freesurfer|$ENV{DESTDIR}/usr/lib/freesurfer|g' {} +

%cmake_install

%files
%license LICENSE.txt
%{_prefix}/lib/freesurfer/

%changelog
* Wed Mar 25 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-1
- Initial Fedora package of FreeSurfer 8.2.0 CLI tools
- MINIMAL build: core recon-all stream programs only, no GUI tools
- Uses system VTK 9.5.2 (COPR) and ITK 5.4.5 (COPR)
- Uses system zlib, openssl, libtiff, libjpeg, libpng, expat, libxml2, blas, lapack
- Bundles: minc, netcdf, nifti, gifti, dicom, dcm2niix, cephes, tetgen, nrrdio, svm, glut
