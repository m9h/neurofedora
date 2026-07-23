# SPHARM-PDM — Spherical Harmonics Point Distribution Models: the flagship shape
# analysis pipeline of SlicerSALT. Computes spherical-harmonic parameterizations
# of segmented 3D objects and the corresponding point-based shape models, the
# basis for group statistical shape analysis (e.g. subcortical structures). C++
# extension: a set of SlicerExecutionModel CLI modules (GenParaMesh,
# ParaToSPHARMMesh, SegPostProcess, MetaMeshTools, SpharmTool) + scripted modules,
# built NON-superbuild against the system 3dslicer foundation (>= -50).
#
# Standalone: the inner build (SPHARM-PDM.cmake) find_package()s only
# ITK / VTK / SlicerExecutionModel / Slicer — all system. The GROUPS extension
# is FetchContent'd ONLY in the superbuild phase, so SUPERBUILD=OFF needs no
# network. First of the SlicerSALT (Shape AnaLysis Toolbox) extensions.

%global commit      522de7b54ff0748d57d04bd70d0f7048e48361e2
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260601

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.12

Name:           3dslicer-spharm-pdm
Version:        2.0.0
Release:        0.2.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Spherical-harmonics point-distribution shape analysis for 3D Slicer (SlicerSALT)

License:        Apache-2.0
URL:            https://github.com/slicersalt/SPHARM-PDM
Source0:        %{url}/archive/%{commit}/SPHARM-PDM-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
# Common.cmake does find_package(Git REQUIRED) at configure time.
BuildRequires:  git-core

BuildRequires:  3dslicer-devel >= 5.12.1

# Full Qt6 set find_package(Slicer)'s Qt check demands.
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Sql)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6Xml)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6PrintSupport)
BuildRequires:  cmake(Qt6Multimedia)
BuildRequires:  cmake(Qt6MultimediaWidgets)
BuildRequires:  cmake(Qt6Core5Compat)
BuildRequires:  cmake(Qt6StateMachine)
BuildRequires:  cmake(Qt6WebEngineCore)
BuildRequires:  cmake(Qt6WebEngineWidgets)
BuildRequires:  cmake(Qt6WebChannel)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickWidgets)
BuildRequires:  cmake(Qt6Test)
BuildRequires:  cmake(Qt6UiTools)
BuildRequires:  qt6-qttools-devel
BuildRequires:  InsightToolkit5-devel >= 5.4.6-7
BuildRequires:  InsightToolkit5-vtk-devel
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  ctk-devel
BuildRequires:  qttesting-devel
BuildRequires:  vtkAddon-devel
BuildRequires:  qRestAPI-devel
BuildRequires:  python-pythonqt-devel
BuildRequires:  commontk-applauncher-devel
BuildRequires:  dcmtk-devel
BuildRequires:  SlicerExecutionModel-devel
BuildRequires:  rapidjson-devel
BuildRequires:  libcurl-devel
BuildRequires:  jsoncpp-devel
# Loading the foundation SlicerConfig.cmake triggers find_package(Teem) (config
# mode); Fedora ships TeemConfig.cmake under %{_libdir}/cmake. Provide it + point
# Teem_DIR there so the config resolves (SPHARM itself doesn't use Teem).
BuildRequires:  teem-devel

Requires:       3dslicer

%description
SPHARM-PDM is the spherical-harmonics point-distribution-model shape analysis
toolbox, the flagship pipeline of SlicerSALT. From binary segmentations it
computes a spherical-harmonic surface parameterization and a corresponding
point-based shape model with consistent point correspondence across a
population, enabling statistical shape analysis of anatomical structures.

This package provides the SPHARM-PDM command-line modules (GenParaMesh,
ParaToSPHARMMesh, SegPostProcess, and the MetaMeshTools utilities) plus the
scripted Shape Analysis modules, built non-superbuild against the system 3D
Slicer foundation.

%prep
%autosetup -n SPHARM-PDM-%{commit}

# Distro build: install modules directly, not as an Extension-Manager bundle, so
# skip SlicerExtensionCPack (wants README/license + s4ext template the install
# tree doesn't ship). Guarded by if(DEFINED Slicer_DIR), which we set.
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' SPHARM-PDM.cmake

# CMake/CMakeLists.txt does a configure-time file(DOWNLOAD) of FindVcvars.cmake
# (a Windows-MSVC helper that is never used on Linux) — the build env has no
# network, so the download fails the whole configure. Neutralize it.
: > CMake/CMakeLists.txt

# GCC 16 (Fedora 44) rejects unqualified std names. Several old NIRAL sources use
# bare cout/cerr/endl assuming `using namespace std` was in effect. Inject the
# directive after each affected file's last #include (namespace scope, post-
# includes) so they compile unmodified otherwise.
for f in Modules/CLI/MetaMeshTools/MeshMath.cxx \
         Modules/CLI/MetaMeshTools/BYU2VTK.cxx \
         Modules/CLI/MetaMeshTools/STL2VTK.cxx \
         Libraries/Shape/Algorithms/ParametricMeshToSPHARMSpatialObjectFilter.cxx \
         Libraries/SparseLibMVIml/mvvcio.cxx \
         Libraries/SparseLibMVIml/mvvi.cxx \
         Libraries/SparseLibMVIml/mvvd.cxx \
         Libraries/SparseLibMVIml/mvvc.cxx \
         Libraries/SparseLibMVIml/mvvf.cxx; do
    [ -f "$f" ] || continue
    awk 'NR==FNR{if($0 ~ /^[[:space:]]*#[[:space:]]*include/) last=FNR; next}
         {print; if(FNR==last) print "using namespace std;"}' "$f" "$f" > "$f.tmp" \
      && mv "$f.tmp" "$f"
done

%build
%cmake -G Ninja \
    -DSPHARM-PDM_SUPERBUILD:BOOL=OFF \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DTeem_DIR:PATH=%{_libdir}/cmake \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_SKIP_SlicerBlockAdditionalLauncherSettings:BOOL=TRUE \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst}
%cmake_build

%install
%cmake_install
# Catch-all file list (files + symlinks only, so the shared module dirs that
# 3dslicer owns are never claimed). Tightened later.
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/spharm.files

%files -f %{_builddir}/spharm.files
%license License.txt
%doc README.md

%changelog
* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.2.20260601git522de7b5
- Retarget from Slicer-5.11 to Slicer-5.12 core (3dslicer 5.12.1); bump
  3dslicer-devel floor to 5.12.1.

* Thu Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.1.20260601git522de7b5
- Initial package. SPHARM-PDM (spherical-harmonics PDM shape analysis CLIs +
  scripted modules) built non-superbuild against the system 3dslicer foundation
  >= -50. First SlicerSALT (Shape AnaLysis Toolbox) extension.
