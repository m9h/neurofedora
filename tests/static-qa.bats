#!/usr/bin/env bats
# static-qa.bats — Phase 2 static QA layer.
#
# Wraps check-static-qa.sh's three modes (--rpmlint, --ldd, --providers)
# and turns each into a regression test against a per-machine baseline.
#
# Why per-machine: different boxes have different COPR + Fedora package
# sets, so a single committed baseline can't be the source of truth.
# First run on a new machine captures its own baseline; subsequent
# runs fail ONLY on regressions (counts that increase vs the baseline).
# Baselines live under tests/baselines/<hostname>/ — gitignored so each
# box owns its own.

bats_require_minimum_version 1.5.0

HERE="$(dirname "${BATS_TEST_FILENAME}")"
BASELINE_BASE="${HERE}/baselines"
HOST="$(uname -n)"
BASELINE="${BASELINE_BASE}/${HOST}"

setup_file() {
    mkdir -p "$BASELINE"
    export HERE BASELINE
}

# _compare_counts <current.tsv> <baseline.tsv> <metric-name>
# Returns 0 if baseline didn't exist (captures it instead), 0 if no
# regressions, 1 if any package's count went UP vs baseline.
# Emits regression diagnostics on >&3 (visible in BATS failure output).
_compare_counts() {
    local current="$1" baseline="$2" metric="$3"

    if [[ ! -f "$baseline" ]]; then
        cp "$current" "$baseline"
        local n total
        n=$(wc -l < "$baseline")
        total=$(awk -F'\t' '{s+=$2} END {print s+0}' "$baseline")
        echo "captured ${metric} baseline for ${HOST}: ${n} packages, ${total} ${metric}" >&3
        echo "  → ${baseline}" >&3
        echo "  re-run to validate against it" >&3
        return 0
    fi

    local regressions="" improvements=""
    while IFS=$'\t' read -r pkg new_count _rest; do
        local old_count
        old_count=$(awk -F'\t' -v p="$pkg" '$1==p{print $2; exit}' "$baseline")
        [[ -z "$old_count" ]] && old_count=0
        if (( new_count > old_count )); then
            regressions+=$'\n'"  + ${pkg}: ${old_count} → ${new_count} ${metric}"
        elif (( new_count < old_count )); then
            improvements+=$'\n'"  - ${pkg}: ${old_count} → ${new_count} ${metric}"
        fi
    done < "$current"

    if [[ -n "$improvements" ]]; then
        echo "${metric} improvements (consider refreshing baseline):${improvements}" >&3
    fi
    if [[ -n "$regressions" ]]; then
        echo "${metric} REGRESSIONS:${regressions}" >&3
        echo "" >&3
        echo "  baseline: ${baseline}" >&3
        echo "  refresh after fixing:  cp ${current} ${baseline}" >&3
        return 1
    fi
    return 0
}

@test "[qa-1] rpmlint: no NEW errors above baseline (per-host)" {
    command -v rpmlint >/dev/null || skip "rpmlint not installed (sudo dnf install rpmlint)"

    local current="${BATS_FILE_TMPDIR}/rpmlint.tsv"
    "$HERE/check-static-qa.sh" --rpmlint > "$current" 2> "${BATS_FILE_TMPDIR}/rpmlint.err"

    if [[ ! -s "$current" ]]; then
        cat "${BATS_FILE_TMPDIR}/rpmlint.err" >&2
        skip "rpmlint produced no rows (no installed COPR packages or scanner error)"
    fi

    # The TSV has 3 columns (pkg, errors, warnings). _compare_counts uses
    # column 2 = errors.
    _compare_counts "$current" "${BASELINE}/rpmlint.tsv" "rpmlint errors"
}

@test "[qa-2] ldd: no shipped binary has 'not found' dependencies" {
    local current="${BATS_FILE_TMPDIR}/ldd.tsv"
    "$HERE/check-static-qa.sh" --ldd > "$current" 2> "${BATS_FILE_TMPDIR}/ldd.err"

    if [[ ! -s "$current" ]]; then
        cat "${BATS_FILE_TMPDIR}/ldd.err" >&2
        skip "ldd scan produced no rows (no installed COPR packages)"
    fi

    # Stronger guarantee than rpmlint: ANY 'not found' is a real bug
    # (the binary will segfault on the missing symbol). Hard fail with
    # 0 baseline — don't tolerate any.
    #
    # Diagnostic shows missing LIBRARIES not binary counts. One broken
    # lib (say libmrix.so) typically affects many binaries in the same
    # package; the user wants "afni is missing libmrix.so", not
    # "afni has 47 broken binaries" without saying why.
    local summary="${HERE}/.static-qa-logs/ldd-missing-libs.tsv"
    local broken
    broken=$(awk -F'\t' '$2>0 {printf "  %-30s missing: %s (%d affected binaries)\n", $1, $3, $2}' "$summary")
    if [[ -n "$broken" ]]; then
        echo "shipped binaries with unresolved shared-library deps:" >&3
        echo "${broken}" >&3
        echo "" >&3
        echo "  per-binary detail:  ${HERE}/.static-qa-logs/ldd-not-found.log" >&3
        echo "  format:             package <TAB> binary <TAB> missing-lib" >&3
        return 1
    fi
}

@test "[qa-3] providers: every Requires of every installed COPR pkg resolves" {
    # Slowest check — one dnf repoquery per Requires. Cache enabled by
    # default; first run is the heaviest. Per-host baseline so existing
    # unresolved deps (e.g., optional features behind weak deps) don't
    # blow up first-run pristine boxes.
    local current="${BATS_FILE_TMPDIR}/providers.tsv"
    if ! "$HERE/check-static-qa.sh" --providers > "$current" 2> "${BATS_FILE_TMPDIR}/providers.err"; then
        cat "${BATS_FILE_TMPDIR}/providers.err" >&2
        skip "providers scan failed (dnf unavailable or repos disabled?)"
    fi

    if [[ ! -s "$current" ]]; then
        skip "providers scan produced no rows"
    fi

    _compare_counts "$current" "${BASELINE}/providers.tsv" "unresolved Requires"
}
