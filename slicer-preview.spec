# 3D Slicer Preview — same packaging strategy as 3dslicer, but tracks the
# Slicer/Slicer `main` branch HEAD instead of a tagged release. Coexists
# with the stable 3dslicer package via parallel-install (separate
# install root + separate /usr/bin entry point: `slicer-preview`).
#
# Bumping policy: refresh %{snapdate}/%{commit} to the most recent main
# branch HEAD whenever rebuilding. The release suffix encodes the date
# so subsequent rebuilds compare cleanly.

%global snapdate 20260628
%global commit   9774a684fb062714f5cc7e0e732c5d036d3dd87f
%global shortcommit %(c=%{commit}; echo ${c:0:8})

# We pin to the upcoming-release nominal version 5.11.0~preview… so RPM
# treats us as newer than 3dslicer 5.10.0 stable, and any in-between
# Slicer 5.11.0 release will compare cleanly newer than this preview.
%global preview_ver 5.13.0~preview.%{snapdate}git%{shortcommit}
%global slicer_inst %{_prefix}/lib/slicer-preview

%define debug_package %{nil}
%global _smp_mflags -j8

Name:           slicer-preview
Version:        %{preview_ver}
Release:        2%{?dist}
Summary:        3D Slicer development snapshot (main branch) for medical image analysis

License:        BSD-3-Clause
URL:            https://slicer.org/
Source0:        https://github.com/Slicer/Slicer/archive/%{commit}/Slicer-preview-%{shortcommit}.tar.gz
# Profile.d hook (shared script: re-uses logic from stable, looks for
# both slicer-VER and slicer-preview)
Source1:        slicer-preview.sh

# Build infrastructure — same as 3dslicer; see 3dslicer.spec for rationale.
BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  git-core
BuildRequires:  python3-devel
BuildRequires:  xxd

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

BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  InsightToolkit5-vtk-devel >= 5.4.6
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  ctk-devel
BuildRequires:  vtkAddon-devel
BuildRequires:  qRestAPI-devel
BuildRequires:  commontk-applauncher-devel
BuildRequires:  python-simpleitk

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

BuildRequires:  python3-pip
BuildRequires:  python3-numpy

Requires:       qt6-qtbase
Requires:       qt6-qtwebengine
Requires:       qt6-qtmultimedia
Requires:       hicolor-icon-theme
Requires:       libGL

%description
3D Slicer Preview tracks the current Slicer development branch (main) and
is intended for users who want access to features and bug-fixes that
have landed since the last stable release (5.10.0).

This package coexists with the stable 3dslicer package. Stable installs
to /usr/lib/slicer-5.10.0/ and is invoked as `slicer`. Preview installs
to /usr/lib/slicer-preview/ and is invoked as `slicer-preview`.

Use stable for routine work; use preview to validate upcoming-release
behaviour or to use new modules before they reach a tagged release.

%package devel
Summary:        Development headers for 3D Slicer Preview
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers, cmake config files, and devel symlinks for building Slicer
extension modules against the preview channel out of tree.

%prep
%autosetup -p1 -n Slicer-%{commit}

# Sanity patch: relax Slicer_REQUIRED_PYTHON_VERSION strict-equal to allow
# Fedora's Python 3.14 (Slicer pins 3.12.10 nominally).
sed -i 's/Slicer_REQUIRED_PYTHON_VERSION "3\.[0-9]*\.[0-9]*")/Slicer_REQUIRED_PYTHON_VERSION "3.12.0")/' CMakeLists.txt 2>/dev/null || :

%build
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error -include cstdint -fpermissive"
export CFLAGS="%{optflags} -Wno-error -std=gnu17"
export QT_QPA_PLATFORM=offscreen

%cmake -G Ninja \
    -DSlicer_SUPERBUILD:BOOL=OFF \
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
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    -DCTK_DIR:PATH=%{_libdir}/cmake/CTK \
    -DDCMTK_DIR:PATH=%{_libdir}/cmake/dcmtk \
    -DCTKAppLauncher_DIR:PATH=%{_libdir}/cmake/CTKAppLauncher \
    -DqRestAPI_DIR:PATH=%{_libdir}/cmake/qRestAPI \
    `# Store settings + extensions in the user's home, not the read-only system` \
    `# tree (else the Extensions Manager fails on a system install). See 3dslicer.` \
    -DSlicer_STORE_SETTINGS_IN_APPLICATION_HOME_DIR:BOOL=OFF \
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
    -DSlicer_REQUIRED_QT_VERSION:STRING=6.8 \
    -DSlicer_VTK_VERSION_MAJOR:STRING=9 \
    -DSlicer_VTK_VERSION_MINOR:STRING=6 \
    -DSlicer_VTK_SMP_IMPLEMENTATION_TYPE:STRING=TBB \
    -DSlicer_INSTALL_NO_DEVELOPMENT:BOOL=OFF \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst} \
    -DSlicer_INSTALL_ROOT:PATH=%{slicer_inst} \
    -DSlicer_INSTALL_DEVELOPMENT:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DSlicer_USE_VTK_DEBUG_LEAKS:BOOL=OFF

%cmake_build

%install
%cmake_install
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/profile.d/slicer-preview.sh
install -d %{buildroot}%{_bindir}
ln -sf %{slicer_inst}/Slicer %{buildroot}%{_bindir}/slicer-preview

%files
%license License.txt
%doc README.md
%{_bindir}/slicer-preview
%{_sysconfdir}/profile.d/slicer-preview.sh
%{slicer_inst}/
%exclude %{slicer_inst}/include/
%exclude %{slicer_inst}/lib/cmake/

%files devel
%{slicer_inst}/include/
%{slicer_inst}/lib/cmake/

%changelog
* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.13.0~preview.20260628git9774a684-2
- Slicer_STORE_SETTINGS_IN_APPLICATION_HOME_DIR=OFF so user settings + extensions
  land in the user's home, not the read-only install tree (Extensions Manager fix;
  see 3dslicer 5.12.0-2).

* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.13.0~preview.20260628git9774a684-1
- Refresh the dev/preview track from the 5.11.0~preview snapshot to the current
  5.13.0 main HEAD (Slicer's dev version; even minor 5.12 is now stable in
  3dslicer). Parallel-installable with stable 3dslicer (separate
  /usr/lib/slicer-preview root + /usr/bin/slicer-preview launcher).

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~preview.20260517git208adb86-1
- Initial preview-channel package tracking Slicer main branch.
- Same system-deps strategy as the stable 3dslicer package (5.10.0).
- Coexists via parallel-install at /usr/lib/slicer-preview/ ;
  invoked as `slicer-preview` to keep `slicer` pointing at stable.
