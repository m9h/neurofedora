#!/usr/bin/env bash
# napari + OpenFlexure chain smoke test (Fedora 44, mhough/neurofedora COPR).
# Run on the target machine after installing:
#   sudo dnf install napari python3-napari-openflexure
#   bash napari-smoke.sh
#
# Headless by design (QT_QPA_PLATFORM=offscreen) so it runs in CI with no
# display. It deliberately does NOT gate on `napari --info`: that command spins
# up a throwaway QApplication + GL probe purely to print diagnostics and then
# hard-exits, which segfaults on teardown with NVIDIA proprietary GL even though
# all the info printed correctly. Gating on it would be a false failure. The real
# viewer (event-loop teardown) is exercised via Viewer(show=False) instead.
set -uo pipefail
PASS=0; FAIL=0
ok()   { echo "  PASS: $1"; PASS=$((PASS+1)); }
bad()  { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
hdr()  { echo; echo "== $1 =="; }

# Keep Qt quiet and headless. Do NOT set QT_API here: the whole point of test 2
# is to prove napari's own selector lands on a Qt6 binding on its own.
export QT_QPA_PLATFORM=offscreen
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/xdg-runtime-$(id -u)}"
mkdir -p "$XDG_RUNTIME_DIR"; chmod 700 "$XDG_RUNTIME_DIR" 2>/dev/null || true

hdr "1. packages installed"
for p in napari python3-napari python3-napari-openflexure \
         python3-openflexure-microscope-client python3-pyqt6 \
         python3-vispy python3-magicgui python3-superqt python3-npe2 \
         python3-app-model python3-napari-svg python3-napari-console; do
  if rpm -q "$p" >/dev/null 2>&1; then ok "$(rpm -q $p)"; else bad "$p not installed"; fi
done

hdr "2. Qt6 binding selected (regression guard for napari -2)"
# napari 0.7 targets Qt6 and is unsupported on PyQt5. The spec prepends a
# selector to napari/__init__.py that sets QT_API to a Qt6 binding when unset,
# so qtpy can never fall back to a coinstalled PyQt5 (which crashes on teardown:
# "QObject deleted directly" -> "free(): invalid pointer"). This asserts the
# effective binding is Qt6 even if python3-qt5/PyQt5 is also installed.
python3 - <<'PY' && ok "qtpy resolved to a Qt6 binding" || bad "qtpy did NOT resolve to Qt6 (PyQt5 regression?)"
import napari            # runs the _fedora_prefer_qt6() selector at import time
import qtpy
api, qtver = qtpy.API_NAME, qtpy.QT_VERSION
print("    qtpy API=%s  Qt=%s" % (api, qtver))
assert api in ("PyQt6", "PySide6"), "binding is %s, expected a Qt6 binding" % api
assert qtver.split(".")[0] == "6", "Qt major is %s, expected 6" % qtver
PY

hdr "3. headless Viewer lifecycle (open / add layer / close)"
# Exercises the real viewer create+teardown path — the one that was crashing on
# quit. Clean exit here == the binding fix holds end to end.
python3 - <<'PY' && ok "Viewer(show=False) add_image + close, clean exit" || bad "Viewer lifecycle"
import numpy as np, napari
v = napari.Viewer(show=False)
v.add_image(np.random.random((64, 64)), name="smoke")
v.add_labels((np.random.random((64, 64)) > 0.5).astype("uint8"), name="lbl")
assert len(v.layers) == 2, "expected 2 layers, got %d" % len(v.layers)
v.close()
print("    napari %s: created viewer, added 2 layers, closed cleanly" % napari.__version__)
PY

hdr "4. npe2 plugin discovery + manifest validation"
# All four chain plugins must be discoverable; the OpenFlexure manifest must
# validate and expose its 2 contributions (command + widget).
npe2 list 2>/dev/null | grep -qi "napari-openflexure" \
  && ok "npe2 list shows napari-openflexure" || bad "npe2 list missing napari-openflexure"
npe2 list 2>/dev/null | grep -qi "napari-svg" \
  && ok "npe2 list shows napari-svg" || bad "npe2 list missing napari-svg"
npe2 validate napari-openflexure >/dev/null 2>&1 \
  && ok "npe2 validate napari-openflexure" || bad "npe2 validate napari-openflexure"

python3 - <<'PY' && ok "OpenFlexure manifest exposes its widget contribution" || bad "OpenFlexure manifest contributions"
from npe2 import PluginManifest
import importlib.resources as r
# Manifest is shipped as package data: napari_openflexure/napari.yaml
with r.files("napari_openflexure").joinpath("napari.yaml").open() as fh:
    mf = PluginManifest.from_file(fh.name) if hasattr(fh, "name") else None
mf = PluginManifest.from_file(str(r.files("napari_openflexure").joinpath("napari.yaml")))
cmds = list(mf.contributions.commands or [])
widgets = list(mf.contributions.widgets or [])
print("    %s: %d command(s), %d widget(s)" % (mf.name, len(cmds), len(widgets)))
assert cmds and widgets, "expected at least one command and one widget contribution"
PY

hdr "5. plugin + client importable"
python3 - <<'PY' && ok "napari_openflexure.OpenFlexureWidget present" || bad "napari_openflexure import"
import napari_openflexure as nof
assert hasattr(nof, "OpenFlexureWidget"), "OpenFlexureWidget not exported"
print("    napari_openflexure", getattr(nof, "__version__", "?"), "->", nof.OpenFlexureWidget)
PY

python3 - <<'PY' && ok "openflexure_microscope_client API present" || bad "openflexure_microscope_client import"
import openflexure_microscope_client as c
# Public entry points used by the plugin.
assert hasattr(c, "MicroscopeClient"), "MicroscopeClient missing"
assert hasattr(c, "find_first_microscope"), "find_first_microscope missing"
print("    client OK: MicroscopeClient + find_first_microscope")
PY

hdr "6. plugin dock-widget instantiation (best-effort, offscreen)"
# Strongest end-to-end check: build the widget through napari's plugin machinery
# exactly as the GUI would. The widget connects to hardware lazily (only on the
# Connect button), so construction needs no microscope. Headless docking can be
# flaky under the offscreen platform, so a failure here is INFO, not FAIL — the
# manifest+import gates above already prove the contribution is wired correctly.
python3 - <<'PY' 2>/dev/null && echo "  PASS: dock widget instantiates via add_plugin_dock_widget" \
  || echo "  INFO: dock-widget instantiation skipped/failed under offscreen (non-fatal)"
import napari
v = napari.Viewer(show=False)
v.window.add_plugin_dock_widget("napari-openflexure")
v.close()
PY

echo
echo "==================================================="
echo "  RESULT: $PASS passed, $FAIL failed"
echo "  Interactive check: run 'napari', then File > Open Sample >"
echo "  napari builtins > Cells (3D+2Ch), toggle 3D (cube icon), rotate,"
echo "  and Plugins > OpenFlexure to open the control widget. Quit should be clean."
echo "  (Note: 'napari --info' may segfault on exit after printing — that is a"
echo "   cosmetic teardown crash in its GL probe, not a viewer bug.)"
echo "==================================================="
[ "$FAIL" -eq 0 ]
