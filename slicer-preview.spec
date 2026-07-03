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

# Nominal version tracks Slicer's dev minor (5.13.0, odd = dev). RPM treats
# 5.13.0~preview as newer than stable 3dslicer 5.12.0 (even = stable), and a
# future 5.13.0 tag would compare cleanly newer than this preview snapshot.
%global preview_ver 5.13.0~preview.%{snapdate}git%{shortcommit}
%global slicer_inst %{_prefix}/lib/slicer-preview

%define debug_package %{nil}

# Disable LTO — Fedora's default -flto=auto -ffat-lto-objects roughly doubles
# C++ compile time and inflates link memory. See 3dslicer: with LTO the build
# times out; LTO off ~halves compile time.
%global _lto_cflags %{nil}

# Build single-threaded. At higher -j the ~16 simultaneous Qt/VTK-heavy module
# compiles that start at ninja step ~705 blow memory on low-RAM COPR builders
# and swap-stall (3dslicer proved -j8/-j4/-j2 all stall there). -j1 + a raised
# --timeout 86400 on submission is the working combination.
%global _smp_mflags -j1

# Slicer's ctkAppLauncher shebang normalization can leave a /usr/bin/python-real
# auto-dependency that no package provides; exclude it as a backstop.
%global __requires_exclude ^/usr/bin/python-real$

Name:           slicer-preview
Version:        %{preview_ver}
Release:        5%{?dist}
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
# CTK is built with CTK_USE_QTTESTING=ON, so CTKConfig.cmake always calls
# find_dependency(QtTesting); qMRML*EventPlayer sources also link CTKQtTesting.
BuildRequires:  qttesting-devel
# Slicer_USE_PYTHONQT=ON: find_package(PythonQt REQUIRED) + Python-scripted layer.
BuildRequires:  python-pythonqt-devel
# Pulled in transitively by Slicer's cmake config consumers (VTK/SEM).
BuildRequires:  cli11-devel
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
# DICOM/Python-scripted layer: Slicer's DICOMLib imports these at module load.
Requires:       python3-dicomweb-client
Requires:       python3-highdicom
Requires:       python3-legacy-cgi

%description
3D Slicer Preview tracks the current Slicer development branch (main) and
is intended for users who want access to features and bug-fixes that
have landed since the current stable release (5.12.0).

This package coexists with the stable 3dslicer package via parallel install:
stable installs to /usr/lib/slicer and is invoked as `Slicer`; preview installs
to /usr/lib/slicer-preview and is invoked as `slicer-preview`. User settings and
downloaded extensions are revision-keyed under ~/.config/slicer.org, so the two
stay isolated.

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

# ---------------------------------------------------------------------------
# System-libs (non-superbuild) source-bug fixes — ported verbatim from the
# battle-tested stable 3dslicer spec. 5.13 (main HEAD) and 5.12 share these
# trees, so the same fixes apply. See 3dslicer.spec for the full rationale.
# ---------------------------------------------------------------------------

# Short-circuit SlicerBlockInstallTBB. It expects to bundle specific TBB SONAME
# versions that don't exist on Fedora; as an RPM we rely on the system tbb.
echo 'return()' > CMake/SlicerBlockInstallTBB.cmake

# VTK linkage: Fedora's modular VTK leaves several modules out of the legacy
# VTK_LIBRARIES that Slicer libs link, so they fail with undefined references.
# Force the requested VTK:: targets (+ the foundational Common* family) onto
# link_libraries() right after find_package(VTK).
python3 - CMakeLists.txt <<'PYEOF'
import sys, re
f = sys.argv[1]; s = open(f).read()
inj = ("\n# Fedora modular-VTK linkage fix (packaging): the new VTK no longer puts the\n"
       "# full module closure into the legacy VTK_LIBRARIES that several Slicer libs\n"
       "# link, so they fail with undefined references (vtkImageAccumulate,\n"
       "# vtkExtractSelection, vtkPolyDataToImageStencil, vtkTimerLog, ...). Rather\n"
       "# than chase modules one at a time, link every component Slicer already\n"
       "# requested (Slicer_VTK_COMPONENTS) PLUS the foundational Common* family that\n"
       "# Slicer libs reference transitively but the components list omits (vtkTimerLog\n"
       "# = CommonSystem); link them all onto every target defined afterwards via\n"
       "# link_libraries() (--as-needed drops the unused ones). Robust against any\n"
       "# VTK_LIBRARIES scope/propagation gaps without per-module whack-a-mole.\n"
       "set(_PKGVTK_EXTRA\n"
       "  CommonCore CommonSystem CommonMath CommonMisc CommonTransforms\n"
       "  CommonExecutionModel CommonDataModel CommonColor CommonComputationalGeometry\n"
       "  FiltersCore FiltersGeneral FiltersGeometry FiltersSources\n"
       "  ImagingCore ImagingGeneral)\n"
       "foreach(_vmod ${Slicer_VTK_COMPONENTS} ${_PKGVTK_EXTRA})\n"
       "  if(TARGET VTK::${_vmod})\n"
       "    link_libraries(VTK::${_vmod})\n"
       "  else()\n"
       "    message(WARNING \"PKGVTKFIX: VTK::${_vmod} is NOT a target\")\n"
       "  endif()\n"
       "endforeach()\n"
       "message(STATUS \"PKGVTKFIX: link_libraries over components + Common* done\")\n")
s2 = re.sub(r'(find_package\(VTK [^\n]*COMPONENTS[^\n]*REQUIRED\)\n)',
            lambda m: m.group(1) + inj, s, count=1)
assert s2 != s, "find_package(VTK COMPONENTS) anchor not found"
open(f, "w").write(s2)
print("VTK link_libraries fix injected")
PYEOF

# Slicer source bug #1: 4 Libs/*/CMakeLists.txt use POSIX-regex alternation
# in cmake glob patterns: `file(GLOB headers "...*.(h|hxx)")`. cmake's
# file(GLOB) doesn't support alternation — globs return empty. Rewrite to
# two valid glob patterns separated by a space.
for f in Libs/vtkTeem/CMakeLists.txt \
         Libs/vtkSegmentationCore/CMakeLists.txt \
         Libs/vtkITK/CMakeLists.txt \
         Libs/ITKFactoryRegistration/CMakeLists.txt; do
    sed -i 's|file(GLOB headers "${CMAKE_CURRENT_SOURCE_DIR}/\*\.(h\|hxx)")|file(GLOB headers "${CMAKE_CURRENT_SOURCE_DIR}/*.h" "${CMAKE_CURRENT_SOURCE_DIR}/*.hxx")|' "$f"
done

# Slicer expects an itkNamespace.h header that its SuperBuild normally patches
# into ITK's source tree. Since we don't superbuild, the file is just missing.
# Stub it locally in each Libs/<dir> that includes it.
cat > Libs/ITKFactoryRegistration/itkNamespace.h <<'EOF'
// Stub for Fedora packaging. Slicer SuperBuild normally patches this
// file into ITK's source; we don't superbuild.
#ifndef itkNamespace_h
#define itkNamespace_h
namespace itk {}
#endif
EOF
cp -p Libs/ITKFactoryRegistration/itkNamespace.h Libs/vtkITK/itkNamespace.h

# Slicer source bug #2: 4 Libs/*/CMakeLists.txt reference
# ${CMAKE_CURRENT_BINARY_DIR}/${configure_header_file} in install(FILES ...)
# but never set(configure_header_file ...) so the var is empty and install
# gets a trailing-slash directory path, aborting. Drop the unresolved ref.
for f in Libs/vtkTeem/CMakeLists.txt \
         Libs/MRML/CLI/CMakeLists.txt \
         Libs/RemoteIO/CMakeLists.txt \
         Libs/MRML/Logic/CMakeLists.txt; do
    sed -i 's| ${CMAKE_CURRENT_BINARY_DIR}/${configure_header_file}||' "$f"
done

# Slicer source bug #3: Base/QTCore/Testing/Python/CMakeLists.txt installs its
# generic Python test template from ${CMAKE_CURRENT_BINARY_DIR}, but nothing
# stages it there — it's a verbatim template in the source tree. Install from
# source so %install doesn't abort with BUILD_TESTING=OFF + dev install.
sed -i 's|${CMAKE_CURRENT_BINARY_DIR}/qSlicerModuleGenericTest.py.in|${CMAKE_CURRENT_SOURCE_DIR}/qSlicerModuleGenericTest.py.in|' \
    Base/QTCore/Testing/Python/CMakeLists.txt

# Slicer source bug #4: SlicerCPack.cmake copies the Qt-designer launcher from
# ${CTKAppLauncher_DIR}/bin/ — correct in the superbuild but wrong on Fedora,
# where commontk-applauncher splits the binary (%{_bindir}) from its cmake
# config (%{_libdir}/cmake/CTKAppLauncher). Point at the real binary location.
sed -i 's|${CTKAppLauncher_DIR}/bin/${_launcher}|%{_bindir}/${_launcher}|' \
    CMake/SlicerCPack.cmake

%build
# -I gdcm: Libs/vtkITK includes gdcmDict.h directly but GDCM only comes in
# transitively via ITK's use-file, which doesn't propagate with system GDCM.
# -I QtTesting / -I PythonQt: installed CTK headers (ctkQtTestingUtility.h,
# ctkAbstractPythonManager.h) #include pq*/PythonQt* headers directly, but many
# Slicer targets link CTKWidgets (not CTKQtTesting / a PythonQt-bearing CTK lib)
# and so never inherit those third-party include dirs. Add them globally.
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error -include cstdint -fpermissive -I%{_includedir}/gdcm -I%{_includedir}/QtTesting -I%{_includedir}/PythonQt"
export CFLAGS="%{optflags} -Wno-error -std=gnu17"
export QT_QPA_PLATFORM=offscreen

# Workaround for Fedora teem-devel packaging bug: the shipped TeemConfig.cmake
# computes Teem_USE_FILE one parent dir up (/usr/lib64/lib/TeemUse.cmake) but
# the config lives in /usr/lib64/cmake/, so the file resolves wrong. Build a
# corrected shim in a private dir and point Teem_DIR there.
mkdir -p teem-shim
cat > teem-shim/TeemConfig.cmake <<'EOF'
# Slicer-build shim — corrects path computation that Fedora teem-devel gets
# wrong because TeemConfig.cmake is installed in /usr/lib64/cmake/ instead of
# /usr/lib64/cmake/Teem/.
set(Teem_USE_FILE "%{_libdir}/cmake/TeemUse.cmake")
set(Teem_BUILD_SETTINGS_FILE "%{_libdir}/cmake/TeemBuildSettings.cmake")
set(Teem_EXECUTABLE_DIRS "%{_bindir}")
set(Teem_LIBRARY_DIRS "%{_libdir}")
set(Teem_INCLUDE_DIRS "%{_includedir}")
set(Teem_LIBRARIES "teem")
set(Teem_REQUIRED_C_FLAGS "")
set(Teem_VERSION_MAJOR "1")
set(Teem_VERSION_MINOR "12")
set(Teem_VERSION_PATCH "0")
set(Teem_BUILD_SHARED_LIBS "ON")
set(Teem_TOOLS "")
EOF

%cmake -G Ninja \
    -DSlicer_SUPERBUILD:BOOL=OFF \
    -DSlicer_USE_SYSTEM_ITK:BOOL=ON \
    -DSlicer_USE_SYSTEM_VTK:BOOL=ON \
    -DSlicer_USE_SYSTEM_CTK:BOOL=ON \
    -DSlicer_USE_SYSTEM_DCMTK:BOOL=ON \
    `# Use system OpenJPEG so 5.12+ CPack does not fatal bundling it. See 3dslicer.` \
    -DSlicer_USE_SYSTEM_OpenJPEG:BOOL=ON \
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
    `# CTKConfig find_dependency(QtTesting) resolves the imported qttesting target.` \
    -DQtTesting_DIR:PATH=%{_libdir}/cmake/qttesting \
    -DDCMTK_DIR:PATH=%{_libdir}/cmake/dcmtk \
    -DCTKAppLauncher_DIR:PATH=%{_libdir}/cmake/CTKAppLauncher \
    `# CTKAppLauncherLib is a distinct package to CMake though its config shares` \
    `# the CTKAppLauncher dir; point both _DIR variables.` \
    -DCTKAppLauncherLib_DIR:PATH=%{_libdir}/cmake/CTKAppLauncher \
    -DqRestAPI_DIR:PATH=%{_libdir}/cmake/qRestAPI \
    -DPythonQt_DIR:PATH=%{_libdir}/cmake/PythonQt \
    `# Slicer's top-level CMakeLists references ${vtkAddon_CMAKE_DIR} directly` \
    `# (no find_package(vtkAddon)); set both so the module path + wrap macros resolve.` \
    -DvtkAddon_DIR:PATH=%{_libdir}/cmake/vtkAddon \
    -DvtkAddon_CMAKE_DIR:PATH=%{_libdir}/cmake/vtkAddon \
    `# SlicerExecutionModel ships its config at %{_libdir}/SlicerExecutionModel/` \
    `# (not under cmake/), which Slicer's find_package doesn't auto-discover.` \
    -DSlicerExecutionModel_DIR:PATH=%{_libdir}/SlicerExecutionModel \
    -DGenerateCLP_DIR:PATH=%{_libdir}/GenerateCLP \
    -DModuleDescriptionParser_DIR:PATH=%{_libdir}/ModuleDescriptionParser \
    `# Point at our local TeemConfig.cmake shim — see %%build above for why.` \
    -DTeem_DIR:PATH=$(pwd)/teem-shim \
    `# Qt6 detection: SlicerBlockFindQtAndCheckVersion checks if(DEFINED Qt6_DIR)` \
    `# to pick Qt6 over Qt5; without it, find_package(Qt5) aborts.` \
    -DQt6_DIR:PATH=%{_libdir}/cmake/Qt6 \
    `# Store settings + extensions in the user's home, not the read-only system` \
    `# tree (else the Extensions Manager fails on a system install). See 3dslicer.` \
    -DSlicer_STORE_SETTINGS_IN_APPLICATION_HOME_DIR:BOOL=OFF \
    `# Tarball builds have no .git, so pre-define the revision (else it is empty).` \
    `# With STORE_SETTINGS=OFF the user-home settings/extensions paths are` \
    `# revision-keyed (~/.config/slicer.org/Slicer-<rev>.ini, Extensions-<rev>), so` \
    `# a distinct revision is what keeps this preview isolated from stable 3dslicer` \
    `# in parallel installs — and the Extensions Manager queries the server by it.` \
    -DSlicer_REVISION:STRING=%{shortcommit} \
    -DSlicer_WC_LAST_CHANGED_DATE:STRING=2026-06-28 \
    -DSlicer_WC_URL:STRING=https://github.com/Slicer/Slicer/commit/%{commit} \
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
* Wed Jul 01 2026 Morgan Hough <morgan.hough@gmail.com> - 5.13.0~preview.20260628git9774a684-5
- Full parity port of the stable 3dslicer system-libs build recipe (this preview
  spec had never built — -1..-4 all FTBFS on missing build machinery):
  * BuildRequires qttesting-devel, python-pythonqt-devel, cli11-devel.
  * cmake hints: QtTesting_DIR, PythonQt_DIR, CTKAppLauncherLib_DIR, vtkAddon_DIR
    + vtkAddon_CMAKE_DIR, SlicerExecutionModel_DIR, GenerateCLP_DIR,
    ModuleDescriptionParser_DIR, Teem_DIR (shim), Qt6_DIR.
  * %prep source-bug fixes: SlicerBlockInstallTBB short-circuit, modular-VTK
    link_libraries injection, GLOB-alternation rewrites, itkNamespace.h stubs,
    configure_header_file / qSlicerModuleGenericTest / SlicerCPack install seds.
  * CXXFLAGS -I gdcm/QtTesting/PythonQt; teem-shim for Fedora TeemConfig bug.
  * LTO off + -j1 (submit with --timeout 86400) to avoid the step-~705 swap-stall.
  * Requires python3-dicomweb-client/highdicom/legacy-cgi; python-real exclude.

* Mon Jun 29 2026 Morgan Hough <morgan.hough@gmail.com> - 5.13.0~preview.20260628git9774a684-4
- Slicer_USE_SYSTEM_OpenJPEG=ON to fix the 5.12+ CPack OpenJPEG configure fatal
  (see 3dslicer 5.12.0-3).

* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.13.0~preview.20260628git9774a684-3
- Pre-define Slicer_REVISION (=shortcommit) + WC date/URL. With
  STORE_SETTINGS=OFF the user-home settings/extensions paths are revision-keyed,
  so a distinct revision is what keeps preview isolated from stable 3dslicer in
  parallel installs; an empty revision also breaks the Extensions Manager's
  by-revision server query. 3dslicer already sets this.

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
