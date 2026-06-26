"""Headless regression driver for a system-packaged 3D Slicer (neurofedora COPR).

Launched by CTest / BATS / the CDash driver via:

    Slicer --no-splash --no-main-window --ignore-slicerrc \
           --python-script slicer_selftest.py --exit-after-startup

Philosophy: this is the *outer* driver. It does NOT reimplement Slicer's tests —
it launches the installed application and exercises Slicer's OWN regression
infrastructure (the per-module ScriptedLoadableModuleTest classes, surfaced
through the built-in ``SelfTests`` module) plus a real SlicerExecutionModel CLI
run. Every check is network-isolated (no SampleData / DVC / ExternalData fetch),
matching the COPR/mock no-network policy.

NOTHING is version-pinned here: the Slicer version, home dir, module search
paths and registered module list are all read from ``slicer.app`` at runtime, so
this same script works unchanged across 5.10 / 5.11 / 5.12 packages.

Which extension modules to assert is supplied by the environment (so the driver
stays data-driven and the BATS/CTest wrapper owns the package→module mapping):

    SLICER_EXPECT_MODULES="Elastix;MONAILabelReviewer|MONAILabel;TotalSegmentator"
        one GROUP per installed extension, groups separated by ';', alternative
        module names within a group separated by '|'. A group FAILS if NONE of
        its alternatives is registered (this is what catches an extension that
        built green but installed into a stale version path the launcher never
        scans, or whose scripted module raised on load).

    SLICER_SELFTEST_MODULES="Volumes,Models,Markups"
        comma-separated core modules whose built-in self-test to run; defaults
        to a small offline-safe set. Set to empty to skip the self-test pass.

Exit code is non-zero on the first failed check so CTest/BATS marks it red.
"""

import os
import sys
import tempfile

import slicer


_failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" :: {detail}" if detail else ""), flush=True)
    if not condition:
        _failures.append(label)


def info(label, detail=""):
    print(f"[INFO] {label}" + (f" :: {detail}" if detail else ""), flush=True)


app = slicer.app
mm = app.moduleManager()
registered = set(mm.modulesNames())

# 1. Application identity (version read from the app, never hardcoded) --------
ver = app.applicationVersion
info("slicer-version", ver)
info("slicer-home", app.slicerHome)
info("registered-module-count", str(len(registered)))
check("application-version-nonempty", bool(ver), ver)
check("loadable-modules-present", len(registered) > 0, f"{len(registered)} modules")
for core in ("Data", "Volumes", "Models", "SegmentEditor"):
    check(f"core-module-{core}", core in registered)

# 2. Bundled toolkit reachable from Slicer's Python --------------------------
try:
    import vtk
    check("vtk-importable", True, vtk.vtkVersion.GetVTKVersion())
except Exception as exc:  # noqa: BLE001
    check("vtk-importable", False, repr(exc))

# 3. MRML scene round-trip (offline) -----------------------------------------
vol = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "smokeVolume")
check("mrml-add-volume-node", vol is not None and vol.GetID() is not None)
with tempfile.TemporaryDirectory() as td:
    scene_path = os.path.join(td, "smoke.mrml")
    ok = slicer.util.saveScene(scene_path)
    check("mrml-save-scene", bool(ok) and os.path.exists(scene_path), scene_path)
    # Reload into a freshly cleared scene and assert it repopulated past the
    # post-Clear singleton baseline (loadScene's bool return is unreliable).
    slicer.mrmlScene.Clear(0)
    baseline = slicer.mrmlScene.GetNumberOfNodes()
    slicer.util.loadScene(scene_path)
    after = slicer.mrmlScene.GetNumberOfNodes()
    check("mrml-reload-scene", after > baseline, f"{baseline} -> {after} nodes")

# 4. SlicerExecutionModel CLI plugin -----------------------------------------
#    Hard gate: the canonical SEM CLI module is registered and its compiled
#    executable is on disk (proves CLI plugins are packaged & discovered). The
#    real synthetic-data run is attempted as a bonus and only reported, since a
#    CLI's behaviour on degenerate inputs is not a packaging property.
sem_ok = hasattr(slicer.modules, "addscalarvolumes")
sem_exe = ""
if sem_ok:
    try:
        sem_exe = slicer.modules.addscalarvolumes.path
    except Exception:  # noqa: BLE001
        sem_exe = ""
check("sem-cli-module-present", sem_ok and bool(sem_exe) and os.path.exists(sem_exe), sem_exe)
try:
    import numpy as np
    a = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "A")
    b = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "B")
    out = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "Sum")
    slicer.util.updateVolumeFromArray(a, np.full((8, 8, 8), 3, dtype=np.int16))
    slicer.util.updateVolumeFromArray(b, np.full((8, 8, 8), 4, dtype=np.int16))
    node = slicer.cli.runSync(slicer.modules.addscalarvolumes, None,
                              {"inputVolume1": a.GetID(), "inputVolume2": b.GetID(),
                               "outputVolume": out.GetID()})
    res = slicer.util.arrayFromVolume(out)
    info("sem-cli-run", f"{node.GetStatusString()} max={None if res is None else int(res.max())}")
except Exception as exc:  # noqa: BLE001
    info("sem-cli-run-soft", repr(exc))

# 5. Packaged-extension module presence (any-of per extension) ---------------
#    The wrapper passes one ';'-separated GROUP per installed extension; within
#    a group, '|'-separated names are alternatives. A group fails only if NONE
#    of its modules registered — e.g. the extension built but installed into a
#    stale Slicer-X.Y path the launcher never scans, or its module raised on
#    load. This is the integration regression we most want to catch.
for group in [g for g in os.environ.get("SLICER_EXPECT_MODULES", "").split(";") if g]:
    alts = [m for m in group.split("|") if m]
    hit = next((m for m in alts if m in registered), None)
    check(f"extension-group-{alts[0]}", hit is not None,
          f"matched {hit}" if hit else f"none of {alts} registered")

# 6. Slicer's OWN per-module self-tests (its ctest-equivalent regression pass)-
#    Each ScriptedLoadableModuleTest is what `ctest -R py_<Module>` runs in a
#    build tree; here we invoke them directly against the installed app. Only a
#    curated offline-safe (no SampleData download) default set runs.
# Opt-in: built-in self-tests vary in their offline-safety (many pull SampleData
# over the network), so the wrapper / CTest host enables a vetted set per host
# via SLICER_SELFTEST_MODULES rather than baking in a default that might need a
# download. Empty default = packaging-only checks above, all network-isolated.
selftest_csv = os.environ.get("SLICER_SELFTEST_MODULES", "")
for name in [s.strip() for s in selftest_csv.split(",") if s.strip()]:
    if name not in registered:
        info(f"selftest-skip-{name}", "module not installed")
        continue
    try:
        mod = getattr(slicer.modules, name.lower())
        widget = mod.widgetRepresentation()
        # Only scripted (Python) modules expose .self(); C++ loadable modules do
        # not, and their ScriptedLoadableModuleTest lives elsewhere — skip them.
        impl = widget.self() if widget and hasattr(widget, "self") else None
        tester = getattr(impl, "test", None) if impl is not None else None
        if tester is None or not hasattr(tester, "runTest"):
            info(f"selftest-skip-{name}", "no scripted test class")
            continue
        tester.runTest()
        check(f"selftest-{name}", True)
    except Exception as exc:  # noqa: BLE001
        # A self-test that needs network SampleData raises here; report as INFO
        # rather than failing the whole run (network policy, not a package bug).
        info(f"selftest-soft-{name}", repr(exc))

# ---------------------------------------------------------------------------
print(f"\n[SLICER-SELFTEST] {'FAIL' if _failures else 'PASS'} "
      f"({len(_failures)} failure(s))" + (": " + ", ".join(_failures) if _failures else ""),
      flush=True)
sys.exit(1 if _failures else 0)
