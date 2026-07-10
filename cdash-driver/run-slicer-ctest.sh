#!/usr/bin/env bash
# run-slicer-ctest.sh — nightly CTest of the *Fedora* Slicer build, to CDash.
#
# Unlike the other cdash-driver components (which build a tiny consumer project
# against an installed -devel RPM), this drives Slicer's OWN upstream CTest
# suite against the EXACT system-libs config we package. It does that by
# building through the spec with the testing bcond flipped on:
#
#     rpmbuild -bc --with testing SPECS/slicer-preview.spec
#
# so the tree under test is byte-for-byte the Fedora build (same %prep patches,
# same ~20 cmake system-lib hints) — just with BUILD_TESTING=ON so the test
# executables compile. Then we run ctest in that build tree and submit to
# my.cdash.org/neurofedora.
#
# GL/render tests need a GL context:
#   * x86_64 legion  -> real RTX 2080 on the live session's DISPLAY=:0
#   * aarch64 hetzner-> no GPU; software GL via `xvfb-run` (mesa llvmpipe)
#
# Usage:
#   ./run-slicer-ctest.sh [Nightly|Experimental]     # default: Nightly
#
# IMPORTANT: the first build is long (~7-9h, tests add a wave on top of the
# ~7h core). This script is intentionally NOT in run-dashboard.sh's auto
# rotation yet — validate one manual run before cron-enabling it.
set -euo pipefail

MODEL="${1:-Nightly}"
case "$MODEL" in Nightly|Experimental) ;; *)
  echo "error: model must be Nightly or Experimental" >&2; exit 2 ;; esac

DRIVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RPMBUILD="${RPMBUILD:-$HOME/rpmbuild}"
ARCH="$(uname -m)"

# Which spec this box owns: explicit override, else preview (5.13) if present,
# else 3dslicer (5.12). SLICER_CTEST_SPEC may be a basename or absolute path.
if [[ -n "${SLICER_CTEST_SPEC:-}" ]]; then
  case "$SLICER_CTEST_SPEC" in
    /*) SPEC="$SLICER_CTEST_SPEC" ;;
    *)  SPEC="$RPMBUILD/SPECS/$SLICER_CTEST_SPEC" ;;
  esac
elif [[ -f "$RPMBUILD/SPECS/slicer-preview.spec" ]]; then
  SPEC="$RPMBUILD/SPECS/slicer-preview.spec"
else
  SPEC="$RPMBUILD/SPECS/3dslicer.spec"
fi
[[ -f "$SPEC" ]] || { echo "error: spec not found: $SPEC" >&2; exit 2; }

# Parallelism: legion is shared (FreeSurfer etc.) so leave headroom; hetzner is
# an 8-core box we own outright. Override with SLICER_CTEST_J.
if [[ -n "${SLICER_CTEST_J:-}" ]]; then
  J="$SLICER_CTEST_J"
else
  # Leave 2 cores free (for interactive use / Claude) — floor at 1.
  J=$(( $(nproc) - 2 )); (( J < 1 )) && J=1
fi

echo "=== Slicer CTest dashboard (spec=$(basename "$SPEC") model=$MODEL arch=$ARCH j=$J) ==="

# 1. Build the Fedora config WITH tests. -bc = %prep + %build (no install/pkg).
#    Not incremental yet (rpmbuild re-preps each run); acceptable for nightly.
echo "--- rpmbuild -bc --with testing ---"
rpmbuild -bc --with testing --define "_smp_mflags -j${J}" "$SPEC"

# 2. Locate the configured build tree (%cmake puts it in redhat-linux-build).
BT="$(find "$RPMBUILD/BUILD" -maxdepth 3 -type d \
        -path '*/Slicer-*/redhat-linux-build' 2>/dev/null \
        | sort | tail -1)"
if [[ -z "$BT" || ! -f "$BT/CTestTestfile.cmake" ]]; then
  echo "error: no configured Slicer build tree with tests found under BUILD/" >&2
  echo "       (expected .../redhat-linux-build/CTestTestfile.cmake)" >&2
  exit 1
fi
echo "--- build tree: $BT ---"

# 3. Point the tree's CTest submission at the neurofedora CDash project.
cp -f "$DRIVER_DIR/CTestConfig.cmake" "$BT/CTestConfig.cmake"

# 4. Run + submit. Prefer REAL hardware GL on the live :0 session (Intel iGPU /
#    NVIDIA), which matches upstream's rendered baselines far better than xvfb's
#    llvmpipe software GL. Fall back to xvfb only if no hardware-GL :0 is reachable.
#
# Submission is opt-out: SLICER_CTEST_SUBMIT=0 runs Start+Test but skips the
# CDash Submit step, so a container / CI / third-party node can validate a build
# locally without publishing to the public my.cdash.org/neurofedora dashboard.
if [[ "${SLICER_CTEST_SUBMIT:-1}" == 0 ]]; then
  echo "--- SLICER_CTEST_SUBMIT=0 — running tests WITHOUT CDash submission ---"
  CTEST_STEPS=(-D "${MODEL}Start" -D "${MODEL}Test")
else
  CTEST_STEPS=(-D "${MODEL}Start" -D "${MODEL}Test" -D "${MODEL}Submit")
fi

# Find the session's X auth cookie (GNOME/Wayland → Xwayland at :0).
_xw="$(ls -1t /run/user/$(id -u)/.mutter-Xwaylandauth.* 2>/dev/null | head -1)"
[[ -z "$_xw" && -f "$HOME/.Xauthority" ]] && _xw="$HOME/.Xauthority"
_hw_gl=0
if [[ -e /tmp/.X11-unix/X0 && -n "$_xw" ]]; then
  # Confirm :0 gives a HARDWARE renderer (not llvmpipe/softpipe) before using it.
  if DISPLAY=:0 XAUTHORITY="$_xw" glxinfo 2>/dev/null | grep -iE "OpenGL renderer" \
       | grep -qivE "llvmpipe|softpipe|swrast"; then
    _hw_gl=1
  fi
fi

if [[ "$_hw_gl" == 1 ]]; then
  _rend="$(DISPLAY=:0 XAUTHORITY="$_xw" glxinfo 2>/dev/null | grep -i 'OpenGL renderer' | sed 's/.*: //')"
  echo "--- hardware GL on :0 ($_rend) ---"
  DISPLAY=:0 XAUTHORITY="$_xw" \
    ctest --test-dir "$BT" "${CTEST_STEPS[@]}" -j "$J" || true
else
  echo "--- no hardware :0 — falling back to xvfb-run (mesa software GL) ---"
  xvfb-run -a -s "-screen 0 1920x1080x24" \
    ctest --test-dir "$BT" "${CTEST_STEPS[@]}" -j "$J" || true
fi

# 5. Archive the per-test output BEFORE the next cycle re-preps and wipes it.
#    Keeps a timestamped history for known-fail triage / baselining.
ARCH="$HOME/.local/state/slicer-ctest/triage"
mkdir -p "$ARCH"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
_lt="$(find "$BT/Testing" -name LastTest.log 2>/dev/null | head -1)"
_lf="$(find "$BT/Testing" -name LastTestsFailed.log 2>/dev/null | head -1)"
[[ -n "$_lt" ]] && cp "$_lt" "$ARCH/LastTest-$ts.log"
[[ -n "$_lf" ]] && cp "$_lf" "$ARCH/LastTestsFailed-$ts.log"
# keep last 10 of each
ls -1t "$ARCH"/LastTest-*.log 2>/dev/null | tail -n +11 | xargs -r rm -f
ls -1t "$ARCH"/LastTestsFailed-*.log 2>/dev/null | tail -n +11 | xargs -r rm -f
echo "--- archived test logs to $ARCH/*-$ts.log ---"

echo "=== Slicer CTest dashboard done — see my.cdash.org/index.php?project=neurofedora ==="
