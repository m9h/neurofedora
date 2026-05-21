%global debug_package %{nil}

Name:           dart
Version:        6.16.7
Release:        1%{?dist}
Summary:        Dynamic Animation and Robotics Toolkit

# Source is BSD-2-Clause. Bundled imgui (in dart/external/imgui/) is MIT;
# bundled lodepng is zlib; ikfast is BSD-3-Clause (OpenRAVE project); ODE
# LCP solver fork is BSD-3-Clause; convhull_3d is MIT.
License:        BSD-2-Clause AND MIT AND Zlib AND BSD-3-Clause
URL:            https://dartsim.github.io/
Source0:        https://github.com/dartsim/dart/archive/refs/tags/v%{version}/dart-%{version}.tar.gz

# DART vendors the following third-party libraries inside dart/external/.
# Where Fedora ships a system version we'd prefer to unbundle, but the
# bundled forks carry small patches needed by DART. Declare them so
# fedora-review can audit licensing/security exposure.
Provides:       bundled(imgui)
Provides:       bundled(lodepng)
Provides:       bundled(ikfast)
Provides:       bundled(odelcpsolver)
Provides:       bundled(convhull_3d)

BuildRequires:  cmake >= 3.22.1
BuildRequires:  ninja-build
BuildRequires:  gcc-c++

# Core required deps (CMakeLists find_package REQUIRED)
BuildRequires:  assimp-devel
BuildRequires:  eigen3-devel
BuildRequires:  fmt-devel
BuildRequires:  spdlog-devel

# Collision detection (REQUIRED)
BuildRequires:  fcl-devel
BuildRequires:  libccd-devel
BuildRequires:  octomap-devel

# Optional collision backends — DART_USE_SYSTEM_BULLET / _ODE default ON
BuildRequires:  bullet-devel
BuildRequires:  ode-devel

# URDF parsing
BuildRequires:  urdfdom-devel
BuildRequires:  urdfdom-headers-devel
BuildRequires:  tinyxml-devel
BuildRequires:  tinyxml2-devel
BuildRequires:  console-bridge-devel

# Optimization solvers (optional but useful)
BuildRequires:  NLopt-devel
BuildRequires:  coin-or-Ipopt-devel

# GUI viewer (OSG-based; DART_BUILD_GUI_OSG=ON default)
BuildRequires:  OpenSceneGraph-devel
BuildRequires:  freeglut-devel
BuildRequires:  libXi-devel
BuildRequires:  libXmu-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel

# Boost — used for filesystem, regex, system
BuildRequires:  boost-devel

%description
DART (Dynamic Animation and Robotics Toolkit) is a collaborative,
cross-platform, open-source library providing data structures and
algorithms for kinematic and dynamic applications in robotics and
computer animation. DART is distinguished by:

  * accurate and stable dynamics simulation using generalized coordinates
    and Featherstone algorithms;
  * support for hierarchical multibody systems with sliding, revolute,
    universal, ball, and free joints;
  * a fast inverse-kinematics solver;
  * built-in collision detection (FCL + Bullet + ODE backends);
  * URDF and SDF parsers for robot model loading;
  * an OpenSceneGraph-based 3D viewer for visualizing simulations.

This metapackage is empty; install dart-libs for the runtime libraries,
dart-devel for headers, and dart-gui-osg for the visual viewer.

%package libs
Summary:        Runtime libraries for DART
Requires:       assimp
Requires:       fcl
Requires:       octomap
Requires:       urdfdom
Requires:       console-bridge

%description libs
Runtime shared libraries (libdart-*.so) for DART. Contains the core
simulation engine, dynamics solver, collision detection, IO modules
(URDF/SDF), and optimization layers.

%package devel
Summary:        Development files for DART
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       eigen3-devel
Requires:       fcl-devel
Requires:       octomap-devel
Requires:       assimp-devel
Requires:       urdfdom-devel
Requires:       fmt-devel
Requires:       spdlog-devel

%description devel
Headers and cmake configuration files for developing C++ applications
that use DART.

%package gui-osg
Summary:        OpenSceneGraph-based 3D viewer for DART simulations
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       OpenSceneGraph

%description gui-osg
osgDart — an OpenSceneGraph-based viewer for visualizing DART
simulations. Provides ImGui-style overlays (via DART's bundled imgui
fork) for runtime parameter manipulation.

%package gui-osg-devel
Summary:        Development files for the DART OSG viewer
Requires:       %{name}-gui-osg%{?_isa} = %{version}-%{release}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       OpenSceneGraph-devel

%description gui-osg-devel
Headers and cmake config for building applications using DART's
OSG-based viewer (osgDart).

%prep
%autosetup -p1 -n dart-%{version}

%build
export CXXFLAGS="%{optflags} -std=c++17"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    `# Disable Python bindings (DART_BUILD_DARTPY) — they bundle pybind11` \
    `# and produce a large dartpy wheel. Add as python3-dart subpackage` \
    `# later when we want to ship Python support.` \
    -DDART_BUILD_DARTPY=OFF \
    `# OSG-based GUI default ON — produces libdart-gui-osg.so` \
    -DDART_BUILD_GUI_OSG=ON \
    `# System libraries for optional collision backends` \
    -DDART_USE_SYSTEM_ODE=ON \
    -DDART_USE_SYSTEM_BULLET=ON \
    `# imgui is bundled (not packaged in Fedora); keep at OFF` \
    -DDART_USE_SYSTEM_IMGUI=OFF \
    `# Skip tests and tutorials in the COPR build` \
    -DDART_BUILD_TESTS=OFF \
    -DDART_BUILD_TUTORIALS=OFF \
    -DDART_BUILD_EXAMPLES=OFF

%cmake_build

%install
%cmake_install

%ldconfig_scriptlets libs
%ldconfig_scriptlets gui-osg

%files libs
%license LICENSE
%doc README.md
%{_libdir}/libdart.so.*
%{_libdir}/libdart-collision-*.so.*
%{_libdir}/libdart-constraint-*.so.*
%{_libdir}/libdart-dynamics-*.so.*
%{_libdir}/libdart-external-*.so.*
%{_libdir}/libdart-integration-*.so.*
%{_libdir}/libdart-io-*.so.*
%{_libdir}/libdart-lcpsolver-*.so.*
%{_libdir}/libdart-math-*.so.*
%{_libdir}/libdart-optimization-*.so.*
%{_libdir}/libdart-simulation-*.so.*
%{_libdir}/libdart-utils-*.so.*

%files devel
%{_includedir}/dart/
%{_libdir}/libdart.so
%{_libdir}/libdart-collision-*.so
%{_libdir}/libdart-constraint-*.so
%{_libdir}/libdart-dynamics-*.so
%{_libdir}/libdart-external-*.so
%{_libdir}/libdart-integration-*.so
%{_libdir}/libdart-io-*.so
%{_libdir}/libdart-lcpsolver-*.so
%{_libdir}/libdart-math-*.so
%{_libdir}/libdart-optimization-*.so
%{_libdir}/libdart-simulation-*.so
%{_libdir}/libdart-utils-*.so
%{_libdir}/cmake/dart/
%{_libdir}/pkgconfig/dart*.pc

%files gui-osg
%{_libdir}/libdart-gui-osg.so.*

%files gui-osg-devel
%{_libdir}/libdart-gui-osg.so

%changelog
* Wed May 20 2026 Morgan Hough <morgan.hough@gmail.com> - 6.16.7-1
- Initial package for DART (Dynamic Animation and Robotics Toolkit) 6.16.7.
- BSD-2-Clause source; declares bundled() for imgui (MIT), lodepng (zlib),
  ikfast (BSD-3-Clause), odelcpsolver (BSD-3-Clause), convhull_3d (MIT).
- Subpackages: -libs (runtime), -devel (headers+cmake), -gui-osg (OSG
  viewer), -gui-osg-devel.
- DART_BUILD_DARTPY=OFF for the initial build — Python bindings deferred
  (pybind11 is bundled by DART, producing a large dartpy wheel; will
  enable once we have a clean story for the Python module layout).
- DART_USE_SYSTEM_ODE=ON, DART_USE_SYSTEM_BULLET=ON to consume Fedora's
  ode-devel and bullet-devel.
- Depends on the urdfdom-headers + urdfdom + flann + fcl chain we revived
  in this round from Fedora orphan status (all originally dropped after
  F42, August 2025).
