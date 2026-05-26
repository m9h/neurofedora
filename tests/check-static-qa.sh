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
    detail="$OUTDIR/ldd-not-found.log"   # one line per (pkg, bin, libname)
    summary="$OUTDIR/ldd-missing-libs.tsv"  # per-package deduped missing libs
    : > "$detail" "$summary"
    while read -r pkg; do
        # All ELF files shipped by this package
        bins=$(rpm -ql "$pkg" 2>/dev/null \
                | xargs -r file 2>/dev/null \
                | awk -F: '/ELF .* (executable|shared object)/{print $1}')
        # Track BOTH the affected-binary count AND the deduplicated set of
        # missing libraries. One broken lib (say libmrix.so) typically
        # affects many binaries in the same package; the bats layer wants
        # to show "afni is missing libmrix.so", not "afni has 47 broken
        # binaries" without saying why. `local` doesn't work here (case
        # block is at script scope, not function scope) — plain shell
        # vars are fine since OUTDIR is per-invocation.
        count=0
        missing_libs="$OUTDIR/.ldd-tmp-${pkg}.libs"
        : > "$missing_libs"
        for bin in $bins; do
            # ldd output for a missing dep:
            #   libmrix.so.1 => not found
            # awk '/not found/{print $1}' isolates the libname.
            while read -r lib; do
                count=$((count + 1))
                printf '%s\t%s\t%s\n' "$pkg" "$bin" "$lib" >> "$detail"
                printf '%s\n' "$lib" >> "$missing_libs"
            done < <(ldd "$bin" 2>/dev/null | awk '/not found/{print $1}')
        done
        # Per-package unique missing libs (csv) for bats consumption
        unique=$(sort -u "$missing_libs" | paste -sd, -)
        rm -f "$missing_libs"
        printf '%s\t%d\t%s\n' "$pkg" "$count" "$unique" >> "$summary"
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
        # and meta deps that always resolve). `|| true` on each grep
        # because grep returns 1 when nothing matches its INCLUDE pattern
        # — with `set -e` that aborts the script. We're using -v
        # (invert), so grep returning 1 means "every line was filtered
        # out" which IS the legitimate empty case for tiny packages.
        reqs=$(rpm -q --requires "$pkg" 2>/dev/null \
                | { grep -vE '^(rpmlib\(|/bin/sh|/usr/bin/python3|/usr/bin/env)' || true; } \
                | { grep -vE '^(config\(|systemd-units)' || true; } \
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
