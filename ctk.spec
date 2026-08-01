# Disable LTO - causes linker issues with VTK/ITK on Fedora 43+
%global _lto_cflags %{nil}

%global soname_version 0.1

%global commit fd37b874033c6589e28f5cefdd56a5f605d09960
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate 20260126

Name:           ctk
Version:        2026.01.26
Release:        0.19.%{snapdate}git%{shortcommit}%{?dist}
Summary:        The Common Toolkit for biomedical imaging (Qt6 build with VTK/ITK)

# The entire source is Apache-2.0; CMake/CMakeFindDependencyMacro.cmake is
# BSD-3-Clause, but does not contribute to the licenses of the binary RPMs.
License:        Apache-2.0
URL:            https://commontk.org/
Source0:        https://github.com/commontk/CTK/archive/%{commit}/CTK-%{shortcommit}.tar.gz

# Qt6 port of CTK_USE_QTTESTING (cherry-picks, Hans Johnson, 2026-03-28):
# isolate the removed QtXmlPatterns dependency to Qt5-only paths and detect the
# new lowercase "qttesting" external target name, so CTK_USE_QTTESTING can be
# enabled against the Qt6 qttesting package (unblocks 3D Slicer GUI tests).
Patch0:         ctk-qttesting-01-enable-qt6.patch
Patch1:         ctk-qttesting-02-guard-xmlpatterns-source.patch
Patch2:         ctk-qttesting-03-detect-target-name.patch
Patch3:         ctk-qttesting-04-guard-xmlpatterns-link.patch
# Qt6 made QInputEvent::operator= protected, so QMouseEvent value members are
# non-assignable; convert them to std::optional<QMouseEvent> with .emplace().
Patch4:         ctk-qttesting-05-qmouseevent-optional.patch

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

# This is the Qt6 CTK build for 3D Slicer, with VTK, ITK, and DICOM.
# It Conflicts with the Fedora stock ctk package (which is Qt5-only,
# has no VTK/ITK, and is at version 2023.07.13).
Conflicts:      ctk < 2026
# PluginFramework is now ENABLED (see %%build): MITK's plugin system is built on
# ctkPluginContext/ctkPluginActivator (160 files under MITK's Plugins/ use it), so
# MITK_USE_BLUEBERRY=ON is impossible without it. Slicer does not use it, and the
# change is purely additive -- it adds libCTKPluginFramework.so without altering
# CTKCore/Widgets/DICOM/VTK/ITK/Python -- so Slicer is unaffected.
# We now ship it as the ctk-plugin-framework subpackage below, which supersedes
# Fedora's 2023.07.13 one by version, so the old Obsoletes is no longer needed
# (and would be wrong now that we provide a package of that very name).

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  python-pythonqt-devel

# Qt6 — COPR VTK 9.5 is Qt6-based, so CTK must also use Qt6
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qttools-static
BuildRequires:  qt6-qtshadertools-devel
BuildRequires:  qt6-qt5compat-devel
# Qt6::StateMachine lives in qtscxml (moved from qtbase in Qt6)
BuildRequires:  qt6-qtscxml-devel

# DCMTK
BuildRequires:  dcmtk-devel

# VTK (COPR 9.5.2)
BuildRequires:  vtk-devel
# VTK cmake config transitive deps (COPR vtk-devel doesn't Require these yet)
BuildRequires:  json-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  hdf5-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  fmt-devel
BuildRequires:  libglvnd-devel
BuildRequires:  libtheora-devel
BuildRequires:  libogg-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel
BuildRequires:  expat-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  sqlite-devel
BuildRequires:  libxml2-devel
BuildRequires:  netcdf-devel
BuildRequires:  pugixml-devel
BuildRequires:  proj-devel
BuildRequires:  tbb-devel
BuildRequires:  PEGTL-devel
BuildRequires:  libharu-devel
BuildRequires:  gl2ps-devel
BuildRequires:  double-conversion-devel
BuildRequires:  eigen3-devel
BuildRequires:  cli11-devel
BuildRequires:  boost-devel
BuildRequires:  gdal-devel
# postgresql-server-devel conflicts with libpq-devel on F43; use libpq-devel
BuildRequires:  libpq-devel

# ITK5 (COPR)
BuildRequires:  InsightToolkit5-devel

# QtTesting (COPR) — external Qt6 record/replay lib for CTK_USE_QTTESTING=ON
BuildRequires:  qttesting-devel

%global _description %{expand:
The Common Toolkit is a community effort to provide support code for medical
image analysis, surgical navigation, and related projects. This build uses
Qt6 and includes VTK visualization, ITK image processing, and DICOM support
for use by 3D Slicer and other Qt6-based medical imaging applications.}

%description %{_description}
This package contains the CTK Core library.

%package        plugin-framework
Summary:        CTK dynamic plugin framework (OSGi-like)
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    plugin-framework %{_description}
The CTK Plugin Framework is a dynamic component system modelled on OSGi.
It is the foundation MITK's BlueBerry plugin system and all org.mitk.*
Workbench plugins are built on.

%package        widgets
Summary:        Qt6 widgets for biomedical imaging applications
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    widgets %{_description}
The Widgets library is a collection of Qt widgets for usage in biomedical
imaging applications.

%package        dicom
Summary:        High-level DICOM query/retrieve library
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-widgets%{?_isa} = %{version}-%{release}

%description    dicom %{_description}
DICOM library provides high-level classes supporting query and retrieve
operations from PACS and local databases.

%package        vtk
Summary:        CTK VTK visualization components
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-widgets%{?_isa} = %{version}-%{release}

%description    vtk %{_description}
VTK visualization widgets and core components for CTK.

%package        itk
Summary:        CTK ITK image processing components
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    itk %{_description}
ITK image processing core components for CTK.

%package        python
Summary:        CTK Python (PythonQt) bindings
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-widgets%{?_isa} = %{version}-%{release}
Requires:       python-pythonqt%{?_isa}

%description    python %{_description}
PythonQt-based Python bindings for CTK Core and Widgets, used by
3D Slicer for its scripted module / extension system.

%package        devel
Summary:        Development files for CTK
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-plugin-framework%{?_isa} = %{version}-%{release}
Requires:       %{name}-widgets%{?_isa} = %{version}-%{release}
Requires:       %{name}-dicom%{?_isa} = %{version}-%{release}
Requires:       %{name}-vtk%{?_isa} = %{version}-%{release}
Requires:       %{name}-itk%{?_isa} = %{version}-%{release}
Requires:       %{name}-python%{?_isa} = %{version}-%{release}
Requires:       dcmtk-devel%{?_isa}
Requires:       qt6-qtbase-devel%{?_isa}
Requires:       qt6-qtscxml-devel%{?_isa}
Requires:       qt6-qt5compat-devel%{?_isa}
Requires:       vtk-devel
Requires:       InsightToolkit5-devel

%description    devel %{_description}
This package contains development files for building applications with CTK.

%prep
%autosetup -p1 -n CTK-%{commit}

# Change EOL encoding
tr -d '\r' < README.md > README
mv -vf README README.md

# Fix cmake_minimum_required for CMake 4 compatibility
for f in \
    Utilities/DGraph/CMakeLists.txt \
    CMake/ctkCheckoutRepo.cmake.in \
    CMake/ctkDashboardScript.TEMPLATE.cmake \
    CMake/ctkMacroSetupQt.cmake \
    CMakeLists.txt \
    Libs/Core/CMake/TestBFD/CMakeLists.txt
do
    if [ -f "${f}" ]; then
        sed -i 's/cmake_minimum_required(VERSION.*)/cmake_minimum_required(VERSION 3.16)/' "${f}"
    fi
done

%build
# GCC 15 / Fedora 43+ fixes
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint -fpermissive"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17"

%cmake \
    -GNinja \
    -DCTK_SUPERBUILD=OFF \
    -DCTK_QT_VERSION=6 \
    -DBUILD_TESTING:BOOL=OFF \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCTK_INSTALL_LIB_DIR=%{_libdir} \
    -DCTK_INSTALL_CMAKE_DIR=%{_libdir}/cmake/ctk \
    -DCTK_INSTALL_PLUGIN_DIR=%{_libdir}/ctk/plugins \
    -DCTK_INSTALL_QTPLUGIN_DIR=%{_qt6_plugindir} \
    -DDOCUMENTATION_TARGET_IN_ALL=OFF \
    -DCTK_ENABLE_DICOM=ON \
    -DCTK_ENABLE_Widgets=ON \
    `# Required by MITK: its plugin system (BlueBerry + all org.mitk.* plugins)` \
    `# is built on ctkPluginContext/ctkPluginActivator. Additive for Slicer,` \
    `# which links none of the PluginFramework symbols.` \
    -DCTK_ENABLE_PluginFramework=ON \
    -DCTK_LIB_Visualization/VTK/Widgets=ON \
    `# ctkVTKChartView + transfer-function/volume-property/scalars-to-colors` \
    `# widgets are gated behind this (default OFF). 3D Slicer's qMRMLPlotView` \
    `# and qMRMLVolumePropertyNodeWidget link them, so enable it.` \
    -DCTK_LIB_Visualization/VTK/Widgets_USE_TRANSFER_FUNCTION_CHARTS:BOOL=ON \
    -DCTK_LIB_ImageProcessing/ITK/Core=ON \
    -DCTK_LIB_Scripting/Python/Core=ON \
    -DCTK_LIB_Scripting/Python/Widgets=ON \
    `# Compiles ctkVTKPythonQtWrapperFactory into CTKVisualizationVTKCore` \
    `# (default OFF). 3D Slicer's qSlicerCorePythonManager instantiates it` \
    `# unconditionally, so without this Slicer fails linking` \
    `# libqSlicerBaseQTCore.so with an undefined reference.` \
    -DCTK_LIB_Scripting/Python/Core_PYTHONQT_USE_VTK:BOOL=ON \
    `# CTK's top-level CMakeLists.txt (~line 927) does` \
    `#   set(CTK_WRAP_PYTHONQT_LIGHT ${CTK_ENABLE_Python_Wrapping})` \
    `# which unconditionally overwrites our -DCTK_WRAP_PYTHONQT_LIGHT=ON below` \
    `# with this variable's value (default OFF), silently disabling` \
    `# ctkMacroBuildLibWrapper for every kit (Core/Widgets/DICOM/VTK/ITK/` \
    `# QtTesting). That leaves ctk/__init__.py's templated __kits_to_load` \
    `# empty, so "import ctk" yields a module with zero real classes` \
    `# (ctk.ctkSettingsPanel, ctk.ctkErrorLogContext, ... all missing),` \
    `# breaking 3D Slicer's DICOM, ExtensionWizard, and Segment Editor` \
    `# modules at runtime. Must set this explicitly.` \
    -DCTK_ENABLE_Python_Wrapping=ON \
    -DCTK_WRAP_PYTHONQT_LIGHT=ON \
    -DPYTHONQT_INSTALL_DIR=%{_prefix} \
    -DPythonQt_DIR=%{_libdir}/cmake/PythonQt \
    -DCTK_USE_SYSTEM_VTK=ON \
    -DCTK_USE_SYSTEM_ITK=ON \
    -DCTK_USE_SYSTEM_DCMTK=ON \
    -DCTK_BUILD_QTDESIGNER_PLUGINS=ON \
    -DCTK_USE_QTTESTING=ON \
    -DQtTesting_DIR=%{_libdir}/cmake/qttesting \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4

%cmake_build

%install
%cmake_install

# CTK's own install rules don't pick up the CMake helper templates
# (*.cpp.in / *.py / *.cmake.in inside CMake/). They live in source-tree
# CMAKE_MODULE_PATH for superbuild consumers, but downstream consumers
# like 3D Slicer expect them at ${CTK_CMAKE_DIR}=/usr/lib64/cmake/ctk/.
# Install the ones that Slicer references.
install -p -m 0644 CMake/ctkMacroWrapPythonQtModuleInit.cpp.in \
    %{buildroot}%{_libdir}/cmake/ctk/
install -p -m 0644 CMake/ctkWrapPythonQt.py \
    %{buildroot}%{_libdir}/cmake/ctk/
install -p -m 0644 CMake/ctk_compile_python_scripts.cmake.in \
    %{buildroot}%{_libdir}/cmake/ctk/

# CTK's Config doesn't find_dependency() its link-time deps. When a
# downstream consumer (e.g. 3D Slicer) calls find_package(CTK) without
# having pre-called find_package(DCMTK) and find_package(ITK), the
# CTKExports.cmake step aborts at the generate phase with messages like
# "The link interface of target CTKDICOMCore contains: DCMTK::ofstd
#  but the target was not found." Inject the missing find_dependency
# calls at the top of CTKConfig.cmake.
#
# QtTesting must be here too: CTKQtTesting's interface link names the bare
# target "qttesting". Without find_dependency(QtTesting) that target is
# undefined in the consumer, so CMake degrades it to a plain -lqttesting —
# which links but carries NONE of qttesting's INTERFACE_INCLUDE_DIRECTORIES,
# leaving Slicer's qSlicerApplication.cxx unable to find pqTestUtility.h
# (pulled in via the installed ctkQtTestingUtility.h header).
sed -i '0,/^include/{s|^include|include(CMakeFindDependencyMacro)\nfind_dependency(DCMTK)\nfind_dependency(ITK 5.4)\nfind_dependency(QtTesting)\n\ninclude|}' \
    %{buildroot}%{_libdir}/cmake/ctk/CTKConfig.cmake

# 3D Slicer bug #9a: CTK installs the PythonQt stub modules "qt" and "ctk"
# under %{_bindir}/Python (upstream PYTHONQT_INSTALL_DIR layout), which is NOT
# on any default Python module path. Slicer's embedded interpreter therefore
# cannot "import qt"/"import ctk", breaking every scripted module. Slicer's
# interpreter DOES scan the system site-packages (numpy/SimpleITK load from
# there), so expose the stubs by symlinking them into %{python3_sitelib}.
# Symlink (rather than move) so the build-time layout that find_package(CTK)
# and Slicer's configure step expect stays untouched. The stubs are guarded
# against import outside a running Qt app, so they're inert in a plain python3.
install -d %{buildroot}%{python3_sitelib}
ln -s %{_bindir}/Python/qt  %{buildroot}%{python3_sitelib}/qt
ln -s %{_bindir}/Python/ctk %{buildroot}%{python3_sitelib}/ctk

# Same bug #9a problem, one level deeper: ctk/__init__.py loads each wrapped
# kit with a plain Python-level "from CTK<Kit>PythonQt import *", but those
# CTK*PythonQt.so extension modules are installed to CTK_INSTALL_LIB_DIR
# (%{_libdir} here) — not on sys.path (bare /usr/lib64 never is, only its
# python3.14/site-packages subdirectory is). Every kit import therefore
# raises ImportError, silently swallowed by ctk/__init__.py's try/except,
# leaving "ctk" a class-less module even though __kits_to_load now correctly
# lists all 11 kits. Symlink each built wrapper module into
# %{python3_sitelib} so Python's import machinery can actually find it.
for kit in Core Widgets DICOMCore DICOMWidgets VisualizationVTKCore \
           VisualizationVTKWidgets ImageProcessingITKCore \
           ScriptingPythonWidgets QtTesting; do
    ln -s %{_libdir}/CTK${kit}PythonQt.so %{buildroot}%{python3_sitelib}/CTK${kit}PythonQt.so
done

%files
%doc README.md
%license NOTICE LICENSE
%{_libdir}/libCTKCore.so.%{soname_version}{,.*}

%files plugin-framework
%{_libdir}/libCTKPluginFramework.so.%{soname_version}{,.*}

%files widgets
%{_libdir}/libCTKWidgets.so.%{soname_version}{,.*}
%{_libdir}/libCTKQtTesting.so.%{soname_version}{,.*}

%files dicom
%{_libdir}/libCTKDICOMCore.so.%{soname_version}{,.*}
%{_libdir}/libCTKDICOMWidgets.so.%{soname_version}{,.*}

%files vtk
%{_libdir}/libCTKVisualizationVTK*.so.%{soname_version}{,.*}

%files itk
%{_libdir}/libCTKImageProcessingITK*.so.%{soname_version}{,.*}

%files python
%{_libdir}/libCTKScriptingPython*.so.%{soname_version}{,.*}
# Per-kit PythonQt wrapper modules (ctkMacroBuildLibWrapper, one per wrapped
# kit: CTKCorePythonQt.so, CTKWidgetsPythonQt.so, CTKDICOMCorePythonQt.so,
# CTKDICOMWidgetsPythonQt.so, CTKVisualizationVTK{Core,Widgets}PythonQt.so,
# CTKImageProcessingITKCorePythonQt.so, CTKQtTestingPythonQt.so, ...). Built
# as MODULE libraries with no "lib" prefix, unversioned. ctk/__init__.py
# imports each of these by bare module name for every kit in
# __kits_to_load — without them present, "import ctk" yields a module
# with zero real classes.
%{_libdir}/CTK*PythonQt.so
# Symlinks onto the default Python path (bug #9a, one level deeper — see
# above): bare %%{_libdir} is never on sys.path, so ctk/__init__.py's plain
# "from CTK<Kit>PythonQt import *" can't find these otherwise.
%{python3_sitelib}/CTK*PythonQt.so
# CTK builds Python stubs under /usr/bin/Python/ (upstream layout — not ideal,
# but moving them breaks find_package(CTK) for Slicer).
/usr/bin/Python/ctk/
/usr/bin/Python/qt/
# Symlinks onto the default Python path so Slicer can import them (bug #9a).
%{python3_sitelib}/qt
%{python3_sitelib}/ctk

%files devel
%{_includedir}/ctk-%{soname_version}/
%{_libdir}/libCTKCore.so
%{_libdir}/libCTKPluginFramework.so
%{_libdir}/libCTKWidgets.so
%{_libdir}/libCTKQtTesting.so
%{_libdir}/libCTKDICOMCore.so
%{_libdir}/libCTKDICOMWidgets.so
%{_libdir}/libCTKVisualizationVTK*.so
%{_libdir}/libCTKImageProcessingITK*.so
%{_libdir}/libCTKScriptingPython*.so
%{_qt6_plugindir}/designer/libCTK*.so
%{_libdir}/cmake/ctk/

%changelog
* Fri Jul 31 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.19.20260126gitfd37b874
- Enable CTK_ENABLE_PluginFramework and ship it as a new ctk-plugin-framework
  subpackage. MITK's plugin system (BlueBerry and every org.mitk.* Workbench
  plugin) is built on ctkPluginContext/ctkPluginActivator -- 160 files under
  MITK's Plugins/ use it -- so MITK_USE_BLUEBERRY=ON, and therefore any MITK
  Workbench package, is impossible without it.
- Additive for 3D Slicer, which links 9 CTK libraries, none of them
  PluginFramework, and whose spec has zero references to it.
- Drop the "Obsoletes: ctk-plugin-framework" from the main package: we now
  provide a package of that name, which supersedes Fedora's 2023.07.13 by
  version on its own.

* Fri Jul 03 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.18.20260126gitfd37b874
- Fix -0.17 turning out to be a no-op on the actual failure: ctk.ctkSettingsPanel
  etc. were still AttributeError after upgrading, verified live in 3D Slicer.
  ctk/__init__.py loads each wrapped kit with a plain Python-level
  "from CTK<Kit>PythonQt import *", but -0.17 only fixed __kits_to_load
  (via CTK_ENABLE_Python_Wrapping) — it left the resulting CTK*PythonQt.so
  modules installed to %{_libdir} (bare /usr/lib64), which is never on
  sys.path (only its python3.14/site-packages subdirectory is). Every kit
  import therefore still raised ImportError, silently swallowed by
  ctk/__init__.py's try/except. Same root shape as bug #9a (-0.15), one
  level deeper: symlink each of the 9 built CTK*PythonQt.so wrapper modules
  into %{python3_sitelib} alongside the existing qt/ctk stub symlinks.

* Thu Jul 02 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.17.20260126gitfd37b874
- Fix "import ctk" yielding a class-less module (ctk.ctkSettingsPanel,
  ctk.ctkErrorLogContext, etc. all AttributeError), breaking 3D Slicer's
  DICOM, ExtensionWizard, and Segment Editor modules at runtime on every
  Slicer version. Root cause: CTK's top-level CMakeLists.txt unconditionally
  overwrites our -DCTK_WRAP_PYTHONQT_LIGHT=ON with
  set(CTK_WRAP_PYTHONQT_LIGHT ${CTK_ENABLE_Python_Wrapping}), and
  CTK_ENABLE_Python_Wrapping defaults OFF and was never set by this spec —
  so ctkMacroBuildLibWrapper never ran for any kit, no CTK*PythonQt.so
  wrapper modules were built, and ctk/__init__.py's templated
  __kits_to_load ended up empty. Add -DCTK_ENABLE_Python_Wrapping=ON and
  package the resulting per-kit CTK*PythonQt.so modules in -python.

* Sun Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.16.20260126gitfd37b874
- Obsolete ctk-plugin-framework < this version. We build with PluginFramework=OFF
  so we ship no ctk-plugin-framework; without the Obsoletes, Fedora's
  ctk-plugin-framework-2023 (Requires ctk = 2023) lingered and blocked the upgrade
  to this ctk on user systems (Conflicts: ctk < 2026) — a dnf-update deadlock.
  Also supersedes the stale 0.14 build that left two ctk versions in the repo.

* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.15.20260126gitfd37b874
- Fix 3D Slicer bug #9a: symlink the qt/ctk PythonQt stub modules from
  %{_bindir}/Python into %{python3_sitelib} so Slicer's embedded interpreter
  (which scans system site-packages) can import them. CTK's upstream
  PYTHONQT_INSTALL_DIR layout drops them under /usr/bin/Python, off every
  default module path, so "import qt"/"import ctk" failed in all scripted
  modules. Symlinked (not moved) to preserve the layout find_package(CTK) and
  Slicer's configure step expect.

* Tue Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.14.20260126gitfd37b874
- Inject find_dependency(QtTesting) into CTKConfig.cmake. CTKQtTesting's
  interface link names the bare target "qttesting"; without the find_dependency
  that target is undefined in downstream consumers and CMake degrades it to a
  plain -lqttesting, dropping qttesting's INTERFACE_INCLUDE_DIRECTORIES. That
  left 3D Slicer unable to find pqTestUtility.h (via the installed
  ctkQtTestingUtility.h header) when compiling qSlicerApplication.cxx. Same
  root cause as the earlier -lqttesting link failure.

* Tue Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.13.20260126gitfd37b874
- Enable CTK_LIB_Scripting/Python/Core_PYTHONQT_USE_VTK so the
  ctkVTKPythonQtWrapperFactory class is compiled into CTKVisualizationVTKCore
  (default OFF). 3D Slicer's qSlicerCorePythonManager instantiates it
  unconditionally; without it the Slicer libqSlicerBaseQTCore.so link fails
  with an undefined reference to ctkVTKPythonQtWrapperFactory::ctkVTKPythonQtWrapperFactory().

* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.12.20260126gitfd37b874
- Enable CTK_LIB_Visualization/VTK/Widgets_USE_TRANSFER_FUNCTION_CHARTS so
  libCTKVisualizationVTKWidgets exports ctkVTKChartView and the volume-property
  / scalars-to-colors widgets. 3D Slicer's qMRMLPlotView links these; without
  them the Slicer qMRMLWidgets link fails with undefined ctkVTKChartView refs.

* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.11.20260126gitfd37b874
- Add 5th cherry-pick (upstream 43225929): convert ctkVTKRenderViewEventTranslator
  QMouseEvent value members to std::optional, since Qt6 made QInputEvent::operator=
  protected. Fixes the -0.10 FTBFS at the CTKVisualizationVTKWidgets compile.

* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.10.20260126gitfd37b874
- Enable CTK_USE_QTTESTING=ON against the new Qt6 qttesting COPR package
  (4 cherry-picks isolate the removed QtXmlPatterns dependency to Qt5 paths
  and detect the lowercase "qttesting" external target name). Builds
  libCTKQtTesting.so, which unblocks the 3D Slicer GUI record/replay tests.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.9.20260126gitfd37b874
- Inject find_dependency(DCMTK) and find_dependency(ITK 5.4) at the
  top of CTKConfig.cmake. CTK's upstream Config doesn't auto-load its
  link-time deps, so find_package(CTK) by downstream consumers
  (e.g. 3D Slicer) aborts at the generate phase with
  "DCMTK::ofstd / ITKInternalEigen3::Eigen ... target was not found."
  CTKConfig even has a comment acknowledging this: "Ideally projects
  like DCMTK or PythonQt should provide both Config and Use files."
  Surfaced by 3dslicer-17.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.8.20260126gitfd37b874
- Explicitly install CMake/ctkMacroWrapPythonQtModuleInit.cpp.in,
  ctkWrapPythonQt.py, and ctk_compile_python_scripts.cmake.in. CTK
  upstream's CMakeLists has no install() rule for these (they live
  in CMake/ source dir and are accessed via CMAKE_MODULE_PATH in
  superbuild consumers). Downstream consumers like 3D Slicer expect
  them at \${CTK_CMAKE_DIR}=/usr/lib64/cmake/ctk/ — without them
  Slicer's Libs/MRML/Widgets fails at ctkMacroBuildLibWrapper.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.7.20260126gitfd37b874
- Add ctk-python subpackage to ship the new Python/PythonQt-related
  files surfaced by -0.6 (libCTKScriptingPython{Core,Widgets}.so* and
  the /usr/bin/Python/{ctk,qt}/__init__.py stubs that CTK's build
  installs when PythonQt support is on). Also list the unversioned
  .so symlinks under ctk-devel and add a -python dependency.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.6.20260126gitfd37b874
- Re-enable PythonQt support now that python-pythonqt-devel (Qt6) is
  available in COPR. Flip CTK_LIB_Scripting/Python/Core,
  CTK_LIB_Scripting/Python/Widgets, CTK_WRAP_PYTHONQT_LIGHT back to ON.
  3D Slicer's Libs/MRML/Widgets calls ctkMacroWrapPythonQt, which
  configures ctkMacroWrapPythonQtModuleInit.cpp.in — a file CTK only
  installs when its own PythonQt support is enabled. Without it, the
  Slicer configure aborts at qMRMLWidgetsPythonQt wrapping.

* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.4.20260126gitfd37b874
- Fix build: add qt6-qtscxml-devel (provides Qt6::StateMachine for CTKCore)
- Add qt6-qttools-static (Qt6::UiTools)
- Add -fpermissive to CXXFLAGS for GCC 15 compatibility
- Disable CTK_USE_QTTESTING (requires XmlPatterns, removed in Qt6)
- Disable CTK_WRAP_PYTHONQT_LIGHT explicitly
- Remove python subpackage (PythonQt not rebuilt for Qt6 yet)

* Mon Mar 09 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.3.20260126gitfd37b874
- Add qt6-qtshadertools-devel for VTK transitive deps

* Fri Mar 06 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.2.20260126gitfd37b874
- Switch to Qt6 (COPR VTK 9.5 is Qt6-based, cannot mix with Qt5)

* Thu Mar 05 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.1.20260126gitfd37b874
- Full CTK build for 3D Slicer (git snapshot from master)
- Enable VTK visualization, ITK image processing
- Enable DICOM support, disable PluginFramework (not needed by Slicer)
- Based on Slicer's pinned CTK commit fd37b874
- Uses Qt6, system VTK 9.5, ITK 5.4
