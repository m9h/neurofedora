# Fedora VTK-bump impact analysis (F44)

**Date:** 2026-07-22
**Question:** If bumping VTK in Fedora were required, which packages across the distro depend on VTK?
**Data source:** `dnf repoquery` against `fedora` + `updates` (binary) and `fedora-source` + `updates-source` (SRPM BuildRequires), F44/x86_64. COPR repo excluded.

## TL;DR
- **3D Slicer does NOT force a Fedora VTK bump.** The neurofedora COPR ships a *parallel* `vtk`/`vtk-mpi` **9.6.2** so Slicer/ParaView build against it without touching Fedora's system VTK (9.5.2). This analysis is for the *hypothetical* where a bump lands in Fedora proper.
- **VTK's Fedora reverse-dep footprint is SMALL** — nothing like boost/Qt. A SONAME/ABI bump directly forces **6 source rebuilds** and breaks **~12–14 runtime binaries** until they rebuild.

## Fedora system VTK
- `vtk-9.5.2-9.fc44` (base) / `vtk-9.5.2-12.fc44` (updates). COPR ships `vtk-9.6.2-11`.
- Subpackages from the `vtk` SRPM: vtk, vtk-devel, vtk-data, vtk-doc, vtk-examples, vtk-java, vtk-qt, vtk-testing, and mpich/openmpi variants (vtk-mpich[-devel/-java/-qt], vtk-openmpi[...]).

## Tier 1 — DIRECT build consumers (BuildRequires vtk-devel) — MUST rebuild on ABI bump
6 leaf SRPMs:
| SRPM | Notes |
|---|---|
| **f3d** | 3D viewer; links VTK directly |
| **InsightToolkit** | Fedora's ITK; builds `InsightToolkit-vtk` bridge module against VTK |
| **opencascade** | CAD kernel; `opencascade-visualization`/`-draw` link VTK |
| **opencv** | only the `opencv-viz` subpackage links VTK |
| **pcl** | Point Cloud Library; core links VTK |
| **paraview** | links system VTK; ships `paraview-devel` (Requires vtk-devel) |

## Tier 2 — DIRECT runtime linkers (break with unsatisfied libvtk*.so.N until rebuilt)
~12–14 binaries (via SONAME provides of vtk / vtk-qt / python3-vtk / mpi variants):
f3d · InsightToolkit-vtk · opencascade-draw · opencascade-visualization · opencv-viz ·
pcl · pcl-tools · python3-mayavi · python3-vascpy · python3-vedo ·
python3-vtk-mpich · python3-vtk-openmpi · (+ vtk's own python3-vtk, java, qt).

## Tier 3 — TRANSITIVE build consumers (only the parts that pull VTK-linking modules)
Second-order rebuilds *if* they consume the VTK-exposing part of a Tier-1 lib:
- via **opencascade-visualization/-devel**: gmsh, kicad, netgen-mesher, prusa-slicer, python-cascadio
- via **InsightToolkit(-vtk)-devel**: alizams, petpvc (through InsightToolkit-devel)
- via **paraview-devel**: (no external Fedora build-consumers found)
- via **pcl-devel**: (no additional VTK-specific consumers)

### Important scoping caveat (avoids massive overcount)
`opencv-devel` has a very large reverse-dep list (digikam, kstars, OpenImageIO, gstreamer plugins, monado, …) — **these do NOT touch VTK.** Only `opencv-viz` links VTK, and **nothing external build-depends on opencv-viz** (only opencv's own subpackages). So the opencv reverse-dep tree is VTK-irrelevant and must be excluded from the bump blast radius. Same principle applies to ITK and OpenCASCADE: only their VTK-bridge subpackages matter.

## Bottom line for a Fedora VTK bump
Rebuild order: **VTK → {ITK, opencascade, pcl, opencv(-viz), f3d, paraview}** → then the handful of Tier-3 CAD/medical consumers (gmsh, kicad, netgen-mesher, prusa-slicer, python-cascadio, alizams, petpvc). This is a **tractable ~6 + ~7 package rebuild**, not a mass rebuild. The neurofedora COPR's parallel-VTK strategy sidesteps it entirely for the Slicer/ParaView stack.

*(F44 snapshot; rawhide may differ slightly. Regenerate with the repoquery commands in scratchpad/vtk-deps/.)*
