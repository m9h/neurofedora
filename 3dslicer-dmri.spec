# SlicerDMRI — diffusion MRI for 3D Slicer: tractography, tensor estimation,
# fiber-bundle visualization. C++ extension (vtkDMRI library + loadable/CLI
# modules), built NON-superbuild against the system foundation (3dslicer-devel
# >= -46, which ships the install-tree SlicerConfig + the Base/Logic and
# loadable-module headers these modules #include). Standalone: find_package is
# only Slicer/DCMTK/SlicerExecutionModel — no extra bundled libraries. The
# EXTENSION_DEPENDS (UKFTractography, SlicerDcm2nii) are soft extension-manager
# companions, not build dependencies.

%global commit      a40200bfb9df21a6092b308188175d1e339b5771
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260601

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11

Name:           3dslicer-dmri
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Diffusion MRI (tractography, tensors, fiber bundles) extension for 3D Slicer

# 3D Slicer license: BSD-style.
License:        BSD-3-Clause
URL:            https://github.com/SlicerDMRI/SlicerDMRI
Source0:        %{url}/archive/%{commit}/SlicerDMRI-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel

BuildRequires:  3dslicer-devel >= 5.11.0~pre.20260517git208adb86-49

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
BuildRequires:  teem-devel
BuildRequires:  SlicerExecutionModel-devel
BuildRequires:  rapidjson-devel
BuildRequires:  libcurl-devel
BuildRequires:  jsoncpp-devel

Requires:       3dslicer

%description
SlicerDMRI brings diffusion-weighted MRI analysis to 3D Slicer: diffusion-tensor
estimation, deterministic and interactive tractography, fiber-bundle handling and
visualization, and a set of diffusion CLI tools. It is a core neuroimaging
extension. The vtkDMRI library and its loadable/CLI modules are built against the
system 3D Slicer foundation.

%prep
%autosetup -n SlicerDMRI-%{commit}

# Distro build: install modules directly, not as an Extension-Manager bundle, so
# skip SlicerExtensionCPack (wants README/license + the s4ext description
# template the install tree doesn't ship).
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' CMakeLists.txt

# vtkDMRI does find_package(Teem); include(${Teem_USE_FILE}) directly, but
# Fedora's teem ships no TeemUse.cmake (resolves to a nonexistent path). Drop
# the include — modern Teem needs no use-file.
sed -i '/include(${Teem_USE_FILE})/d' Libs/vtkDMRI/CMakeLists.txt

# Transitional shims until building against foundation -47 (which bakes these in:
# Qt include dirs + loadable-module imported targets). Harmless on -47.
sed -i 's|^include(${Slicer_USE_FILE})|&\ninclude_directories("/usr/include/qt6" "/usr/include/qt6/QtCore" "/usr/include/qt6/QtGui" "/usr/include/qt6/QtWidgets" "/usr/include/qt6/QtCore5Compat")\nlink_directories("/usr/lib/slicer/lib/Slicer-5.11/qt-loadable-modules")|' CMakeLists.txt

%build
%cmake -G Ninja \
    -DSlicerDMRI_SUPERBUILD:BOOL=OFF \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_SKIP_SlicerBlockAdditionalLauncherSettings:BOOL=TRUE \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst}
%cmake_build

%install
%cmake_install
# Catch-all file list (files + symlinks only, so the shared module dirs that
# 3dslicer owns are never claimed). Tightened later.
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/dmri.files

%files -f %{_builddir}/dmri.files
%license License.txt
%doc README.md

%changelog
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260601gita40200bf
- Initial real package. SlicerDMRI (vtkDMRI library + tractography/tensor
  loadable & CLI modules) built non-superbuild against system 3dslicer-devel
  >= -46. Replaces the stale Version-0 stub.
