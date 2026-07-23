# Packages to check / test — 2026-07-22

Worklist coming out of this session's builds + the COPR VTK-9.6.2 audit. "Check" =
`dnf install` resolves + pulls COPR VTK 9.6.2 (not Fedora 9.5.x). "Smoke" = launch /
import / run a trivial op headless. The Slicer extension set is already covered on the
farm nodes by `slicer-ext-smoke.sh`; everything else needs a manual pass or a CDash
component.

## Tier A — NEW / REBUILT this session (install + smoke first)

| Package | Build | State | Test |
|---|---|---|---|
| **3dslicer** 5.12.1-5 | 10760587 | ✅ | launch headless; `slicer_selftest.py` (identity, MRML, CLI, 34 CLI modules) |
| 3dslicer-igsio | 10762923 | ✅ | module load |
| 3dslicer-dmri | 10762924 | ✅ | TractographyDisplay / DWIToDTIEstimation loads |
| 3dslicer-elastix | 10762925 | ✅ | Elastix module loads |
| 3dslicer-monailabel | 10762926 | ✅ | MONAILabel loads |
| 3dslicer-openigtlink | 10762927 | ✅ | OpenIGTLinkIF loads |
| 3dslicer-openlifu | 10762928 | ✅ | OpenLIFUHome loads |
| 3dslicer-spharm-pdm | 10762929 | ✅ | ShapeAnalysisModule loads (was regressed — verify!) |
| 3dslicer-totalsegmentator | 10762931 | ✅ | TotalSegmentator loads |
| **3dslicer-igt** 1.0-0.5 | 10763726 | ✅ | FiducialRegistrationWizard/Watchdog/PivotCalibration load |
| **3dslicer-srep** 1.0-0.7 | 10763751 | ✅ | SRep/SRepCreator load (terminology API port — verify color path) |
| **opencascade** 7.9.3-3 | 10765268 | ✅ | `dnf install opencascade-visualization` pulls vtk 9.6.2; DRAWEXE runs |
| **opencv** 5.0.0-1 | 10766113 | ⏳ building | `import cv2; cv2.__version__==5.x`; opencv-viz links vtk 9.6.2 |
| **f3d** 3.5.0-2 | 10766117 | ⏳ building | `f3d --version`; open a mesh headless (pulls vtk 9.6.2 + opencascade) |
| **mitk** 2026.06 | 10738793 | ✅ | lib load / Mitk* .so resolve |

Full-set install test: `dnf install 3dslicer 3dslicer-{igsio,dmri,elastix,monailabel,openigtlink,openlifu,spharm-pdm,totalsegmentator,igt,srep}`
then `run-slicer-selftest.sh` (BATS driver, offline).

## Tier B — VTK-9.6.2 collision check (COPR VTK consumers WITHOUT the explicit pin)

All build against COPR VTK 9.6.2, but only rely on the bare `libvtk*.so.1` soname dep
(Fedora 9.5.2 also satisfies it). Usually fine via version precedence; check each loads
against 9.6.2 without an undefined-symbol ImportError. **Pinned already (skip): compucell3d,
python3-vtk, opencascade-visualization.**

Soft-dep (require vtk but unversioned):
- 3dslicer + extensions (via vtkAddon-devel) — covered by Tier A / farm smoke
- paraview, slicer-preview, vespa-libs, ctk-devel, python3-vtkAddon

Soname-only (~24) — the real audit targets:
- acvd, anima, greedy
- ctk-python, ctk-vtk
- InsightToolkit5-vtk, InsightToolkit6
- itksnap, mitk, tomviz, TTK
- openigtlinkio
- pcl, pcl-tools
- vmtk, python3-vmtk
- shapeworks, python3-shapeworks, SPHARM-PDM
- python3-charm_gems, python3-compucell3d, python3-samseg
- vtkAddon

Quick check per package: `dnf install <pkg>` then, for python ones,
`python3 -c "import <mod>"`; for apps, launch `--version` / trivial run. A silent
`ImportError: undefined symbol` = collision (needs the `Requires: vtk >= 9.6.2` pin +
rebuild). CDash: the existing VTK/ITK/vmtk/ParaView smoke components already exercise
several of these nightly.

## Optional hardening (not a functional gap)
Sweep `Requires: vtk%{?_isa} >= 9.6.2` across the ~35 unpinned specs (mechanical, like the
opencascade/f3d change) so the collision can't bite under versionlock / a future Fedora
9.6.x. ~35 spec bumps + rebuilds — awaiting go-ahead.
