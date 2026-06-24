# SlicerIGSIO — Slicer interface to the IGSIO (Image-Guided Surgery
# InterOperability) toolkit: sequence/metafile import-export, video utilities and
# the SlicerIGSIOCommon bridge library. A utility extension whose main purpose is
# to be a build dependency of SlicerIGT (which find_package(SlicerIGSIO REQUIRED)).
# C++ loadable modules built NON-superbuild against the system 3dslicer foundation
# and the system igsio library (which now ships an install-tree IGSIOConfig.cmake).

%global commit      82345aea56fbfbe99e53106a4f3e9413d93bc761
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260513

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11

Name:           3dslicer-igsio
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        IGSIO sequence/video tools for 3D Slicer (SlicerIGT dependency)

# 3D Slicer / IGSIO extension: BSD-style.
License:        BSD-3-Clause
URL:            https://github.com/IGSIO/SlicerIGSIO
Source0:        %{url}/archive/%{commit}/SlicerIGSIO-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  git-core

BuildRequires:  3dslicer-devel >= 5.11.0~pre.20260517git208adb86-54
# IGSIO library + its install-tree IGSIOConfig.cmake (igsio >= 0.2).
BuildRequires:  igsio-devel >= 1.0-0.2

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
Requires:       igsio

%description
SlicerIGSIO integrates the IGSIO (Image-Guided Surgery InterOperability) toolkit
into 3D Slicer: importing and exporting tracked image sequences and metafiles,
video utilities, and the SlicerIGSIOCommon bridge library used by other IGT
extensions. It is primarily a build and runtime dependency for SlicerIGT. The
modules are built non-superbuild against the system 3D Slicer foundation and the
system igsio library.

%prep
%autosetup -n SlicerIGSIO-%{commit}

# Distro build: install modules directly, not as an Extension-Manager bundle, so
# skip SlicerExtensionCPack (wants README/license + the s4ext description template
# the install tree doesn't ship) and the IGSIO RuntimeLibraries CPack staging
# (igsio is already a system package, installed separately).
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' CMakeLists.txt

%build
%cmake -G Ninja \
    -DSlicerIGSIO_SUPERBUILD:BOOL=OFF \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DIGSIO_DIR:PATH=%{_libdir}/cmake/IGSIO \
    -DSlicerIGSIO_USE_VP9:BOOL=OFF \
    -DSlicerIGSIO_USE_GPU:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_SKIP_SlicerBlockAdditionalLauncherSettings:BOOL=TRUE \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst}
%cmake_build

%install
%cmake_install
# Catch-all file list (files + symlinks only, so the shared module dirs that
# 3dslicer owns are never claimed). Tightened later.
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/igsio.files

%files -f %{_builddir}/igsio.files
%license LICENSE
%doc README.md

%changelog
* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260513git82345aea
- Initial package. SlicerIGSIO (SlicerIGSIOCommon library + SequenceIO, VideoUtil
  and MetafileImporter loadable modules) built non-superbuild against the system
  3dslicer foundation (>= -54) and the system igsio library (>= 0.2, which now
  ships an install-tree IGSIOConfig.cmake). VP9/MKV disabled to match the igsio
  build. Build dependency for SlicerIGT.
