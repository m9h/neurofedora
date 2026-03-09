%define debug_package %{nil}

Name:           medInria
Version:        5.0.1~beta
Release:        0.4%{?dist}
Summary:        Medical image navigation and research tool

License:        BSD-3-Clause
URL:            https://github.com/medInria/medInria-public
Source0:        https://github.com/medInria/medInria-public/archive/refs/tags/V5.0.1beta/medInria-public-V5.0.1beta.tar.gz

BuildRequires:  cmake >= 3.19
BuildRequires:  ninja-build
BuildRequires:  gcc-c++

# Qt5
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtxmlpatterns-devel

# Core dependencies
BuildRequires:  dtk-devel >= 1.7.1
BuildRequires:  InsightToolkit5-devel >= 5.4.5-12
BuildRequires:  InsightToolkit5-vtk-devel >= 5.4.5-12
# Pin to system VTK 9.2.6 (Qt5 GUISupportQt); avoid COPR VTK 9.5.2 (Qt6)
BuildRequires:  vtk-devel < 9.3
BuildRequires:  vtk-qt < 9.3
# java-devel needed because VTK 9.2.6 cmake targets reference JVM include paths
BuildRequires:  java-devel
BuildRequires:  dcmtk-devel
BuildRequires:  TTK-devel >= 4.0.1
BuildRequires:  RPI-devel >= 4.0

# System libraries
BuildRequires:  mesa-libGL-devel
BuildRequires:  hdf5-devel
BuildRequires:  gdcm-devel
BuildRequires:  openssl-devel
BuildRequires:  sqlite-devel

Requires:       qt5-qtbase
Requires:       qt5-qtsvg
Requires:       qt5-qtdeclarative
Requires:       dtk >= 1.7.1

%description
medInria is a free medical image viewer and processing tool developed at
Inria. It provides visualization of 3D/4D medical images, diffusion MRI
processing (tensor estimation, tractography), image registration, and
segmentation tools through a plugin-based architecture.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and cmake config files for medInria development.

%prep
%setup -q -n medInria-public-5.0.1beta

# ---------------------------------------------------------------------------
# All patches apply to src/ (the standalone cmake project, not the superbuild)
# ---------------------------------------------------------------------------

# Strip Windows carriage returns (source has CRLF line endings that break sed $ anchors)
find src/ -name '*.cmake' -o -name '*.cmake.in' | xargs sed -i 's/\r$//'
sed -i 's/\r$//' src/CMakeLists.txt

# Fix hardcoded lib/ install destinations to respect CMAKE_INSTALL_LIBDIR
# Libraries -> CMAKE_INSTALL_LIBDIR (lib64 on x86_64)
sed -i 's|LIBRARY   DESTINATION lib$|LIBRARY   DESTINATION ${CMAKE_INSTALL_LIBDIR}|' \
  src/cmake/module/set_lib_install_rules.cmake
sed -i 's|ARCHIVE   DESTINATION lib$|ARCHIVE   DESTINATION ${CMAKE_INSTALL_LIBDIR}|' \
  src/cmake/module/set_lib_install_rules.cmake
sed -i 's|FRAMEWORK DESTINATION lib$|FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR}|' \
  src/cmake/module/set_lib_install_rules.cmake

# Plugins -> lib64/medInria/plugins{,_legacy}
sed -i 's|LIBRARY DESTINATION bin/plugins\(.*\)|LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/medInria/plugins\1|' \
  src/cmake/module/set_plugin_install_rules.cmake
sed -i 's|RUNTIME DESTINATION bin/plugins\(.*\)|RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}/medInria/plugins\1|' \
  src/cmake/module/set_plugin_install_rules.cmake
sed -i 's|ARCHIVE DESTINATION lib/plugins\(.*\)|ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}/medInria/plugins\1|' \
  src/cmake/module/set_plugin_install_rules.cmake

# cmake config install paths in set_lib_install_rules.cmake
# (only install-time DESTINATION lines, not build-tree CMAKE_BINARY_DIR refs)
sed -i 's|INSTALL_DESTINATION lib/cmake/|INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|g' \
  src/cmake/module/set_lib_install_rules.cmake
sed -i '/ConfigPackageLocation/s|lib/cmake/|${CMAKE_INSTALL_LIBDIR}/cmake/|' \
  src/cmake/module/set_lib_install_rules.cmake
sed -i '/DESTINATION.*lib\/cmake/s|DESTINATION lib/cmake/|DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|' \
  src/cmake/module/set_lib_install_rules.cmake

# cmake config install paths in top-level CMakeLists.txt
sed -i 's|INSTALL_DESTINATION lib/cmake/|INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|' \
  src/CMakeLists.txt
sed -i 's|DESTINATION          lib/cmake/|DESTINATION          ${CMAKE_INSTALL_LIBDIR}/cmake/|g' \
  src/CMakeLists.txt
# cmake module dir -> share/cmake/medInria/ (noarch data)
sed -i 's|DESTINATION          cmake/)|DESTINATION          share/cmake/medInria/)|' \
  src/CMakeLists.txt

# Remove -Wformat=0 which conflicts with Fedora's -Werror=format-security (GCC 15)
sed -i '/Wformat=0/d' src/CMakeLists.txt

# Shim vtkLegacyReaderVersion.h (VTK 9.3+ only): define version constants for VTK 9.2
sed -i 's|#include <vtkLegacyReaderVersion.h>|// VTK 9.2 lacks vtkLegacyReaderVersion.h; define constants\nstatic constexpr int vtkLegacyReaderMajorVersion = 5;\nstatic constexpr int vtkLegacyReaderMinorVersion = 1;|' \
  src/layers/legacy/medVtkDataMeshBase/vtkMetaSurfaceMesh.cxx \
  src/layers/legacy/medVtkDataMeshBase/vtkMetaVolumeMesh.cxx

# Fix plugin search paths: upstream uses paths relative to the binary (bin/plugins,
# bin/plugins_legacy) which don't work with FHS lib64 install layout.
# Patch both the new-style (medApplication.cpp) and legacy (medPluginManager.cpp)
# plugin managers to use the correct absolute paths.
# New-style plugins (medApplication.cpp line 195)
sed -i 's|plugins_dir = qApp->applicationDirPath() + "/plugins";|plugins_dir = QString("%{_libdir}/medInria/plugins");|' \
  src/app/medInria/medApplication.cpp
# Legacy plugins (medPluginManager.cpp line 77)
sed -i 's|plugins_dir = qApp->applicationDirPath() + "/plugins_legacy";|plugins_dir = QString("%{_libdir}/medInria/plugins_legacy");|' \
  src/layers/medCore/legacy/medPluginManager.cpp

%build
# dtk cmake config omits dtkMathSupport/dtkVrSupport include dirs
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive -I/usr/include/dtkMathSupport -I/usr/include/dtkVrSupport"

# Build from src/ subdirectory (self-contained cmake project, not superbuild)
cd src
%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -Ddtk_DIR=%{_libdir}/cmake/dtk \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4 \
    -DDCMTK_DIR=%{_libdir}/cmake/dcmtk \
    -DTTK_DIR=%{_libdir}/cmake/TTK \
    -DRPI_DIR=%{_libdir}/cmake/RPI \
    -DUSE_Python=OFF \
    -DUSE_DTKIMAGING=OFF \
    -DUSE_OSPRay=OFF \
    -DUSE_FFmpeg=OFF \
    -DBUILD_ALL_PLUGINS=ON \
    -DBUILD_EXAMPLE_PLUGINS=OFF \
    -DBUILD_COMPOSITEDATASET_PLUGIN=OFF \
    -DmedInria_BUILD_TESTS=OFF \
    -DmedInria_BUILD_DOCUMENTATION=OFF

%cmake_build

%install
cd src
%cmake_install
cd ..

# Remove any qt.conf deploy artifact (not needed for system Qt)
rm -f %{buildroot}%{_bindir}/qt.conf

# Move any libraries that landed in /usr/lib to /usr/lib64 (fallback for missed patches)
if [ -d %{buildroot}%{_prefix}/lib ] && [ "%{_lib}" != "lib" ]; then
    find %{buildroot}%{_prefix}/lib -name '*.so*' -exec mv -t %{buildroot}%{_libdir}/ {} + 2>/dev/null || true
    # Move cmake configs from /usr/lib/cmake/ to /usr/lib64/cmake/
    if [ -d %{buildroot}%{_prefix}/lib/cmake ]; then
        cp -a %{buildroot}%{_prefix}/lib/cmake/* %{buildroot}%{_libdir}/cmake/ 2>/dev/null || true
        rm -rf %{buildroot}%{_prefix}/lib/cmake
    fi
    # Clean up empty /usr/lib if possible
    find %{buildroot}%{_prefix}/lib -type d -empty -delete 2>/dev/null || true
fi

%ldconfig_scriptlets

%files
%license LICENSE.txt
%doc LICENSES_EXT.txt
%{_bindir}/medInria
%{_libdir}/libmed*.so
%{_libdir}/medInria/
# cmake module files (noarch build helpers)
%{_datadir}/cmake/medInria/

%files devel
%{_includedir}/med*/
%{_libdir}/cmake/med*/

%changelog
* Thu Mar 06 2026 Morgan Hough <morgan.hough@gmail.com> - 5.0.1~beta-0.3
- Add BuildRequires on InsightToolkit5-vtk-devel for ITKVtkGlue cmake module
* Wed Mar 05 2026 Morgan Hough <morgan.hough@gmail.com> - 5.0.1~beta-0.2
- Fix CRLF line endings breaking sed patches (libraries landing in /usr/lib)
- Fix FRAMEWORK DESTINATION lib not patched
- Fix top-level CMakeLists.txt cmake config install paths
- Add fallback install fixup for any remaining lib/ vs lib64/ issues

* Tue Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 5.0.1~beta-0.1
- Initial package for medInria V5.0.1beta
- Build src/ directly, bypassing the superbuild
- System dependencies: Qt5, ITK 5.4.5 with VtkGlue, VTK 9.2.6, dtk 1.7.1,
  TTK 4.0.1, RPI 4.0, DCMTK
- Disable Python, dtkImaging, FFmpeg, OSPRay
