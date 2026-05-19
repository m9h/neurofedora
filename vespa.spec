%global debug_package %{nil}

Name:           vespa
Version:        1.0
Release:        1%{?dist}
Summary:        VTK Enhanced with Surface Processing Algorithms (CGAL bridge)

# BSD-3-Clause for source code, GPL-3.0-or-later for any binary because
# CGAL itself is GPL-3.0-or-later when used without a commercial license.
# Per upstream Licence.txt and README: "as it is linked to CGAL, any
# binary generated with it retains the GPLv3 license, unless you get a
# commercial license from GeometryFactory".
License:        BSD-3-Clause AND GPL-3.0-or-later
URL:            https://gitlab.kitware.com/vtk/meshing/vespa
Source0:        %{url}/-/archive/v%{version}/%{name}-v%{version}.tar.gz

BuildRequires:  cmake >= 3.8
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
# Plugin variant pulls VTK transitively via paraview-devel; require both
# explicitly so cmake's find_package(VTK) succeeds for the module half.
BuildRequires:  vtk-devel >= 9.0
BuildRequires:  paraview-devel >= 5.10
BuildRequires:  CGAL-devel >= 5.3
BuildRequires:  eigen3-devel
# Ceres is detected QUIET in CMakeLists; pull it in so the optional
# USE_CERES code path is enabled.
BuildRequires:  ceres-solver-devel
# Common transitive deps of VTK/ParaView cmake configs on F44
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  python3-devel
# ParaView 6.x's cmake config pulls in additional Qt6 sub-components at
# find_package time (Qt6 is itself modular). Each one needs an explicit
# BR or the find_package(ParaView) call fails before we get to compile.
BuildRequires:  cmake(Qt6)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  qt6-qtbase-devel
# More ParaView 6.x transitive find_package deps — each appears at
# configure time when paraview-config.cmake loads its module manifest.
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-compiler
BuildRequires:  boost-devel
BuildRequires:  python3-numpy
BuildRequires:  hdf5-devel
BuildRequires:  libxml2-devel

%description
VESPA wraps the CGAL geometry library (surface mesh smoothing, alpha
wrapping, point-set processing, shape reconstruction, Delaunay
triangulation, isotropic remeshing, mesh deformation) and exposes it
both as a VTK module set and as a ParaView plugin.

This base package is empty; install vespa-libs for the VTK modules and
vespa-paraview-plugin for the loadable ParaView filter set.

Note: VESPA binaries inherit GPL-3.0-or-later from the CGAL license
unless a commercial CGAL license is obtained from GeometryFactory.

%package libs
Summary:        VTK modules for VESPA's CGAL bridge
Requires:       vtk-libs%{?_isa}
Requires:       CGAL-libs%{?_isa}

%description libs
The vtkCGAL* VTK modules: Delaunay, PointSetProcessing,
PolygonMeshProcessing, ShapeReconstruction, plus the Algorithm
support layer. Useful when consuming VESPA from a standalone VTK
application (not via ParaView).

%package paraview-plugin
Summary:        ParaView plugin exposing VESPA's CGAL filters
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       paraview

%description paraview-plugin
Loadable ParaView plugin (VESPAPlugin.so) that registers the VESPA
filters under the Filters > VESPA menu — isotropic remeshing, surface
reconstruction from point clouds, alpha wrapping, as-rigid-as-possible
mesh deformation, and more.

After installing, the plugin auto-loads via ParaView's plugin scan; if
not, load it manually via Tools > Manage Plugins > Load New.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       vtk-devel
Requires:       CGAL-devel

%description devel
Headers and cmake config files for building C++ applications against
VESPA's VTK modules.

%prep
%autosetup -n %{name}-v%{version}

# Fedora 44 ships Eigen3 5.0.1 (SameMajorVersion compat). The upstream
# `find_package(Eigen3 3.2.0 REQUIRED)` rejects 5.0.1 because of the
# major-version mismatch. The actual API usage (vector/matrix
# arithmetic) is stable across Eigen3 3.x..5.x. Drop the version pin.
sed -i 's/find_package(Eigen3 3.2.0 REQUIRED)/find_package(Eigen3 REQUIRED)/' \
    CMakeLists.txt

# Fedora 44 ships CGAL 6.1.1 (also SameMajorVersion compat). Same fix:
# drop the version pin and rely on the source code working against
# CGAL 6.x. If it doesn't, we'll surface the actual API breaks on
# first build.
sed -i 's/find_package(CGAL 5.3.0 REQUIRED)/find_package(CGAL REQUIRED)/' \
    CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error=deprecated-declarations"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DVESPA_BUILD_PV_PLUGIN=ON \
    -DBUILD_PYTHON_WRAPPERS=ON

%cmake_build

%install
%cmake_install

%files
%license License.txt
%doc README.md

%files libs
%{_libdir}/libvtkCGAL*.so.*

%files paraview-plugin
# Plugin .so lands under PARAVIEW_PLUGIN_SUBDIR which on F44 resolves
# to /usr/lib64/paraview/paraview/plugins/VESPAPlugin/. Wildcarded
# because the exact name suffix depends on ParaView 6.x's plugin
# manifest format.
%{_libdir}/paraview/paraview/plugins/VESPAPlugin*

%files devel
%{_includedir}/vtkCGAL*
%{_libdir}/libvtkCGAL*.so
%{_libdir}/cmake/vespa/

%changelog
* Tue May 19 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-1
- Initial package for VESPA 1.0 — Kitware's VTK+ParaView CGAL bridge
- Built against F44 VTK 9.5.2, ParaView 6.0.1, CGAL 6.1.1, Eigen3 5.0.1
- Drop upstream's `find_package(Eigen3 3.2.0)` and
  `find_package(CGAL 5.3.0)` version pins (F44's libraries use
  SameMajorVersion cmake compat which rejects older-version queries
  even though the API is compatible)
- Three subpackages: -libs (VTK modules), -paraview-plugin (.so),
  -devel (headers + cmake config)
