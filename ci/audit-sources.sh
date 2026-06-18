#!/usr/bin/env bash
#
# audit-sources.sh — SCM source-completeness gate for the neurofedora spec repo.
#
# COPR builds these specs via rpkg (`rpkg srpm`), which clones THIS git repo and
# must find every Source/Patch file referenced by a spec either committed here or
# fetchable from a URL. A spec can look "green" on COPR yet have an uncommitted
# Source file if it was last built from an *uploaded* SRPM (which bundles files
# from the local ~/rpmbuild/SOURCES). The next SCM build then fails at the source
# stage with `Bad file: <name>: No such file or directory`.
#
# This script preprocesses every spec, lists its Source/Patch entries, and fails
# if any non-URL file is neither committed to the repo nor allow-listed as a
# lookaside-backed upstream tarball (ci/lookaside-allowlist.txt).
#
# Exit 0 = all good; Exit 1 = a missing local source (block the push/build).

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2   # repo root

ALLOWLIST="ci/lookaside-allowlist.txt"

# Stubs so rpmspec -P expands even without the full rpkg/autospec stack.
# forge-srpm-macros (installed in CI) expands %forgesource to a real URL.
RPMDEFS=(--define 'autorelease 1' --define 'autochangelog %{nil}' --undefine dist)

# Load allow-list as glob patterns (basenames), skipping comments/blanks.
ALLOW_PATTERNS=()
if [[ -f "$ALLOWLIST" ]]; then
  while IFS= read -r line; do
    line="${line%%#*}"
    line="$(printf '%s' "$line" | tr -d '[:space:]')"
    [[ -n "$line" ]] && ALLOW_PATTERNS+=("$line")
  done < "$ALLOWLIST"
fi

is_allowlisted() {
  local bn="$1" pat
  for pat in "${ALLOW_PATTERNS[@]:-}"; do
    # shellcheck disable=SC2053
    [[ "$bn" == $pat ]] && return 0
  done
  return 1
}

fail=0
parse_skip=0
missing_list=()

shopt -s nullglob
for spec in *.spec; do
  out="$(rpmspec -P "$spec" "${RPMDEFS[@]}" 2>/dev/null)"
  if [[ -z "$out" ]]; then
    echo "WARN: could not preprocess $spec (build-time macros?) — skipped"
    parse_skip=$((parse_skip + 1))
    continue
  fi
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      http://*|https://*|ftp://*|git+*|*%*) continue ;;  # URL or unexpanded macro
    esac
    bn="$(basename "$f")"
    [[ -f "$bn" ]] && continue
    is_allowlisted "$bn" && continue
    echo "MISSING: $spec -> $bn"
    missing_list+=("$bn")
    fail=1
  done < <(printf '%s\n' "$out" | awk '/^(Source|Patch)[0-9]*:/{print $NF}')
done

echo
if [[ $fail -ne 0 ]]; then
  echo "FAIL: ${#missing_list[@]} Source/Patch file(s) referenced by specs are not in the repo."
  echo
  echo "Fix one of these ways:"
  echo "  * small patch / cmake shim / script / man page  -> git add the file"
  echo "  * upstream tarball with a canonical URL          -> use a URL or %forgesource"
  echo "  * large un-hostable upstream tarball (lookaside) -> add a glob to $ALLOWLIST"
  exit 1
fi

echo "OK: every spec's Source/Patch is committed, URL-backed, or allow-listed."
[[ $parse_skip -gt 0 ]] && echo "(note: $parse_skip spec(s) skipped — could not preprocess in CI)"
exit 0
