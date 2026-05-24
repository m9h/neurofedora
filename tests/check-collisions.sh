#!/usr/bin/env bash
# check-collisions.sh — pairwise file-conflict detector across the
# neurofedora package set.
#
# Two modes:
#
#   --installed (default) — only checks packages currently installed.
#       Fast; reflects what dnf has actually committed to your system.
#       Uses `rpm -ql`.
#
#   --repo                — checks ALL manifest packages against COPR
#       metadata, including ones not installed. Slower (one repoquery
#       per pair) but catches conflicts BEFORE you hit them at install
#       time (the way the itksnap × c3d × greedy bug should have been
#       caught). Uses `dnf repoquery -l`.
#
# Outputs one line per conflict on stdout:
#   CONFLICT  pkgA  pkgB  /usr/bin/foo
# Exit code = number of distinct package pairs with conflicts (0 = clean).
#
# Run after install.sh as part of QA, or directly:
#   ./check-collisions.sh
#   ./check-collisions.sh --repo
#
# Env:
#   NEUROFEDORA_TESTS_MANIFEST    default: ./packages.tsv

set -euo pipefail

HERE="$(dirname "$(readlink -f "$0")")"
MANIFEST="${NEUROFEDORA_TESTS_MANIFEST:-${HERE}/packages.tsv}"
MODE="installed"

while (( $# > 0 )); do
    case "$1" in
        --installed) MODE="installed"; shift ;;
        --repo)      MODE="repo";      shift ;;
        -h|--help)   sed -n '2,28p' "$0" | sed 's/^# \?//'; exit 0 ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -f "$MANIFEST" ]] || { echo "manifest not found: $MANIFEST" >&2; exit 2; }

# Active package list (drop comments + WIP rows, take column 1)
mapfile -t PKGS < <(awk -F'\t' '
    /^[[:space:]]*$/ || /^[[:space:]]*#/ { next }
    NF >= 3 { print $1 }
' "$MANIFEST")

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Step 1: collect a per-package file list, filtered to "real" files that
# matter for conflicts. We deliberately drop:
#   /usr/lib/.build-id/*    — per-package, harmless
#   /usr/share/doc/<pkg>/*  — per-package by name, never collides
#   /usr/share/licenses/*   — same
#   /usr/share/man/*        — only true conflict matters, skip the rest
#   directories             — RPM permits multiple owners
# What's left: binaries, libraries, headers, cmake configs, data files —
# i.e. exactly the surface where collisions break installs.
collect() {
    local pkg="$1"
    local out="$TMP/${pkg}.files"
    case "$MODE" in
        installed)
            rpm -q --quiet "$pkg" 2>/dev/null || { : >"$out"; return; }
            rpm -ql "$pkg" 2>/dev/null \
                | awk '
                    /^\/usr\/lib\/\.build-id\// {next}
                    /^\/usr\/share\/doc\// {next}
                    /^\/usr\/share\/licenses\// {next}
                    /^\/usr\/share\/man\// {next}
                    {print}
                ' | sort -u >"$out"
            # Drop directory entries — they cannot conflict.
            # We can only stat them when MODE=installed; do it here.
            grep -v '/$' "$out" > "$out.tmp"
            while IFS= read -r f; do [[ -d "$f" ]] || echo "$f"; done <"$out.tmp" >"$out"
            rm -f "$out.tmp"
            ;;
        repo)
            # repoquery -l works for not-yet-installed packages; it queries
            # dnf metadata directly. The output mixes files and directories
            # and there's no flag to distinguish them, so we filter out
            # known shared-root directories explicitly. Anything left is
            # almost always a real file (libraries, binaries, headers,
            # cmake config) — exactly what causes install-time conflicts.
            dnf -q repoquery --quiet -l "$pkg" 2>/dev/null \
                | awk '
                    # build-id tree: per-package by design, never a real conflict
                    /^\/usr\/lib\/\.build-id(\/|$)/ {next}
                    # per-package by name
                    /^\/usr\/share\/doc(\/|$)/ {next}
                    /^\/usr\/share\/licenses(\/|$)/ {next}
                    /^\/usr\/share\/man(\/|$)/ {next}
                    # known shared-root directories that all packages co-own
                    $0 == "/usr"  || $0 == "/etc"  {next}
                    $0 == "/usr/bin" || $0 == "/usr/sbin" {next}
                    $0 == "/usr/lib" || $0 == "/usr/lib64" {next}
                    $0 == "/usr/include" {next}
                    $0 == "/usr/share" {next}
                    $0 == "/usr/share/cmake" {next}
                    $0 == "/usr/share/applications" {next}
                    $0 == "/usr/share/pixmaps" {next}
                    $0 == "/usr/share/icons" || $0 == "/usr/share/icons/hicolor" {next}
                    $0 == "/usr/share/metainfo" || $0 == "/usr/share/mime" {next}
                    # Single-component root paths (e.g. SRPM source tarballs
                    # like /c3d-<sha>.tar.gz that repoquery sometimes echoes)
                    # — never a real install conflict.
                    /^\/[^\/]+$/ {next}
                    /\/$/ {next}
                    {print}
                ' | sort -u >"$out"
            ;;
    esac
}

# Pre-collect once per package (O(N), much faster than O(N²) rpm calls)
echo "[check-collisions] mode=$MODE  packages=${#PKGS[@]}" >&2
for p in "${PKGS[@]}"; do collect "$p"; done

# Pairwise check: comm -12 produces lines present in BOTH file lists.
CONFLICTS=0
for ((i=0; i<${#PKGS[@]}; i++)); do
    a="${PKGS[$i]}"
    [[ -s "$TMP/${a}.files" ]] || continue
    for ((j=i+1; j<${#PKGS[@]}; j++)); do
        b="${PKGS[$j]}"
        [[ -s "$TMP/${b}.files" ]] || continue
        # Get shared paths
        shared=$(comm -12 "$TMP/${a}.files" "$TMP/${b}.files")
        if [[ -n "$shared" ]]; then
            CONFLICTS=$((CONFLICTS + 1))
            # Print up to 5 representative paths; full list often noisy
            n=$(printf '%s\n' "$shared" | wc -l)
            printf '%s\n' "$shared" | head -5 | while IFS= read -r path; do
                printf 'CONFLICT\t%s\t%s\t%s\n' "$a" "$b" "$path"
            done
            if (( n > 5 )); then
                printf '  …and %d more file(s) shared\n' $((n - 5)) >&2
            fi
        fi
    done
done

if (( CONFLICTS == 0 )); then
    echo "[check-collisions] no file conflicts among ${#PKGS[@]} packages ($MODE mode)" >&2
fi
exit "$CONFLICTS"
