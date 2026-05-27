# 3D Slicer 5.10.0 packaging — direct cmake build (NO superbuild).
# Per Slicer's CMakeLists.txt option set, Slicer_SUPERBUILD=OFF expects
# every external dep to be discoverable via find_package(...). We pin each
# to system or our COPR build:
#
#   ITK 5.4.6  -> mhough/neurofedora InsightToolkit5
#   VTK 9.6.2  -> mhough/neurofedora vtk
#   CTK Qt6    -> mhough/neurofedora ctk (2026.01.26-0.5)
#   DCMTK      -> Fedora system
#   teem       -> Fedora system
#   SlicerExecutionModel -> Fedora system
#   qRestAPI   -> mhough/neurofedora (Slicer-pinned commit 88c02c5d)
#   commontk-applauncher -> mhough/neurofedora (a37ad37c)
#   JsonCpp, RapidJSON, LibArchive, TBB, Qt6 -> Fedora system
#   Python     -> bundled by Slicer itself (this v1)
#
# Parallel-install layout under %{_prefix}/lib/slicer-%{version}/ to leave
# room for slicer 6.x someday.

# NOTE: Slicer 5.10.0 release is Qt5-only (find_package(Qt5) hardcoded in
# CMake/SlicerBlockFindQtAndCheckVersion.cmake). Qt6 support landed only
# after the 5.10.0 tag on main. Until 5.11.0 ships, "stable 3dslicer"
# tracks a pinned main-branch commit that has the Qt6 conditional.
# Different commit from slicer-preview so stable users get less churn.
%global slicer_commit 208adb862bc329e6370ae400fef1b18e9ac54cbd
%global slicer_shortcommit %(c=%{slicer_commit}; echo ${c:0:8})
%global slicer_snapdate 20260517
%global slicer_ver  5.11.0~pre.%{slicer_snapdate}git%{slicer_shortcommit}
%global slicer_inst %{_prefix}/lib/slicer

# Slicer ships ~600 MB of shared libs + bundled Python — debuginfo balloons
# to several GB. Disable.
%define debug_package %{nil}

# Slicer's build is huge; use up to 8 jobs concurrently (matching freesurfer).
%global _smp_mflags -j8

Name:           3dslicer
Version:        %{slicer_ver}
Release:        5%{?dist}
Summary:        Open-source platform for medical image analysis and visualization

License:        BSD-3-Clause
URL:            https://slicer.org/
Source0:        https://github.com/Slicer/Slicer/archive/%{slicer_commit}/Slicer-%{slicer_shortcommit}.tar.gz

# Profile environment hook (sets $Slicer_HOME, prepends bin to PATH)
Source1:        slicer.sh

# Build infrastructure
BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  git-core
BuildRequires:  python3-devel
BuildRequires:  xxd

# Qt6 - core, GUI, multimedia, WebEngine, networking, sql, designer plugins
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Sql)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6Multimedia)
BuildRequires:  cmake(Qt6MultimediaWidgets)
BuildRequires:  cmake(Qt6Xml)
BuildRequires:  cmake(Qt6Concurrent)
BuildRequires:  cmake(Qt6PrintSupport)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6WebEngineCore)
BuildRequires:  cmake(Qt6WebEngineWidgets)
BuildRequires:  cmake(Qt6WebChannel)
BuildRequires:  cmake(Qt6Test)
BuildRequires:  cmake(Qt6LinguistTools)
BuildRequires:  cmake(Qt6UiTools)
BuildRequires:  cmake(Qt6Designer)
BuildRequires:  cmake(Qt6Core5Compat)
BuildRequires:  qt6-qttools-devel

# COPR deps
BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  InsightToolkit5-vtk-devel >= 5.4.6
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  ctk-devel
BuildRequires:  vtkAddon-devel
BuildRequires:  qRestAPI-devel
BuildRequires:  commontk-applauncher-devel
BuildRequires:  python-simpleitk

# Fedora system deps
BuildRequires:  dcmtk-devel
BuildRequires:  teem-devel
BuildRequires:  SlicerExecutionModel-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  rapidjson-devel
BuildRequires:  libarchive-devel
BuildRequires:  tbb-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  libcurl-devel
BuildRequires:  libxml2-devel
BuildRequires:  expat-devel
BuildRequires:  bzip2-devel
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel
BuildRequires:  fmt-devel

# VTK transitive deps (our standard ~30-item list)
BuildRequires:  pugixml-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  json-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  double-conversion-devel
BuildRequires:  glew-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  proj-devel
BuildRequires:  gdal-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  cgnslib-devel
BuildRequires:  libpq-devel
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  openslide-devel
BuildRequires:  libtiff-devel
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  libXcursor-devel
BuildRequires:  hdf5-devel
BuildRequires:  boost-devel
BuildRequires:  gdcm-devel

# Python ecosystem (Slicer bundles its own Python, but cmake checks for these)
BuildRequires:  python3-pip
BuildRequires:  python3-numpy

# Runtime requirements
Requires:       qt6-qtbase
Requires:       qt6-qtwebengine
Requires:       qt6-qtmultimedia
Requires:       hicolor-icon-theme
Requires:       libGL

%description
3D Slicer is a free, open-source software platform for biomedical image
analysis, visualization, and clinical translation. It provides modules
for image registration, segmentation, surface mesh processing, DICOM I/O,
diffusion MRI tractography, neuroimaging, and Python-scriptable
workflows.

This package builds Slicer with system-installed dependencies (ITK 5,
VTK 9.6, CTK Qt6, DCMTK, teem, SimpleITK) rather than via the upstream
SuperBuild, for Fedora-policy compliance.

%package devel
Summary:        Development headers for 3D Slicer
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers, cmake configuration, and devel symlinks for building Slicer
extension modules out of tree.

%prep
%autosetup -p1 -n Slicer-%{slicer_commit}

# Slicer main HEAD already supports Qt6 and VTK 9.6 natively — no sed
# patches needed for those. Python version: defaults to 3.12.10 floor;
# Fedora 44 ships 3.14 which satisfies >= 3.12.10 fine.

%build
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error -include cstdint -fpermissive"
export CFLAGS="%{optflags} -Wno-error -std=gnu17"
# Required for the bundled qt-keyword build harness
export QT_QPA_PLATFORM=offscreen

%cmake -G Ninja \
    `# THE flag — drop superbuild` \
    -DSlicer_SUPERBUILD:BOOL=OFF \
    \
    `# System packages for every external` \
    -DSlicer_USE_SYSTEM_ITK:BOOL=ON \
    -DSlicer_USE_SYSTEM_VTK:BOOL=ON \
    -DSlicer_USE_SYSTEM_CTK:BOOL=ON \
    -DSlicer_USE_SYSTEM_DCMTK:BOOL=ON \
    -DSlicer_USE_SYSTEM_teem:BOOL=ON \
    -DSlicer_USE_SYSTEM_SlicerExecutionModel:BOOL=ON \
    -DSlicer_USE_SYSTEM_jsoncpp:BOOL=ON \
    -DSlicer_USE_SYSTEM_RapidJSON:BOOL=ON \
    -DSlicer_USE_SYSTEM_LibArchive:BOOL=ON \
    -DSlicer_USE_SYSTEM_python:BOOL=ON \
    -DSlicer_USE_SYSTEM_qRestAPI:BOOL=ON \
    -DSlicer_USE_SYSTEM_python_SimpleITK:BOOL=ON \
    \
    `# Find_package paths` \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    -DCTK_DIR:PATH=%{_libdir}/cmake/CTK \
    -DDCMTK_DIR:PATH=%{_libdir}/cmake/dcmtk \
    -DCTKAppLauncher_DIR:PATH=%{_libdir}/cmake/CTKAppLauncher \
    -DqRestAPI_DIR:PATH=%{_libdir}/cmake/qRestAPI \
    `# Qt6 detection: SlicerBlockFindQtAndCheckVersion.cmake checks` \
    `# if(DEFINED Qt6_DIR) to pick Qt6 over Qt5. Without this hint it` \
    `# tries find_package(Qt5) and aborts with "Qt5 was not found".` \
    -DQt6_DIR:PATH=%{_libdir}/cmake/Qt6 \
    \
    `# Feature toggles` \
    -DSlicer_USE_PYTHONQT:BOOL=ON \
    -DSlicer_USE_NUMPY:BOOL=ON \
    -DSlicer_USE_SCIPY:BOOL=ON \
    -DSlicer_USE_SimpleITK:BOOL=ON \
    -DSlicer_USE_CTKAPPLAUNCHER:BOOL=ON \
    -DSlicer_USE_TBB:BOOL=ON \
    -DSlicer_USE_QtTesting:BOOL=ON \
    -DSlicer_BUILD_CLI:BOOL=ON \
    -DSlicer_BUILD_QTLOADABLEMODULES:BOOL=ON \
    -DSlicer_BUILD_QTSCRIPTEDMODULES:BOOL=ON \
    -DSlicer_BUILD_DICOM_SUPPORT:BOOL=ON \
    -DSlicer_BUILD_DIFFUSION_SUPPORT:BOOL=ON \
    -DSlicer_BUILD_I18N_SUPPORT:BOOL=OFF \
    -DSlicer_BUILD_WEBENGINE_SUPPORT:BOOL=ON \
    -DSlicer_BUILD_MULTIMEDIA_SUPPORT:BOOL=ON \
    -DSlicer_BUILD_EXTENSIONMANAGER_SUPPORT:BOOL=ON \
    -DSlicer_BUILD_APPLICATIONUPDATE_SUPPORT:BOOL=ON \
    -DSlicer_BUILD_DOCUMENTATION:BOOL=OFF \
    -DSlicer_BUILD_KRB5_GSSAPI_STUB:BOOL=OFF \
    \
    `# Qt + VTK pins matching what our COPR ships` \
    -DSlicer_REQUIRED_QT_VERSION:STRING=6.8 \
    -DSlicer_VTK_VERSION_MAJOR:STRING=9 \
    -DSlicer_VTK_VERSION_MINOR:STRING=6 \
    -DSlicer_VTK_SMP_IMPLEMENTATION_TYPE:STRING=TBB \
    \
    `# Install layout — parallel-install under slicer-%{version}/` \
    -DSlicer_INSTALL_NO_DEVELOPMENT:BOOL=OFF \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst} \
    -DSlicer_INSTALL_ROOT:PATH=%{slicer_inst} \
    -DSlicer_INSTALL_DEVELOPMENT:BOOL=ON \
    \
    `# Misc` \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DSlicer_USE_VTK_DEBUG_LEAKS:BOOL=OFF

%cmake_build

%install
%cmake_install

# Profile.d hook
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/profile.d/slicer.sh

# /usr/bin/slicer wrapper
install -d %{buildroot}%{_bindir}
ln -sf %{slicer_inst}/Slicer %{buildroot}%{_bindir}/slicer
# Drop the leftover Source0 reference to v%{version} since 5.10.0 tag is unused now
# (Source0 fetches from main HEAD by commit SHA).

%files
%license License.txt
%doc README.md
%{_bindir}/slicer
%{_sysconfdir}/profile.d/slicer.sh
%{slicer_inst}/
%exclude %{slicer_inst}/include/
%exclude %{slicer_inst}/lib/cmake/

%files devel
%{slicer_inst}/include/
%{slicer_inst}/lib/cmake/

%changelog

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-5
- MAJOR PIVOT: switch stable channel to Slicer main HEAD (commit
  208adb86, 2026-05-17). Slicer 5.10.0 release tag is Qt5-only;
  Qt6 + VTK 9.6 + ITK 5.4 system-package support only landed on
  main after the v5.10.0 tag. Tracking a pinned main commit gets
  us a buildable stable today; we'll re-anchor to 5.11.0 when
  upstream tags it.
- Install layout simplified to /usr/lib/slicer (no version suffix)
  since main HEAD is the only Qt6-ready branch and stable+preview
  effectively share one tree until 5.11.0.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.10.0-4
- Set Qt6_DIR explicitly: SlicerBlockFindQtAndCheckVersion.cmake
  checks if(DEFINED Qt6_DIR) to choose Qt6 over Qt5. Without the
  flag, Slicer falls back to find_package(Qt5) and aborts.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.10.0-3
- Switch sed delimiter to @ (was |, which collided with the |
  alternator inside the VTK version regex — sed errored silently
  and the patch never applied in -2).

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.10.0-2
- Sed-patch CMakeLists.txt:441 to allow Slicer_VTK_VERSION_MINOR=6
  (Slicer 5.10.0 only whitelists 2/4/5; main branch already accepts 6).
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.10.0-1
- Initial RPM package for 3D Slicer 5.10.0.
- Built with Slicer_SUPERBUILD=OFF — all externals from system / COPR.
- Qt6 (>= 6.8); ITK 5.4.6; VTK 9.6.2; CTK 2026.01.26 Qt6 build.
- DICOM/diffusion/webengine/multimedia/extension-manager all enabled.
- Documentation/i18n disabled to keep first build small.
- Parallel-install under /usr/lib/slicer-5.10.0/ with /etc/profile.d hook.
