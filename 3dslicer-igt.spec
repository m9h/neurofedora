# SlicerIGT — image-guided therapy / interventions toolkit for 3D Slicer:
# patient/landmark registration, model creation, tracked-tool visualization,
# transform processing, volume reslice/reconstruction, pivot/landmark calibration,
# breach warning, and related real-time navigation modules. The flagship IGT
# extension; used for tracked ultrasound and (with OpenIGTLinkIF) neuronavigation.
#
# C++ loadable modules + scripted Python modules, built NON-superbuild against the
# system 3dslicer foundation, the SlicerIGSIO extension (find_package(SlicerIGSIO))
# and the system igsio library. No superbuild: SlicerIGT has no bundled external
# projects — its only build dependency, SlicerIGSIO, is a system package.

%global commit      47c8b3a5eb0ecbea999b23bb62a51f85ca1fc609
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260408

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11

Name:           3dslicer-igt
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Image-guided therapy / navigation toolkit for 3D Slicer (SlicerIGT)

License:        BSD-3-Clause
URL:            https://github.com/SlicerIGT/SlicerIGT
Source0:        %{url}/archive/%{commit}/SlicerIGT-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  git-core

BuildRequires:  3dslicer-devel >= 5.11.0~pre.20260517git208adb86-54
# SlicerIGSIO extension (ships SlicerIGSIOConfig.cmake + libvtkSlicerIGSIOCommon)
# and the IGSIO library (its IGSIOConfig.cmake).
BuildRequires:  3dslicer-igsio >= 1.0-0.3
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
Requires:       3dslicer-igsio
# Soft runtime companion for live navigation (OpenIGTLink network I/O).
Recommends:     3dslicer-openigtlink

%description
SlicerIGT brings image-guided therapy and surgical-navigation tooling to 3D
Slicer: fiducial and landmark registration, model creation from tracked tools,
pivot and landmark calibration, transform processing, real-time volume reslicing
and reconstruction, breach warning, and viewpoint control. Combined with tracked
imaging/tracking hardware (typically via OpenIGTLink), it supports tracked
ultrasound and neuronavigation workflows.

The C++ loadable modules and scripted Python modules are built non-superbuild
against the system 3D Slicer foundation, the SlicerIGSIO extension, and the
system igsio library.

%prep
%autosetup -n SlicerIGT-%{commit}

# Distro build: install modules directly, not as an Extension-Manager bundle, so
# skip SlicerExtensionCPack (wants README/license + the s4ext description template
# the install tree doesn't ship).
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' CMakeLists.txt

%build
%cmake -G Ninja \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DSlicerIGSIO_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DIGSIO_DIR:PATH=%{_libdir}/cmake/IGSIO \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_SKIP_SlicerBlockAdditionalLauncherSettings:BOOL=TRUE \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst}
%cmake_build

%install
%cmake_install
# Catch-all file list (files + symlinks only, so the shared module dirs that
# 3dslicer owns are never claimed). Tightened later.
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/igt.files

%files -f %{_builddir}/igt.files
%license LICENSE
%doc README.md

%changelog
* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260408git47c8b3a5
- Initial package. SlicerIGT (image-guided therapy / navigation modules) built
  non-superbuild against the system 3dslicer foundation (>= -54), the SlicerIGSIO
  extension (>= 0.3, ships SlicerIGSIOConfig.cmake) and the system igsio library.
  Layer 3 (final) of the IGT build chain.
