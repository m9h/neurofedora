# SlicerSkeletalRepresentation (SRep) — skeletal representations (s-reps) for 3D
# Slicer: a discrete medial/skeletal shape model with creation, refinement,
# warping and statistical tooling. Part of SlicerSALT, and a build dependency of
# ShapePopulationViewer's Slicer module (which links vtkSlicerSRepModule{MRML,
# Logic}). C++ loadable module (SRep) + small C++ CLIs + scripted Python modules,
# built NON-superbuild against the system 3dslicer foundation.
#
# Unlike ShapePopulationViewer, SRep has no Qt5/VTK8 hard-gate — it just
# find_package(Slicer) and inherits the foundation's Qt6/VTK9 — and uses no
# Qt5-specific APIs, so it builds against the modern foundation unmodified.
# GTest is only pulled by the (disabled) Testing subdirs.

%global commit      dd362a120d43d2f9872d0e21639acf463816651f
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260601

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11

Name:           3dslicer-srep
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Skeletal representation (s-rep) shape modeling for 3D Slicer (SlicerSALT)

License:        Apache-2.0
URL:            https://github.com/KitwareMedical/SlicerSkeletalRepresentation
Source0:        %{url}/archive/%{commit}/SlicerSkeletalRepresentation-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  git-core

BuildRequires:  3dslicer-devel >= 5.11.0~pre.20260517git208adb86-50

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
# Loading the foundation SlicerConfig.cmake triggers find_package(Teem).
BuildRequires:  teem-devel

Requires:       3dslicer

%description
SlicerSkeletalRepresentation brings skeletal representations (s-reps) to 3D
Slicer: a discrete medial shape model and the tooling to create, refine, warp,
and statistically analyze it (including the EvolutionarySRep methods). It is a
SlicerSALT shape-analysis extension and provides the s-rep MRML/logic libraries
that ShapePopulationViewer's Slicer module builds against.

This package provides the SRep loadable module, the s-rep creation/refinement/
warping CLIs, and the scripted s-rep pipeline modules, built non-superbuild
against the system 3D Slicer foundation.

%prep
%autosetup -n SlicerSkeletalRepresentation-%{commit}

# Distro build: install modules directly, not as an Extension-Manager bundle, so
# skip SlicerExtensionCPack (wants README/license + s4ext template the install
# tree doesn't ship).
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' CMakeLists.txt

# VTK's wrap-hierarchy parser (vtkWrapHierarchy) errors with "syntax error" on
# every SRep header that uses the VTK_NEWINSTANCE hint macro (it isn't defined in
# the parser's context when SRep builds against the installed foundation, so it
# reads as an unexpected token before the return type). VTK_NEWINSTANCE is only
# an ownership hint for the Python wrapper — strip it so the methods stay wrapped
# and the parser is happy. Normal compilation is unaffected (the macro expands to
# nothing without the wrapping-hints header anyway).
sed -i 's/\bVTK_NEWINSTANCE //g' \
    SRep/MRML/vtkEllipticalSRep.h SRep/MRML/vtkSRepSkeletalPoint.h \
    SRep/MRML/vtkMeshSRepInterface.h SRep/MRML/vtkMRMLSRepDisplayNode.h \
    SRep/MRML/vtkSRepSpoke.h SRep/Logic/vtkSlicerSRepLogic.h \
    SRep/Logic/SRepInterpolation.h

%build
%cmake -G Ninja \
    -DSkeletalRepresentation_SUPERBUILD:BOOL=OFF \
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
    > %{_builddir}/srep.files

%files -f %{_builddir}/srep.files
%license LICENSE
%doc README.md

%changelog
* Fri Jun 19 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260601gitdd362a12
- Initial package. SlicerSkeletalRepresentation (SRep loadable module + s-rep
  creation/refinement/warping CLIs + scripted pipelines) built non-superbuild
  against the system 3dslicer foundation. SlicerSALT shape-analysis extension
  and the s-rep library dependency for ShapePopulationViewer.
