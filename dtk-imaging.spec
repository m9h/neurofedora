%define commit 9e7cecf64c4144ed3750f9a0604554333faba59f
%define shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           dtk-imaging
Version:        0.1.0
Release:        1%{?dist}
Summary:        Medical imaging algorithms based on dtk
License:        BSD
URL:            https://github.com/medInria/dtk-imaging
Source0:        dtk-imaging-%{commit}.tar.gz
Source1:        xtl-0.7.5.tar.gz
Source2:        xtensor-0.24.7.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  dtk-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  vtk-devel
BuildRequires:  InsightToolkit-devel

%description
dtk-imaging provides core imaging data structures and algorithms.

%prep
%setup -q -n dtk-imaging-%{commit}
%setup -q -T -D -a 1 -n dtk-imaging-%{commit}
%setup -q -T -D -a 2 -n dtk-imaging-%{commit}

# ---------------------------------------------------------
# FIX 1: API Mismatch - Rename dtkCoreObjectManager -> dtkObjectManager
# ---------------------------------------------------------
sed -i 's/dtkCoreObjectManager/dtkObjectManager/g' src/dtkImagingCore/dtkImaging.cpp

# ---------------------------------------------------------
# FIX 2: Header Include Style
# ---------------------------------------------------------
# Replace the missing specific header with the module header
grep -rl "#include <dtkWidgetsWidget>" . | xargs sed -i 's|#include <dtkWidgetsWidget>|#include <dtkWidgets>|g'

# ---------------------------------------------------------
# FIX 3: Forwarding Header for xarray.hpp
# ---------------------------------------------------------
mkdir -p local_include/xtensor
echo '#include "xtensor/containers/xarray.hpp"' > local_include/xtensor/xarray.hpp

# ---------------------------------------------------------
# FIX 4: Shadow broken system dtkWidgets header
# ---------------------------------------------------------
mkdir -p local_include/dtkWidgets
cp /usr/include/dtkWidgets/dtkWidgets local_include/dtkWidgets/
sed -i '/dtkDistributedGuiApplication.h/d' local_include/dtkWidgets/dtkWidgets

# ---------------------------------------------------------
# FIX 5: Rename Missing Class (dtkWidgetsWidget -> QWidget)
# ---------------------------------------------------------
# The class dtkWidgetsWidget was removed in dtk 1.7.1. 
# We assume it was just a wrapper around QWidget.
grep -rl "dtkWidgetsWidget" src | xargs sed -i 's/dtkWidgetsWidget/QWidget/g'

%build
# We add -I.../local_include/dtkWidgets so the compiler finds our patched "dtkWidgets" 
# header before looking in /usr/include.
export CXXFLAGS="%{optflags} \
  -I$(pwd)/xtl-0.7.5/include \
  -I$(pwd)/xtensor-0.24.7/include \
  -I$(pwd)/local_include \
  -I$(pwd)/local_include/dtkWidgets \
  -I%{_includedir}/dtk \
  -I%{_includedir}/dtkCore \
  -I%{_includedir}/dtkLog \
  -I%{_includedir}/dtkMath \
  -I%{_includedir}/dtkMeta \
  -I%{_includedir}/dtkWidgets \
  -I%{_includedir} \
  -idirafter %{_includedir}"

%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DdtkCore_DIR=%{_libdir}/cmake/dtk \
    -DdtkLog_DIR=%{_libdir}/cmake/dtk \
    -DdtkMath_DIR=%{_libdir}/cmake/dtk \
    -DdtkMeta_DIR=%{_libdir}/cmake/dtk \
    -DdtkFonts_DIR=%{_libdir}/cmake/dtk \
    -DdtkWidgets_DIR=%{_libdir}/cmake/dtk \
    -DdtkThemes_DIR=%{_libdir}/cmake/dtk \
    -DdtkSettings_DIR=%{_libdir}/cmake/dtk \
    -Dxtl_DIR=%{_libdir}/cmake/xtl \
    -Dxtensor_DIR=%{_libdir}/cmake/xtensor

%cmake_build

%install
%cmake_install

%files
# Match all library versions (so.2, so.2.0.4, etc.)
%{_libdir}/libdtkImaging*.so*
# Match all dtkImaging include directories (Core, Filters, Widgets)
%{_includedir}/dtkImaging*
# Match the correct CamelCase cmake directory
%{_libdir}/cmake/dtkImaging

%changelog
* Tue Jan 06 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-1
- Fix API mismatch, include paths, and broken system headers
