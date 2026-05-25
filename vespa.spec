%global debug_package %{nil}

# Fedora's ParaView ships its private VTK libraries under
# /usr/lib64/paraview/, not /usr/lib64/. RPM's auto-Requires extracts
# SONAMEs from VESPAPlugin.so (libvtkRemoting*.so.1, libvtkCommonCore.so.1,
# libvtksys.so.1, etc.) and looks for providers in standard library paths,
# where they aren't indexed. The libraries are present at runtime — ParaView
# adds /usr/lib64/paraview to LD_LIBRARY_PATH via its plugin loader — but
# install-time resolution fails. Exclude the ParaView-private SONAMEs from
# auto-Requires and rely on the explicit `Requires: paraview` instead.
#
# Also exclude the meta-level vtk-libs / CGAL-libs package Requires that
# rpmbuild auto-generates from the CMake exported targets. Fedora's VTK
# and CGAL packages don't split into a -libs subpackage — VTK is just
# `vtk` and CGAL is just `CGAL`. The exported targets mention `vtk-libs`
# and `CGAL-libs` (other distros do split them out) and that confuses
# rpmbuild's auto-Requires into asking for providers that don't exist.
# Drop those; the explicit `Requires: vtk` and `Requires: CGAL` in the
# subpackage stanzas below cover the real deps.
%global __requires_exclude ^libvtk.*\\.so\\.1\\(\\(64bit\\)\\)?$|^libvtk(Common|Filters|IO|Imaging|Interaction|Parallel|Remoting|Rendering|Views|sys).*\\.so|^(vtk-libs|CGAL-libs)(\\(x86-64\\))?$

Name:           vespa
Version:        1.0
Release:        9%{?dist}
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
# ParaView 6.x's find_package(Qt6 COMPONENTS ...) requires the full Qt6
# component set used by its GUI client + Qt-based plugin infrastructure.
# Each missing component dies one-at-a-time at ParaView-vtk-module-find-
# packages.cmake:168 with "Failed to find required Qt component <X>".
# Adding them all preemptively (vs whack-a-mole one resubmit per missing
# Qt6 sub-component):
#   Qt6Core5Compat  → qt6-qt5compat-devel    (XML, Concurrent, etc.)
#   Qt6Help         → qt6-qttools-devel      (assistant/help system)
#   Qt6Designer     → qt6-qttools-devel      (.ui designer)
#   Qt6LinguistTools→ qt6-qttools-devel      (lupdate/lrelease)
#   Qt6Tools        → qt6-qttools-devel      (umbrella)
BuildRequires:  cmake(Qt6Core5Compat)
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtbase-devel
# VTK 9.6's cmake config does find_package(CLI11) for its command-line
# parsing layer (vtkscn module). Header-only library; provides
# CLI11Config.cmake in cli11-devel.
BuildRequires:  cli11-devel
# VTK 9.6's vtkscn (string parsing) ALSO does find_package(FastFloat)
# for IEEE-754 fast string-to-float conversion. Header-only; provides
# FastFloatConfig.cmake in fast_float-devel.
BuildRequires:  fast_float-devel
# More ParaView 6.x transitive find_package deps — each appears at
# configure time when paraview-config.cmake loads its module manifest.
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-compiler
BuildRequires:  boost-devel
BuildRequires:  python3-numpy
BuildRequires:  hdf5-devel
BuildRequires:  libxml2-devel
BuildRequires:  metis-devel
# F44 paper-cut: lapack-devel's cmake config references /usr/lib64/libblas.a
# and /usr/lib64/liblapack.a (static archives) which only live in
# blas-static / lapack-static. Without these, find_package(LAPACK) succeeds
# but imported-target resolution fails. Affects any consumer pulling
# lapack via CGAL (vespa) or VTK's accelerated linear algebra options.
# F44 papercut: -devel packages export cmake imported targets pointing at
# /usr/lib64/lib*.a files that live in -static subpackages without the
# -devel pulling them in. This is downstream-only — Fedora's own VTK
# builds clean because it doesn't consume the broken exports — but any
# package doing find_package(VTK) / find_package(ParaView) / find_package(CGAL)
# hits each one in sequence. Front-load the static archives here.
BuildRequires:  blas-static
BuildRequires:  lapack-static
BuildRequires:  zlib-static
BuildRequires:  libpng-static
BuildRequires:  libtiff-static
BuildRequires:  bzip2-static
BuildRequires:  xz-static
BuildRequires:  expat-static
BuildRequires:  libxml2-static
# ParaView 6's `paraview_client_documentation()` macro renders plugin
# XML schema docs via xsltproc at build time; without it,
# ParaViewClient.cmake:609 aborts.
BuildRequires:  libxslt

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
Requires:       vtk%{?_isa}
# CGAL is header-only on Fedora — there is no runtime `CGAL` package at
# all, only `CGAL-devel` (and CGAL-qt6-devel, CGAL-demos-source). vespa
# vtkCGAL*.so already has the CGAL template code baked in at build time,
# so no runtime CGAL Requires is needed. (vespa-devel still pulls in
# CGAL-devel below for downstream consumers building against the headers.)

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
# CGAL-devel is also noarch (it just provides headers); no _isa needed.
Requires:       CGAL-devel

%description devel
Headers and cmake config files for building C++ applications against
VESPA's VTK modules.

%package -n python3-vespa
Summary:        Python 3 bindings for VESPA
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       python3
# Fedora's VTK Python bindings package — the actual name on F44 is
# python3-vtk; pull it explicitly so import works without manual setup.
Requires:       python3-vtk

%description -n python3-vespa
Python 3 module exposing VESPA's vtkCGAL* VTK modules
(Algorithm, Delaunay, PointSetProcessing, PolygonMeshProcessing,
ShapeReconstruction). `import vespa` after installing.

%prep
%autosetup -n %{name}-v%{version}

# Fedora 44 ships Eigen3 5.0.1 (SameMajorVersion compat). The upstream
# `find_package(Eigen3 3.2.0 REQUIRED)` rejects 5.0.1 because of the
# major-version mismatch. The actual API usage (vector/matrix
# arithmetic) is stable across Eigen3 3.x..5.x. Drop the version pin.
sed -i 's/find_package(Eigen3 3.2.0 REQUIRED)/find_package(Eigen3 REQUIRED)/' \
    CMakeLists.txt

# Fedora 44 ships CGAL 6.1.1 (also SameMajorVersion compat). Drop the
# version pin and rely on the source code working against CGAL 6.x.
sed -i 's/find_package(CGAL 5.3.0 REQUIRED)/find_package(CGAL REQUIRED)/' \
    CMakeLists.txt

# CGAL 6.0 renamed AABB_traits<> -> AABB_traits_3<> as part of the 3D
# namespace cleanup. Vespa 1.0 still uses the old name in exactly one
# place. Mechanical s///.
sed -i 's/CGAL::AABB_traits</CGAL::AABB_traits_3</g' \
    vespa/PolygonMeshProcessing/vtkCGALSignedDistanceFunction.cxx

%build
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error=deprecated-declarations"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DVESPA_BUILD_PV_PLUGIN=ON \
    `# VTK 9.6 has a Python-wrapper code-generator bug: emits references` \
    `# to PyVTKGetSet / PyVTKObject_GetProperty / PyVTKObject_SetProperty` \
    `# in auto-generated *Python.cxx files, but those symbols are NOT` \
    `# defined in VTK 9.6 itself. Every vtkCGAL* module fails to compile` \
    `# with "PyVTKGetSet does not name a type". Disable wrapping until` \
    `# VTK 9.6.x ships a fix or vespa upstream catches up — the C++` \
    `# modules and ParaView plugin still build and are the primary` \
    `# consumers. python3-vespa subpackage temporarily empty (see %%files).` \
    -DBUILD_PYTHON_WRAPPERS=OFF \
    `# F44 Eigen3 5.0.1 + VTK 9.5.2 incompatibility: VTK ships its own` \
    `# FindEigen3.cmake module that greps for the legacy EIGEN_*_VERSION` \
    `# macros which Eigen 5.x removed. The module-mode lookup reports` \
    `# version "..", which fails every >= 3.x check. Eigen3 ships a` \
    `# correct Eigen3Config.cmake at /usr/share/cmake/eigen3/.` \
    `# Force config-mode globally so cmake bypasses VTK's broken shim.` \
    -DCMAKE_FIND_PACKAGE_PREFER_CONFIG=TRUE

%cmake_build

%install
%cmake_install

# Vespa's cmake mistakenly installs the bundled Python header
# (/usr/include/Python.h) as part of vtk_module_wrap_python's
# header-copy logic. Drop it to avoid clobbering the system
# python3-devel-provided Python.h on install. Upstream bug.
rm -f %{buildroot}%{_includedir}/Python.h

%files
%license License.txt
%doc README.md

%files libs
# VTK modules build unversioned (no .so.1 suffix) — that's how VTK's
# vtk_module_build() ships them. They live alongside the system VTK
# install convention.
%{_libdir}/libvtkCGALAlgorithm.so
%{_libdir}/libvtkCGALDelaunay.so
%{_libdir}/libvtkCGALPMP.so
%{_libdir}/libvtkCGALPSP.so
%{_libdir}/libvtkCGALSR.so
# VTK hierarchy descriptors used by ParaView's introspection at load time
%{_libdir}/vtk/hierarchy/vespa/

%files paraview-plugin
%{_libdir}/paraview/plugins/VESPAPlugin/

# python3-vespa is currently empty: VTK 9.6 Python wrapper-generator bug
# (PyVTKGetSet undefined) blocks the build. Subpackage stays declared so
# downstream Requires don't break; re-enable BUILD_PYTHON_WRAPPERS and
# restore these %%files lines when VTK 9.6.x emits matching symbols.
%files -n python3-vespa
# (intentionally empty pending VTK 9.6 PyVTKGetSet fix)
%doc README.md
# %{python3_sitearch}/vespa/
# %{_libdir}/cmake/vespaPython/

%files devel
%{_includedir}/vtkCGAL*.h
# Client-server static archives — vtk_module_build emits these as
# the .CS.a companion to each module .so; consumers only need them at
# link time, not runtime.
%{_libdir}/libvtkCGAL*CS.a
%{_libdir}/cmake/vespa/

%changelog
* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-9
- Drop the runtime `Requires: CGAL` from vespa-libs entirely. -8 changed
  it from `CGAL(x86-64)` to bare `CGAL` but Fedora has NO runtime CGAL
  package at all — only CGAL-devel / CGAL-qt6-devel / CGAL-demos-source.
  Since CGAL is header-only and its template code is baked into
  libvtkCGAL*.so at build time, no runtime dep is needed.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-8
- Drop %%{?_isa} from `Requires: CGAL` / `Requires: CGAL-devel`. Fedora's
  CGAL package is noarch (header-only library) and doesn't provide a
  CGAL(x86-64) tag, so dnf couldn't resolve the dep on the harness install.
- (Rawhide chroot still fails on VTK::cli11 missing target; F44 builds and
  installs cleanly.)

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-7
- Set -DBUILD_PYTHON_WRAPPERS=OFF: VTK 9.6's Python wrapper code
  generator emits *Python.cxx files referencing PyVTKGetSet,
  PyVTKObject_GetProperty, PyVTKObject_SetProperty — symbols not
  defined in VTK 9.6 itself. Every vtkCGAL*Python.cxx fails to
  compile. Upstream VTK 9.6 bug. Drops the python3-vespa subpackage
  contents but unblocks vespa-libs + vespa-paraview-plugin (which
  are the primary downstream consumers anyway).

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-6
- Add `BuildRequires: fast_float-devel`. -5 cleared cli11-devel only
  to hit FastFloat next at VTK-vtk-module-find-packages.cmake:1202.
  vtkscn pulls in both for its string parsing.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-5
- Add `BuildRequires: cli11-devel`. VTK 9.6's vtkscn cmake module does
  find_package(CLI11) at configure time. -4 cleared the Qt6 cascade
  only to hit this next.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-4
- Add `BuildRequires: qt6-qttools-devel` (provides Qt6Help, Qt6Designer,
  Qt6LinguistTools). -3 cleared Qt6Core5Compat only to hit Qt6Help next
  — ParaView's find_package wants the full Qt-tools-side suite. Adding
  it as one package avoids one-at-a-time discovery.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-3
- Add `BuildRequires: cmake(Qt6Core5Compat)`. ParaView 6.x's cmake
  config does `find_package(Qt6 COMPONENTS Core5Compat REQUIRED)` from
  ParaView-vtk-module-find-packages.cmake:168, which dies with
  "Failed to find required Qt component Core5Compat" without this BR.
  Build 10509069 (-2) failed at exactly this configure step.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-2
- Extend %%__requires_exclude to also drop the auto-generated
  vtk-libs(x86-64) and CGAL-libs(x86-64) package-level Requires.
  Fedora's VTK and CGAL packages aren't split into -libs subpackages
  (just `vtk` and `CGAL`), but the CMake exported targets reference
  the -libs names, so rpmbuild auto-Requires invents providers that
  don't exist. Without this, `dnf install vespa-libs` fails with
  "nothing provides vtk-libs(x86-64)" / "nothing provides CGAL-libs(x86-64)".
  The explicit `Requires: vtk` and `Requires: CGAL` in the subpackages
  cover the real deps. Surfaced by the neurofedora test harness on
  the fedora-imac fresh-install run.

* Tue May 19 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-1
- Initial package for VESPA 1.0 — Kitware's VTK+ParaView CGAL bridge
- Built against F44 VTK 9.5.2, ParaView 6.0.1, CGAL 6.1.1, Eigen3 5.0.1
- Drop upstream's `find_package(Eigen3 3.2.0)` and
  `find_package(CGAL 5.3.0)` version pins (F44's libraries use
  SameMajorVersion cmake compat which rejects older-version queries
  even though the API is compatible)
- Three subpackages: -libs (VTK modules), -paraview-plugin (.so),
  -devel (headers + cmake config)
