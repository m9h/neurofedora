%global commit      6565932c434827a2e2b103bb4f80e46f449cba40
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20251104

# CLI shape-analysis tools; strip the debug subpackage to keep it lean.
%global debug_package %{nil}

Name:           SPHARM-PDM
Version:        2.0.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Spherical harmonic point distribution model shape analysis tools

License:        Apache-2.0
URL:            https://github.com/NIRALUser/SPHARM-PDM
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  git-core
# The three superbuild dependencies — all provided as system packages, so we
# disable the (offline-fatal) superbuild and build the inner project directly.
BuildRequires:  InsightToolkit5-devel
BuildRequires:  vtk-devel
BuildRequires:  SlicerExecutionModel-devel
# VTK cmake config runs find_package for all its module deps at configure time.
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  hdf5-devel
BuildRequires:  double-conversion-devel
BuildRequires:  expat-devel
BuildRequires:  glew-devel
BuildRequires:  lz4-devel
BuildRequires:  libxml2-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel

%description
SPHARM-PDM is a set of command-line tools for spherical-harmonic-based shape
analysis. It computes correspondent point-based shape models (PDMs) from
binary segmentations by parameterising the surface with spherical harmonics
and sampling a corresponding icosahedral mesh, enabling group statistical
shape analysis of brain structures and other objects. Part of the NIRAL /
SlicerSALT shape-analysis ecosystem.

This build uses the system ITK, VTK and SlicerExecutionModel (no superbuild).

%prep
%autosetup -n %{name}-%{commit}

# CMake/CMakeLists.txt does nothing but file(DOWNLOAD) a Windows-only
# FindVcvars.cmake from GitHub at configure time (fatal offline). FindVcvars is
# never used on Linux — neutralise the whole sub-CMakeLists.
echo '# FindVcvars download removed: Windows-only, unused on Linux, offline build' \
    > CMake/CMakeLists.txt

# GCC 16 rejects this legacy code's unqualified std names (e.g. MeshMath.cxx
# uses bare `cout`/`endl`, relying on a `using namespace std` that older
# standard headers pulled in transitively). Force-include a small compat header
# that brings the std names into scope for every translation unit.
cat > std-compat.h <<'EOF'
#pragma once
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <string>
using namespace std;
EOF

%build
export CXXFLAGS="%{optflags} -include ${PWD}/std-compat.h -fpermissive"
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DSPHARM-PDM_SUPERBUILD:BOOL=OFF \
    -DUSE_SYSTEM_ITK:BOOL=ON \
    -DUSE_SYSTEM_VTK:BOOL=ON \
    -DUSE_SYSTEM_SlicerExecutionModel:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

# This is a CLI-tools package: drop the static dev libraries and headers the
# build also installs (the tools are statically linked and self-contained).
rm -rf %{buildroot}%{_includedir}/Shape
rm -f  %{buildroot}%{_libdir}/*.a

# Strip any residual build-tree RPATHs the SEM macros may leave.
find %{buildroot} -type f -perm -111 \
    -exec chrpath --delete {} \; 2>/dev/null || :

%files
%license License.txt
%{_bindir}/*

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.1.20251104git6565932
- Initial package: SPHARM-PDM spherical-harmonic shape-analysis CLI tools
  (master snapshot 6565932). Built against system ITK/VTK/SlicerExecutionModel
  with the superbuild disabled (Fedora no-superbuild policy). Complements the
  FSL FIRST mesh shape-analysis workflow.
