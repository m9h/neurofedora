#!/bin/bash
# Install 3D Slicer (+ OpenLIFU + bug#9 scriptability deps) from the
# mhough/neurofedora COPR and probe module discovery, to pin down exactly
# which module classes Slicer can/can't find on a real install.
#
#   sudo bash install-and-probe-slicer.sh
#
# Safe to re-run; it refreshes to the latest COPR builds each time.
set -euo pipefail

echo "=== 1. enable COPR + install ==="
dnf -y copr enable mhough/neurofedora || true
dnf -y --refresh install 3dslicer 3dslicer-openlifu \
    ctk-python python3-vtkAddon || {
  echo "install failed — check the depsolve output above"; exit 1; }

SL=/usr/lib/slicer/Slicer
[ -x "$SL" ] || { echo "ERROR: $SL not found after install"; exit 1; }

echo
echo "=== 2. on-disk module dir inventory ==="
for d in qt-loadable-modules qt-scripted-modules cli-modules; do
  printf '  %-22s %s entries\n' "$d" \
    "$(ls /usr/lib/slicer/lib/Slicer-5.11/$d 2>/dev/null | wc -l)"
done
echo "  bin/ CLI executables (*.xml descriptors): $(ls /usr/lib/slicer/bin/*.xml 2>/dev/null | wc -l)"

echo
echo "=== 3. headless module-discovery probe ==="
cat > /tmp/slicer_modprobe.py <<'PY'
import slicer
fac = slicer.app.moduleManager().factoryManager()
names = list(fac.instantiatedModuleNames()) or list(fac.loadedModuleNames())
allnames = list(fac.registeredModuleNames())
print("registered modules :", len(allnames))
print("instantiated/loaded:", len(names))

# search paths the factory actually used
try:
    print("additionalModulePaths:", list(slicer.app.revisionUserSettings().value("Modules/AdditionalPaths") or []))
except Exception as e:
    print("additionalModulePaths: <err>", e)
for key in ("loadable", "scripted", "cli"):
    pass

# bucket a few known modules per type to see what's missing
probe = {
  "loadable(Volumes)": "Volumes",
  "loadable(Markups)": "Markups",
  "scripted(DICOM)":   "DICOM",
  "scripted(SegmentEditor)": "SegmentEditor",
  "cli(AddScalarVolumes)": "AddScalarVolumes",
}
for label, mod in probe.items():
    print(f"  {label:28s}", "FOUND" if mod in allnames else "MISSING")

olifu = sorted(n for n in allnames if n.lower().startswith("openlifu"))
print("OpenLIFU modules registered:", len(olifu), olifu[:6])

# scriptability (bug #9)
import importlib
for m in ("qt", "ctk", "vtkAddon"):
    try:
        importlib.import_module(m); print(f"  import {m:9s} OK")
    except Exception as e:
        print(f"  import {m:9s} FAIL: {e}")
PY
QT_QPA_PLATFORM=offscreen "$SL" --no-splash --no-main-window \
    --python-script /tmp/slicer_modprobe.py 2>&1 \
  | grep -E 'registered|instantiated|FOUND|MISSING|OpenLIFU|import |AdditionalPaths' || true

echo
echo "Done. Paste the section-3 output back so we can see exactly what's unfindable."
echo "(If CLI modules show MISSING, the cause is the empty cli-modules dir —"
echo " the CLI binaries are in bin/ instead. That's a foundation-spec layout fix.)"
