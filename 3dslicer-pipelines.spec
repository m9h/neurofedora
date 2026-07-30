# SlicerPipelines ("Pipelines") — build simple 3D Slicer modules by chaining
# existing ones through a GUI, with no coding. Provides the PipelineCreator
# Python API (`slicerPipeline`, `PipelineProgressCallback`) that other
# extensions' generated modules import: SlicerSkeletalRepresentation's
# SRepCreateAndRefine is a PipelineCreator-generated module and does not load
# without it.
#
# Pure Python: three scripted modules, no compiled code anywhere in the tree.
# EXTENSION_DEPENDS is "NA" — no other Slicer extension is required.
#
# Upstream has no tags; pin the commit.

%global commit      5fbd4a26e36d2c6f49da9af986593a62e053c2a6
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20240423

# Scripted-only extension: nothing is compiled, so the debuginfo machinery finds
# no sources and dies on an empty debugsourcefiles.list.
%global debug_package %{nil}

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.12

Name:           3dslicer-pipelines
Version:        1.0
Release:        0.2.%{snapdate}git%{shortcommit}%{?dist}
Summary:        GUI-built processing pipelines for 3D Slicer (PipelineCreator)

License:        Apache-2.0
URL:            https://github.com/KitwareMedical/SlicerPipelines
Source0:        %{url}/archive/%{commit}/SlicerPipelines-%{shortcommit}.tar.gz

# Scripted-only extension, but the Slicer module-install machinery is CMake and
# the install layout is arch-specific (%%{_lib}), so this is not noarch.
BuildRequires:  cmake >= 3.13.4
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  3dslicer-devel >= 5.12.1

# find_package(Slicer) demands the full Qt6 set even for a scripted-only
# extension.
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
# Its only third-party Python import. Upstream self-installs it with
# slicer.util.pip_install on ImportError; we satisfy it from the distro instead
# (see %%prep).
Requires:       python3-networkx

%description
SlicerPipelines lets you assemble a new 3D Slicer module by chaining existing
modules together in a GUI, with no code: pick a sequence of steps, wire their
inputs and outputs, and the extension generates a working scripted module from
it. It also ships PipelineCaseIterator for running a pipeline in batch over a
directory of cases.

Beyond the GUI it provides the PipelineCreator Python API (the slicerPipeline
decorator and PipelineProgressCallback) that pipeline-generated modules import
at load time, so it is a runtime prerequisite for other extensions that ship
such modules — notably SlicerSkeletalRepresentation's SRepCreateAndRefine.

%prep
%autosetup -n SlicerPipelines-%{commit}

# Distro build: install modules directly rather than as an Extension-Manager
# bundle, so skip SlicerExtensionCPack (it wants an s4ext template the install
# tree does not ship).
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' CMakeLists.txt

# PipelineCreator.py self-heals a missing networkx by calling
# slicer.util.pip_install("networkx") at import. In an RPM that is wrong twice
# over: it needs network at first import, and it would try to write into a
# read-only /usr (it fails outright headless, where PythonSlicer is not on the
# path). networkx is a proper Requires, so let the import speak for itself.
python3 - <<'PYEOF'
p = "PipelineCreator/PipelineCreator.py"
s = open(p, encoding="utf-8").read()
old = (
    "try:\n"
    "    import networkx as nx\n"
    "except ImportError:\n"
    "    import slicer\n"
    "    slicer.util.pip_install(\"networkx\")\n"
    "    import networkx as nx\n"
)
new = "import networkx as nx\n"
assert old in s, "networkx pip_install bootstrap not found (upstream changed?)"
open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
print("replaced the networkx pip_install bootstrap with a plain import")
PYEOF

# PipelineModules imports four wrapping modules at module scope, one of which
# does `from SurfaceToolbox import SurfaceToolboxLogic`. SurfaceToolbox was a
# CORE Slicer scripted module when this commit was made (2024-04-23), but it left
# core in Slicer 5.12 -- the 5.12.1 tarball keeps only its documentation page,
# and the code now lives in the separate SlicerSurfaceToolbox extension. The
# module-scope import therefore takes the whole of PipelineModules down with it.
# The four wrappings are independent (each merely registers @slicerPipeline
# steps), so make this one optional: Segmentations, SegmentEditor and vtk
# wrappings keep working, and only the SurfaceToolbox pipeline steps go missing.
# Packaging SlicerSurfaceToolbox would bring them back.
python3 - <<'PYEOF'
p = "PipelineModules/PipelineModules.py"
s = open(p, encoding="utf-8").read()
old = (
    "from _PipelineModules import (\n"
    "    SegmentationsWrapping,\n"
    "    SegmentEditorWrapping,\n"
    "    SurfaceToolboxWrapping,\n"
    "    vtkWrapping,\n"
    ")\n"
)
new = (
    "from _PipelineModules import (\n"
    "    SegmentationsWrapping,\n"
    "    SegmentEditorWrapping,\n"
    "    vtkWrapping,\n"
    ")\n"
    "\n"
    "# SurfaceToolbox left Slicer core in 5.12 and is now its own extension; its\n"
    "# wrapping is optional so the other three still register.\n"
    "try:\n"
    "    from _PipelineModules import SurfaceToolboxWrapping  # noqa: F401\n"
    "except ImportError:\n"
    "    import logging\n"
    "    logging.info(\n"
    "        'PipelineModules: SurfaceToolbox not available, skipping its pipeline'\n"
    "        ' steps (install the SurfaceToolbox extension to enable them).')\n"
)
assert old in s, "PipelineModules wrapping import block not found (upstream changed?)"
open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
print("made the SurfaceToolbox wrapping import optional")
PYEOF

%build
%cmake -G Ninja \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DTeem_DIR:PATH=%{_libdir}/cmake \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_SKIP_SlicerBlockAdditionalLauncherSettings:BOOL=TRUE \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst}
%cmake_build

%install
%cmake_install
# Catch-all file list (files + symlinks only, so the shared module dirs that
# 3dslicer owns are never claimed).
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/pipelines.files

%files -f %{_builddir}/pipelines.files
%license LICENSE
%doc README.md

%changelog
* Thu Jul 30 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.2.20240423git5fbd4a26
- Make PipelineModules load on Slicer 5.12. It imports four wrapping modules at
  module scope, one of which does 'from SurfaceToolbox import SurfaceToolboxLogic'.
  SurfaceToolbox was a CORE scripted module when this commit was cut (2024-04-23)
  but left core in Slicer 5.12 -- the 5.12.1 tarball retains only its
  documentation page and the code now lives in the separate SlicerSurfaceToolbox
  extension. The module-scope import took all of PipelineModules down with it.
  The four wrappings are independent, so make this one optional: Segmentations,
  SegmentEditor and vtk wrappings still register and only the SurfaceToolbox
  pipeline steps go missing. Packaging SlicerSurfaceToolbox would restore them.
  Caught by the CDash modules-all-instantiated check immediately after -0.1 was
  installed.

* Mon Jul 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20240423git5fbd4a26
- Initial package, pinned to commit 5fbd4a26 (upstream has no tags).
- Packaged to fix SlicerSkeletalRepresentation's SRepCreateAndRefine, a
  PipelineCreator-generated module that fails to instantiate without the
  PipelineCreator Python API.
- Replace the slicer.util.pip_install("networkx") bootstrap with a plain import
  backed by Requires: python3-networkx.
