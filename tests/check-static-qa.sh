#!/usr/bin/env bash
# check-static-qa.sh — static QA checks against installed neurofedora packages.
#
# Three modes:
#   --rpmlint    Run rpmlint on every installed COPR package, emit per-package
#                error counts. Used by static-qa.bats to detect regressions vs
#                a per-machine baseline.
#   --ldd        Scan every shipped ELF binary in installed COPR packages for
#                'not found' library deps. Catches the exact bug class that
#                produced afni libmrix.so unfindable, vmtk vtkvmtk missing,
#                without needing per-package test rows.
#   --providers  Verify every Requires of every installed COPR package can be
#                resolved by the currently-enabled repos. Catches "I added a
#                Requires but its provider isn't in COPR yet".
#
# All three modes share a "packages to scan" definition: the intersection of
# packages.tsv (the manifest of every COPR package the harness tracks) and
# `rpm -qa` (what's actually installed). That way the static checks scale
# with the rest of the harness automatically.
#
# Output is TSV to stdout, one row per package:
#   pkg\tcount
# where count is errors / not-found-deps / unresolved-Requires depending on
# mode. Detail logs (full rpmlint / ldd output) go to $OUTDIR if set.
#
# Exit code is 0 if the scan ran cleanly (regardless of error counts) —
# the bats layer interprets the counts against a baseline.

set -euo pipefail

HERE="$(dirname "$(readlink -f "$0")")"
MODE="${1:-}"
OUTDIR="${OUTDIR:-${HERE}/.static-qa-logs}"
mkdir -p "$OUTDIR"

# ── Build the "packages to scan" list ─────────────────────────────────────
# packages.tsv is the manifest of every package this harness tracks. First
# column is the package name (skip blank lines and # comments).
PKGS_WANT="$OUTDIR/pkgs.want"
PKGS_INSTALLED="$OUTDIR/pkgs.installed"
PKGS_SCAN="$OUTDIR/pkgs.scan"

awk -F'\t' '!/^#/ && NF >= 1 && $1 != "" {print $1}' "$HERE/packages.tsv" \
    | sort -u > "$PKGS_WANT"
rpm -qa --queryformat '%{NAME}\n' | sort -u > "$PKGS_INSTALLED"
comm -12 "$PKGS_WANT" "$PKGS_INSTALLED" > "$PKGS_SCAN"

n=$(wc -l < "$PKGS_SCAN")
[[ "$n" -eq 0 ]] && {
    echo "no neurofedora packages installed (intersection of packages.tsv and rpm -qa is empty)" >&2
    exit 0
}

case "$MODE" in

# ── Mode 1: rpmlint ───────────────────────────────────────────────────────
--rpmlint)
    command -v rpmlint >/dev/null || {
        echo "rpmlint not installed" >&2; exit 2;
    }
    # rpmlint takes ~5-15s per package (it unpacks the RPM each time).
    # Run in parallel via xargs -P; otherwise a 60-package scan exceeds
    # 10 minutes. Use a helper function exported to subshells.
    _scan_one() {
        local pkg="$1"
        local log="${OUTDIR}/rpmlint-${pkg}.log"
        # rpmlint 2.x: -i NAME (or --installed NAME) resolves against
        # the installed RPM via rpmdb. Older syntax 'rpmlint NAME' is
        # gone — only file paths work positionally.
        rpmlint -i "$pkg" >"$log" 2>&1 || true
        # Format: 'pkg.arch: E: code message'.  Grep is fine; rpmlint's
        # final summary line ('N packages and 0 specfiles checked; ...')
        # doesn't contain ': E: ' so it won't double-count.
        local errs warns
        errs=$(grep -cE ': E: ' "$log" || true)
        warns=$(grep -cE ': W: ' "$log" || true)
        printf '%s\t%d\t%d\n' "$pkg" "$errs" "$warns"
    }
    export -f _scan_one
    export OUTDIR
    xargs -a "$PKGS_SCAN" -P "$(nproc)" -I{} bash -c '_scan_one "$@"' _ {}
    ;;

# ── Mode 2: ldd on shipped binaries ───────────────────────────────────────
--ldd)
    summary="$OUTDIR/ldd-not-found.log"
    : > "$summary"
    while read -r pkg; do
        # All ELF files shipped by this package
        bins=$(rpm -ql "$pkg" 2>/dev/null \
                | xargs -r file 2>/dev/null \
                | awk -F: '/ELF .* (executable|shared object)/{print $1}')
        count=0
        for bin in $bins; do
            # ldd writes 'not found' to stderr for unresolved deps; the rest
            # of its output is `lib => path`. Just count 'not found' lines.
            nf=$(ldd "$bin" 2>/dev/null | grep -cE 'not found' || true)
            if (( nf > 0 )); then
                count=$((count + nf))
                printf '%s\t%s\t%d\n' "$pkg" "$bin" "$nf" >> "$summary"
            fi
        done
        printf '%s\t%d\n' "$pkg" "$count"
    done < "$PKGS_SCAN"
    ;;

# ── Mode 3: providers ─────────────────────────────────────────────────────
--providers)
    # For each installed COPR package, list its Requires and verify each
    # has a Provides in the currently-enabled repos. dnf repoquery does
    # this in one go via --resolve, but we want per-package attribution
    # so iterate.
    while read -r pkg; do
        log="$OUTDIR/providers-$pkg.log"
        : > "$log"
        # Get the Requires list (filter rpmlib(), built-in soft deps,
        # and meta deps that always resolve)
        reqs=$(rpm -q --requires "$pkg" 2>/dev/null \
                | grep -vE '^(rpmlib\(|/bin/sh|/usr/bin/python3|/usr/bin/env)' \
                | grep -vE '^(config\(|systemd-units)' \
                | sed 's/[[:space:]].*//' | sort -u)
        unresolved=0
        for req in $reqs; do
            # dnf repoquery --whatprovides 'req' returns 1+ providers or
            # empty. Empty = unresolved.
            providers=$(dnf -q repoquery --whatprovides "$req" 2>/dev/null | head -1)
            if [[ -z "$providers" ]]; then
                # Re-check via rpm -q --whatprovides for cases dnf misses
                # (e.g., file deps already installed but not in any repo)
                if ! rpm -q --whatprovides "$req" >/dev/null 2>&1; then
                    unresolved=$((unresolved + 1))
                    printf '%s\n' "$req" >> "$log"
                fi
            fi
        done
        printf '%s\t%d\n' "$pkg" "$unresolved"
    done < "$PKGS_SCAN"
    ;;

*)
    echo "usage: $0 --rpmlint | --ldd | --providers" >&2
    exit 1
    ;;
esac
