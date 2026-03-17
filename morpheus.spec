%define debug_package %{nil}

Name:           morpheus
Version:        2.3.7
Release:        2%{?dist}
Summary:        Modeling environment for multicellular systems biology

License:        BSD-3-Clause
URL:            https://morpheus.gitlab.io
Source0:        morpheus-%{version}.tar.gz
# Bundled header-only libraries (Fedora 43 xtensor 0.27.0 has incompatible
# header layout — restructured include/ hierarchy breaks Morpheus includes)
Source1:        xtl-0.7.5.tar.gz
Source2:        xsimd-10.0.0.tar.gz
Source3:        xtensor-0.24.6.tar.gz

BuildRequires:  cmake >= 3.5
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  boost-devel
BuildRequires:  pugixml-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  libtiff-devel
BuildRequires:  libxslt
BuildRequires:  libxml2
BuildRequires:  doxygen

# GUI subpackage dependencies
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtwebengine-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libsbml-devel

Requires:       gnuplot

Provides:       bundled(muParser)
Provides:       bundled(gnuplot_i)
Provides:       bundled(tiny-process-library)
Provides:       bundled(xtensor) = 0.24.6
Provides:       bundled(xtl) = 0.7.5
Provides:       bundled(xsimd) = 10.0.0

%description
Morpheus is a modeling and simulation environment for the study of
multi-scale and multicellular systems. It includes simulators for ODEs,
PDEs, and cellular Potts models (CPM). Models are defined in XML
(MorpheusML) without programming.

This package provides the command-line simulator.

%package        gui
Summary:        Graphical user interface for Morpheus
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       gnuplot
Requires:       qt5-qtbase
Requires:       qt5-qtsvg

%description    gui
Graphical modeling and simulation environment for Morpheus. Provides a
GUI for creating, editing, running, and visualizing multicellular
models.

%prep
%autosetup -n morpheus-%{version}

# Morpheus bundles muParser, gnuplot_i, tiny-process-lib, qtsingleapp.
# Fedora 43 xtensor 0.27.0 restructured its include layout (xtensor/containers/
# instead of xtensor/) making it incompatible with Morpheus.  Bundle the
# versions Morpheus was developed against (all header-only, MIT/BSD).

# Extract bundled xtensor-stack headers alongside the source tree
tar xzf %{SOURCE1} -C 3rdparty/
tar xzf %{SOURCE2} -C 3rdparty/
tar xzf %{SOURCE3} -C 3rdparty/

# Disable system xtensor detection — force bundled path
sed -i 's/FIND_PACKAGE(xtensor QUIET)/# FIND_PACKAGE(xtensor QUIET)/' 3rdparty/CMakeLists.txt
sed -i 's/IF(\${xtensor_DIR} STREQUAL "xtensor_DIR-NOTFOUND" )/IF(TRUE)/' 3rdparty/CMakeLists.txt

# Replace xtl download with local header copy
cat > 3rdparty/xtl/CMakeLists.txt << 'XTLEOF'
SET(XTL_INCLUDE_DIR ${CMAKE_BINARY_DIR}/3rdparty/include)
add_library(xtl INTERFACE)
target_include_directories(xtl INTERFACE ${XTL_INCLUDE_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/3rdparty/xtl-0.7.5/include/xtl
     DESTINATION ${XTL_INCLUDE_DIR})
message(STATUS "Using bundled xtl from ${XTL_INCLUDE_DIR}/xtl")
XTLEOF

# Replace xsimd download with local header copy
cat > 3rdparty/xsimd/CMakeLists.txt << 'XSIMDEOF'
SET(XSIMD_INCLUDE_DIR ${CMAKE_BINARY_DIR}/3rdparty/include)
add_library(xsimd INTERFACE)
target_include_directories(xsimd INTERFACE ${XSIMD_INCLUDE_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/3rdparty/xsimd-10.0.0/include/xsimd
     DESTINATION ${XSIMD_INCLUDE_DIR})
message(STATUS "Using bundled xsimd from ${XSIMD_INCLUDE_DIR}/xsimd")
XSIMDEOF

# Replace xtensor download with local header copy
cat > 3rdparty/xtensor/CMakeLists.txt << 'XTENSOREOF'
SET(XTENSOR_INCLUDE_DIR ${CMAKE_BINARY_DIR}/3rdparty/include)
add_library(xtensor INTERFACE)
target_include_directories(xtensor INTERFACE ${XTENSOR_INCLUDE_DIR})
target_compile_definitions(xtensor INTERFACE XTENSOR_USE_XSIMD=1 XTENSOR_OPENMP_TRESHOLD=1000)
target_link_libraries(xtensor INTERFACE xsimd xtl)
file(COPY ${CMAKE_SOURCE_DIR}/3rdparty/xtensor-0.24.6/include/xtensor
     DESTINATION ${XTENSOR_INCLUDE_DIR})
message(STATUS "Using bundled xtensor from ${XTENSOR_INCLUDE_DIR}/xtensor")
XTENSOREOF

# Disable xtensor download option
sed -i 's/OPTION(DOWNLOAD_XTENSOR "Download latest xtensor source" ON)/OPTION(DOWNLOAD_XTENSOR "Download latest xtensor source" OFF)/' CMakeLists.txt

# Fix static Boost linkage: upstream sets Boost_USE_STATIC_LIBS ON when BUILD_TESTING=OFF
# Fedora does not ship static Boost libs by default — force dynamic linking
sed -i 's/Boost_USE_STATIC_LIBS ON/Boost_USE_STATIC_LIBS OFF/' CMakeLists.txt morpheus/CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -std=c++17"

%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DMORPHEUS_GUI=ON \
    -DBUILD_TESTING=OFF \
    -DDOWNLOAD_XTENSOR=OFF \
    -DMORPHEUS_STATIC_BUILD=OFF \
    -DMORPHEUS_OPENMP=ON

%cmake_build

%install
%cmake_install

# Install desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/morpheus.desktop || true

%files
%license LICENSE.md
%{_bindir}/morpheus

%files gui
%{_bindir}/morpheus-gui
%{_datadir}/applications/morpheus.desktop
%{_datadir}/icons/hicolor/scalable/apps/morpheus.svg
%dir %{_datadir}/morpheus
%{_datadir}/morpheus/

%changelog
* Sat Mar 14 2026 Morgan Hough <mhough@fedoraproject.org> - 2.3.7-2
- Bundle xtensor/xtl/xsimd 0.24.6/0.7.5/10.0.0 (Fedora 43 xtensor 0.27.0 incompatible headers)
- Add doxygen BuildRequires (GUI appdoc)

* Sat Mar 14 2026 Morgan Hough <mhough@fedoraproject.org> - 2.3.7-1
- Initial Fedora/COPR package
- Replaced bundled xmlParser (AFPL) with pugixml (MIT) via xml_compat wrapper
- Provides: bundled(muParser), bundled(gnuplot_i), bundled(tiny-process-library)
