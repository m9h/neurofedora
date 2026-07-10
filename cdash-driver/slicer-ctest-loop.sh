#!/usr/bin/env bash
# slicer-ctest-loop.sh — run the Slicer CTest dashboard continuously (24/7).
#
# Each cycle: build the Fedora config --with testing, run ctest on the local
# Intel iGPU, submit to my.cdash.org/neurofedora. Then a short cooldown and
# repeat, so the box is effectively always producing fresh dashboard results.
#
# Which spec to drive is auto-detected: slicer-preview.spec (5.13) if present,
# else 3dslicer.spec (5.12). Override with SLICER_SPEC=<name>.
#
# Model defaults to Nightly. Cooldown between cycles: SLICER_COOLDOWN (default
# 600s) — long enough to not hammer, short enough to be "always building".
set -uo pipefail

DRIVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${SLICER_MODEL:-Nightly}"
COOLDOWN="${SLICER_COOLDOWN:-600}"
STATE="$HOME/.local/state/slicer-ctest"
mkdir -p "$STATE"

# Pick the spec this box owns.
if [[ -n "${SLICER_SPEC:-}" ]]; then
  SPEC="$SLICER_SPEC"
elif [[ -f "$HOME/rpmbuild/SPECS/slicer-preview.spec" ]]; then
  SPEC="slicer-preview.spec"
else
  SPEC="3dslicer.spec"
fi
export SLICER_DRIVER_SPEC="$SPEC"

echo "[loop] spec=$SPEC model=$MODEL cooldown=${COOLDOWN}s driver=$DRIVER_DIR"

while true; do
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  log="$STATE/cycle-$ts.log"
  echo "[loop] $ts starting cycle -> $log"
  SLICER_CTEST_SPEC="$SPEC" "$DRIVER_DIR/run-slicer-ctest.sh" "$MODEL" >"$log" 2>&1
  rc=$?
  echo "[loop] $ts cycle exit=$rc"
  # keep only the last 20 cycle logs
  ls -1t "$STATE"/cycle-*.log 2>/dev/null | tail -n +21 | xargs -r rm -f
  sleep "$COOLDOWN"
done
