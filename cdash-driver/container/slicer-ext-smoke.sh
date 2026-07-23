#!/usr/bin/env bash
# slicer-ext-smoke.sh — per-node 3D Slicer *extension* load-smoke for the farm.
#
# The farm's main job (run-slicer-ctest.sh) BUILDS core Slicer and runs its
# built-in ctest against the build tree — it never validates the packaged
# EXTENSION set. This closes that gap on EVERY farm node: install the COPR Slicer
# + extension packages, launch Slicer headless, and assert each installed
# extension registers at least one of its modules (catches an extension that
# built green but installed into a stale Slicer-X.Y path the launcher never scans,
# or whose scripted module raised on load).
#
# SELF-CONTAINED: the module check is inline, so this runs on a bare container /
# curl|bash node with nothing but the driver script. If the CDash driver files
# (neurofedora-slicer.cmake + tests-slicer/) are ALSO present (legion), it
# additionally submits the richer smoke to my.cdash.org/neurofedora.
#
# Network is required (COPR install) — this runs on the host, OUTSIDE mock.
#   slicer-ext-smoke.sh [Experimental|Nightly]      (default Experimental)
set -uo pipefail

MODEL="${1:-Experimental}"
DRIVER_DIR="$(dirname "$(readlink -f "$0")")"

# Which Slicer track: match whatever the farm builds, else stable.
CORE=3dslicer
case "${SLICER_CTEST_SPEC:-}" in *preview*) CORE=slicer-preview ;; esac

# Canonical package->module map (keep in sync with
# neurofedora/tests/slicer/run-slicer-selftest.sh). '|' = alternatives; a group
# passes if ANY alternative registers.
declare -A MAP=(
    [3dslicer-elastix]="Elastix"
    [3dslicer-totalsegmentator]="TotalSegmentator"
    [3dslicer-monailabel]="MONAILabelReviewer|MONAILabel"
    [3dslicer-openlifu]="OpenLIFUHome|OpenLIFUData"
    [3dslicer-spharm-pdm]="ShapeAnalysisModule|SPHARM-PDM"
    [3dslicer-srep]="SRep|SRepCreator"
    [3dslicer-openigtlink]="OpenIGTLinkIF|OpenIGTLinkRemote"
    [3dslicer-dmri]="TractographyDisplay|DWIToDTIEstimation"
    [3dslicer-igt]="FiducialRegistrationWizard|Watchdog|PivotCalibration|VolumeResliceDriver|BreachWarning"
    [3dslicer-rt]="DicomRtImportExport|DoseVolumeHistogram"
    [3dslicer-jupyter]="JupyterKernel"
)

echo "==> ext-smoke: ensuring COPR + installing $CORE + available extensions" >&2
sudo dnf -y copr enable mhough/neurofedora 2>/dev/null || true
inst=("$CORE")
for e in "${!MAP[@]}"; do
    dnf -q info "$e" >/dev/null 2>&1 && inst+=("$e")
done
echo "==> installing: ${inst[*]}" >&2
sudo dnf -y install "${inst[@]}" || { echo "ext-smoke: install failed" >&2; exit 1; }

# Expected-module groups for whatever actually installed.
expect=""
for r in "${!MAP[@]}"; do
    rpm -q --quiet "$r" 2>/dev/null || continue
    expect+="${expect:+;}${MAP[$r]}"
done
export SLICER_EXPECT_MODULES="$expect"
echo "==> ext-smoke expecting: ${expect:-<none installed>}" >&2

LAUNCHER="$(command -v Slicer || true)"
[[ -z "$LAUNCHER" ]] && { echo "ext-smoke: Slicer launcher not found after install" >&2; exit 1; }

# Inline, self-contained headless check (no external smoke files needed).
tmp_py="$(mktemp --suffix=.py)"
trap 'rm -f "$tmp_py"' EXIT
cat > "$tmp_py" <<'PYEOF'
import os, sys, slicer
reg = set(slicer.app.moduleManager().modulesNames())
fails = []
def chk(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""), flush=True)
    if not ok: fails.append(label)
chk("loadable-modules-present", len(reg) > 0, f"{len(reg)} modules")
for core in ("Data", "Volumes", "Models"):
    chk(f"core-module-{core}", core in reg)
for group in [g for g in os.environ.get("SLICER_EXPECT_MODULES", "").split(";") if g]:
    alts = [m for m in group.split("|") if m]
    hit = next((m for m in alts if m in reg), None)
    chk(f"extension-group-{alts[0]}", hit is not None,
        f"matched {hit}" if hit else f"none of {alts} registered")
print(f"\n[SLICER-EXT-SMOKE] {'FAIL' if fails else 'PASS'} ({len(fails)} failure(s))"
      + (": " + ", ".join(fails) if fails else ""), flush=True)
sys.exit(1 if fails else 0)
PYEOF

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
timeout "${SLICER_SELFTEST_TIMEOUT:-300}" "$LAUNCHER" \
    --no-splash --no-main-window --ignore-slicerrc \
    --python-script "$tmp_py" --exit-after-startup
rc=$?

# Bonus: if the full CDash smoke driver is present (legion), submit the richer
# extension-aware smoke to my.cdash.org/neurofedora too.
if [[ -f "$DRIVER_DIR/neurofedora-slicer.cmake" && -d "$DRIVER_DIR/tests-slicer" ]]; then
    echo "==> ext-smoke: submitting CDash extension smoke" >&2
    ctest -V -S "$DRIVER_DIR/neurofedora-slicer.cmake" \
          -DDASHBOARD_MODEL="$MODEL" -DPARALLEL="${SLICER_CTEST_J:-4}" || true
fi

exit "$rc"
