# Disable LTO - causes linker issues with system ITK/VTK on F43
%global _lto_cflags %{nil}

# Limit parallelism to prevent OOM on builds
%global _smp_mflags -j4

Name:           mitk
Version:        2025.12.2
Release:        3%{?dist}
Summary:        Medical Imaging Interaction Toolkit

License:        BSD-3-Clause
URL:            https://www.mitk.org/
Source0:        https://github.com/MITK/MITK/archive/v%{version}/MITK-%{version}.tar.gz
# CMake find modules for system libraries that lack CMake config files
Source1:        FindANN.cmake
Source2:        FindQt6Qwt6.cmake
Source3:        Findlz4.cmake

# MITK embeds a heavily modified fork of CppMicroServices (v2.99.0) in
# Modules/CppMicroServices/. This is NOT the same as the standalone
# CppMicroServices 3.x in Fedora; it cannot be unbundled.
Provides:       bundled(CppMicroServices) = 2.99.0

# Core build tools
BuildRequires:  cmake >= 3.22
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  make
BuildRequires:  git

# The Big Two (from mhough/neurofedora COPR)
# Fedora's InsightToolkit is stuck at 4.13.3; MITK requires ITK 5.x
# Fedora's VTK is 9.2.6; MITK needs 9.3+
BuildRequires:  InsightToolkit5-devel >= 5.4
BuildRequires:  vtk-devel >= 9.5

# Qt6 (MITK requires >= 6.6)
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-qtwebengine-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtscxml-devel
BuildRequires:  qt6-linguist

# System libraries to unbundle from MITK superbuild
BuildRequires:  boost-devel
BuildRequires:  dcmtk-devel >= 3.6.7
BuildRequires:  gdcm-devel
BuildRequires:  hdf5-devel
BuildRequires:  poco-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  tinyxml2-devel
BuildRequires:  ann-devel
BuildRequires:  lz4-devel
BuildRequires:  zlib-devel
BuildRequires:  eigen3-devel
BuildRequires:  cpp-httplib-devel
BuildRequires:  qwt-qt6-devel

# VTK transitive deps (VTK's cmake config requires these at find_package time)
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  python3-devel
BuildRequires:  json-devel
BuildRequires:  xz-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  proj-devel
BuildRequires:  libxml2-devel

# Other build dependencies
BuildRequires:  openssl-devel >= 3.0
BuildRequires:  tbb-devel
BuildRequires:  pcre2-devel
BuildRequires:  libXt-devel
BuildRequires:  libXext-devel
BuildRequires:  libXrender-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  libglvnd-devel

# ITK transitive deps (needed for cmake find_package)
BuildRequires:  fftw-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  expat-devel
BuildRequires:  double-conversion-devel
BuildRequires:  openjpeg2-devel
BuildRequires:  libminc-devel

%description
The Medical Imaging Interaction Toolkit (MITK) is a free open-source software
system for development of interactive medical image processing software.
MITK combines the Insight Toolkit (ITK) and the Visualization Toolkit (VTK)
with an application framework for medical imaging.

This package provides the core MITK libraries without the Workbench application
(BlueBerry/CTK require Qt6 CTK which is not yet available in Fedora).

%package devel
Summary:        Development files for MITK
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       InsightToolkit5-devel
Requires:       vtk-devel
Requires:       boost-devel
Requires:       dcmtk-devel

%description devel
Development files, headers, and CMake config for building applications
and plugins that use the MITK libraries.

%prep
%autosetup -n MITK-%{version}

# Install CMake find modules for system libs without CMake configs
cp %{SOURCE1} CMake/FindANN.cmake
cp %{SOURCE2} CMake/FindQt6Qwt6.cmake
cp %{SOURCE3} CMake/Findlz4.cmake

# Fix ZLIB config mode failure on Fedora (zlib-ng-compat ships a broken config
# that references ZLIB::ZLIBSTATIC which doesn't exist without static libs).
# Pre-find ZLIB via module mode and mark as found before the EP loop runs.
sed -i '/^get_property(MITK_EXTERNAL_PROJECTS GLOBAL PROPERTY MITK_EXTERNAL_PROJECTS)/i \
find_package(ZLIB REQUIRED MODULE)\
set(ZLIB_FOUND TRUE)' CMakeLists.txt
# Also prevent the EP loop from re-finding ZLIB in CONFIG mode by removing ZLIB
# from the external projects list.
sed -i '/^get_property(MITK_EXTERNAL_PROJECTS GLOBAL PROPERTY MITK_EXTERNAL_PROJECTS)/a \
list(REMOVE_ITEM MITK_EXTERNAL_PROJECTS ZLIB)' CMakeLists.txt

# Fix ITK PhilipsREC IO factory: MITK defines ITK_IO_FACTORY_REGISTER_MANAGER
# which triggers auto-registration of ALL IO factories including PhilipsREC.
# But MitkCore doesn't list IOPhilipsREC in PACKAGE_DEPENDS, so the factory
# registration symbol is unresolved. Add it to the IO modules list.
sed -i 's|IOBioRad+IOBMP|IOBioRad+IOBMP+IOPhilipsREC|' Modules/Core/CMakeLists.txt

# Fix LZ4 target name: VTK's FindLZ4 creates LZ4::LZ4 but MITK
# expects LZ4::lz4_shared from its superbuild
sed -i 's/LZ4::lz4_shared/LZ4::LZ4/g' Modules/DataTypesExt/CMakeLists.txt

# Remove bundled libraries that we use from system
# (Keep CppMicroServices - it's a modified fork we must bundle)

%build
# --- GCC 15 / Fedora 43 Fixes ---
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint -Wno-error=template-id-cdtor"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17"

# Unset env vars to prevent Conda/system tool interference
unset CC CXX LDFLAGS CONDA_PREFIX CONDA_DEFAULT_ENV CMAKE_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DMITK_BUILD_EXAMPLES=OFF \
    \
    -DCMAKE_MODULE_PATH=%{_builddir}/MITK-%{version}/CMake \
    -DMITK_USE_SUPERBUILD=OFF \
    -DMITK_BUILD_CONFIGURATION=Custom \
    \
    -DMITK_USE_Qt6=ON \
    \
    -DMITK_USE_SYSTEM_Boost=ON \
    \
    -DMITK_USE_BLUEBERRY=OFF \
    -DMITK_USE_CTK=OFF \
    \
    -DMITK_USE_DCMQI=OFF \
    -DMITK_USE_MatchPoint=OFF \
    -DMITK_USE_ACVD=OFF \
    \
    -DMITK_USE_Python3=OFF \
    -DMITK_USE_SWIG=OFF \
    -DMITK_USE_CppUnit=OFF \
    \
    -DMITK_USE_OpenMP=ON \
    -DMITK_USE_DCMTK=ON \
    -DMITK_USE_httplib=ON \
    \
    -DITK_DIR=%{_libdir}/cmake/ITK-5.4 \
    -DVTK_DIR=%{_libdir}/cmake/vtk \
    -DDCMTK_DIR=%{_libdir}/cmake/dcmtk \

%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libMitk*.so.*
%{_libdir}/mitk/

%files devel
%{_includedir}/mitk*/
%{_libdir}/libMitk*.so
%{_libdir}/cmake/MITK*/

%changelog
* Thu Mar 19 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-3
- Remove incorrect eigen3-devel Requires from -devel subpackage
  (MITK gets Eigen through ITK5 which bundles it)

* Thu Mar 19 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-2
- Fix ITK PhilipsREC IO factory linkage (add IOPhilipsREC to MitkCore deps)

* Mon Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-1
- Major rewrite: disable superbuild, use system libraries
- Use InsightToolkit5 5.4.5 and VTK 9.5.2 from COPR
- Disable BlueBerry/CTK (Fedora CTK is Qt5-only)
- Phase 1: core libraries only, no MitkWorkbench
- GCC 15 / Fedora 43 compatibility fixes
