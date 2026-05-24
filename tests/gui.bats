#!/usr/bin/env bats
# gui.bats — headless startup smoke for GUI apps listed in gui-binaries.tsv.
#
# Each test launches the binary, keeps it alive for a few seconds, then
# terminates it. A test FAILS only if the process crashed (non-zero exit)
# before the timeout. Tests that can't run (binary missing, xvfb-run
# missing) are SKIPPED, not failed, so a partial install is still useful.

bats_require_minimum_version 1.5.0

HERE="$(dirname "${BATS_TEST_FILENAME}")"
MANIFEST="${HERE}/gui-binaries.tsv"

setup_file() {
    export NEUROFEDORA_TESTS=1
    export NEUROFEDORA_TESTS_LOGDIR="${NEUROFEDORA_TESTS_LOGDIR:-/tmp/neurofedora-gui-smoke}"
}

_require_installed() {
    local pkg="$1"
    rpm -q --quiet "$pkg" 2>/dev/null || skip "$pkg not installed"
}

_require_backend() {
    case "$1" in
        offscreen|wayland) : ;;
        xvfb)
            command -v xvfb-run >/dev/null \
                || skip "xvfb-run not installed (dnf install xorg-x11-server-Xvfb)"
            ;;
    esac
}

# Generate one @test per non-comment row. We can't use a loop at file scope
# in bats; instead we read the manifest and emit @tests via a here-doc-like
# trick using `bats_test_function`. The portable, plain-bats idiom is to
# declare each @test explicitly. We use a helper to keep them one-liners
# and source a generated include file with the @tests.
#
# Generated include — regenerated on every run from gui-binaries.tsv so the
# manifest is the single source of truth.

_generated="${BATS_FILE_TMPDIR:-/tmp}/gui.generated.bash"

setup_suite_unsupported() { :; }  # placeholder; bats has no setup_suite hook

# Emit the @tests at parse time. bats sources this file once; the lines
# below run before any @test is collected, so the dynamic @tests we
# generate via `eval` here are registered correctly.
_emit_tests() {
    [[ -f "$MANIFEST" ]] || return 0
    while IFS=$'\t' read -r pkg binary backend timeout extra; do
        [[ -z "$pkg" || "$pkg" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$binary" ]] && continue
        timeout="${timeout:-5}"
        # Define a @test function dynamically.
        local fn="test_gui_${pkg//[^a-zA-Z0-9_]/_}"
        eval "
        function $fn() {
            _require_installed '$pkg'
            _require_backend '$backend'
            run --separate-stderr \"\$HERE/gui-smoke.sh\" '$pkg' '$binary' '$backend' '$timeout' $extra
            if [ \"\$status\" -ne 0 ]; then
                echo \"gui-smoke failed for $pkg — see \$NEUROFEDORA_TESTS_LOGDIR/$pkg.log\"
                echo \"stdout: \$output\"
                echo \"stderr: \$stderr\"
                false
            fi
        }
        bats_test_function --description '$pkg ($backend, ${timeout}s): startup smoke' -- $fn
        "
    done < "$MANIFEST"
}
_emit_tests
