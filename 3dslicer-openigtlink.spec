# SlicerOpenIGTLink — OpenIGTLinkIF and related modules: real-time IGT
# (tracking/imaging/transform) communication for 3D Slicer over OpenIGTLink.
#
# Built NON-superbuild against the system foundation: our 3dslicer-devel,
# openigtlink 3.x, and openigtlinkio. The OpenIGTLinkIF module is C++ (loadable);
# OpenIGTLinkRemote / PlusRemote / UltrasoundRemoteControl /
# GenericSerialDeviceRemoteControl are scripted.
#
# Builds against the foundation -46 install-tree SlicerConfig (relocatable config
# + imported targets + module/base headers + wrap-hierarchy). A few transitional
# %prep shims remain until the foundation -47 bakes them in: Qt include dirs +
# qt-loadable-modules link dir (so the imported module libs resolve) and dropping
# the PlusRemote/UltrasoundRemoteControl modules (legacy Qt5 APIs; PLUS-toolkit
# front-ends out of scope here). Core neuronavigation = OpenIGTLinkIF.

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

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel

# Foundation + the openigtlink chain this extension links against.
BuildRequires:  3dslicer-devel >= 5.11.0~pre.20260517git208adb86-46
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

# Distro build: we install the modules directly, not as an Extension-Manager
# bundle, so skip SlicerExtensionCPack (it wants a README/license + the
# extension_description.s4ext.in template that the install tree doesn't ship).
# (The Teem-NO_USEFILE and wrap-hierarchy-output-dir fixes are now in the
# foundation -45 install-tree config, so no longer patched here.)
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' CMakeLists.txt
# (vtkAddon include dir now propagates via the foundation -46 imported targets'
# INTERFACE_INCLUDE_DIRECTORIES, and the module/base headers ship in -46.)

# TEMP test (proper fix = INTERFACE_LINK_LIBRARIES Qt6 on the q* imported targets
# in foundation -47): some module logic libs (e.g. PlusRemote) use
# qSlicerCoreApplication, so the Qt headers must be on the path.
sed -i 's|^include(${Slicer_USE_FILE})|&\ninclude_directories("/usr/include/qt6" "/usr/include/qt6/QtCore" "/usr/include/qt6/QtGui" "/usr/include/qt6/QtWidgets" "/usr/include/qt6/QtCore5Compat")\nlink_directories("/usr/lib/slicer/lib/Slicer-5.11/qt-loadable-modules")|' CMakeLists.txt

# Drop the PlusRemote + UltrasoundRemoteControl modules: they are remote-control
# front-ends for the PLUS real-time ultrasound acquisition toolkit (not packaged,
# and out of scope for the neuronavigation use case), and they pull in legacy
# Qt5 APIs (QRegExp via old ctk paths). The core OpenIGTLinkIF neuronavigation
# bridge + OpenIGTLinkRemote + GenericSerialDeviceRemoteControl are kept.
sed -i -e '/add_subdirectory(PlusRemote)/d' \
       -e '/add_subdirectory(UltrasoundRemoteControl)/d' CMakeLists.txt

%build
# Build against the foundation's native install-tree SlicerConfig.cmake, shipped
# by 3dslicer-devel >= -44 (relocatable config + SlicerTargets + wrap-hierarchy).
%cmake -G Ninja \
    -DSlicerOpenIGTLink_SUPERBUILD:BOOL=OFF \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DOpenIGTLink_DIR:PATH=%{_libdir}/cmake/OpenIGTLink \
    -DOpenIGTLinkIO_DIR:PATH=%{_libdir}/cmake/igtlio \
    -DSlicerOpenIGTLink_USE_VP9:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_SKIP_SlicerBlockAdditionalLauncherSettings:BOOL=TRUE \
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
