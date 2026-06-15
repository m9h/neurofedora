# SlicerOpenIGTLink — OpenIGTLinkIF and related modules: real-time IGT
# (tracking/imaging/transform) communication for 3D Slicer over OpenIGTLink.
#
# Built NON-superbuild against the system foundation: our 3dslicer-devel,
# openigtlink 3.x, and openigtlinkio. The OpenIGTLinkIF module is C++ (loadable);
# OpenIGTLinkRemote / PlusRemote / UltrasoundRemoteControl /
# GenericSerialDeviceRemoteControl are scripted.
#
# NOTE (transitional): the installed 3dslicer-devel still ships only the
# build-tree SlicerConfig.cmake (every path points at the vanished COPR build
# tree, and there is no install(EXPORT) targets file — upstream never wired up
# the install-tree variant). Until the foundation (-43) ships a relocatable
# install-tree config natively, %build regenerates one on the fly from the
# installed (broken) config via gen-install-config.py (Source10) — sub-problems
# A (scalar paths), B (include dirs), C (imported targets). This shim is removed
# once -43 lands.

%global commit      85e5f764f3ad3d4adbaa568db0104b2b8f5998e8
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260603

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11

Name:           3dslicer-openigtlink
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        OpenIGTLink real-time IGT communication extension for 3D Slicer

# 3D Slicer license: BSD-style.
License:        BSD-3-Clause
URL:            https://github.com/openigtlink/SlicerOpenIGTLink
Source0:        %{url}/archive/%{commit}/SlicerOpenIGTLink-%{shortcommit}.tar.gz
# Transitional install-tree SlicerConfig generator + the two aux templates the
# installed foundation does not yet ship (see header note).
Source10:       gen-install-config.py
Source11:       qSlicerExport.h.in
Source12:       SlicerExtensionCPackBundleFixup.cmake.in

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel

# Foundation + the openigtlink chain this extension links against.
BuildRequires:  3dslicer-devel
BuildRequires:  openigtlink-devel >= 3.1.0
BuildRequires:  openigtlinkio-devel

# Everything find_package(Slicer) pulls in (mirrors the foundation's externals).
# Full Qt6 module set find_package(Slicer)'s Qt-version check demands
# (Slicer_REQUIRED_QT_MODULES) — missing any one fails the whole check.
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
BuildRequires:  teem-devel
BuildRequires:  SlicerExecutionModel-devel
BuildRequires:  rapidjson-devel
BuildRequires:  libcurl-devel
BuildRequires:  jsoncpp-devel

Requires:       3dslicer
Requires:       openigtlink%{?_isa} >= 3.1.0
Requires:       openigtlinkio%{?_isa}

%description
SlicerOpenIGTLink adds an OpenIGTLink communication interface to 3D Slicer for
exchanging real-time imaging, tracking, transform, and device-control data with
navigation systems, robots, ultrasound, and other image-guided-therapy devices.
It provides the OpenIGTLinkIF loadable module plus the OpenIGTLinkRemote,
PlusRemote, UltrasoundRemoteControl, and GenericSerialDeviceRemoteControl
scripted modules. This is the neuronavigation bridge used in transcranial
focused-ultrasound workflows (e.g. with BabelBrain).

%prep
%autosetup -n SlicerOpenIGTLink-%{commit}

%build
# --- transitional shim: synthesize a working install-tree SlicerConfig ---------
SLCFG=%{_builddir}/slicer-installcfg
mkdir -p "$SLCFG"
python3 %{SOURCE10} \
    %{slicer_inst}/lib/%{slicer_subdir}/SlicerConfig.cmake \
    "$SLCFG" --root=%{slicer_inst}
install -m0644 %{SOURCE11} %{SOURCE12} "$SLCFG/"
# the installed foundation lacks these two aux templates; point at our copies
sed -i \
  -e "s#\${_SLICER_RELOC_ROOT}/lib/%{slicer_subdir}/CMake/qSlicerExport.h.in#$SLCFG/qSlicerExport.h.in#" \
  -e "s#\${_SLICER_RELOC_ROOT}/lib/%{slicer_subdir}/CMake/SlicerExtensionCPackBundleFixup.cmake.in#$SLCFG/SlicerExtensionCPackBundleFixup.cmake.in#" \
  "$SLCFG/SlicerConfig.cmake"
# ------------------------------------------------------------------------------

%cmake -G Ninja \
    -DSlicerOpenIGTLink_SUPERBUILD:BOOL=OFF \
    -DSlicer_DIR:PATH="$SLCFG" \
    -DOpenIGTLink_DIR:PATH=%{_libdir}/cmake/OpenIGTLink \
    -DOpenIGTLinkIO_DIR:PATH=%{_libdir}/cmake/igtlio \
    -DSlicerOpenIGTLink_USE_VP9:BOOL=OFF \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst}
%cmake_build

%install
%cmake_install
# Catch-all file list for this first validation pass (files + symlinks only, so
# we never claim the shared module dirs that 3dslicer owns). Tightened later.
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/openigtlink.files

%files -f %{_builddir}/openigtlink.files
%license License.txt
%doc README.md

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260603git85e5f764
- Initial real package. SlicerOpenIGTLink (OpenIGTLinkIF + remote-control
  modules) built non-superbuild against system 3dslicer-devel, openigtlink 3.x,
  and openigtlinkio. Uses a transitional install-tree SlicerConfig shim until the
  foundation ships a relocatable config natively.
