#!/usr/bin/env bash
# gui-smoke.sh — start a GUI app under a headless display, keep it alive
# for N seconds, terminate it, report whether it died first.
#
# Used by gui.bats. Can be run standalone for debugging:
#   ./gui-smoke.sh itksnap /usr/bin/itksnap offscreen 5
#
# Exit codes:
#   0  app stayed alive for the full timeout OR exited cleanly
#   1  app exited with a non-zero status before the timeout (crash)
#   2  binary missing / required headless tooling missing
#
# Output: writes the captured stdout/stderr to a per-app log under
#         ${NEUROFEDORA_TESTS_LOGDIR:-/tmp/neurofedora-gui-smoke}/<pkg>.log
#         and echoes the log path on stderr so callers can include it in
#         failure messages.

set -uo pipefail

pkg="${1:?pkg required}"
binary="${2:?binary required}"
backend="${3:-offscreen}"
timeout_s="${4:-5}"
shift 4 || true
extra_args=("$@")

LOGDIR="${NEUROFEDORA_TESTS_LOGDIR:-/tmp/neurofedora-gui-smoke}"
mkdir -p "$LOGDIR"
log="$LOGDIR/${pkg}.log"

if [[ ! -x "$binary" ]]; then
    echo "gui-smoke: $binary not executable or missing" >&2
    exit 2
fi

# Need a writable XDG_RUNTIME_DIR or Qt prints noisy warnings. Don't share
# the user's session bus — we want a clean process tree.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/xdg-runtime-$(id -u)}"
mkdir -p "$XDG_RUNTIME_DIR"; chmod 700 "$XDG_RUNTIME_DIR"
unset DBUS_SESSION_BUS_ADDRESS

# Some Qt apps insist on a font dir; the default Fedora one is fine.
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"

case "$backend" in
    offscreen)
        export QT_QPA_PLATFORM=offscreen
        runner=(env "$binary" "${extra_args[@]}")
        ;;
    wayland)
        export QT_QPA_PLATFORM=wayland
        runner=(env "$binary" "${extra_args[@]}")
        ;;
    xvfb)
        command -v xvfb-run >/dev/null || {
            echo "gui-smoke: xvfb-run not installed (dnf install xorg-x11-server-Xvfb)" >&2
            exit 2
        }
        runner=(xvfb-run -a -s "-screen 0 1280x1024x24" "$binary" "${extra_args[@]}")
        ;;
    *)
        echo "gui-smoke: unknown backend '$backend'" >&2
        exit 2
        ;;
esac

# Launch in background, capture combined output to log, watch for early exit.
"${runner[@]}" >"$log" 2>&1 &
pid=$!

deadline=$(( $(date +%s) + timeout_s ))
status=alive
while (( $(date +%s) < deadline )); do
    if ! kill -0 "$pid" 2>/dev/null; then
        # Process died on its own. Reap it; check exit code.
        wait "$pid"
        rc=$?
        if (( rc == 0 )); then
            status=clean_exit
        else
            status=crashed
            echo "gui-smoke: $pkg exited rc=$rc before timeout — log: $log" >&2
            exit 1
        fi
        break
    fi
    sleep 0.25
done

if [[ "$status" == alive ]]; then
    # Still running after the timeout: success. Send SIGTERM, then SIGKILL
    # if it doesn't go quietly within 2s.
    kill -TERM "$pid" 2>/dev/null || true
    for _ in 1 2 3 4 5 6 7 8; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.25
    done
    kill -KILL "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
fi

echo "gui-smoke: $pkg $status (log: $log)" >&2
exit 0
