%define debug_package %{nil}

Name:           RPI
Version:        4.0
Release:        3%{?dist}
Summary:        Registration Programming Interface (INRIA)

License:        BSD-3-Clause
URL:            https://github.com/medInria/RPI
Source0:        https://github.com/medInria/RPI/archive/refs/tags/v%{version}/RPI-%{version}.tar.gz

BuildRequires:  cmake >= 3.24
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  hdf5-devel
# RPI itself doesn't use VTK (grep confirms 0 vtk* type references). The
# transitive vtk-devel BR is for ITK's VtkGlue cmake-config which
# find_package(VTK) at configure time. F44 ships VTK 9.5.x in system
# and our COPR ships 9.5.2 — both satisfy this transitive need.
BuildRequires:  vtk-devel
BuildRequires:  python3-devel
BuildRequires:  java-devel

%description
RPI (Registration Programming Interface) provides a common framework for
image registration methods built on ITK. It includes header-only libraries
for registration transforms and common tools used by medInria.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}
Requires:       InsightToolkit5-devel >= 5.4.5

%description devel
Headers and cmake config files for RPI.

%prep
%autosetup -n RPI-%{version}

# Fix hardcoded lib/ install destinations to respect CMAKE_INSTALL_LIBDIR
sed -i 's|LIBRARY   DESTINATION lib$|LIBRARY   DESTINATION ${CMAKE_INSTALL_LIBDIR}|' cmake/export_and_install_libs.cmake
sed -i 's|ARCHIVE   DESTINATION lib$|ARCHIVE   DESTINATION ${CMAKE_INSTALL_LIBDIR}|' cmake/export_and_install_libs.cmake
sed -i 's|INSTALL_DESTINATION lib/cmake/|INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|' cmake/export_and_install_libs.cmake
sed -i '/^SET(ConfigPackageLocation/s|lib/cmake/|${CMAKE_INSTALL_LIBDIR}/cmake/|' cmake/export_and_install_libs.cmake
sed -i '/DESTINATION lib\/cmake/s|lib/cmake/|${CMAKE_INSTALL_LIBDIR}/cmake/|' cmake/export_and_install_libs.cmake
# Fix top-level CMakeLists.txt install paths
sed -i 's|INSTALL_DESTINATION lib/cmake/|INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|' CMakeLists.txt
sed -i 's|DESTINATION lib/cmake/|DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|' CMakeLists.txt
sed -i 's|DESTINATION  lib/cmake/|DESTINATION  ${CMAKE_INSTALL_LIBDIR}/cmake/|' CMakeLists.txt

# Fix itkTypeMacro wrong class name (GCC 15 -Wtemplate-body)
sed -i 's/itkTypeMacro( StationaryVelocityField,/itkTypeMacro( StationaryVelocityFieldTransform,/' \
  src/RegistrationAddOn/itkStationaryVelocityFieldTransform.h

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"

%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4 \
    -DBUILD_SHARED_LIBS=ON \
    -DRPI_BUILD_EXAMPLES=OFF \
    -DBUILD_ConvertLinearToDF=OFF \
    -DBUILD_ConvertLinearToSVF=OFF \
    -DBUILD_FuseTransformations=OFF \
    -DBUILD_ResampleImage=OFF \
    -DBUILD_RegistrationAddOn=OFF \
    -DBUILD_examples=OFF \
    -DBUILD_DOCUMENTATION=OFF \
    -DTCLAP_FETCH=OFF \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON

%cmake_build

%install
%cmake_install

%files
# RPI common is header-only (INTERFACE library), no shared libraries
# License is BSD-3-Clause per CMakeLists.txt header (no separate LICENSE file)

%files devel
%{_includedir}/common/
%{_includedir}/RegistrationAddOn/
%{_includedir}/examples/
%{_libdir}/cmake/RPI/
%{_libdir}/cmake/common/

%changelog
* Tue May 19 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0-3
- Drop vtk-devel < 9.3 BR (was defensive for the medInria chain's Qt5
  pin; RPI itself has zero VTK API usage — grep confirmed). F44 system
  VTK 9.5.x satisfies the ITK-VtkGlue transitive find_package needs.
- Bump InsightToolkit5-devel requirement to 5.4.6

* Tue Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0-2
- Fix itkTypeMacro wrong class name in itkStationaryVelocityFieldTransform.h

* Tue Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0-1
- Initial package for RPI 4.0
- Header-only library for medInria registration interface
- Disable all executables for library-only package
