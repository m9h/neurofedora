"""Headless smoke test for a system-packaged 3D Slicer (neurofedora COPR).

Run by CTest via:
    slicer --no-splash --no-main-window --python-script slicer_smoke.py \
           --exit-after-startup

Exits non-zero on the first failed check so CTest marks the test red.
All checks are network-isolated (no SampleData / DVC downloads), matching the
COPR/mock no-network policy and the legion nightly cron.

Mirrors the philosophy of Slicer's own ScriptedLoadableModuleTest self-tests
(the model SlicerOpenLIFU / SlicerOpenLIFU's py_<Module> tests build on): launch
Slicer headless, exercise MRML + a real CLI module, assert, exit.
"""

import sys
import os
import tempfile

import slicer


_failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" :: {detail}" if detail else ""), flush=True)
    if not condition:
        _failures.append(label)


# 1. Application identity ----------------------------------------------------
ver = slicer.app.applicationVersion
rev = slicer.app.repositoryRevision
check("application-version-nonempty", bool(ver), ver)
check("repository-revision-nonempty", bool(rev), rev)

# 2. Bundled toolkit versions (VTK / ITK reachable from Slicer's Python) ------
try:
    import vtk
    vtk_ver = vtk.vtkVersion.GetVTKVersion()
    check("vtk-importable", True, vtk_ver)
except Exception as exc:  # noqa: BLE001
    check("vtk-importable", False, repr(exc))

try:
    import itk  # Slicer ships its own ITK Python; tolerate absence
    check("itk-importable", True, getattr(itk, "Version", lambda: "?"))
except Exception as exc:  # noqa: BLE001
    # ITK Python is optional in a Qt-only Slicer build; report, don't fail hard
    print(f"[INFO] itk-importable skipped :: {exc!r}", flush=True)

# 3. Loadable modules registered --------------------------------------------
module_names = list(slicer.app.moduleManager().modulesNames())
check("loadable-modules-present", len(module_names) > 0, f"{len(module_names)} modules")
for expected in ("Volumes", "Models", "Data"):
    check(f"core-module-{expected}", expected in module_names)

# 3b. Modules that were DISCOVERED but failed to instantiate ------------------
#     A scripted module that raises on import is found by the factory, logged to
#     stderr as "The following modules failed to be instantiated", and then
#     silently dropped. The extension-group check in section 6 does not catch it
#     when a sibling module in the same extension registered fine, so a broken
#     module can ship unnoticed (this is how three of them did). The factory
#     manager tracks both sets, so the difference is the exact failure list.
try:
    _fm = slicer.app.moduleManager().factoryManager()
    _registered = set(_fm.registeredModuleNames())
    _instantiated = set(_fm.instantiatedModuleNames())
    # modulesToIgnore is a property (a tuple), not a method -- deliberately
    # skipped modules are not failures.
    _ignored = set(getattr(_fm, "modulesToIgnore", ()) or ())
    _failed = sorted(_registered - _instantiated - _ignored)
    check("modules-all-instantiated", not _failed,
          ", ".join(_failed) if _failed
          else f"{len(_instantiated)}/{len(_registered)} instantiated")
except Exception as exc:  # noqa: BLE001
    check("modules-all-instantiated", False, repr(exc))

# 4. MRML scene round-trip (offline) ----------------------------------------
scene = slicer.mrmlScene
vol = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "smokeVolume")
check("mrml-add-volume-node", vol is not None and vol.GetID() is not None)

with tempfile.TemporaryDirectory() as td:
    scene_path = os.path.join(td, "smoke.mrml")
    ok = slicer.util.saveScene(scene_path)
    check("mrml-save-scene", ok and os.path.exists(scene_path), scene_path)
    slicer.mrmlScene.Clear(0)
    # bool(loadScene(...)) is NOT a success test. loadScene delegates to
    # loadNodeFromFile, which returns the first entry of the loaded-nodes
    # collection -- and a SceneFile load never populates that collection (nodes
    # go straight into the scene), so it returns None on SUCCESS too. Failure is
    # signalled by RuntimeError instead. Assert on the observable effect: no
    # exception, and the node we saved is back in the scene.
    try:
        slicer.util.loadScene(scene_path)
        recovered = slicer.mrmlScene.GetFirstNodeByName("smokeVolume") is not None
        detail = f"{slicer.mrmlScene.GetNumberOfNodes()} nodes"
    except Exception as exc:  # noqa: BLE001
        recovered, detail = False, repr(exc)
    check("mrml-reload-scene", recovered, detail)

# 5. Real CLI-module execution via SlicerExecutionModel (offline) -----------
#    Exercises a packaged CLI plugin end to end on synthetic data — the kind of
#    integration an extension like SlicerOpenLIFU relies on.
try:
    import numpy as np
    a = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "A")
    b = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "B")
    out = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "Sum")
    slicer.util.updateVolumeFromArray(a, np.ones((4, 4, 4), dtype="int16"))
    slicer.util.updateVolumeFromArray(b, np.ones((4, 4, 4), dtype="int16") * 2)
    cli = slicer.modules.addscalarvolumes
    params = {"inputVolume1": a.GetID(), "inputVolume2": b.GetID(),
              "outputVolume": out.GetID()}
    node = slicer.cli.runSync(cli, None, params)
    status = node.GetStatusString()
    result = slicer.util.arrayFromVolume(out)
    check("cli-addscalarvolumes-completed", status == "Completed", status)
    check("cli-addscalarvolumes-result", bool((result == 3).all()),
          f"mean={float(result.mean())}")
except Exception as exc:  # noqa: BLE001
    check("cli-addscalarvolumes", False, repr(exc))

# 6. Packaged-extension module presence (any-of per extension) ---------------
#    SLICER_EXPECT_MODULES is supplied by the CDash driver (run-slicer-ctest.sh)
#    from whichever 3dslicer-<ext> packages are installed: one ';'-separated GROUP
#    per extension, '|'-separated alternative module names within a group. A group
#    FAILS only if NONE of its alternatives registered — catching an extension that
#    built green but installed into a stale Slicer-X.Y path the launcher never
#    scans, or whose scripted module raised on load. Mirrors the BATS
#    slicer_selftest.py check so CDash and the BATS suite agree.
registered = set(module_names)
for group in [g for g in os.environ.get("SLICER_EXPECT_MODULES", "").split(";") if g]:
    alts = [m for m in group.split("|") if m]
    hit = next((m for m in alts if m in registered), None)
    check(f"extension-group-{alts[0]}", hit is not None,
          f"matched {hit}" if hit else f"none of {alts} registered")

# Verdict --------------------------------------------------------------------
print(f"\nSMOKE SUMMARY: {len(_failures)} failure(s)"
      + (": " + ", ".join(_failures) if _failures else ""), flush=True)
sys.exit(1 if _failures else 0)
