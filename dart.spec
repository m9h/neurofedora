%global debug_package %{nil}

Name:           dart
Version:        6.19.4
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

# Optimization solvers (optional) — each produces a libdart-optimizer-*.so
BuildRequires:  NLopt-devel
BuildRequires:  coin-or-Ipopt-devel
BuildRequires:  pagmo2-devel

# OpenSceneGraph viewer (dart-gui-osg)
BuildRequires:  OpenSceneGraph-devel

# OpenGL/GLUT viewer (dart-gui)
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
dart-devel for headers, dart-gui for the OpenGL/GLUT viewer, and
dart-gui-osg for the OpenSceneGraph viewer.

%package libs
Summary:        Runtime libraries for DART
Requires:       assimp
Requires:       fcl
Requires:       octomap
Requires:       urdfdom
Requires:       console-bridge

%description libs
Runtime shared libraries for DART: the core engine (libdart.so), the
Bullet and ODE collision backends, the URDF/SDF/MJCF parsers, the
NLopt/Ipopt/pagmo optimizer backends, and the bundled external helper
libraries.

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

%package gui
Summary:        OpenGL/GLUT-based 3D viewer for DART simulations
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       freeglut

%description gui
libdart-gui — DART's lightweight OpenGL/GLUT viewer (SimWindow,
Win3D, Trackball) for visualizing simulations without OpenSceneGraph.

%package gui-devel
Summary:        Development files for the DART OpenGL/GLUT viewer
Requires:       %{name}-gui%{?_isa} = %{version}-%{release}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       freeglut-devel

%description gui-devel
Headers and cmake config for building applications using DART's
OpenGL/GLUT viewer (libdart-gui).

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
    `# Do not treat warnings as errors. DART defaults this ON, but its` \
    `# code triggers -Wdeprecated-declarations against Fedora 44's Eigen` \
    `# 5.x (the JacobiSVD runtime-Options API is deprecated in Eigen 5).` \
    `# Upstream's own setup.py / packaging scripts pass this OFF too.` \
    -DDART_TREAT_WARNINGS_AS_ERRORS=OFF \
    `# DART has no DART_BUILD_TESTS option — tests are gated by the` \
    `# standard CTest BUILD_TESTING variable. Left ON, tests/CMakeLists.txt` \
    `# runs FetchContent_MakeAvailable(googletest), which git-clones from` \
    `# GitHub at configure time and fails under mock/COPR network isolation.` \
    `# examples/ and tutorials/ are add_subdirectory(... EXCLUDE_FROM_ALL),` \
    `# so they configure cleanly and never build — no separate flag needed.` \
    -DBUILD_TESTING=OFF

%cmake_build

%install
%cmake_install

%ldconfig_scriptlets libs
%ldconfig_scriptlets gui
%ldconfig_scriptlets gui-osg

# DART 6.x consolidates the kinematics/dynamics/math/constraint/simulation/
# integration/lcpsolver/collision-core code into a single libdart.so. Only
# the optional backends (collision-bullet/ode, optimizer-nlopt/ipopt/pagmo),
# the parsers (utils, utils-urdf), the GUIs (gui, gui-osg) and the bundled
# external helpers (imgui, lodepng, odelcpsolver) are separate libraries.
%files libs
%license LICENSE
%doc README.md
%{_libdir}/libdart.so.*
%{_libdir}/libdart-collision-*.so.*
%{_libdir}/libdart-external-*.so.*
%{_libdir}/libdart-optimizer-*.so.*
%{_libdir}/libdart-utils*.so.*
# Upstream installs the data/ resource tree (loaded at runtime via
# DartResourceRetriever / DART_DATA_PATH) plus example and tutorial
# sources here under %%{_docdir}/dart/.
%{_docdir}/%{name}/

%files devel
%{_includedir}/dart/
%{_libdir}/libdart.so
%{_libdir}/libdart-collision-*.so
%{_libdir}/libdart-external-*.so
%{_libdir}/libdart-optimizer-*.so
%{_libdir}/libdart-utils*.so
# cmake package config and the ROS/colcon package.xml manifest both
# install under %%{_datadir}/dart/ (CONFIG_INSTALL_DIR), not %%{_libdir}.
%{_datadir}/%{name}/
%{_libdir}/pkgconfig/dart*.pc

%files gui
%{_libdir}/libdart-gui.so.*

%files gui-devel
%{_libdir}/libdart-gui.so

%files gui-osg
%{_libdir}/libdart-gui-osg.so.*

%files gui-osg-devel
%{_libdir}/libdart-gui-osg.so

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 6.19.4-1
- Update to 6.19.4

* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 6.18.0-1
- Update to 6.18.0 (current upstream; freshness sweep 2026-06-14)

* Thu May 21 2026 Morgan Hough <morgan.hough@gmail.com> - 6.16.7-5
- Fix %%files paths revealed once the compile finally completed: DART
  installs its cmake config and package.xml to %%{_datadir}/dart/ (not
  %%{_libdir}/cmake/dart), and installs the data/ resource tree plus
  example/tutorial sources under %%{_docdir}/dart/. Own both locations.

* Thu May 21 2026 Morgan Hough <morgan.hough@gmail.com> - 6.16.7-4
- Build the pagmo optimizer backend: add pagmo2-devel BuildRequires, which
  enables the dart-optimizer-pagmo module (libdart-optimizer-pagmo.so).
- New dart-gui / dart-gui-devel subpackages for the OpenGL/GLUT viewer
  (libdart-gui.so). It was compiled before but never packaged.
- Rewrite %files with the real DART 6.x library names. DART consolidates
  constraint/dynamics/math/simulation/integration/lcpsolver/collision-core
  into a single libdart.so; the previous %files listed per-module libraries
  (libdart-constraint-*, libdart-math-*, libdart-optimization-* ...) that
  DART does not produce, and omitted libdart-optimizer-* and libdart-gui.

* Thu May 21 2026 Morgan Hough <morgan.hough@gmail.com> - 6.16.7-3
- Fix FTBFS against Eigen 5.x: pass -DDART_TREAT_WARNINGS_AS_ERRORS=OFF.
  Fedora 44 ships Eigen 5.0.1, which deprecates the JacobiSVD runtime
  Options API that DART 6.16.7 still uses; DART defaults -Werror ON, so
  the deprecation warning was fatal. Upstream setup.py disables it too.

* Thu May 21 2026 Morgan Hough <morgan.hough@gmail.com> - 6.16.7-2
- Fix FTBFS in mock/COPR: pass -DBUILD_TESTING=OFF. DART has no
  DART_BUILD_TESTS option (the -DDART_BUILD_TESTS/TUTORIALS/EXAMPLES flags
  were silent no-ops); tests are gated by CTest's BUILD_TESTING, and with
  it left ON tests/CMakeLists.txt git-clones googletest via FetchContent
  at configure time, which fails under network isolation.

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
