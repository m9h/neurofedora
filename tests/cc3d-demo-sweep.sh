#!/usr/bin/env bash
# cc3d-demo-sweep.sh — run EVERY example simulation CompuCell3D ships, headless,
# and report which load-and-step cleanly vs which crash or error.
#
# CC3D's run_script.py has no "max steps" flag — the step count lives inside
# each simulation — so the only bounded way to sweep all ~236 demos is a
# per-demo timeout. We run each .cc3d under `cc3d_runScript.sh` with
# QT_QPA_PLATFORM=offscreen and classify the outcome:
#
#   exit 0                        -> PASS     (ran to its own completion)
#   killed by our timeout (137/124) and no error in the log
#                                 -> PASS/RUN (loaded and was stepping when we
#                                              stopped it — healthy)
#   SIGABRT/SIGSEGV (134/139), python error (1), or a Traceback/Assertion
#   /ImportError in the log       -> FAIL     (real crash or error)
#
# Knobs (env vars):
#   CC3D_DEMO_TIMEOUT=20    per-demo wall-clock seconds before we KILL it
#   CC3D_DEMO_LIMIT=0       run only the first N demos (0 = all)
#   CC3D_DEMO_GLOB='*'      only demos whose path matches this glob
#                           (e.g. CC3D_DEMO_GLOB='*MaBoSS*' or '*SBML*')
#   CC3D_DEMO_ROOT=/usr/share/compucell3d/Demos
#
# Exit status: 0 only if zero demos FAILed.

set -uo pipefail

ROOT="${CC3D_DEMO_ROOT:-/usr/share/compucell3d/Demos}"
TIMEOUT="${CC3D_DEMO_TIMEOUT:-20}"
LIMIT="${CC3D_DEMO_LIMIT:-0}"
GLOB="${CC3D_DEMO_GLOB:-*}"

command -v cc3d_runScript.sh >/dev/null 2>&1 \
    || { echo "ERROR: cc3d_runScript.sh not found — install compucell3d first." >&2; exit 2; }
[ -d "$ROOT" ] \
    || { echo "ERROR: demo root $ROOT not found — install compucell3d first." >&2; exit 2; }

# Headless: no Qt display, deterministic numerics, no GPU.
export QT_QPA_PLATFORM=offscreen
export LC_NUMERIC="C.UTF-8"

# Collect demos (sorted, stable order).
mapfile -t DEMOS < <(find "$ROOT" -name '*.cc3d' -path "$GLOB" 2>/dev/null | sort)
TOTAL=${#DEMOS[@]}
(( LIMIT > 0 && LIMIT < TOTAL )) && { DEMOS=("${DEMOS[@]:0:LIMIT}"); }
N=${#DEMOS[@]}

echo "==================================================================="
echo " CompuCell3D demo sweep"
echo "   demo root : $ROOT"
echo "   found     : $TOTAL .cc3d simulations  (running $N this pass)"
echo "   timeout   : ${TIMEOUT}s per demo      glob: $GLOB"
echo "==================================================================="

PASS=0; RUN=0; FAIL=0
FAILED_LIST=()
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
i=0
for demo in "${DEMOS[@]}"; do
    i=$((i+1))
    rel="${demo#$ROOT/}"
    out="$WORK/out"; rm -rf "$out"; mkdir -p "$out"
    log="$WORK/run.log"
    # Background + wait: a synchronous foreground command killed by SIGKILL
    # makes bash print a "Killed" job notice to the terminal. Backgrounding it
    # and waiting suppresses that notice (non-interactive shells don't report
    # signals for waited-on background jobs) while still giving us the status.
    ec=0
    timeout --signal=KILL "$TIMEOUT" \
        cc3d_runScript.sh -i "$demo" -o "$out" -f 0 >"$log" 2>&1 &
    wait "$!" 2>/dev/null || ec=$?

    # A swallowed exception or hard C++ assertion can still exit 0 / be killed,
    # so always scan the log for the tell-tale lines.
    errline=$(grep -m1 -E \
        'Traceback \(most recent call last\)|Assertion .*failed|core dumped|Segmentation fault|ModuleNotFoundError|ImportError|NoMaBoSSExtensionError|AttributeError|CC3D ERROR' \
        "$log" 2>/dev/null || true)

    if [ -n "$errline" ]; then
        verdict="FAIL"; FAIL=$((FAIL+1)); FAILED_LIST+=("$rel :: ${errline:0:160}")
    elif [ "$ec" -eq 0 ]; then
        verdict="PASS"; PASS=$((PASS+1))
    elif [ "$ec" -eq 137 ] || [ "$ec" -eq 124 ]; then
        verdict="RUN "; RUN=$((RUN+1))           # alive at timeout = healthy
    else
        verdict="FAIL"; FAIL=$((FAIL+1))
        last=$(tail -1 "$log" 2>/dev/null)
        FAILED_LIST+=("$rel :: exit $ec :: ${last:0:140}")
    fi
    printf '[%3d/%-3d] %-5s %s\n' "$i" "$N" "$verdict" "$rel"
done

echo "==================================================================="
echo "  PASS (ran to completion) : $PASS"
echo "  RUN  (stepping at ${TIMEOUT}s cutoff): $RUN"
echo "  FAIL (crash / error)     : $FAIL"
echo "  TOTAL run                : $N / $TOTAL"
echo "==================================================================="
if (( FAIL > 0 )); then
    echo "Failures:"
    printf '  - %s\n' "${FAILED_LIST[@]}"
    echo "==================================================================="
fi
# Healthy = PASS + RUN; only crashes/errors count against us.
[ "$FAIL" -eq 0 ]
