# SlicerSkeletalRepresentation (SRep) — skeletal representations (s-reps) for 3D
# Slicer: a discrete medial/skeletal shape model with creation, refinement,
# warping and statistical tooling. Part of SlicerSALT, and a build dependency of
# ShapePopulationViewer's Slicer module (which links vtkSlicerSRepModule{MRML,
# Logic}). C++ loadable module (SRep) + small C++ CLIs + scripted Python modules,
# built NON-superbuild against the system 3dslicer foundation.
#
# Unlike ShapePopulationViewer, SRep has no Qt5/VTK8 hard-gate — it just
# find_package(Slicer) and inherits the foundation's Qt6/VTK9 — and uses no
# Qt5-specific APIs, so it builds against the modern foundation unmodified.
# GTest is only pulled by the (disabled) Testing subdirs.

%global commit      dd362a120d43d2f9872d0e21639acf463816651f
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260601

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.12

Name:           3dslicer-srep
Version:        1.0
Release:        0.8.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Skeletal representation (s-rep) shape modeling for 3D Slicer (SlicerSALT)

License:        Apache-2.0
URL:            https://github.com/KitwareMedical/SlicerSkeletalRepresentation
Source0:        %{url}/archive/%{commit}/SlicerSkeletalRepresentation-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  git-core

BuildRequires:  3dslicer-devel >= 5.12.1

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
# SRepCreateAndRefine is a PipelineCreator-generated module: it imports
# PipelineCreator/Widgets at module scope and decorates its entry point with
# @slicerPipeline, so it cannot load without the Pipelines extension.
Requires:       3dslicer-pipelines
# EvolutionarySRep's declared runtime set (see EvolutionarySRepUtil). Upstream
# pins nlopt==2.7.1, but that is a lockfile-style pin, not a real API bound --
# Fedora ships 2.10.0 and the module only uses the stable opt/optimize API.
Requires:       python3-lapy
Requires:       python3-pyacvd
Requires:       python3-pyvista
Requires:       python3-NLopt

%description
SlicerSkeletalRepresentation brings skeletal representations (s-reps) to 3D
Slicer: a discrete medial shape model and the tooling to create, refine, warp,
and statistically analyze it (including the EvolutionarySRep methods). It is a
SlicerSALT shape-analysis extension and provides the s-rep MRML/logic libraries
that ShapePopulationViewer's Slicer module builds against.

This package provides the SRep loadable module, the s-rep creation/refinement/
warping CLIs, and the scripted s-rep pipeline modules, built non-superbuild
against the system 3D Slicer foundation.

%prep
%autosetup -n SlicerSkeletalRepresentation-%{commit}

# Distro build: install modules directly, not as an Extension-Manager bundle, so
# skip SlicerExtensionCPack (wants README/license + s4ext template the install
# tree doesn't ship).
sed -i '/include(${Slicer_EXTENSION_CPACK})/d' CMakeLists.txt

# VTK's wrap-hierarchy parser (vtkWrapHierarchy) errors with "syntax error" on
# every SRep header that uses VTK wrapping-hint macros (VTK_NEWINSTANCE, and the
# function-like VTK_EXPECTS(...)): they aren't defined in the parser's context
# when SRep builds against the installed foundation, so they read as unexpected
# tokens. They are wrapper-only annotations (ownership / preconditions) — strip
# them from the headers so the parser is happy and the methods stay wrapped.
# Normal compilation is unaffected (the macros expand to nothing anyway).
python3 - <<'PYEOF'
import glob
def strip_expects(s):
    out=[]; i=0; tok='VTK_EXPECTS('
    while True:
        j=s.find(tok, i)
        if j<0: out.append(s[i:]); break
        out.append(s[i:j]); k=j+len(tok); depth=1
        while k<len(s) and depth>0:
            depth += (s[k]=='(') - (s[k]==')'); k+=1
        i=k
    return ''.join(out)
for f in glob.glob('SRep*/**/*.h', recursive=True):
    s=open(f).read()
    s2=strip_expects(s.replace('VTK_NEWINSTANCE ',''))
    if s2!=s:
        open(f,'w').write(s2)
        print("stripped VTK hints from", f)
PYEOF

# (No VTK include / VTK link / Slicer-base-include workarounds: foundation
# -52/-53/-54 bake all of these into the generated imported targets — VTK
# include+lib closure (-52), inter-Slicer + CTK closure (-53), and ITK closure
# (-54). Validated by 3dslicer-dmri building clean against -54.)

# The SRepRefinement and SRepWarper Logic modules use vtkImageMagnitude (VTK's
# ImagingMath module) but their TARGET_LIBRARIES list only ${ITK_LIBRARIES} + the
# SRep libs — upstream relied on the superbuild exposing all of VTK. ImagingMath
# IS in the foundation's Slicer_VTK_COMPONENTS, so VTK::ImagingMath is a valid
# target; declare it explicitly so the module .so links vtkImageMagnitude::New().
# (The foundation's generated imported-target VTK closure is a curated subset that
# happens to omit ImagingMath; broadening it to the full Slicer_VTK_COMPONENTS set
# is the durable fix, tracked separately for the next foundation rev.)
python3 - <<'PYEOF'
for f in ("SRepRefinement/Logic/CMakeLists.txt", "SRepWarper/Logic/CMakeLists.txt"):
    s = open(f).read()
    anchor = "set(${KIT}_TARGET_LIBRARIES\n"
    assert anchor in s, "TARGET_LIBRARIES anchor not found in " + f
    s = s.replace(anchor, anchor + "  VTK::ImagingMath\n", 1)
    open(f, "w").write(s)
    print("added VTK::ImagingMath to", f)
PYEOF

# Slicer 5.12 API change: qSlicerSubjectHierarchyAbstractPlugin's virtual
# set/getDisplayColor now take a strongly-typed qSlicerTerminologyMetadata struct
# (the old QMap<int,QVariant> forms became NON-virtual compatibility overloads). The
# SRep SubjectHierarchy plugin still overrides the QMap virtuals, so under 5.12 the
# compiler rejects them ("marked override, but does not override"). Port both the
# declarations and the bodies to the struct API (has*/getter/set* map 1:1 to the old
# TerminologyRole/NameRole/NameAutoGeneratedRole/ColorAutoGeneratedRole keys).
python3 - <<'PYEOF'
base = "SRep/SubjectHierarchyPlugins/qSlicerSubjectHierarchySRepPlugin"

# --- header: retype the two override signatures ---
h = open(base + ".h").read()
h2 = h.replace(
  "void setDisplayColor(vtkIdType itemID, QColor color, QMap<int, QVariant> terminologyMetaData) override;",
  "void setDisplayColor(vtkIdType itemID, QColor color, const qSlicerTerminologyMetadata& terminologyMetaData) override;")
h2 = h2.replace(
  "QColor getDisplayColor(vtkIdType itemID, QMap<int, QVariant> &terminologyMetaData)const override;",
  "QColor getDisplayColor(vtkIdType itemID, qSlicerTerminologyMetadata& terminologyMetaData)const override;")
assert h2 != h, "srep plugin .h signatures not found (upstream changed?)"
open(base + ".h", "w").write(h2)

# --- impl: retype signatures + port both bodies ---
c = open(base + ".cxx").read()
orig = c
c = c.replace(
  "void qSlicerSubjectHierarchySRepPlugin::setDisplayColor(vtkIdType itemID, QColor color, QMap<int, QVariant> terminologyMetaData)",
  "void qSlicerSubjectHierarchySRepPlugin::setDisplayColor(vtkIdType itemID, QColor color, const qSlicerTerminologyMetadata& terminologyMetaData)")
c = c.replace(
  "QColor qSlicerSubjectHierarchySRepPlugin::getDisplayColor(vtkIdType itemID, QMap<int, QVariant> &terminologyMetaData)const",
  "QColor qSlicerSubjectHierarchySRepPlugin::getDisplayColor(vtkIdType itemID, qSlicerTerminologyMetadata& terminologyMetaData)const")

# setDisplayColor body: contains()/[] reads -> hasX()/getter
set_old = """  if (terminologyMetaData.contains(qSlicerTerminologyItemDelegate::TerminologyRole)) {
    srepNode->SetAttribute(vtkSegment::GetTerminologyEntryTagName(),
      terminologyMetaData[qSlicerTerminologyItemDelegate::TerminologyRole].toString().toUtf8().constData() );
  }
  if (terminologyMetaData.contains(qSlicerTerminologyItemDelegate::NameRole)) {
    srepNode->SetName(
      terminologyMetaData[qSlicerTerminologyItemDelegate::NameRole].toString().toUtf8().constData() );
  }
  if (terminologyMetaData.contains(qSlicerTerminologyItemDelegate::NameAutoGeneratedRole)) {
    srepNode->SetAttribute( vtkSlicerTerminologiesModuleLogic::GetNameAutoGeneratedAttributeName(),
      terminologyMetaData[qSlicerTerminologyItemDelegate::NameAutoGeneratedRole].toString().toUtf8().constData() );
  }
  if (terminologyMetaData.contains(qSlicerTerminologyItemDelegate::ColorAutoGeneratedRole)) {
    srepNode->SetAttribute( vtkSlicerTerminologiesModuleLogic::GetColorAutoGeneratedAttributeName(),
      terminologyMetaData[qSlicerTerminologyItemDelegate::ColorAutoGeneratedRole].toString().toUtf8().constData() );
  }"""
set_new = """  if (terminologyMetaData.hasTerminology()) {
    srepNode->SetAttribute(vtkSegment::GetTerminologyEntryTagName(),
      terminologyMetaData.terminology().toUtf8().constData() );
  }
  if (terminologyMetaData.hasName()) {
    srepNode->SetName(
      terminologyMetaData.name().toUtf8().constData() );
  }
  if (terminologyMetaData.hasNameAutoGenerated()) {
    srepNode->SetAttribute( vtkSlicerTerminologiesModuleLogic::GetNameAutoGeneratedAttributeName(),
      QVariant(terminologyMetaData.nameAutoGenerated()).toString().toUtf8().constData() );
  }
  if (terminologyMetaData.hasColorAutoGenerated()) {
    srepNode->SetAttribute( vtkSlicerTerminologiesModuleLogic::GetColorAutoGeneratedAttributeName(),
      QVariant(terminologyMetaData.colorAutoGenerated()).toString().toUtf8().constData() );
  }"""
assert set_old in c, "srep setDisplayColor body not found (upstream changed?)"
c = c.replace(set_old, set_new)

# getDisplayColor body: [] writes -> setX()
get_old1 = """  terminologyMetaData.clear();
  terminologyMetaData[qSlicerTerminologyItemDelegate::TerminologyRole] =
    srepNode->GetAttribute(vtkSegment::GetTerminologyEntryTagName());
  terminologyMetaData[qSlicerTerminologyItemDelegate::NameRole] = srepNode->GetName();"""
get_new1 = """  terminologyMetaData.clear();
  terminologyMetaData.setTerminology(QString::fromUtf8(srepNode->GetAttribute(vtkSegment::GetTerminologyEntryTagName())));
  terminologyMetaData.setName(QString::fromUtf8(srepNode->GetName()));"""
assert get_old1 in c, "srep getDisplayColor head not found (upstream changed?)"
c = c.replace(get_old1, get_new1)
c = c.replace(
  "  terminologyMetaData[qSlicerTerminologyItemDelegate::NameAutoGeneratedRole] = nameAutoGenerated;",
  "  terminologyMetaData.setNameAutoGenerated(nameAutoGenerated);")
c = c.replace(
  "  terminologyMetaData[qSlicerTerminologyItemDelegate::ColorAutoGeneratedRole] = colorAutoGenerated;",
  "  terminologyMetaData.setColorAutoGenerated(colorAutoGenerated);")

# The auto-generated flags are still read from VTK char* via QVariant(...).toBool().
# Qt6 deleted the implicit QVariant(const char*) ctor, so wrap those two char* in
# QString::fromUtf8 (binds QVariant(const QString&); fromUtf8(nullptr) -> empty QString,
# QVariant(QString("1")).toBool()==true, so behaviour is preserved).
for attr in ("GetNameAutoGeneratedAttributeName", "GetColorAutoGeneratedAttributeName"):
    old = "QVariant(srepNode->GetAttribute(vtkSlicerTerminologiesModuleLogic::%s()))" % attr
    new = "QVariant(QString::fromUtf8(srepNode->GetAttribute(vtkSlicerTerminologiesModuleLogic::%s())))" % attr
    assert old in c, "QVariant(char*) pattern not found: " + attr
    c = c.replace(old, new)
assert c != orig, "srep .cxx unchanged (upstream changed?)"
# The port removed every qSlicerTerminologyItemDelegate::*Role reference, so its
# header (not on the 5.12 install include path anyway) is now a dead include -> drop it.
c = c.replace('#include "qSlicerTerminologyItemDelegate.h"\n', '')
assert "qSlicerTerminologyItemDelegate" not in c, "stray qSlicerTerminologyItemDelegate ref remains"
open(base + ".cxx", "w").write(c)
print("ported SRep SubjectHierarchy plugin to the 5.12 qSlicerTerminologyMetadata API")
PYEOF

# EvolutionarySRepUtil bootstraps its own dependencies at IMPORT time: it calls
# ensure_requirements(), and on ImportError falls through to
# install_requirements() -> slicer.util.pip_install(). In a distro package that
# is wrong on every count -- it wants network during a plain module load, it
# would write into a read-only /usr, and headless it does not even get that far
# (slicer.util.pip_install raises "PythonSlicer executable not found"). The
# RuntimeError escapes the `except ImportError`, so EvolutionarySRep failed to
# instantiate outright and Slicer dropped it.
# The four requirements are now real Requires (lapy, pyacvd, pyvista, NLopt), so
# drop the pip fallback and let a genuinely missing dependency surface as the
# plain ImportError it is.
python3 - <<'PYEOF'
p = "EvolutionarySRep/EvolutionarySRepUtil/__init__.py"
s = open(p, encoding="utf-8").read()

old = (
    "try:\n"
    "    ensure_requirements()\n"
    "except ImportError:\n"
    "    install_requirements()\n"
)
new = (
    "# Fedora packaging: the requirements above are RPM Requires, so there is\n"
    "# nothing to install at import time. A missing one is a packaging bug and\n"
    "# should raise ImportError rather than trigger a network pip install into\n"
    "# a read-only prefix.\n"
    "ensure_requirements()\n"
)
assert old in s, "EvolutionarySRepUtil pip bootstrap not found (upstream changed?)"
s = s.replace(old, new, 1)
assert "install_requirements()" in s, "install_requirements definition unexpectedly gone"
open(p, "w", encoding="utf-8").write(s)
print("removed the EvolutionarySRepUtil pip_install bootstrap")
PYEOF

%build
%cmake -G Ninja \
    -DSkeletalRepresentation_SUPERBUILD:BOOL=OFF \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DTeem_DIR:PATH=%{_libdir}/cmake \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_SKIP_SlicerBlockAdditionalLauncherSettings:BOOL=TRUE \
    -DCMAKE_INSTALL_PREFIX:PATH=%{slicer_inst}
%cmake_build

%install
%cmake_install
# Catch-all file list (files + symlinks only, so the shared module dirs that
# 3dslicer owns are never claimed). Tightened later.
( cd %{buildroot} && find . \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/srep.files

%files -f %{_builddir}/srep.files
%license LICENSE
%doc README.md

%changelog
* Mon Jul 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.8.20260601gitdd362a12
- Make EvolutionarySRep and SRepCreateAndRefine actually load.
  EvolutionarySRepUtil bootstrapped its own dependencies at import time
  (ensure_requirements, falling through to slicer.util.pip_install on
  ImportError). In a distro package that wants network during a plain module
  load and would write into a read-only /usr; headless it never gets that far --
  pip_install raises "PythonSlicer executable not found", and that RuntimeError
  escapes the 'except ImportError', so the module failed to instantiate and
  Slicer dropped it. Drop the pip fallback and declare the four requirements as
  real Requires (python3-lapy, python3-pyacvd, python3-pyvista, python3-NLopt);
  upstream's nlopt==2.7.1 is a lockfile pin, not an API bound.
  SRepCreateAndRefine is a PipelineCreator-generated module (module-scope
  PipelineCreator/Widgets imports plus an @slicerPipeline decorator), so it
  cannot load without the Pipelines extension -- add Requires: 3dslicer-pipelines,
  newly packaged for this. Both caught by the new CDash
  modules-all-instantiated check.

* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.7.20260601gitdd362a12
- Drop now-dead qSlicerTerminologyItemDelegate.h include (all *Role uses removed
  by the 5.12 terminology port; header not on the 5.12 install include path).

* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.6.20260601gitdd362a12
- Port SRep SubjectHierarchy plugin set/getDisplayColor to the Slicer 5.12
  strongly-typed qSlicerTerminologyMetadata API (the QMap<int,QVariant> virtuals
  became non-virtual compat overloads; overrides no longer matched).

* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.5.20260601gitdd362a12
- Retarget from Slicer-5.11 to Slicer-5.12 core (3dslicer 5.12.1); bump
  3dslicer-devel floor to 5.12.1.

* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.4.20260601gitdd362a12
- Link VTK::ImagingMath in the SRepRefinement and SRepWarper Logic modules: they
  use vtkImageMagnitude but only listed ITK + SRep libs in TARGET_LIBRARIES
  (upstream relied on the superbuild's full VTK). ImagingMath is in the foundation's
  Slicer_VTK_COMPONENTS so VTK::ImagingMath is a valid target. (Foundation's curated
  imported-target VTK closure omits ImagingMath; broadening it to the full
  Slicer_VTK_COMPONENTS set is the durable fix, tracked for the next foundation rev.)

* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.3.20260601gitdd362a12
- Qt6 source port: wrap the four VTK char* (GetName()/GetAttribute()) feeds into
  QVariant in qSlicerSubjectHierarchySRepPlugin.cxx with QString::fromUtf8 — Qt6
  deleted the implicit QVariant(const char*) constructor. Confirmed (against -54,
  with the install-tree workarounds removed) that this is the only remaining build
  blocker: the foundation trilogy linkage is sound, leaving just this real Qt6 port.

* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.2.20260601gitdd362a12
- Build against foundation -54 and drop the extension-side install-tree
  workarounds (VTK include_directories, find_package(VTK)+link_libraries closure,
  Slicer base include dirs). The -52/-53/-54 trilogy bakes the VTK + inter-Slicer
  + CTK + ITK closures into the generated imported targets, so the foundation is
  now self-sufficient — validated by 3dslicer-dmri building clean against -54.
  Keep the VTK_NEWINSTANCE / VTK_EXPECTS wrap-hint strip (a real vtkWrapHierarchy
  source fix, not a packaging workaround).

* Fri Jun 19 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260601gitdd362a12
- Initial package. SlicerSkeletalRepresentation (SRep loadable module + s-rep
  creation/refinement/warping CLIs + scripted pipelines) built non-superbuild
  against the system 3dslicer foundation. SlicerSALT shape-analysis extension
  and the s-rep library dependency for ShapePopulationViewer.
