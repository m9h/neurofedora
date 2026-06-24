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
Release:        0.3.%{snapdate}git%{shortcommit}%{?dist}
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

# MetafileImporter (a GUI convenience module) #includes qSlicerSequencesReader.h,
# a top-level header of Slicer's built-in Sequences loadable module that the
# foundation install tree does not yet ship (it ships the Sequences Logic/MRML
# headers, but not the module-root qSlicer GUI headers). The SlicerIGSIOCommon
# library + SequenceIO + VideoUtil — which is what SlicerIGT find_package()s and
# links — build fine, so drop this one module for now. Re-enable once the
# foundation ships the loadable-module top-level qSlicer headers (tracked).
sed -i '/add_subdirectory(MetafileImporter)/d' CMakeLists.txt

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

# Ship the SlicerIGSIOCommon public headers + a relocatable SlicerIGSIOConfig.cmake
# so SlicerIGT can find_package(SlicerIGSIO REQUIRED). Upstream's Slicer
# EXTENSION_GENERATE_CONFIG macro only writes a build-tree <Ext>Config.cmake
# (configure_file -> build dir, never installed), so the install tree ships none
# and SlicerIGSIOCommon's headers aren't installed either. Headers go into the
# Slicer include tree (resolved via the imported target's interface includes); the
# config defines the imported vtkSlicerIGSIOCommon target + include dirs and pulls
# in the system IGSIO. The library installed in qt-loadable-modules already records
# its IGSIO/VTK/MRML closure in DT_NEEDED.
_si_inc=%{buildroot}%{slicer_inst}/include/%{slicer_subdir}
mkdir -p "$_si_inc"
cp -an SlicerIGSIOCommon/*.h "$_si_inc/"
cat > %{buildroot}%{slicer_inst}/lib/%{slicer_subdir}/SlicerIGSIOConfig.cmake <<'SICFG'
# Relocatable install-tree SlicerIGSIOConfig.cmake (Fedora 3dslicer-igsio package).
get_filename_component(_sigsio_libdir "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
get_filename_component(_sigsio_incdir "${_sigsio_libdir}/../../include/Slicer-5.11" ABSOLUTE)

# Pull in the system IGSIO (the in-tree SlicerIGSIO build does this via its custom
# config: include(${IGSIO_DIR}/IGSIOConfig.cmake)). Provides vtkIGSIOCommon etc.
# and VTKIGSIOCOMMON_INCLUDE_DIRS.
find_package(IGSIO QUIET)

set(SlicerIGSIO_INCLUDE_DIRS "${_sigsio_incdir}" "${VTKIGSIOCOMMON_INCLUDE_DIRS}")
set(vtkSlicerIGSIOCommon_INCLUDE_DIRS "${_sigsio_incdir}" "${VTKIGSIOCOMMON_INCLUDE_DIRS}")

if(NOT TARGET vtkSlicerIGSIOCommon)
  add_library(vtkSlicerIGSIOCommon SHARED IMPORTED)
  set_target_properties(vtkSlicerIGSIOCommon PROPERTIES
    IMPORTED_LOCATION "${_sigsio_libdir}/qt-loadable-modules/libvtkSlicerIGSIOCommon.so"
    INTERFACE_INCLUDE_DIRECTORIES "${_sigsio_incdir};${VTKIGSIOCOMMON_INCLUDE_DIRS}")
endif()

set(SlicerIGSIO_LIBRARIES vtkSlicerIGSIOCommon)
set(SlicerIGSIO_FOUND TRUE)
SICFG

# Catch-all file list (files + symlinks only, so the shared module dirs that
# 3dslicer owns are never claimed). Tightened later.
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/igsio.files

%files -f %{_builddir}/igsio.files
%license LICENSE
%doc README.md

%changelog
* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.3.20260513git82345aea
- Ship SlicerIGSIOCommon headers + a relocatable SlicerIGSIOConfig.cmake so
  SlicerIGT can find_package(SlicerIGSIO) (the Slicer generate-config macro only
  writes a build-tree config; install tree got none, and the headers weren't
  installed). Defines the imported vtkSlicerIGSIOCommon target + include dirs and
  pulls in the system IGSIO.

* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.2.20260513git82345aea
- Drop the MetafileImporter GUI module (stopgap): it needs Slicer's Sequences
  module-root header qSlicerSequencesReader.h, which the foundation install tree
  doesn't yet ship. The SlicerIGSIOCommon library + SequenceIO + VideoUtil (what
  SlicerIGT depends on) build fine. Re-enable once the foundation ships the
  loadable-module top-level qSlicer headers.

* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260513git82345aea
- Initial package. SlicerIGSIO (SlicerIGSIOCommon library + SequenceIO, VideoUtil
  and MetafileImporter loadable modules) built non-superbuild against the system
  3dslicer foundation (>= -54) and the system igsio library (>= 0.2, which now
  ships an install-tree IGSIOConfig.cmake). VP9/MKV disabled to match the igsio
  build. Build dependency for SlicerIGT.
