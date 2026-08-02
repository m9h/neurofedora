# Disable LTO - causes linker issues with system ITK/VTK on F43
%global _lto_cflags %{nil}

# Limit parallelism to prevent OOM on builds
%global _smp_mflags -j4

Name:           mitk
Version:        2026.06
Release:        8%{?dist}
Summary:        Medical Imaging Interaction Toolkit

License:        BSD-3-Clause
URL:            https://www.mitk.org/
Source0:        https://github.com/MITK/MITK/archive/v%{version}/MITK-%{version}.tar.gz
# CMake find modules for system libraries that lack CMake config files
Source1:        FindANN.cmake
Source2:        FindQt6Qwt6.cmake
Source3:        Findlz4.cmake

# MITK embeds a heavily modified fork of CppMicroServices (v2.99.0) in
# Modules/CppMicroServices/. This is NOT the same as the standalone
# CppMicroServices 3.x in Fedora; it cannot be unbundled.
Provides:       bundled(CppMicroServices) = 2.99.0

# Core build tools
BuildRequires:  cmake >= 3.22
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  make
BuildRequires:  git

# The Big Two (from mhough/neurofedora COPR)
# Fedora's InsightToolkit is stuck at 4.13.3; MITK requires ITK 5.x
# Fedora's VTK is 9.2.6; MITK needs 9.3+
BuildRequires:  InsightToolkit5-devel >= 5.4
BuildRequires:  vtk-devel >= 9.5

# Qt6 (MITK requires >= 6.6)
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-qtwebengine-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtscxml-devel
BuildRequires:  qt6-linguist

# System libraries to unbundle from MITK superbuild
BuildRequires:  boost-devel
BuildRequires:  dcmtk-devel >= 3.6.7
BuildRequires:  gdcm-devel
BuildRequires:  hdf5-devel
BuildRequires:  poco-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  tinyxml2-devel
BuildRequires:  ann-devel
BuildRequires:  lz4-devel
BuildRequires:  zlib-devel
BuildRequires:  eigen3-devel
BuildRequires:  cpp-httplib-devel
BuildRequires:  qwt-qt6-devel

# VTK transitive deps (VTK's cmake config requires these at find_package time)
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  python3-devel
BuildRequires:  pybind11-devel
BuildRequires:  python3-numpy
# strip the build-tree RUNPATH off the pybind11 extension in %install
BuildRequires:  patchelf
BuildRequires:  json-devel
BuildRequires:  xz-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  proj-devel
BuildRequires:  libxml2-devel

# Other build dependencies
BuildRequires:  openssl-devel >= 3.0
BuildRequires:  tbb-devel
BuildRequires:  pcre2-devel
BuildRequires:  libXt-devel
BuildRequires:  libXext-devel
BuildRequires:  libXrender-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  libglvnd-devel

# ITK transitive deps (needed for cmake find_package)
BuildRequires:  fftw-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  expat-devel
BuildRequires:  double-conversion-devel
BuildRequires:  openjpeg2-devel
BuildRequires:  libminc-devel

# --- MITK Workbench (BlueBerry) ------------------------------------------
# CTK provides the plugin framework BlueBerry and every org.mitk.* plugin is
# built on; 0.19 is the first release that ships libCTKPluginFramework.so.
# (qwt-qt6-devel and qt6-qtwebengine-devel are already required above, for the
# plotting widgets and the welcome plugin's start page respectively.)
BuildRequires:  ctk-devel >= 2026.01.26-0.21
# CTKConfig.cmake does an unconditional find_dependency(QtTesting) (CTK is built
# with CTK_USE_QTTESTING=ON for Slicer's GUI tests), so every consumer of
# ctk-devel must have this present or find_package(CTK) fails outright.
# 3dslicer.spec carries the same BuildRequires for the same reason.
BuildRequires:  qttesting-devel
# ACVD backs the remeshing plugin in the Default configuration.
BuildRequires:  acvd-devel

%description
The Medical Imaging Interaction Toolkit (MITK) is a free open-source software
system for development of interactive medical image processing software.
MITK combines the Insight Toolkit (ITK) and the Visualization Toolkit (VTK)
with an application framework for medical imaging.

This package provides the core MITK libraries. The end-user application is in
the mitk-workbench subpackage, and the Python bindings in python3-mitk.

%package devel
Summary:        Development files for MITK
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       InsightToolkit5-devel
Requires:       vtk-devel
Requires:       boost-devel
Requires:       dcmtk-devel

%description devel
Development files, headers, and CMake config for building applications
and plugins that use the MITK libraries.

%package        workbench
Summary:        MITK Workbench application
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       ctk-plugin-framework%{?_isa} >= 2026.01.26-0.21
Requires:       hicolor-icon-theme

%description    workbench
The MITK Workbench is the end-user application built on MITK's BlueBerry
plugin framework. It provides the data manager, multi-widget image viewer,
DICOM browser, segmentation, measurement, volume visualization, movie maker
and remeshing tools.

%package -n python3-mitk
Summary:        Python bindings for MITK (built against system Python 3.14)
Requires:       mitk%{?_isa} = %{version}-%{release}
%description -n python3-mitk
pybind11-based Python bindings for the Medical Imaging Interaction Toolkit,
built against the system Python and ITK/VTK/DCMTK (no bundled libraries).

%prep
%autosetup -n MITK-%{version}

# UPSTREAM WORKAROUND: Wrapping/Python/mitk/CMakeLists.txt sets
#   mitk_PACKAGE_DIR = ${Python3_SITEARCH}/mitk
# which writes the module into the live interpreter site-packages at build
# time (outside the buildroot) and desyncs from the install rule. Stage it in
# the build tree instead, where install(DIRECTORY ${MITK_BINARY_DIR}/python/)
# picks it up. (Reported upstream.)
sed -i 's|set(mitk_PACKAGE_DIR "${Python3_SITEARCH}/mitk")|set(mitk_PACKAGE_DIR "${MITK_BINARY_DIR}/python/mitk")|' Wrapping/Python/mitk/CMakeLists.txt

# Install CMake find modules for system libs without CMake configs
cp %{SOURCE1} CMake/FindANN.cmake
cp %{SOURCE2} CMake/FindQt6Qwt6.cmake
cp %{SOURCE3} CMake/Findlz4.cmake

# Fix ZLIB config mode failure on Fedora (zlib-ng-compat ships a broken config
# that references ZLIB::ZLIBSTATIC which doesn't exist without static libs).
# Pre-find ZLIB via module mode and mark as found before the EP loop runs.
sed -i '/^get_property(MITK_EXTERNAL_PROJECTS GLOBAL PROPERTY MITK_EXTERNAL_PROJECTS)/i \
find_package(ZLIB REQUIRED MODULE)\
set(ZLIB_FOUND TRUE)' CMakeLists.txt
# Also prevent the EP loop from re-finding ZLIB in CONFIG mode by removing ZLIB
# from the external projects list.
sed -i '/^get_property(MITK_EXTERNAL_PROJECTS GLOBAL PROPERTY MITK_EXTERNAL_PROJECTS)/a \
list(REMOVE_ITEM MITK_EXTERNAL_PROJECTS ZLIB)' CMakeLists.txt

# Fix ITK PhilipsREC IO factory: MITK defines ITK_IO_FACTORY_REGISTER_MANAGER
# which triggers auto-registration of ALL IO factories including PhilipsREC.
# But MitkCore doesn't list IOPhilipsREC in PACKAGE_DEPENDS, so the factory
# registration symbol is unresolved. Add it to the IO modules list.
sed -i 's|IOBioRad+IOBMP|IOBioRad+IOBMP+IOPhilipsREC|' Modules/Core/CMakeLists.txt

# Fix cpp-httplib API break: Fedora ships 0.30+ which renamed
# MultipartFormDataItems → UploadFormDataItems (same struct, just renamed)
# (2026.06: mitkMonaiLabelTool.cpp was refactored away and the httplib
# MultipartFormDataItems->UploadFormDataItems rename landed upstream — sed dropped.)

# Fix LZ4 target name: VTK's FindLZ4 creates LZ4::LZ4 but MITK
# expects LZ4::lz4_shared from its superbuild
sed -i 's/LZ4::lz4_shared/LZ4::LZ4/g' Modules/DataTypesExt/CMakeLists.txt

# MITK 2026.06 upstream bug: Modules/PET/CMakeLists.txt adds its test/ subdir
# UNCONDITIONALLY (Modules/Core correctly wraps it in if(BUILD_TESTING)). That test
# dir includes cmake/PETIBSIData.cmake, which FetchContent-git-clones an IBSI PET
# dataset (oncoray/suv_computation.git) at CONFIGURE time. In mock/COPR there is no
# network, so configure dies -- and downloading sources at build time violates Fedora
# policy regardless. Guard it exactly like Core so BUILD_TESTING=OFF really skips it.
sed -i 's|^add_subdirectory(test)$|if(BUILD_TESTING)\n  add_subdirectory(test)\nendif()|' \
    Modules/PET/CMakeLists.txt

# MITK 2026.06 calls OFTime::hasTimeZone() (Modules/DICOM/src/mitkDICOMTimeUtil.cpp),
# which Fedora's DCMTK 3.6.9 does not provide (it has only get/setTimeZone()).
# Version-guard the UTC-normalization block: keep the feature on a newer DCMTK, and
# on 3.6.9 skip it -- which is exactly upstream's documented fallback ("leave the
# value as-is ... keeps the common single-timezone path bit-identical").
python3 - Modules/DICOM/src/mitkDICOMTimeUtil.cpp <<'PYFIX'
import sys
p = sys.argv[1]
src = open(p).read()
old = """    if (time.getTime().hasTimeZone())
    {
      const double tzHours = time.getTime().getTimeZone();
      tp -= milliseconds{std::llround(tzHours * 3600.0 * 1000.0)};
    }"""
new = """#if defined(DCMTK_VERSION_NUMBER) && DCMTK_VERSION_NUMBER > 369
    if (time.getTime().hasTimeZone())
    {
      const double tzHours = time.getTime().getTimeZone();
      tp -= milliseconds{std::llround(tzHours * 3600.0 * 1000.0)};
    }
#endif"""
assert old in src, "hasTimeZone block not found -- upstream changed it"
open(p, "w").write(src.replace(old, new, 1))
print("DCMTK hasTimeZone block version-guarded")
PYFIX

# Boost 1.87+ removed boost::detail::lcast_get_precision<T>().
# It always returned std::numeric_limits<T>::max_digits10; substitute that.
sed -i 's|boost::detail::lcast_get_precision<\([A-Za-z_][A-Za-z0-9_]*\)>()|std::numeric_limits<\1>::max_digits10|g' \
    Modules/Core/include/mitkLexicalCast.h
grep -q '^#include <limits>' Modules/Core/include/mitkLexicalCast.h || \
    sed -i '0,/^#include/{s|^#include|#include <limits>\n#include|}' Modules/Core/include/mitkLexicalCast.h

# Remove bundled libraries that we use from system
# (Keep CppMicroServices - it's a modified fork we must bundle)

# VTK 9.6 (F44 system VTK overrides our COPR 9.5.2): removed
# vtkCutter::GetCellTypeDimensions(unsigned char*) — deprecated in 9.4
# with replacement hint "Use vtkCellTypes::GetDimension(type) instead."
# Replace the static buffer-fill with an inline loop using the new API,
# and pull in <vtkCellTypes.h> for the declaration.
# (2026.06: Modules/MapperExt/src/vtkPointSetSlicer.cxx was removed upstream —
# the vtkCutter::GetCellTypeDimensions VTK9 workaround is no longer needed.)

# MitkCore enables ITK_IO_FACTORY_REGISTER_MANAGER, which generates a
# header listing every IO factory in ITK_MODULES_ENABLED. Our COPR
# InsightToolkit5 ships MGHIO, IOScanco and ITKIODCMTK (needed by
# 3D Slicer), so mitkCoreActivator.cpp references e.g.
#   itk::MGHImageIOFactoryRegister__Private()
# But MITK's PACKAGE_DEPENDS parser auto-prefixes "ITK" onto component
# names, turning "MGHIO" into "ITKMGHIO" which isn't a real ITK
# component — so the libraries don't end up on the link line. Add them
# directly, bypassing the parser. (Surfaced by build 10525253.)
cat >> Modules/Core/CMakeLists.txt <<'EOF'

# Fedora packaging patch: link IO factories autoinited by
# ITK_IO_FACTORY_REGISTER_MANAGER but missing from MitkCore's
# PACKAGE_DEPENDS due to the ITK-prefix parser limitation.
target_link_libraries(MitkCore PRIVATE MGHIO IOScanco ITKIODCMTK)
EOF

# VTK 9.6: vtkVectorOperators.h was removed; the operators were merged
# into vtkVector.h. Two MITK gizmo sources still include the old header.
# Surfaced by build 10525366 (-9 advanced past the link error).
sed -i 's|#include <vtkVectorOperators\.h>|#include <vtkVector.h>|' \
    Modules/Gizmo/src/mitkGizmoInteractor.cpp \
    Modules/Gizmo/src/mitkGizmoMapper2D.cpp

# MITK 2025.12.2's CMake has NO install(TARGETS ...) for module libraries.
# Upstream only installs the Workbench bundle via MITK_INSTALL_TARGETS
# (EXECUTABLES Workbench GLOB_PLUGINS), but we build with BUILD_WORKBENCH
# off (BlueBerry/CTK aren't available for Qt6 on Fedora), so cmake_install
# produces only stray Qt6 WebEngine bundles — no libMitk*.so are copied.
# Append a bulk install at the end of root CMakeLists.txt using the
# MITK_MODULE_TARGETS global property that mitk_create_module already
# populates. Surfaced by build 10525956: compile OK, %files saw empty
# buildroot.
cat >> CMakeLists.txt <<'EOF'

# ---- Fedora packaging: install module libraries + headers ----
# No install(EXPORT) — MITK's mitk_create_module uses raw paths in
# target_include_directories (no BUILD_INTERFACE/INSTALL_INTERFACE
# generator expressions), which cmake rejects in an export set.
# find_package(MITK) support would require patching every module's
# include declaration; defer that. For now, just install the libs
# and headers so packages downstream can link via -lMitkCore etc.
get_property(_mitk_install_targets GLOBAL PROPERTY MITK_MODULE_TARGETS)
if(_mitk_install_targets)
  install(TARGETS ${_mitk_install_targets}
          LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
          RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
  foreach(_t ${_mitk_install_targets})
    get_target_property(_src ${_t} SOURCE_DIR)
    if(_src AND EXISTS ${_src}/include)
      install(DIRECTORY ${_src}/include/
              DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/mitk)
    endif()
  endforeach()
endif()
EOF

%build
# --- GCC 15 / Fedora 43 Fixes ---
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint -Wno-error=template-id-cdtor -Wno-error=unused-but-set-variable -Wno-error=array-bounds"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17"

# Unset env vars to prevent Conda/system tool interference
unset CC CXX LDFLAGS CONDA_PREFIX CONDA_DEFAULT_ENV CMAKE_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DMITK_BUILD_EXAMPLES=OFF \
    \
    -DCMAKE_MODULE_PATH=%{_builddir}/MITK-%{version}/CMake \
    -DMITK_USE_SUPERBUILD=OFF \
    `# Default = the plain MITK Workbench: BlueBerry + ACVD + Qt6 and the 17` \
    `# core GUI plugins (datamanager, segmentation, dicombrowser, imagenavigator,` \
    `# measurementtoolbox, volumevisualization, moviemaker, remeshing, ...).` \
    `# NOT WorkbenchRelease, which additionally needs MatchPoint (unpackaged)` \
    `# and DCMQI (packaged as 3dslicer-dcmqi but not yet building).` \
    -DMITK_BUILD_CONFIGURATION=Default \
    \
    -DMITK_USE_Qt6=ON \
    \
    -DMITK_USE_SYSTEM_Boost=ON \
    \
    `# BlueBerry is MITK's plugin framework and the basis of the Workbench` \
    `# application; it forces MITK_USE_CTK=ON and needs CTK built with` \
    `# CTK_ENABLE_PluginFramework (ctk >= 2026.01.26-0.19 ships it as the` \
    `# ctk-plugin-framework subpackage).` \
    -DMITK_USE_BLUEBERRY=ON \
    -DMITK_USE_CTK=ON \
    \
    -DMITK_USE_DCMQI=OFF \
    -DMITK_USE_MatchPoint=OFF \
    `# ACVD provides the remeshing plugin required by the Default config` \
    -DMITK_USE_ACVD=ON \
    \
    -DMITK_USE_Python3=ON \
    -DMITK_USE_pybind11=ON \
    -DPython3_EXECUTABLE=%{python3} \
    -DPython3_ROOT_DIR=%{_prefix} \
    -DMITK_USE_SWIG=OFF \
    -DMITK_USE_CppUnit=OFF \
    \
    -DMITK_USE_OpenMP=ON \
    -DMITK_USE_DCMTK=ON \
    -DMITK_USE_httplib=ON \
    \
    -DITK_DIR=%{_libdir}/cmake/ITK-5.4 \
    -DVTK_DIR=%{_libdir}/cmake/vtk \
    -DDCMTK_DIR=%{_libdir}/cmake/dcmtk \

%cmake_build

%install
%cmake_install

# mitkInstallRules.cmake (loaded unconditionally) drops a Qt6 runtime bundle
# into %{_bindir}: plugins/, translations/, resources/, QtWebEngineProcess.
# These duplicate the system qt6-* packages, which the Workbench finds on the
# normal Qt plugin path anyway.
#
# CAREFUL: with MITK_USE_BLUEBERRY=ON, %{_bindir}/plugins is ALSO where MITK's
# own BlueBerry plugins land (mitkFunctionCreatePlugin.cmake: install_directories
# = bin/plugins) as flat liborg_{mitk,blueberry}_*.so files. Qt's bundle instead
# uses per-category SUBdirectories (platforms/, imageformats/, sqldrivers/, ...).
# So delete only the subdirectories and keep the flat .so files -- a blanket
# `rm -rf %%{_bindir}/plugins` would silently remove every MITK plugin and leave
# an unusable Workbench.
if [ -d %{buildroot}%{_bindir}/plugins ]; then
  find %{buildroot}%{_bindir}/plugins -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
fi
rm -rf %{buildroot}%{_bindir}/translations
rm -rf %{buildroot}%{_bindir}/resources
rm -f  %{buildroot}%{_bindir}/QtWebEngineProcess

# mitkFunctionCreateBlueBerryApplication installs a relocatable-bundle launcher
# (CMake/RunInstalledApp.sh) to the install prefix ROOT, i.e. %{_prefix}/*.sh.
# It only exists to set LD_LIBRARY_PATH for a self-contained tarball; in an FHS
# install the loader already finds everything. Drop it -- %{_prefix}/*.sh is not
# a legal location for a shipped file.
rm -f %{buildroot}%{_prefix}/*.sh

# Desktop integration for the Workbench
if [ -f %{buildroot}%{_bindir}/MitkWorkbench ]; then
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/org.mitk.MitkWorkbench.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=MITK Workbench
GenericName=Medical Image Viewer
Comment=Interactive medical image processing and visualization
Exec=MitkWorkbench %F
Icon=org.mitk.MitkWorkbench
Terminal=false
Categories=Science;MedicalSoftware;Graphics;Viewer;
MimeType=application/dicom;image/x-nifti;
EOF
  for sz in 48 64 128; do
    icon=$(find %{_builddir}/MITK-%{version} -name "icon.png" -path "*Workbench*" | head -1)
    if [ -n "$icon" ]; then
      mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${sz}x${sz}/apps
      cp "$icon" %{buildroot}%{_datadir}/icons/hicolor/${sz}x${sz}/apps/org.mitk.MitkWorkbench.png
    fi
  done
fi

# Reveal the Workbench layout so %files can be tuned from the build log rather
# than another 3-hour round trip.
echo "=== bindir top level ==="; ls %{buildroot}%{_bindir}/ 2>/dev/null | head -30
echo "=== bin/plugins (MITK BlueBerry plugins) ==="; ls %{buildroot}%{_bindir}/plugins/ 2>/dev/null | head -40
echo "=== provisioning / config files ==="; find %{buildroot} -name "*.provisioning" -o -name "*.ini" 2>/dev/null | head
echo "=== anything left directly under %{_prefix} ==="; find %{buildroot}%{_prefix} -maxdepth 1 -type f 2>/dev/null | head

# --- Python bindings ------------------------------------------------------
# The pybind11 'mitk' package needs relocating + de-rpath'ing. Two upstream
# quirks are in play:
#  * In a non-wheel (Custom) build, Wrapping/Python/mitk/CMakeLists.txt installs
#    the extension only under -DMITK_BUILD_CONFIGURATION=PythonWheel (the
#    install(TARGETS mitk_python_bindings)/install(FILES __init__.py) calls are
#    guarded by `if(MITK_BUILD_CONFIGURATION STREQUAL "PythonWheel")`). What
#    DOES install it is mitkInstallRules.cmake, which copies the staged
#    build-tree python/ dir to %{_prefix}/python -- so the package lands at
#    %{_prefix}/python/mitk (the %prep sed redirected mitk_PACKAGE_DIR into the
#    build tree so this staging dir exists). Relocate it to the interpreter
#    sitearch, the canonical location.
#  * The extension is linked against the not-yet-installed MitkCore/… via
#    build-tree paths, so it carries a build-dir RUNPATH (+ a trailing empty
#    entry) that RPM's check-rpaths rejects. Upstream applies a $ORIGIN
#    INSTALL_RPATH, but only in the PythonWheel config; in a Custom build the
#    module needs no rpath -- the libMitk*.so install to %{_libdir}, on the
#    default loader path. Strip it. (Both reported upstream.)
if [ -d %{buildroot}%{_prefix}/python/mitk ]; then
  mkdir -p %{buildroot}%{python3_sitearch}
  cp -a %{buildroot}%{_prefix}/python/mitk %{buildroot}%{python3_sitearch}/
  rm -rf %{buildroot}%{_prefix}/python
  patchelf --remove-rpath %{buildroot}%{python3_sitearch}/mitk/mitk.cpython-*.so
fi
# reveal the resulting layout for %files tuning on the first NUC build
echo "=== python3-mitk install tree ==="; find %{buildroot}%{python3_sitearch}/mitk 2>/dev/null | head -40 || echo "NO mitk module"

%files
%license LICENSE
%doc README.md
# MITK 2026.06 installs its shared libraries as RUNTIME artifacts, so they land in
# %{_bindir} (+ per-module micro-service subdirs), NOT %{_libdir}. The old
# %{_libdir}/libMitk*.so glob matched nothing -> 196 unpackaged files. MITK modules
# ship without SOVERSION (only libMitk*.so, no .so.<n> chain).
%{_bindir}/libMitk*.so
%dir %{_bindir}/MitkCore
%{_bindir}/MitkCore/libMitk*.so
%dir %{_bindir}/MitkDICOM
%{_bindir}/MitkDICOM/libMitk*.so
%dir %{_bindir}/MitkModelFit
%{_bindir}/MitkModelFit/libMitk*.so
# MITK also installs the flat shared libs to %{_libdir} (same SONAMEs, dual RUNTIME+
# LIBRARY destinations); package those too or ~98 stay unpackaged.
%{_libdir}/libMitk*.so

%files workbench
# The BlueBerry application and its plugin set. MITK installs plugins as flat
# liborg_{mitk,blueberry}_*.so under %{_bindir}/plugins (bin/plugins upstream);
# Qt's bundled per-category subdirectories are stripped in %install.
%{_bindir}/MitkWorkbench
%dir %{_bindir}/plugins
%{_bindir}/plugins/liborg_*.so
# BlueBerry reads this at startup to decide which plugins to provision.
%{_bindir}/*.provisioning
%{_datadir}/applications/org.mitk.MitkWorkbench.desktop
%{_datadir}/icons/hicolor/*/apps/org.mitk.MitkWorkbench.png

%files devel
%{_includedir}/mitk/
%{_libdir}/libqtsingleapplication.a

%files -n python3-mitk
%license LICENSE
%{python3_sitearch}/mitk/

%changelog
* Fri Jul 31 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-8
- Build the MITK Workbench: MITK_USE_BLUEBERRY=ON, MITK_USE_CTK=ON,
  MITK_USE_ACVD=ON and MITK_BUILD_CONFIGURATION=Default. Until now this was a
  library-only package -- 108 libraries but zero of upstream's 65 plugins and
  neither application -- so nearly everything in the 2026.06 release notes
  (segmentation tools, PET SUV, screenshot maker) was unreachable.
- New mitk-workbench subpackage: the MitkWorkbench binary, the BlueBerry
  plugins, the provisioning file, plus a desktop entry and icons.
- Requires ctk >= 2026.01.26-0.19, the first build shipping
  libCTKPluginFramework.so; MITK's plugin system uses ctkPluginContext /
  ctkPluginActivator across 160 files and cannot build without it.
- %%install: strip ONLY the per-category subdirectories of %%{_bindir}/plugins
  (Qt's bundled runtime) instead of the whole directory. With BlueBerry enabled
  that directory is also where MITK's own liborg_*.so plugins install, so the
  previous blanket rm would have removed every plugin.
- %%install: drop the RunInstalledApp.sh launcher that upstream installs to the
  prefix root (%%{_prefix}/*.sh); it only sets LD_LIBRARY_PATH for relocatable
  tarballs and is not a legal location for a shipped file.
- Chose Default over WorkbenchRelease: the latter additionally needs MatchPoint
  (not packaged) and DCMQI (packaged as 3dslicer-dcmqi, not yet building).
- BuildRequires qttesting-devel: CTKConfig.cmake does an unconditional
  find_dependency(QtTesting), so find_package(CTK) fails without it.
- Requires ctk >= 2026.01.26-0.20, which packages the DGraph utility and exports
  CTK_DGRAPH_EXECUTABLE; ctkMacroSetupPlugins aborts with "Executable doesn't
  exist!" without it, so no MITK plugin can configure against an installed CTK.

* Sun Jul 26 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-7
- Add python3-mitk subpackage (pybind11 bindings against system Python 3.14).
  MITK_USE_Python3=ON + MITK_USE_pybind11=ON. Upstream only installs the 'mitk'
  Python package under MITK_BUILD_CONFIGURATION=PythonWheel; in our Custom build
  cmake_install ships nothing, so %%prep redirects mitk_PACKAGE_DIR into the
  build tree and %%install copies the staged package (extension + __init__.py +
  mxn/ DSL) into %%{python3_sitearch}. Strip the build-dir RUNPATH off the
  extension (check-rpaths rejects it; libMitk*.so are on the default path).

* Thu Jul 17 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-6
- Complete the %%files fix: MITK 2026.06 installs its shared libs to BOTH %%{_bindir}
  AND %%{_libdir} (dual RUNTIME+LIBRARY destinations). -5 packaged only %%{_bindir},
  leaving 98 %%{_libdir}/libMitk*.so unpackaged. Add the %%{_libdir} glob.

* Tue Jul 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-5
- Fix %%files: MITK 2026.06 compiled 100%% (2079/2079) but failed packaging with 196
  unpackaged files. It installs shared libs as RUNTIME artifacts under %%{_bindir}
  (+ MitkCore/MitkDICOM/MitkModelFit micro-service subdirs), not %%{_libdir}, so the
  old %%{_libdir}/libMitk*.so glob matched nothing. Package the real locations.

* Tue Jul 14 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-4
- Add -Wno-error=array-bounds. MITK builds with -Werror, and GCC's -Warray-bounds
  fires a false positive inside ITK's own header (itkIndex.h:430, on
  itk::Index<2>), which killed MitkSegmentation (mitkCorrectorAlgorithm,
  mitkImageLiveWireContourModelFilter) at step 1784/2079. Same treatment already
  applied to template-id-cdtor and unused-but-set-variable.

* Sun Jul 12 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-3
- Fix compile against Fedora's DCMTK 3.6.9: MITK 2026.06's mitkDICOMTimeUtil.cpp
  calls OFTime::hasTimeZone(), which 3.6.9 does not provide (only get/setTimeZone).
  Version-guard the UTC-normalization block on DCMTK_VERSION_NUMBER > 369 -- the
  feature stays on newer DCMTK, and on 3.6.9 it degrades to upstream's own
  documented fallback (leave as-is; the single-timezone path is bit-identical).

* Sun Jul 12 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-2
- Fix configure FTBFS in mock/COPR: MITK 2026.06's Modules/PET/CMakeLists.txt adds
  its test/ subdir unconditionally (Modules/Core correctly guards with
  if(BUILD_TESTING)). That subdir FetchContent-git-clones an IBSI PET dataset at
  CONFIGURE time, which fails with no network and violates Fedora's no-downloads
  policy. Guard the PET test subdir on BUILD_TESTING so -DBUILD_TESTING=OFF honors it.

* Sun Jul 12 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.06-1
- Update to upstream MITK v2026.06 (released 2026-07-07; was 2025.12.2, which was
  also FTBFS on F44). Two %%prep seds dropped as upstream fixes landed:
  * mitkMonaiLabelTool.cpp refactored away + the httplib
    MultipartFormDataItems->UploadFormDataItems rename is upstream.
  * Modules/MapperExt/src/vtkPointSetSlicer.cxx removed upstream, so the
    vtkCutter::GetCellTypeDimensions VTK9 workaround is obsolete.
  Still required and verified against the 2026.06 tree: system-ZLIB external-project
  removal, IOPhilipsREC reader, LZ4::lz4_shared->LZ4::LZ4, Gizmo vtkVectorOperators
  ->vtkVector include. %%prep verified clean.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-13
- Realign %%files to what actually lands. -12's cmake patch installed
  49 MITK module libraries but they're unversioned (MITK doesn't set
  SOVERSION); spec was still requesting %%{_libdir}/libMitk*.so.* which
  doesn't exist. Ship the unversioned %%{_libdir}/libMitk*.so in main,
  headers + libqtsingleapplication.a in -devel.
- Strip Qt6 WebEngine bundle that mitkInstallRules.cmake drops in
  %%{_bindir} (plugins/, translations/, resources/, QtWebEngineProcess) —
  these collide with system qt6-qtwebengine packages.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-12
- Drop install(EXPORT) — MITK's mitk_create_module uses raw paths in
  target_include_directories without BUILD_INTERFACE / INSTALL_INTERFACE
  generator expressions, which cmake rejects in an export set (-11
  failed with "INTERFACE_INCLUDE_DIRECTORIES contains path ... which
  is prefixed in the build directory"). Install libs and headers
  unconditionally; find_package(MITK) support deferred until a
  follow-up patch upgrades every module's include declaration.
- Update %%files to match what actually lands: drop %%{_libdir}/mitk/
  and %%{_libdir}/cmake/MITK*/ (neither produced without EXPORT and
  Workbench), keep libraries and headers.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-11
- Add bulk install rules for module libraries + headers + export set.
  MITK 2025.12.2 has no install(TARGETS ...) for its module libraries —
  only the Workbench bundle gets installed via MITK_INSTALL_TARGETS,
  which we don't use (BUILD_WORKBENCH=OFF; BlueBerry/CTK unavailable
  for Qt6 on Fedora). Append a CMakeLists.txt snippet that iterates
  the MITK_MODULE_TARGETS global property (populated by
  mitk_create_module) and installs each library, its include/ tree,
  and a unified MITKTargets.cmake export set. Surfaced by build
  10525956: compile + cmake_install ran clean but %files saw an
  empty buildroot.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-10
- Fix VTK 9.6 FTBFS in Modules/Gizmo/src/mitkGizmo{Interactor,Mapper2D}.cpp:
  vtkVectorOperators.h was removed in VTK 9.6 (the operator overloads
  were merged into vtkVector.h). Replace the include. Surfaced by
  build 10525366 (mitk-9 cleared link errors and reached step 1012/1149
  before this hit).

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-9
- Link MGHIO, IOScanco and ITKIODCMTK into MitkCore. Build 10525253
  cleared the vtkCutter::GetCellTypeDimensions error from -8 but then
  hit undefined references to itk::{MGH,Scanco,DCMTK}ImageIOFactoryRegister
  __Private(). MITK's ITK_IO_FACTORY_REGISTER_MANAGER autoinit pulls
  these from ITK_MODULES_ENABLED, but MITK's PACKAGE_DEPENDS parser
  auto-prefixes "ITK" onto component names — so MGHIO/IOScanco get
  rewritten as ITKMGHIO/ITKIOScanco (which don't exist) and never
  reach the link line. Add the link directly after mitk_create_module().

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-8
- Fix VTK 9.6 FTBFS in Modules/MapperExt/src/vtkPointSetSlicer.cxx:280
  ("'GetCellTypeDimensions' is not a member of 'vtkCutter'"). F44's
  system VTK 9.6.2 outranks COPR's 9.5.2, so MITK now compiles
  against 9.6 which removed the static helper. Replace with the
  documented successor: vtkCellTypes::GetDimension(type) in an
  inline loop, and include vtkCellTypes.h. Surfaced by build 10506601.

* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-6
- Fix Boost 1.87+ FTBFS in Modules/Core/include/mitkLexicalCast.h:37 —
  boost::detail::lcast_get_precision<T>() was removed. Replace with
  std::numeric_limits<T>::max_digits10 (its historical implementation).

* Thu Mar 19 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-3
- Remove incorrect eigen3-devel Requires from -devel subpackage
  (MITK gets Eigen through ITK5 which bundles it)

* Thu Mar 19 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-2
- Fix ITK PhilipsREC IO factory linkage (add IOPhilipsREC to MitkCore deps)

* Mon Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-1
- Major rewrite: disable superbuild, use system libraries
- Use InsightToolkit5 5.4.5 and VTK 9.5.2 from COPR
- Disable BlueBerry/CTK (Fedora CTK is Qt5-only)
- Phase 1: core libraries only, no MitkWorkbench
- GCC 15 / Fedora 43 compatibility fixes
