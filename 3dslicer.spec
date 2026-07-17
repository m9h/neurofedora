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
# Parallel-install layout under the prefix lib/slicer dir to leave
# room for slicer 6.x someday.

# Slicer 5.12.0 is the current STABLE release (even minor = stable). It has
# full Qt6 support (landed during the 5.11 preview cycle). Built from the
# v5.12.0 tag. The dev/preview track (5.13.0, odd minor) is slicer-preview.
%global slicer_xy   5.12
%global slicer_commit 30a9c0f86a9ac626b98d4671df7d12894983b82b
%global slicer_shortcommit %(c=%{slicer_commit}; echo ${c:0:8})
%global slicer_ver  5.12.1
%global slicer_inst %{_prefix}/lib/slicer

# Nightly CTest dashboard switch. Default OFF so the shipped RPM never carries
# test binaries. Build the dashboard tree with `rpmbuild -bc --with testing ...`
# to compile Slicer's CTest suite against this EXACT Fedora (system-libs) config,
# then run `ctest` in the build tree. Mirrors slicer-preview.spec. See cdash-driver/.
%bcond_with testing

# Slicer ships ~600 MB of shared libs + bundled Python — debuginfo balloons
# to several GB. Disable.
%define debug_package %{nil}

# Bug #8 backstop: even after rewriting shebangs (in %install), guard against
# RPM's automatic script-dependency generator ever emitting an unsatisfiable
# Requires: /usr/bin/python-real (no Fedora package provides that interpreter).
%global __requires_exclude ^/usr/bin/python-real$

# Disable LTO. Fedora's default -flto=auto -ffat-lto-objects roughly doubles
# C++ compile time (fat objects build both a normal .o and LTO bytecode) and
# makes every one of Slicer's ~150 CLI executable links do a slow, memory-heavy
# LTO pass. With -j8 + LTO the build only reached ~705/2843 steps before COPR's
# 5h builder timeout (10528880, 10529439). LTO off ~halves compile time and
# slashes link memory, which also lets us drop the -j8 cap and use all builder
# CPUs (the cap existed only to contain LTO memory pressure).
%global _lto_cflags %{nil}

# Cap build parallelism to bound peak compile/link memory. With all-core -j,
# the ~16 simultaneous Qt/VTK-heavy module compiles that start at ninja step
# ~705 (right after the CLI-link phase) exhaust RAM on low-memory COPR builders
# and the build swap-thrashes to a dead stall there (10587493 timed out at 705
# while thrashing; 10587875 hard-stalled at 705 for ~4h). A high-RAM builder
# completes fine (10586961 reached 2843) -- so it is the builder-RAM lottery.
# Bounds peak memory so ANY builder finishes; the slower wall clock is fine now
# that we submit with a raised --timeout (86400s). -j4 cleared step 705 on a
# higher-RAM builder (build 10588367 reached 2843) but a RAM-poorer builder
# still swap-stalled there ~1.5h with zero output (build 10591218) -- the lottery
# just has a lower threshold than the all-core case. -j2 halves peak memory
# again so even the smallest builders get through the Qt/VTK module-compile
# burst at ~705. If -j2 still stalls, drop to -j1 (or add -fuse-ld=mold).
# 2026-06-13: -j2 ALSO swap-stalled at 705 (build 10599211, ~39min zero output
# on a low-RAM builder) -- the lottery threshold is below -j2 too. Drop to -j1
# for guaranteed completion; serial compile is slow (~8-10h) but --timeout 86400
# absorbs it, and this build (-42) is only the cosmetic launcher rename.
# ONLY for the shipped/COPR build: the --with testing CTest dashboard runs on
# real boxes with RAM to spare, where the driver passes its own -j via --define.
%if %{without testing}
%global _smp_mflags -j1
%endif

Name:           3dslicer
Version:        %{slicer_ver}
Release:        3%{?dist}
Summary:        Open-source platform for medical image analysis and visualization

License:        BSD-3-Clause
URL:            https://slicer.org/
Source0:        https://github.com/Slicer/Slicer/archive/refs/tags/v%{slicer_ver}/Slicer-%{slicer_ver}.tar.gz

# Profile environment hook (sets $Slicer_HOME, prepends bin to PATH)
Source1:        slicer.sh

# Generator that turns the build-tree SlicerConfig.cmake (which Slicer installs
# verbatim, with every path pointing at the vanished build tree and NO imported
# targets) into a relocatable install-tree config + SlicerTargets.cmake, so C++
# extensions can find_package(Slicer) against this install. Upstream only ever
# wired up the build-tree variant; this is the install-tree half it never did.
Source10:       gen-install-config.py

# Python 3.14 (F44/rawhide) removed the private _PyInterpreterState_GetConfigCopy
# / _PyInterpreterState_SetConfig functions that qSlicerCoreApplication used to
# refresh sys.argv after PythonQt init. Replace that round-trip with a direct
# PySys_SetObject("argv", ...) using only stable public C-API. Upstream Slicer's
# superbuild still ships Python 3.9, so it never hit this.
Patch0:         slicer-python314-interpreter-config.patch

# Slicer_USE_QtTesting=ON with a system (non-superbuild) QtTesting: CTKQtTesting
# does not re-export the QtTesting include dir, but Slicer's qMRML*EventPlayer/
# EventTranslator headers include <pqWidgetEventPlayer.h> directly, so AUTOMOC of
# qMRMLWidgets fails to find it. Add find_package(QtTesting) + its include dirs.
Patch1:         slicer-qttesting-include-dirs.patch

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
# Slicer's SuperBuild (External_ITK.cmake) pins the Slicer/ITK fork tag
# slicer-v5.4.6-2026-04-20 and does find_package(ITK 5.1 REQUIRED). Our
# InsightToolkit5 (5.4.6) carries the MGHIO/IOScanco remote modules Slicer
# needs. ITK6 was a wrong turn (no itkNamespace.h gain; HDF5/MGHIO regressions).
# >= 5.4.6-7 carries the Slicer/ITK-fork backport patches (5D NRRD / NrrdImageIO
# AxesReorder API) that vtkITKImageSequenceReader requires to compile.
BuildRequires:  InsightToolkit5-devel >= 5.4.6-7
BuildRequires:  InsightToolkit5-vtk-devel
BuildRequires:  vtk-devel >= 9.6
# 0.12 enables CTK transfer-function charts (ctkVTKChartView) that
# Slicer's qMRMLPlotView links against, and wraps QtTesting as CTKQtTesting.
# 0.13 enables CTK_LIB_Scripting/Python/Core_PYTHONQT_USE_VTK so
# ctkVTKPythonQtWrapperFactory is compiled (qSlicerCorePythonManager links it).
# 0.14 adds find_dependency(QtTesting) to CTKConfig so the qttesting imported
# target resolves in consumers (otherwise it degrades to a bare -lqttesting).
BuildRequires:  ctk-devel >= 2026.01.26-0.14
# Slicer_USE_QtTesting=ON: CTKQtTesting links libqttesting transitively.
BuildRequires:  qttesting-devel
BuildRequires:  vtkAddon-devel
BuildRequires:  qRestAPI-devel
BuildRequires:  python-pythonqt-devel
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
BuildRequires:  cli11-devel

# Python ecosystem (Slicer bundles its own Python, but cmake checks for these)
BuildRequires:  python3-pip
BuildRequires:  python3-numpy

# Runtime requirements
Requires:       qt6-qtbase
Requires:       qt6-qtwebengine
Requires:       qt6-qtmultimedia
Requires:       hicolor-icon-theme
Requires:       libGL
# Python deps for the scripted modules. The headless slicer.bats suite caught
# the DICOM module failing to load (No module named dicomweb_client / highdicom)
# and several modules hitting the Python 3.13 removal of cgi.
Requires:       python3-dicomweb-client
Requires:       python3-highdicom
Requires:       python3-legacy-cgi
# Slicer is built with -DSlicer_USE_SCIPY=ON; without this the shipped RPM has
# SciPy support enabled but no SciPy installed and scipy-importing modules break.
Requires:       python3-scipy
# Slicer's bin/Python/vtkAddon.py does "from vtkAddonPython import *"; the
# wrapper ships in python3-vtkAddon (vtkAddonPython.so), NOT vtkAddon-devel.
# Without this, every scripted module that touches vtkAddon fails at runtime
# with "No module named 'vtkAddonPython'" (caught by the CTest dashboard).
Requires:       python3-vtkAddon

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
# Loading the install-tree SlicerConfig.cmake runs find_package() for the system
# externals Slicer was built against; an extension building against -devel needs
# their cmake configs present. teem-devel in particular: SlicerConfig does
# find_package(Teem) and Fedora ships TeemConfig.cmake only in teem-devel.
Requires:       teem-devel
Requires:       vtk-devel
Requires:       InsightToolkit5-devel
Requires:       SlicerExecutionModel-devel
Requires:       ctk-devel
Requires:       qttesting-devel
Requires:       qRestAPI-devel
Requires:       commontk-applauncher-devel
Requires:       vtkAddon-devel

%description devel
Headers, cmake configuration, and devel symlinks for building Slicer
extension modules out of tree.

%prep
%autosetup -p1 -n Slicer-%{slicer_ver}

# Slicer main HEAD already supports Qt6 and VTK 9.6 natively — no sed
# patches needed for those. Python version: defaults to 3.12.10 floor;
# Fedora 44 ships 3.14 which satisfies >= 3.12.10 fine.

# Short-circuit SlicerBlockInstallTBB. This file expects to bundle
# specific TBB SONAME versions (libtbbmalloc.so.2.5) that don't exist
# on Fedora — Fedora's tbb-2022.3 ships libtbbmalloc.so.2.17. As an
# RPM we rely on the system tbb package; no need to bundle.
echo 'return()' > CMake/SlicerBlockInstallTBB.cmake

# VTK linkage: several Slicer libs (vtkSegmentationCore, ...) link the legacy
# ${VTK_LIBRARIES} and use vtkImageAccumulate / vtkExtractSelection /
# vtkPolyDataToImageStencil, but Fedora's modular VTK leaves ImagingStatistics /
# FiltersExtraction / ImagingStencil out of VTK_LIBRARIES even though Slicer
# requests them as COMPONENTS — so the link fails with undefined references.
# Force the VTK:: targets onto VTK_LIBRARIES right after find_package(VTK).
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

# Slicer expects an itkNamespace.h header that its SuperBuild normally
# patches into ITK's source tree. Since we don't superbuild, the file
# is just missing. Stub it locally in each Libs/<dir> that includes it,
# so the #include resolves. The actual contents only need to be a
# placeholder — the surrounding code uses `namespace itk { ... }` blocks
# directly without needing anything from this header.
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
# but never `set(configure_header_file ...)` so the var is empty and install
# gets a trailing-slash directory path, aborting with "install FILES given
# directory ... to install." Drop the unresolved reference.
for f in Libs/vtkTeem/CMakeLists.txt \
         Libs/MRML/CLI/CMakeLists.txt \
         Libs/RemoteIO/CMakeLists.txt \
         Libs/MRML/Logic/CMakeLists.txt; do
    sed -i 's| ${CMAKE_CURRENT_BINARY_DIR}/${configure_header_file}||' "$f"
done

# Slicer source bug #3: Base/QTCore/Testing/Python/CMakeLists.txt installs its
# generic Python test template (qSlicerModuleGenericTest.py.in) from
# ${CMAKE_CURRENT_BINARY_DIR}, but nothing ever stages it there — the file is a
# verbatim template living in the source tree (that CMakeLists registers the
# templates dir as CMAKE_CURRENT_SOURCE_DIR, and its BUILD_TESTING block that
# might otherwise have copied it is empty). With BUILD_TESTING=OFF and the
# development install enabled, %install aborts: "file INSTALL cannot find
# .../qSlicerModuleGenericTest.py.in". Install it from the source tree.
# (grep-verified as the sole occurrence of this install-from-binary .in bug.)
sed -i 's|${CMAKE_CURRENT_BINARY_DIR}/qSlicerModuleGenericTest.py.in|${CMAKE_CURRENT_SOURCE_DIR}/qSlicerModuleGenericTest.py.in|' \
    Base/QTCore/Testing/Python/CMakeLists.txt

# Python 3.13 REMOVED the 'pipes' module (F44 ships 3.14), but Slicer's own test
# helper Applications/SlicerApp/Testing/Python/SlicerAppTesting.py still does
# "import pipes" / pipes.quote(). That kills ~5 py_ tests at import. pipes.quote
# moved to shlex.quote -- the documented migration. (Same class as the cgi removal.)
sed -i -e 's/^import pipes$/import shlex/' -e 's/pipes\.quote/shlex.quote/g' \
    Applications/SlicerApp/Testing/Python/SlicerAppTesting.py


# Slicer source bug (only bites BUILD_TESTING=ON, i.e. the CTest dashboard):
# SlicerMacroConfigureModuleCxxTestDriver unconditionally #includes
# vtkWin32OutputWindow.h in every generated module CxxTest driver, while the code
# that USES it is correctly #ifdef _WIN32-guarded. With system VTK 9.6 that
# Windows-only header is absent on Linux, so all ~10 module test drivers FTBFS
# (fatal error: vtkWin32OutputWindow.h: No such file). Drop the unconditional
# include (swap for the harmless vtkVersionMacros.h already pulled in); the
# _WIN32-guarded usage is not compiled on Linux. Harmless when testing is OFF.
sed -i 's|set(EXTRA_INCLUDE "vtkWin32OutputWindow.h|set(EXTRA_INCLUDE "vtkVersionMacros.h|' \
    CMake/SlicerMacroConfigureModuleCxxTestDriver.cmake

# N4ITKBiasFieldCorrection.cxx is an ITK-template memory bomb: compiling it at -O2
# peaks ~22 GB, which OOMs memory-constrained builders and the CTest farm nodes
# (a single translation unit, so lowering -j does not help). Compile just this one
# CLI source at -O1 -- much lower peak, and N4 is not perf-critical. Same class of
# reduction Fedora/Debian apply to heavy ITK TUs.
cat >> Modules/CLI/N4ITKBiasFieldCorrection/CMakeLists.txt <<'N4EOF'
set_source_files_properties(
  ${CMAKE_CURRENT_SOURCE_DIR}/N4ITKBiasFieldCorrection.cxx
  PROPERTIES COMPILE_OPTIONS "-O1")
N4EOF

# Slicer source bug #4: SlicerCPack.cmake installs the Qt-designer launcher by
# copying the CTKAppLauncher binary from ${CTKAppLauncher_DIR}/bin/ — correct in
# the superbuild, where the launcher build tree and its CMake config share a
# prefix. Fedora's commontk-applauncher splits them: the binary is in %{_bindir}
# (/usr/bin/CTKAppLauncher) while the CMake config (= CTKAppLauncher_DIR) is in
# %{_libdir}/cmake/CTKAppLauncher. So %install aborts: "file INSTALL cannot find
# /usr/lib64/cmake/CTKAppLauncher/bin/CTKAppLauncher". Point this install rule at
# the real binary location. NOTE: the only other launcher install (the Python
# launcher in SlicerBlockInstallPython.cmake) is gated on NOT Slicer_USE_SYSTEM_
# python and is therefore not included in this build; likewise the DCMTK/QtTesting/
# PythonQt/TBB/OpenSSL/LibArchive install blocks are all NOT Slicer_USE_SYSTEM_*
# guarded and skipped here -- this is the sole firing build-tree-path rule.
sed -i 's|${CTKAppLauncher_DIR}/bin/${_launcher}|%{_bindir}/${_launcher}|' \
    CMake/SlicerCPack.cmake

%build
# Libs/vtkITK includes gdcmDict.h directly but only pulls GDCM transitively via
# find_package(ITK ... ITKIOGDCM) + include(${ITK_USE_FILE}); with our system
# GDCM (ITK built ITK_USE_SYSTEM_GDCM=ON) that use-file does not propagate the
# /usr/include/gdcm path to the vtkITK target, so add it to the global include
# search path. gdcm-devel is already BuildRequired.
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error -include cstdint -fpermissive -I%{_includedir}/gdcm"
export CFLAGS="%{optflags} -Wno-error -std=gnu17"
# Required for the bundled qt-keyword build harness
export QT_QPA_PLATFORM=offscreen

# Workaround for Fedora teem-devel packaging bug: the shipped
# TeemConfig.cmake computes Teem_USE_FILE = /usr/lib64/lib/TeemUse.cmake
# (one parent dir up from the config file, then down into lib/) — but the
# config actually lives in /usr/lib64/cmake/, so the file resolves wrong.
# Build our own corrected shim in a private dir and point Teem_DIR there.
mkdir -p teem-shim
cat > teem-shim/TeemConfig.cmake <<'EOF'
# Slicer-build shim — corrects path computation that Fedora teem-devel
# (bz# pending) gets wrong because TeemConfig.cmake is installed in
# /usr/lib64/cmake/ instead of /usr/lib64/cmake/Teem/.
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
    `# THE flag — drop superbuild` \
    -DSlicer_SUPERBUILD:BOOL=OFF \
    \
    `# System packages for every external` \
    -DSlicer_USE_SYSTEM_ITK:BOOL=ON \
    -DSlicer_USE_SYSTEM_VTK:BOOL=ON \
    -DSlicer_USE_SYSTEM_CTK:BOOL=ON \
    -DSlicer_USE_SYSTEM_DCMTK:BOOL=ON \
    `# 5.12 added SlicerBlockInstallOpenJPEG: with DICOM support ON but` \
    `# Slicer_USE_SYSTEM_OpenJPEG unset, CPack tries to bundle OpenJPEG and fatals` \
    `# on the unset OpenJPEG_INSTALL_DIR at configure. We use system openjpeg (via` \
    `# gdcm/dcmtk), so flip it ON to skip the bundling block.` \
    -DSlicer_USE_SYSTEM_OpenJPEG:BOOL=ON \
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
    -DITK_DIR:PATH=%{_libdir}/cmake/ITK-5.4 \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    -DCTK_DIR:PATH=%{_libdir}/cmake/CTK \
    `# CTKConfig find_dependency(QtTesting) resolves the imported qttesting target` \
    `# that CTKQtTesting links against.` \
    -DQtTesting_DIR:PATH=%{_libdir}/cmake/qttesting \
    -DDCMTK_DIR:PATH=%{_libdir}/cmake/dcmtk \
    -DCTKAppLauncher_DIR:PATH=%{_libdir}/cmake/CTKAppLauncher \
    `# CTKAppLauncherLib and CTKAppLauncher both have their configs in` \
    `# the same dir; CMake treats them as distinct packages so both _DIR` \
    `# variables need pointing.` \
    -DCTKAppLauncherLib_DIR:PATH=%{_libdir}/cmake/CTKAppLauncher \
    `# Tarball builds have no .git/.svn — SlicerMacroExtractRepositoryInfo` \
    `# leaves the Slicer_REVISION / Slicer_WC_LAST_CHANGED_DATE /` \
    `# Slicer_WC_URL variables unset, which SlicerPackageAndUploadTarget` \
    `# then rejects. Pre-define them from spec globals.` \
    -DSlicer_REVISION:STRING=%{slicer_shortcommit} \
    -DSlicer_WC_LAST_CHANGED_DATE:STRING=2026-05-17 \
    `# The version header is emitted by a build-time 'cmake -P' script`\
    `# (SlicerConfigureVersionHeaderTarget), which only receives the Slicer_FORCED_*`\
    `# args. Plain Slicer_REVISION / Slicer_WC_LAST_CHANGED_DATE never reach it, so`\
    `# Slicer_BUILDDATE compiled to "" and vtkSlicerVersionConfigureTest1 failed.`\
    -DSlicer_FORCED_REVISION:STRING=%{slicer_shortcommit} \
    -DSlicer_FORCED_WC_LAST_CHANGED_DATE:STRING=2026-05-17 \
    -DSlicer_WC_URL:STRING=https://github.com/Slicer/Slicer/commit/%{slicer_commit} \
    -DqRestAPI_DIR:PATH=%{_libdir}/cmake/qRestAPI \
    -DPythonQt_DIR:PATH=%{_libdir}/cmake/PythonQt \
    `# Slicer's top-level CMakeLists references ${vtkAddon_CMAKE_DIR}` \
    `# directly (no find_package(vtkAddon) call); the superbuild normally` \
    `# sets it. Set both DIR variables so the variable is populated for the` \
    `# CMAKE_MODULE_PATH insertion and downstream include(vtkMacroKitPythonWrap)` \
    `# can resolve.` \
    -DvtkAddon_DIR:PATH=%{_libdir}/cmake/vtkAddon \
    -DvtkAddon_CMAKE_DIR:PATH=%{_libdir}/cmake/vtkAddon \
    `# SlicerExecutionModel ships its config at /usr/lib64/SlicerExecutionModel/` \
    `# (not under cmake/), which Slicer's find_package(SlicerExecutionModel)` \
    `# in Libs/MRML/CLI doesn't auto-discover.` \
    -DSlicerExecutionModel_DIR:PATH=%{_libdir}/SlicerExecutionModel \
    -DGenerateCLP_DIR:PATH=%{_libdir}/GenerateCLP \
    -DModuleDescriptionParser_DIR:PATH=%{_libdir}/ModuleDescriptionParser \
    `# Point at our local TeemConfig.cmake shim — see %build above for why.` \
    -DTeem_DIR:PATH=$(pwd)/teem-shim \
    `# Qt6 detection: SlicerBlockFindQtAndCheckVersion.cmake checks` \
    `# if(DEFINED Qt6_DIR) to pick Qt6 over Qt5. Without this hint it` \
    `# tries find_package(Qt5) and aborts with "Qt5 was not found".` \
    -DQt6_DIR:PATH=%{_libdir}/cmake/Qt6 \
    \
    `# Store user settings + downloaded extensions in the user's home, NOT the` \
    `# application home dir. Upstream defaults this ON ("portable" install), which` \
    `# points settings at <app>/slicer.org/Slicer-<rev>.ini and the extensions` \
    `# install dir into the read-only system tree (/usr/lib/slicer/...), so the` \
    `# Extensions Manager fails with "Extensions can not be installed" on a system` \
    `# RPM install. OFF routes them to ~/.config/slicer.org + a user-writable dir.` \
    -DSlicer_STORE_SETTINGS_IN_APPLICATION_HOME_DIR:BOOL=OFF \
    `# Feature toggles` \
    -DSlicer_USE_PYTHONQT:BOOL=ON \
    -DSlicer_USE_NUMPY:BOOL=ON \
    -DSlicer_USE_SCIPY:BOOL=ON \
    -DSlicer_USE_SimpleITK:BOOL=ON \
    -DSlicer_USE_CTKAPPLAUNCHER:BOOL=ON \
    -DSlicer_USE_TBB:BOOL=ON \
    `# QtTesting (Kitware GUI record/replay): qttesting is now packaged on Fedora` \
    `# and CTK (>= 0.12) wraps it as CTKQtTesting, which Slicer's qMRML*EventPlayer/` \
    `# EventTranslator sources link transitively via CTK_DIR. BUILD_TESTING stays` \
    `# OFF in this rebuild so the test executables are not compiled yet (-31 flips it).` \
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
    -DBUILD_TESTING:BOOL=%{?with_testing:ON}%{!?with_testing:OFF} \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DSlicer_USE_VTK_DEBUG_LEAKS:BOOL=OFF

%cmake_build

%install
%cmake_install

# ---------------------------------------------------------------------------
# (-43) Make 3dslicer-devel usable for building C++ extensions against the
# INSTALL tree. Upstream Slicer only supports building extensions against a
# build tree: SlicerGenerateSlicerConfig.cmake configures SlicerConfig.cmake
# ONLY for ${Slicer_BINARY_DIR} (and Slicer installs that build-tree file
# verbatim), and there is no install(EXPORT SlicerTargets). So the installed
# config points every path at the vanished build tree and ships no imported
# targets. We repair all three gaps here.
_sdir=%{_builddir}/Slicer-%{slicer_ver}
_bdir="$_sdir/%{_vpath_builddir}"
_scmake=%{buildroot}%{slicer_inst}/lib/Slicer-%{slicer_xy}/CMake

# 1. Ship the FULL source CMake/ + Extensions/CMake/ — the installed subset is
#    missing extension-support modules (SlicerBlockAdditionalLauncherSettings,
#    SlicerBlockUploadExtensionPrerequisites, SlicerExtensionDescriptionSpec,
#    ...), plus the qSlicerExport.h.in export-header template and the CPack
#    bundle-fixup template that UseSlicer.cmake / the module-build macros need.
cp -an "$_sdir"/CMake/. "$_scmake"/ || :
# Merge Extensions/CMake into the same dir so every extension-support module is
# reachable via Slicer_CMAKE_DIR (== Slicer_EXTENSIONS_CMAKE_DIR) on the module
# path — UseSlicer.cmake include()s several of them by bare name.
cp -an "$_sdir"/Extensions/CMake/. "$_scmake"/ || :

# 2. Ship the VTK wrap-hierarchy files (.txt) generated in the build tree —
#    needed to python-wrap an extension's VTK classes against Slicer's libs.
mkdir -p %{buildroot}%{slicer_inst}/lib/Slicer-%{slicer_xy}/hierarchy
# The files are named <Target>Hierarchy.txt (MRMLCoreHierarchy.txt,
# vtkTeemHierarchy.txt, ...) in the build root — NOT *-hierarchy.txt.
find "$_bdir" -name '*Hierarchy.txt' 2>/dev/null \
  | while read -r h; do cp -an "$h" \
      %{buildroot}%{slicer_inst}/lib/Slicer-%{slicer_xy}/hierarchy/ 2>/dev/null || :; done

# 2b. Ship the generated *Export.h headers (CMake GenerateExportHeader output,
#     e.g. vtkMRMLExport.h) that Slicer's install rules omit — public library
#     headers #include them, so a C++ extension can't compile without them.
#     Self-discovering: for each installed library include dir, find which
#     *Export.h its headers reference and copy that file next to them.
for _d in %{buildroot}%{slicer_inst}/include/* \
          %{buildroot}%{slicer_inst}/include/Slicer-%{slicer_xy}/*; do
    [ -d "$_d" ] || continue
    grep -rhoE '#include "[A-Za-z0-9_]+Export\.h"' "$_d" 2>/dev/null \
      | sed -E 's/.*"([^"]+)".*/\1/' | sort -u | while read -r _eh; do
        [ -e "$_d/$_eh" ] && continue
        _src=$(find "$_bdir" "$_sdir" -name "$_eh" 2>/dev/null | head -1)
        [ -n "$_src" ] && install -m0644 "$_src" "$_d/$_eh" || :
    done
done

# 2c. Ship the Base/Logic + ALL loadable-module public C++ headers (and their
#     generated export/configure headers). Slicer installs almost none of these,
#     but C++ extensions #include them widely (vtkSlicerBaseLogic.h,
#     vtkSlicerColorLogic.h, vtkMRMLMarkupsNode.h, ...). Flatten into
#     include/Slicer-%{slicer_xy}, which is on every extension's include path. Source
#     headers first, then build-tree generated headers (*Export.h, *Configure.h).
_si=%{buildroot}%{slicer_inst}/include/Slicer-%{slicer_xy}
for _base in "$_sdir" "$_bdir"; do
    for _hd in "$_base"/Base/Logic "$_base"/Base/CLI "$_base"/Base/QTCLI \
               "$_base"/Modules/Loadable/*/Logic \
               "$_base"/Modules/Loadable/*/MRML \
               "$_base"/Modules/Loadable/*/MRMLDM \
               "$_base"/Modules/Loadable/*/Widgets \
               "$_base"/Modules/Loadable/*/VTKWidgets; do
        [ -d "$_hd" ] || continue
        find "$_hd" -maxdepth 1 -name '*.h' \
          -exec cp -an {} "$_si/" \; 2>/dev/null || :
    done
done

# 2c-bis. Ship Slicer's Libs/ public headers PRESERVING the Libs/<lib>/ path, so
#   extensions that include them source-root-relative (e.g. SlicerDMRI's
#   `#include <Libs/vtkTeem/vtkTeemNRRDReader.h>` in its diffusion CLIs) resolve
#   against include/Slicer-%{slicer_xy} (already on every extension's include path). Both
#   the source tree (public *.h) and the build tree (generated *Export.h /
#   *Configure.h the headers reference) are copied with their Libs/<lib>/ prefix.
( cd "$_sdir" && find Libs -name '*.h' -exec cp -an --parents {} "$_si/" \; ) 2>/dev/null || :
( cd "$_bdir" && find Libs -name '*.h' -exec cp -an --parents {} "$_si/" \; ) 2>/dev/null || :

# 2d. Ship the generated SEM CLI library wrapper (Base/CLI/
#     SEMCommandLineLibraryWrapper.cxx) so CLI-module extensions (SlicerDMRI,
#     SlicerRT, ...) can build via SEMMacroBuildCLI (the install-tree config
#     points SlicerExecutionModel_CLI_LIBRARY_WRAPPER_CXX here).
_semw=$(find "$_bdir" "$_sdir" -name 'SEMCommandLineLibraryWrapper.cxx' 2>/dev/null | head -1)
[ -n "$_semw" ] && install -m0644 "$_semw" "$_scmake/" || :

# 3. Synthesize the relocatable install-tree SlicerConfig.cmake (overwrites the
#    broken build-tree one) + a SlicerTargets.cmake with IMPORTED targets for
#    the installed libs. No --root => the config derives its prefix from its own
#    location at load time (fully relocatable).
python3 %{SOURCE10} \
    %{buildroot}%{slicer_inst}/lib/Slicer-%{slicer_xy}/SlicerConfig.cmake \
    %{buildroot}%{slicer_inst}/lib/Slicer-%{slicer_xy}

# 4. CLI module discovery: Slicer's CLI executables land in bin/ but the
#    launcher scans lib/Slicer-%{slicer_xy}/cli-modules (which ends up empty), so CLI
#    modules are unfindable. Symlink the cli-modules dir's expected contents
#    from the installed CLI binaries + their .xml descriptors.
_clidir=%{buildroot}%{slicer_inst}/lib/Slicer-%{slicer_xy}/cli-modules
mkdir -p "$_clidir"
for x in %{buildroot}%{slicer_inst}/bin/*.xml; do
    [ -e "$x" ] || continue
    b=$(basename "$x" .xml)
    if [ -e "%{buildroot}%{slicer_inst}/bin/$b" ]; then
        ln -sf ../../../bin/"$b"     "$_clidir/$b"
        ln -sf ../../../bin/"$b.xml" "$_clidir/$b.xml"
    fi
done
# ---------------------------------------------------------------------------

# Slicer source bug #5/#8: several installed wizard/utility scripts (e.g.
# libexec/Slicer-%{slicer_xy}/ExtensionWizard.py, ModuleWizard.py, and the ScriptedCLI
# Wizard template TemplateKey.py) carry non-system python shebangs:
#  - "#!/usr/bin/env python"  -> brp-mangle-shebangs rejects (ambiguous), fails %install (bug #5)
#  - "#!/usr/bin/python-real" -> RPM's script-dep generator turns it into an
#    unsatisfiable Requires: /usr/bin/python-real, making the package
#    UNINSTALLABLE even though the build succeeds (bug #8).
# Slicer runs these through its own launcher/Python, so the shebang is cosmetic.
# Normalize EVERY non-system python shebang (bare python, pythonX.Y, python-real)
# on line 1 to /usr/bin/python3. Prefilter with grep -I so we only sed real text
# files that actually start with "#!" (never binaries in the tree).
find %{buildroot}%{slicer_inst} -type f -print0 | while IFS= read -r -d '' f; do
    # Read only line 1; only invoke sed on files whose shebang names python
    # (keeps binaries/data files untouched -- never sed a .so).
    IFS= read -r line0 < "$f" 2>/dev/null || continue
    case "$line0" in
        '#!'*python*) sed -i -E '1s|^#!.*/(env[[:space:]]+)?python[0-9.]*(-real)?$|#!/usr/bin/python3|' "$f" ;;
    esac
done

# Profile.d hook
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/profile.d/slicer.sh

# Launcher symlinks. Use the upstream-canonical capitalized "Slicer" plus a
# lowercase "3dslicer" alias (matches the package name). Deliberately do NOT
# ship a lowercase "slicer": FSL installs its own ~/fsl/.../bin/slicer (a
# volume slice viewer), which shadows /usr/bin/slicer on PATH and caused
# "which slicer" to resolve to FSL instead of 3D Slicer (bug: launcher
# collision). "Slicer" and "3dslicer" are unambiguous.
install -d %{buildroot}%{_bindir}
ln -sf %{slicer_inst}/Slicer %{buildroot}%{_bindir}/Slicer
ln -sf %{slicer_inst}/Slicer %{buildroot}%{_bindir}/3dslicer
# Drop the leftover Source0 reference to v%{version} since 5.10.0 tag is unused now
# (Source0 fetches from main HEAD by commit SHA).

%files
%license License.txt
%doc README.md
%{_bindir}/Slicer
%{_bindir}/3dslicer
%{_sysconfdir}/profile.d/slicer.sh
%{slicer_inst}/
%exclude %{slicer_inst}/include/
# Slicer's CMake config installs under lib/Slicer-%%{slicer_xy}/CMake/ (not lib/cmake/);
# route it to -devel. (bug #7: the old lib/cmake/ path matched nothing.)
%exclude %{slicer_inst}/lib/Slicer-%{slicer_xy}/CMake/
# bug #6: Slicer installs Qt6 designer/iconengine/style plugins into the system
# Qt6 plugin tree (outside the slicer_inst prefix); package them explicitly.
%{_libdir}/qt6/plugins/designer/libqMRMLWidgetsPlugins.so
%{_libdir}/qt6/plugins/designer/libqSlicer*Plugins.so
%{_libdir}/qt6/plugins/iconengines/libqSlicerIconEnginePlugin.so
%{_libdir}/qt6/plugins/styles/libqSlicerBaseQTGUIStylePlugins.so

%files devel
%{slicer_inst}/include/
%{slicer_inst}/lib/Slicer-%{slicer_xy}/CMake/

%changelog
* Wed Jul 16 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.1-3
- Compile N4ITKBiasFieldCorrection.cxx at -O1: at -O2 this single ITK-template-heavy
  CLI source peaks ~22 GB and OOMs memory-constrained builders / CTest farm nodes
  (lowering -j does not help -- it is one TU). N4 is not perf-critical.

* Sun Jul 12 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.1-2
- Add Requires: python3-scipy. The spec builds with -DSlicer_USE_SCIPY:BOOL=ON but
  never required SciPy, so the shipped RPM has SciPy support enabled with no SciPy
  installed -- every scipy-importing scripted module fails at runtime. This is a
  real user-facing defect (same class as the missing python3-vtkAddon Requires);
  it accounted for ~17 of the 32 CTest failures, including the whole CLI cluster.
- %%prep: Python 3.13 removed the 'pipes' module (F44 has 3.14) but Slicer's test
  helper SlicerAppTesting.py still imports it; migrate pipes.quote -> shlex.quote.

* Fri Jul 10 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.1-1
- Update to upstream 3D Slicer v5.12.1 (was v5.12.0). Carries forward all
  packaging fixes: python3-vtkAddon Requires, %bcond_with testing + guarded
  -j1, and the %prep vtkWin32OutputWindow.h test-driver fix. %prep verified
  clean against the 5.12.1 tree.

* Fri Jul 10 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.0-5
- Add python3-vtkAddon runtime Requires: Slicer's bin/Python/vtkAddon.py does
  "from vtkAddonPython import *" (ships in python3-vtkAddon, not vtkAddon-devel);
  without it scripted modules fail with "No module named 'vtkAddonPython'".
  Caught by the CTest farm.
- Add `%%bcond_with testing` + guard `_smp_mflags -j1` behind `%%{without testing}`
  so the CDash farm builds this exact Fedora config with BUILD_TESTING=ON at full
  -j; shipped RPM unchanged (tests off, -j1).
- %%prep: drop the unconditional Windows-only vtkWin32OutputWindow.h include the
  test-driver macro injects (breaks module CxxTest drivers on Linux with system
  VTK 9.6 when BUILD_TESTING=ON).

* Tue Jul 07 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.0-4
- Rebuild against ctk 0.18 (CTK_ENABLE_Python_Wrapping=ON) to pick up the
  non-empty `import ctk` fix. The -3 build was linked against ctk 0.16 whose
  scripting libs produced no importable CTK<kit>PythonQt modules. No spec
  changes beyond the Release bump; NVR bump so the rebuild wins the repo.

* Mon Jun 29 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.0-3
- Fix cmake configure FATAL on 5.12: set Slicer_USE_SYSTEM_OpenJPEG=ON. 5.12
  added SlicerBlockInstallOpenJPEG (CPack) which, with DICOM support on and the
  flag unset, fatals on the unset OpenJPEG_INSTALL_DIR. We use system openjpeg.

* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.0-2
- Fix "Extensions can not be installed" on system installs: set
  Slicer_STORE_SETTINGS_IN_APPLICATION_HOME_DIR=OFF. Upstream defaults it ON
  (portable mode), which points the settings file and the extensions install dir
  into the read-only /usr/lib/slicer tree. OFF stores them under the user's home
  (~/.config/slicer.org), so the Extensions Manager works without root.

* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.12.0-1
- Promote stable 3dslicer from the 5.11.0~pre main snapshot to the 5.12.0
  RELEASE (tag v5.12.0). Parametrize the install paths as %%{slicer_xy}=5.12.
  Carries the DICOM Python deps (python3-{dicomweb-client,highdicom,legacy-cgi})
  and all the -36..-55 packaging fixes forward. The dev/preview track moves to
  5.13.0 separately (slicer-preview, parallel-installable).

* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-55
- Require python3-dicomweb-client, python3-highdicom and python3-legacy-cgi.
  The headless slicer.bats suite caught the DICOM scripted module failing to
  load (No module named dicomweb_client / highdicom — neither was in Fedora) and
  modules importing the stdlib cgi module removed in Python 3.13. All three are
  now packaged in the COPR; wire them in so a fresh install resolves them.

* Sun Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-54
- Add the ITK link closure to the generated imported targets (the ITK analog of
  the -52 VTK closure / -53 inter-Slicer+CTK closure). The Slicer C++ libs
  (vtkITK, MRMLCore, MRMLLogic, SlicerBaseLogic, vtkTeem, vtkSegmentationCore,
  ITKFactoryRegistration) are built on ITK and propagated it through their
  interface in-tree; without it a CLI/loadable module that links a Slicer lib and
  uses ITK itself (e.g. SlicerDMRI FiberBundleLabelSelect / TractographyLabelMapSeeding
  reading images) failed with undefined itk::Object::GetDebug /
  itk::InvalidRequestedRegionError — SEM's ${ITK_LIBRARIES} resolves empty against
  the install tree, so ITK was absent from the link line entirely. gen-install-config
  now globs the Fedora ITK .so set (/usr/lib64/libITK*.so + libitk*.so) onto every
  imported target's INTERFACE_LINK_LIBRARIES; --as-needed prunes the unused ones
  from the consumer's DT_NEEDED.

* Sun Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-53
- Complete the install-tree imported-target link interface for loadable-module
  GUI extensions (the -52 follow-up). The generated SlicerTargets.cmake now wires
  the inter-Slicer link closure onto every imported target: Qt-based libs
  (qSlicerBaseQTGUI, qMRMLWidgets, ...) carry the full Slicer library set + Qt +
  the system CTK .so closure (globbed from /usr/lib64/libCTK*.so), while non-Qt
  libs carry only the other non-Qt Slicer libs + VTK (so a pure-CLI extension is
  not forced to drag in Qt/CTK). Upstream's missing install(EXPORT) left these
  interface dependencies unset, so module Widgets libraries failed to link with
  undefined qSlicerAbstractModuleWidget::~ / qMRMLTreeView::* / ctkCollapsibleButton
  references even though the libraries were present. Fixes SlicerDMRI and the
  other C++ loadable-module extensions (SRep, ShapePopulationViewer).

* Sat Jun 20 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-52
- Complete the install-tree config for loadable-module extensions. The generated
  imported targets now (a) link the VTK:: module closure so a consumer linking a
  Slicer lib (e.g. MRMLCore) inherits VTK includes AND libraries — upstream's
  missing install(EXPORT) left these out, so extensions failed with undefined
  vtkObject::* / missing <vtkObject.h>; and (b) carry the Slicer base include
  subdirs (qSlicerBaseQTGUI, ...) so headers like qSlicerAbstractModuleWidget.h
  resolve. Same on the loadable-module imported targets. Also make 3dslicer-devel
  Require the system -devel packages whose cmake configs SlicerConfig
  find_package()s (teem-devel, vtk-devel, ITK, SEM, ctk, qttesting, qRestAPI,
  commontk-applauncher, vtkAddon) so extensions resolve them out of the box.
  Unblocks the C++ GUI/loadable extensions (SRep, ShapePopulationViewer, ...).
* Fri Jun 19 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-51
- Ship Slicer's Libs/ public headers preserving the Libs/<lib>/ path under
  include/Slicer-5.11, so extensions that include them source-root-relative
  resolve. Unblocks SlicerDMRI, whose diffusion CLIs do
  `#include <Libs/vtkTeem/vtkTeemNRRDReader.h>` (and ...Writer.h); the prior
  header shipping only flattened Base/Logic + loadable-module headers, leaving
  every `<Libs/...>` include unresolved. Copies source *.h plus the build-tree
  generated *Export.h / *Configure.h they reference.
* Thu Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-50
- Make the modular-VTK link fix comprehensive: instead of forcing three named
  modules onto VTK_LIBRARIES, link_libraries() the full set Slicer already
  requested (Slicer_VTK_COMPONENTS) plus the foundational Common* family onto
  every target after find_package(VTK). The -49 three-module list only moved the
  failure from vtkImageAccumulate/vtkExtractSelection/vtkPolyDataToImageStencil
  to vtkTimerLog (VTK::CommonSystem, not in Slicer_VTK_COMPONENTS); the full set
  resolves the whole closure once. vtkSegmentationCore now links clean.
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-49
- Fix a VTK link regression: force VTK::ImagingStatistics / FiltersExtraction /
  ImagingStencil onto the legacy VTK_LIBRARIES (Fedora's modular VTK omits them
  there despite Slicer requesting them as COMPONENTS), else vtkSegmentationCore
  fails to link (undefined vtkImageAccumulate/vtkExtractSelection/
  vtkPolyDataToImageStencil). Carries the -48 CLI-module support.
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-48
- Support CLI-module extensions (SlicerDMRI, SlicerRT, ...): ship the generated
  SEMCommandLineLibraryWrapper.cxx + Base/CLI headers, and the install-tree
  config now maps SlicerExecutionModel_CLI_LIBRARY_WRAPPER_CXX and
  _EXTRA_INCLUDE_DIRECTORIES to the installed paths (were neutralized), so
  SEMMacroBuildCLI resolves.
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-47
- Generate imported targets for the loadable-module libraries too (scan
  qt-loadable-modules), so C++ extensions linking module libs by name (e.g.
  vtkSlicerMarkupsModuleMRML) resolve instead of emitting bare -l. Add
  Qt6::Core5Compat to the q* imported targets' interface (legacy QRegExp etc.).
  Folds the SlicerOpenIGTLink %prep shims into the foundation.
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-46
- Ship the Base/Logic + all loadable-module public C++ headers (+ generated
  export headers) that Slicer omits but C++ extensions #include widely
  (vtkSlicerBaseLogic.h, vtkSlicerColorLogic.h, vtkMRMLMarkupsNode.h, ...);
  flattened into include/Slicer-5.11. Scoped from SlicerOpenIGTLink + SlicerIGT
  + SlicerDMRI header needs, so the full set lands at once.
- The install-tree imported targets (SlicerTargets.cmake) now carry
  INTERFACE_INCLUDE_DIRECTORIES=/usr/include/vtkAddon, so extensions linking
  MRML/Slicer libs inherit the system vtkAddon include dir (MRMLCore public
  headers #include vtkAddon's vtkLoggingMacros.h).

* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-45
- Complete C++ extension-build support (found while bringing up SlicerOpenIGTLink):
  (1) ship the generated *Export.h headers (vtkMRMLExport.h + ~129 others) that
  Slicer's install omits but public library headers #include — self-discovered
  per installed include dir; (2) the install-tree config now sets
  Slicer_VTK_WRAP_HIERARCHY_DIR to ${CMAKE_BINARY_DIR} (an extension's own
  writable wrap-hierarchy OUTPUT dir; deps still resolve via the per-target
  install paths); (3) add Teem to Slicer_EXTERNAL_PROJECTS_NO_USEFILE (Fedora's
  teem ships no TeemUse.cmake). With these, a C++ extension configures, wraps,
  and compiles against the system install.

* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-44
- Fix the VTK wrap-hierarchy shipping (was a no-op in -43): the build-tree files
  are named <Target>Hierarchy.txt (MRMLCoreHierarchy.txt, vtkTeemHierarchy.txt,
  ...), not *-hierarchy.txt, so the -43 find matched nothing and hierarchy/
  shipped empty. Correct the find, and the install-tree config now remaps every
  <Target>_WRAP_HIERARCHY_FILE into lib/Slicer-5.11/hierarchy so python-wrapped
  C++ extension modules (e.g. OpenIGTLinkIF MRML) can resolve their link
  hierarchy. Completes install-tree extension-build support.

* Sun Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-43
- Make 3dslicer-devel usable for building C++ extensions against the INSTALL
  tree (upstream only supports build-tree extension builds). %install now:
  (1) generates a relocatable install-tree SlicerConfig.cmake + SlicerTargets
  .cmake (imported targets) via gen-install-config.py, replacing the broken
  build-tree config Slicer ships verbatim; (2) ships the full source CMake/ +
  Extensions/CMake/ (the install was missing extension-support modules, the
  qSlicerExport.h.in export template, and the CPack bundle-fixup template);
  (3) ships the VTK wrap-hierarchy files needed to python-wrap extension VTK
  classes. Validated through configure against the SlicerOpenIGTLink build.
- Fix CLI module discovery: Slicer's CLI executables install to bin/ but the
  launcher scans lib/Slicer-5.11/cli-modules (which was empty), so CLI modules
  were unfindable; symlink them into cli-modules.

* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-42
- Rename the launcher: ship /usr/bin/Slicer (upstream-canonical) and a
  /usr/bin/3dslicer alias instead of the lowercase /usr/bin/slicer, which
  collided on PATH with FSL's own "slicer" volume viewer (~/fsl/.../bin/slicer).
- No Slicer-side change was needed for bug #9 (broken "import qt/ctk/vtkAddon"
  and qt.QWidget in scripted modules): that is fixed entirely in the supporting
  packages — python-pythonqt 0.15 (full Qt wrappers so PythonQt_QtAll::init
  registers QtWidgets), ctk 0.15 (qt/ctk stubs symlinked onto python sitelib),
  and vtkAddon 0.2 (ships vtkAddonPython.so in python3-vtkAddon). Slicer's
  embedded interpreter already scans system site-packages, so these land on
  its path without rebuilding Slicer.

* Thu Jun 11 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-41
- Fix bug #8: the -40 RPM built successfully but was UNINSTALLABLE. The
  ScriptedCLI Wizard template (share/Slicer-5.11/Wizard/.../TemplateKey.py)
  ships a "#!/usr/bin/python-real" shebang; RPM's script-dependency generator
  turned that into Requires: /usr/bin/python-real, which no package provides.
  The -40 bug #5 sed was too narrow (only *.py shebangs ending in bare "python")
  so "python-real" slipped through. Broaden the %install shebang normalization to
  every non-system python shebang (bare python, pythonX.Y, python-real, env
  python), prefiltered with grep -I so only real "#!" text files are touched.
  Add %global __requires_exclude ^/usr/bin/python-real$ as a backstop.
- Reword a comment that tripped rpmbuild's macro-in-comment warning.

* Wed Jun 11 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-40
- No code change from -39 (bug #3-#7 fixes carry forward, still unexercised:
  -39 stalled in the compile before reaching %install/%files).
- Drop build parallelism -j4 -> -j2. -j4 cleared the step-705 module-compile
  burst on a higher-RAM builder but a RAM-poorer builder swap-stalled there
  ~1.5h with zero log output (build 10591218, canceled). -j2 halves peak memory
  again so the smallest COPR builders also get through; raised --timeout absorbs
  the longer wall clock.

* Wed Jun 11 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-39
- Pre-validated %files against the -37 build's full install manifest (6022
  install lines) instead of burning another ~4h compile to discover mismatches.
  Found and fixed two:
- bug #6: 20 files install outside %{slicer_inst} into the system Qt6 plugin
  tree (18 designer + 1 iconengine + 1 style plugin); package them explicitly,
  else %install fails with "installed (but unpackaged) file(s) found".
- bug #7: Slicer's CMake config installs under lib/Slicer-5.11/CMake/, not the
  lib/cmake/ assumed by the -devel %files (which matched nothing -> "file not
  found"). Point both the %exclude and the -devel entry at the real path.
- No code change from -38; bug #5 shebang fix and the -j4 cap carry forward.

* Wed Jun 11 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-38
- BREAKTHROUGH: the -37 build (-j4 cap) COMPILED CLEAN 2843/2843 with NO stall
  at step 705 (memory cap fixed the swap-death) AND %cmake_install ran to
  completion -- bug #3 and bug #4 (CTKAppLauncher) both confirmed FIXED. The
  build now fails only in Fedora's post-install policy scripts.
- Fix Slicer source bug #5: brp-mangle-shebangs aborts %install on the ambiguous
  "#!/usr/bin/env python" shebang in installed scripts (ExtensionWizard.py et
  al.; 14 such files in-tree, all *.py). Normalize bare-python shebangs to
  python3 in the installed tree after %cmake_install. Slicer invokes these via
  its own launcher so the shebang is cosmetic.

* Wed Jun 10 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-37
- No code change from -36 (bug #4 launcher fix unchanged and still unexercised).
- Cap build parallelism: %%global _smp_mflags -j4. The -36 builds repeatedly
  died at ninja step ~705 -- where the ~150-CLI-link phase ends and ~16 parallel
  Qt/VTK-heavy module compiles begin -- by exhausting RAM on low-memory COPR
  builders (10587493 timed out thrashing at 705; 10587875 hard-stalled at 705
  ~4h with zero log output). A high-RAM builder finished the same compile
  (10586961 reached 2843), confirming a builder-RAM lottery, not a code fault.
  -j4 bounds peak memory so any builder completes; the raised --timeout (86400s)
  absorbs the slower wall clock.

* Wed Jun 10 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-36
- The -35 build (f44, run 10586961) COMPILED CLEAN (2843/2843) and cleared the
  bug #3 install fix, advancing deep into %install before failing on the next
  wall: "file INSTALL cannot find /usr/lib64/cmake/CTKAppLauncher/bin/
  CTKAppLauncher" (CMake/LastConfigureStep/cmake_install.cmake).
- Fix Slicer source bug #4: SlicerCPack.cmake installs the designer launcher
  from ${CTKAppLauncher_DIR}/bin/, a superbuild assumption; Fedora's
  commontk-applauncher ships the binary in %{_bindir} while its CMake config
  lives in %{_libdir}/cmake/CTKAppLauncher. Sed the install rule to %{_bindir}.
- Verified via guard analysis that all other build-tree-path install blocks
  (Python launcher, DCMTKApps/Libs, QtTesting, PythonQt, TBB, OpenSSL,
  LibArchive) are NOT Slicer_USE_SYSTEM_* gated and skipped in this config, so
  this is expected to be the last superbuild-path %install wall.
- (rawhide remains blocked separately on py3.15 vs the COPR's py3.14 vtk; this
  build targets fedora-44-x86_64 only.)

* Tue Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-35
- MILESTONE: the -34 build COMPILED CLEAN (the PythonQt include fix worked) —
  all 2843 ninja steps finished and it died in %install, not the compile.
- Fix Slicer source bug #3: Base/QTCore/Testing/Python/CMakeLists.txt installs
  qSlicerModuleGenericTest.py.in from ${CMAKE_CURRENT_BINARY_DIR}, but the file
  is a verbatim template that only exists in the source tree (its BUILD_TESTING
  staging block is empty). With BUILD_TESTING=OFF + development install on,
  %install aborted with "file INSTALL cannot find .../qSlicerModuleGenericTest
  .py.in". Sed the install path to ${CMAKE_CURRENT_SOURCE_DIR}. Grep-verified as
  the only install-from-binary-dir .in occurrence in the tree, so no further
  siblings should fail the remaining %install steps.

* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-34
- The -33 build cleared the QtTesting include wall (got ~2000 objects deeper,
  to 13300/?) and failed compiling qSlicerSubjectHierarchyModule.cxx:
  ctkAbstractPythonManager.h -> "PythonQtPythonInclude.h: No such file or
  directory". Same class as QtTesting: an installed CTK header pulls in a
  third-party (PythonQt) header, but the consuming target only links CTKWidgets
  and never inherits PythonQt's include dir.
- Add a second top-level hunk to slicer-qttesting-include-dirs.patch:
  include_directories(${PYTHONQT_INCLUDE_DIRS}) right after the existing
  find_package(PythonQt REQUIRED), inside if(Slicer_USE_PYTHONQT). Global, so it
  covers every subdirectory (Modules/Loadable/SubjectHierarchy, etc.).

* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-33
- The -32 build cleared the libqSlicerBaseQTCore.so link (ctk -0.13 fix) and
  failed later compiling qSlicerApplication.cxx: ctkQtTestingUtility.h ->
  "pqTestUtility.h: No such file or directory". qSlicerBaseQTGUI links only
  CTKWidgets (not CTKQtTesting), so it never inherits the qttesting include dir,
  yet it #includes the installed ctkQtTestingUtility.h directly.
- Broaden slicer-qttesting-include-dirs.patch with a top-level global
  include_directories(${QtTesting_INCLUDE_DIRS}) gated on Slicer_USE_QtTesting,
  covering every subdirectory (Base/QTApp, Base/QTCLI, Base/QTGUI, ...).
- Also requires ctk-devel >= 0.14 (find_dependency(QtTesting) in CTKConfig).

* Tue Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-32
- The -31 build (Patch1 fixed the qMRMLWidgets pqWidgetEventPlayer.h include)
  compiled far deeper, then failed linking libqSlicerBaseQTCore.so with an
  undefined reference to ctkVTKPythonQtWrapperFactory::ctkVTKPythonQtWrapperFactory().
- Cause: qSlicerCorePythonManager instantiates that class unconditionally, but
  CTK only compiles it into CTKVisualizationVTKCore when
  CTK_LIB_Scripting/Python/Core_PYTHONQT_USE_VTK is ON (default OFF). Fixed in
  ctk -0.13; bump BuildRequires to ctk-devel >= 2026.01.26-0.13. No Slicer code
  change — rebuild once the fixed CTK lands in COPR.

* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-31
- The -30 build (QtTesting ON, qttesting-devel present) ran 6.4h and got far
  past the -29 link wall, then failed in AUTOMOC of qMRMLWidgets at
  mocs_compilation.cpp.o: "pqWidgetEventPlayer.h: No such file or directory".
- Cause: qttesting installs headers under %%{_includedir}/QtTesting and its cmake
  imported target carries the right INTERFACE_INCLUDE_DIRECTORIES, but
  CTKQtTesting (which qMRMLWidgets links) does NOT re-export that include dir.
  Slicer's qMRML*EventPlayer/EventTranslator headers #include <pqWidgetEventPlayer.h>
  directly; the superbuild injects QtTesting's include path explicitly, the
  system build does not.
- Fix: Patch1 (slicer-qttesting-include-dirs.patch) adds find_package(QtTesting)
  + include_directories(${QtTesting_INCLUDE_DIRS}) to Libs/MRML/Widgets/
  CMakeLists.txt under if(Slicer_USE_QtTesting). Libs/MRML/Widgets is the only
  non-test library compiling these sources; all other EventPlayer/Translator
  sources are under Testing/ (BUILD_TESTING still OFF here).

* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-30
- Enable Slicer_USE_QtTesting=ON now that qttesting is packaged and ctk 0.12
  wraps it as CTKQtTesting. Slicer's qMRML*EventPlayer/EventTranslator sources
  link CTKQtTesting transitively via CTK_DIR; add BuildRequires qttesting-devel
  and -DQtTesting_DIR so CTKConfig's find_dependency(QtTesting) resolves the
  imported qttesting target. Upstream 208adb86 already supports Qt6 QtTesting
  (Qt5-only XmlPatterns guard), so no Slicer source patch is needed.
- BUILD_TESTING stays OFF in this step: this proves QtTesting links without
  also compiling the full CTest executable suite (deferred to -31) on an
  already-multi-hour build, isolating any QtTesting link failure from the
  test-compile load.
- Note: the -29 attempt (Slicer_USE_QtTesting=OFF) died at step 680/2837 with
  "cannot find -lqttesting" linking libqSlicerIconEnginePlugin.so. ctk 0.12's
  exported targets carry a transitive link to libqttesting regardless of
  Slicer_USE_QtTesting, so qttesting-devel is mandatory once CTK is built with
  CTK_USE_QTTESTING=ON. A QtTesting-OFF baseline therefore buys nothing here;
  -30 (qttesting-devel present, QtTesting ON) supersedes it.

* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-29
- Functional baseline rebuild against ctk 0.12. The -28 build advanced past the
  Python 3.14 / QtTesting fixes to step 938/2843, then failed linking
  libqMRMLWidgets.so with undefined ctkVTKChartView references. ctk 0.12 now
  exports those (transfer-function charts), so just bump and rebuild; QtTesting
  stays OFF until this functional baseline lands.

* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-28
- LTO-off build (-27) ran 6.7h (raised --timeout worked) and got past the prior
  timeout wall to step ~831/2843, surfacing two real compile errors, both fixed:
- Disable Slicer_USE_QtTesting: the qMRML*EventPlayer/EventTranslator sources
  need Kitware QtTesting's pqWidgetEventPlayer.h, which is not packaged on Fedora.
  BUILD_TESTING is already OFF, so the GUI record/replay feature is dispensable.
- Patch0 (slicer-python314-interpreter-config.patch): Python 3.14 on F44/rawhide
  removed the private _PyInterpreterState_GetConfigCopy / _PyInterpreterState_-
  SetConfig API that qSlicerCoreApplication used to refresh sys.argv post-PythonQt
  init. Replace with a direct PySys_SetObject("argv", ...) via stable public
  C-API; sys.path is left as-is (already runtime-augmented). Upstream Slicer's
  superbuild ships Python 3.9 so never hit this.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-27
- Disable LTO (%%global _lto_cflags %%{nil}) and drop the -j8 cap. -26 proved the
  ITK backport works (compiled cleanly past the AxesReorder wall) but hit COPR's
  5h builder timeout at only ~705/2843 steps: Fedora's default fat-LTO doubles
  compile work and makes each of Slicer's ~150 CLI links a slow memory-heavy LTO
  pass. LTO off ~halves compile time and removes the memory pressure the -j8 cap
  was containing, so we now use all builder CPUs. Build submitted with raised
  --timeout for margin.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-26
- Rebuild against InsightToolkit5 5.4.6-7, which now carries the Slicer/ITK-fork
  backport patches (5D NRRD / NrrdImageIO AxesReorder API). This unblocks the
  vtkITKImageSequenceReader compile that -25 would have hit (-25 was cancelled
  pre-emptively). Pin BR to InsightToolkit5-devel >= 5.4.6-7.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-25
- Rebuild against vtk 9.6.2-10. -24 regressed at configure (CMakeLists.txt:996
  find_package(VTK)): ViskoresTargets.cmake referenced
  /usr/lib64/libviskores_cont_testing-.so.1.1.0 which vtk 9.6.2-9 stripped.
  vtk-10 ships the Viskores testing libs, so find_package(VTK) resolves again.
  The -I/usr/include/gdcm CXXFLAGS fix from -24 (vtkITK gdcmDict.h) carries
  forward untested — configure died before reaching the compile phase.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-24
- Add -I%%{_includedir}/gdcm to CXXFLAGS. -23 cleared the link error and
  reached step 41/2843, then failed compiling Libs/vtkITK
  (vtkITKArchetypeImageSeriesVectorReaderSeries.cxx) with "gdcmDict.h: No
  such file or directory". vtkITK includes the GDCM header directly but only
  gets GDCM transitively via include(${ITK_USE_FILE}), which does not carry
  the system /usr/include/gdcm path to that target.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-23
- Rebuild against SlicerExecutionModel-0.9, which installs
  libModuleDescriptionParser.so into the standard %%{_libdir}. -22 reached
  the link phase but failed at step 38/2843 with "cannot find
  -lModuleDescriptionParser": SlicerBaseCLI links it bare (no -L) while the
  .so lived in the private %%{_libdir}/SlicerExecutionModel. Now resolves via
  the default linker path.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-22
- Rebuild against SlicerExecutionModel-0.8, which drops the broken
  GenerateCLPLauncher. -21 reached the compile phase but failed at
  ninja step 1/2843 generating Modules/CLI/*CLP.h: GenerateCLPLauncher
  resolved its real binary to the nonexistent /usr/GenerateCLP. SEM-0.8
  ships GenerateCLP directly (rpath to its private libdir), so CLP
  generation now works. No 3dslicer spec change beyond the rebuild.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-21
- Revert to InsightToolkit5 (ITK_DIR=ITK-5.4). Confirmed from upstream
  SuperBuild/External_ITK.cmake @208adb86 that Slicer pins the Slicer/ITK
  fork tag slicer-v5.4.6-2026-04-20 and does find_package(ITK 5.1 REQUIRED) —
  upstream is NOT on ITK6. The -18 ITK6 switch was a wrong turn: it gained
  nothing on itkNamespace.h (absent in both ITK5 and ITK6, stubbed either
  way) and regressed configure with an HDF5 imported-target collision and a
  missing MGHIO module. ITK5 (5.4.6, carries MGHIO/IOScanco) configured
  cleanly and was already compiling at -17. Re-add InsightToolkit5-vtk-devel
  BR for ITKVtkGlue headers.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-20
- Add cli11-devel BR. VTK 9.6's cmake config now calls
  find_package(CLI11) — surfaced by 3dslicer-19 since the ITK6 switch
  pulled a fresh build chroot.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-19
- Drop BR on nonexistent InsightToolkit6-vtk-devel. ITK6 bundles
  ITKVtkGlue into the main -devel package (no separate subpackage
  like ITK5 had). Surfaced by -18's dnf resolve failure.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-18
- Switch from InsightToolkit5 to InsightToolkit6 (6.0.0~b02). The
  Slicer main HEAD branch is the Qt6-modernization branch; it
  presumes the corresponding ITK-6 modernization too.
- Stub Libs/ITKFactoryRegistration/itkNamespace.h and
  Libs/vtkITK/itkNamespace.h. Slicer's SuperBuild normally patches
  this file into ITK's source tree; since we don't superbuild,
  the file is just missing and compile fails at the first vtkITK
  / ITKFactoryRegistration translation unit. Stub it as an empty
  `namespace itk {}` so the include resolves.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-17
- Fix Slicer source bug #2: 4 Libs/*/CMakeLists.txt reference
  ${CMAKE_CURRENT_BINARY_DIR}/${configure_header_file} in install(FILES ...)
  without ever setting configure_header_file, leaving a trailing-slash
  directory in the install list. Drop the unresolved reference. Hits
  vtkTeem, MRML/CLI, RemoteIO, MRML/Logic (the 4 files reporting the
  "install FILES given directory" error since -10).

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-16
- Fix 4 broken glob patterns in Libs/*/CMakeLists.txt that use POSIX-
  regex alternation `*.(h|hxx)` — cmake file(GLOB) doesn't support
  alternation, so the glob returns empty, and the downstream
  install(FILES ...) call gets only the trailing directory path,
  aborting with "install FILES given directory ... to install."
  Rewrite to two valid glob patterns: `*.h" "${...}/*.hxx`. Hits
  vtkTeem, vtkSegmentationCore, vtkITK, ITKFactoryRegistration.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-15
- Short-circuit SlicerBlockInstallTBB.cmake. The file expects to
  bundle libtbb.so.12 + libtbbmalloc.so.2.5 + libtbbmalloc_proxy.so.2.5
  into Slicer's install dir, but Fedora's tbb-2022.3 ships .so.2.17
  not .so.2.5 — and we package as RPM so we want system TBB anyway,
  not a bundled copy. Replace the file with bare `return()`.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-14
- Pre-define Slicer_REVISION, Slicer_WC_LAST_CHANGED_DATE, Slicer_WC_URL.
  Tarball builds have no .git/.svn, so SlicerMacroExtractRepositoryInfo
  leaves these vars unset and SlicerPackageAndUploadTarget aborts with
  "Variable Slicer_WC_LAST_CHANGED_DATE is expected to be defined".

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-13
- Hint CTKAppLauncherLib_DIR. The CTKAppLauncher-devel package ships
  both CTKAppLauncherConfig.cmake and CTKAppLauncherLibConfig.cmake in
  /usr/lib64/cmake/CTKAppLauncher/ but cmake treats them as distinct
  packages requiring distinct _DIR hints.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-12
- Hint SlicerExecutionModel + GenerateCLP + ModuleDescriptionParser
  DIR variables. Fedora's SlicerExecutionModel-devel ships configs
  directly under /usr/lib64/SlicerExecutionModel/, /usr/lib64/GenerateCLP/,
  /usr/lib64/ModuleDescriptionParser/ — not the canonical
  /usr/lib64/cmake/<pkg>/ layout, so cmake's default search misses them.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-11
- Set vtkAddon_CMAKE_DIR directly. Slicer's top-level CMakeLists.txt
  references ${vtkAddon_CMAKE_DIR} at line 898 without calling
  find_package(vtkAddon) first — the superbuild normally pre-populates
  it. -10's vtkAddon_DIR hint wasn't enough on its own.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-10
- Hint vtkAddon_DIR explicitly. Slicer's top-level CMakeLists puts
  ${vtkAddon_CMAKE_DIR} on CMAKE_MODULE_PATH so Libs/vtkTeem's
  include(vtkMacroKitPythonWrap) can find the macro that vtkAddon-devel
  ships at /usr/lib64/cmake/vtkAddon/. Without the hint, find_package
  silently doesn't set vtkAddon_CMAKE_DIR and the include fails.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-9
- Ship a Teem cmake shim in %%build. Fedora's teem-devel has a
  packaging bug (TODO: file Bugzilla): the shipped TeemConfig.cmake
  computes Teem_USE_FILE = /usr/lib64/lib/TeemUse.cmake (one level
  up from cmake/ then down into lib/), but the file actually lives
  beside TeemConfig.cmake in /usr/lib64/cmake/. Generate a corrected
  shim locally and point Teem_DIR at it.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-8
- Fix Teem_DIR. Fedora's teem-devel installs TeemConfig.cmake directly
  under /usr/lib64/cmake/ (verified via rpm -qlp teem-devel), not the
  versioned cmake/Teem-1.11.0/ subdir that an outdated dnf repoquery
  output suggested in -7.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-7
- Add -DPythonQt_DIR and -DTeem_DIR explicit hints. Our COPR
  python-pythonqt-devel (-0.13) ships its cmake config at
  /usr/lib64/cmake/PythonQt/. Fedora's teem-devel ships
  TeemConfig.cmake under a version-suffixed dir (cmake/Teem-1.11.0/)
  which Slicer's find_package(Teem) doesn't auto-discover.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 5.11.0~pre.20260517git208adb86-6
- Rebuild against python-pythonqt 4.0.1 (Qt6 build via the
  patched-v4.0.1 commontk branch, commit 7ef4c5ee). Previous
  pythonqt patched-9 was Qt5-only and incompatible with Slicer's
  Qt6 cmake config.

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
