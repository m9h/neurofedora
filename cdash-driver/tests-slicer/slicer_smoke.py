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

# 4. MRML scene round-trip (offline) ----------------------------------------
scene = slicer.mrmlScene
vol = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "smokeVolume")
check("mrml-add-volume-node", vol is not None and vol.GetID() is not None)

with tempfile.TemporaryDirectory() as td:
    scene_path = os.path.join(td, "smoke.mrml")
    ok = slicer.util.saveScene(scene_path)
    check("mrml-save-scene", ok and os.path.exists(scene_path), scene_path)
    slicer.mrmlScene.Clear(0)
    loaded = slicer.util.loadScene(scene_path)
    check("mrml-reload-scene", bool(loaded))

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

# Verdict --------------------------------------------------------------------
print(f"\nSMOKE SUMMARY: {len(_failures)} failure(s)"
      + (": " + ", ".join(_failures) if _failures else ""), flush=True)
sys.exit(1 if _failures else 0)
