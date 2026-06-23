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
%global slicer_subdir Slicer-5.11

Name:           3dslicer-srep
Version:        1.0
Release:        0.4.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Skeletal representation (s-rep) shape modeling for 3D Slicer (SlicerSALT)

License:        Apache-2.0
URL:            https://github.com/KitwareMedical/SlicerSkeletalRepresentation
Source0:        %{url}/archive/%{commit}/SlicerSkeletalRepresentation-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  git-core

BuildRequires:  3dslicer-devel >= 5.11.0~pre.20260517git208adb86-54

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

# Qt6 deleted the implicit QVariant(const char*) constructor. The SubjectHierarchy
# SRep plugin feeds VTK char* (vtkMRMLNode::GetName()/GetAttribute()) straight into
# a QMap<int,QVariant> and into QVariant(...).toBool(); under Qt6 that picks the
# deleted ctor and fails to compile. Wrap each char* in QString::fromUtf8 so it
# binds QVariant(const QString&) instead — exactly what Slicer's own SubjectHierarchy
# plugins do under Qt6. Behaviour is preserved (QVariant(QString("1")).toBool()==true,
# and fromUtf8(nullptr) yields an empty QString). A real Qt6 source port, not a
# packaging workaround. Asserts each pattern is present so an upstream change fails
# loudly instead of silently leaving a deleted-ctor call.
python3 - <<'PYEOF'
f = "SRep/SubjectHierarchyPlugins/qSlicerSubjectHierarchySRepPlugin.cxx"
s = open(f).read()
repls = [
 ("terminologyMetaData[qSlicerTerminologyItemDelegate::NameRole] = srepNode->GetName();",
  "terminologyMetaData[qSlicerTerminologyItemDelegate::NameRole] = QString::fromUtf8(srepNode->GetName());"),
 ("srepNode->GetAttribute(vtkSegment::GetTerminologyEntryTagName());",
  "QString::fromUtf8(srepNode->GetAttribute(vtkSegment::GetTerminologyEntryTagName()));"),
 ("QVariant(srepNode->GetAttribute(vtkSlicerTerminologiesModuleLogic::GetNameAutoGeneratedAttributeName()))",
  "QVariant(QString::fromUtf8(srepNode->GetAttribute(vtkSlicerTerminologiesModuleLogic::GetNameAutoGeneratedAttributeName())))"),
 ("QVariant(srepNode->GetAttribute(vtkSlicerTerminologiesModuleLogic::GetColorAutoGeneratedAttributeName()))",
  "QVariant(QString::fromUtf8(srepNode->GetAttribute(vtkSlicerTerminologiesModuleLogic::GetColorAutoGeneratedAttributeName())))"),
]
for a, b in repls:
    assert s.count(a) >= 1, "Qt6 QVariant patch: pattern not found: " + a[:70]
    s = s.replace(a, b)
open(f, "w").write(s)
print("patched Qt6 QVariant(char*) -> QString::fromUtf8 in", f)
PYEOF

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
