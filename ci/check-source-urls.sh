#!/usr/bin/env bash
#
# check-source-urls.sh — source-URL liveness check.
#
# Companion to audit-sources.sh. That one proves local Source/Patch files are
# committed; this one proves the *remote* ones still resolve. A dead Source URL
# makes the COPR SCM build (`rpkg srpm`) fail at the source stage with
# `curl: (22) ... 404` / `Couldn't download` before any chroot build — exactly
# how libspm (wrong GitHub owner) and InsightToolkit6 (a moved ITK remote module)
# are currently broken.
#
# Network-dependent and slow-ish, so this is NOT a per-push gate — run it on a
# schedule (see .gitlab-ci.yml `source-urls` job) or locally.
#
#   ci/check-source-urls.sh [spec ...]      # default: all *.spec
#
# Exit 0 = all URLs resolve; 1 = at least one dead URL.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

RPMDEFS=(--define 'autorelease 1' --define 'autochangelog %{nil}' --undefine dist)
TIMEOUT=30

specs=("$@")
[[ ${#specs[@]} -eq 0 ]] && { shopt -s nullglob; specs=(*.spec); }

url_ok() {  # 0 if reachable; try HEAD, then a 1-byte ranged GET (some hosts 403 HEAD)
  local u="$1"
  curl -fsIL --max-time "$TIMEOUT" -o /dev/null "$u" 2>/dev/null && return 0
  curl -fsL  --max-time "$TIMEOUT" -r 0-0 -o /dev/null "$u" 2>/dev/null && return 0
  return 1
}

fail=0
declare -A SEEN=()
for spec in "${specs[@]}"; do
  out="$(rpmspec -P "$spec" "${RPMDEFS[@]}" 2>/dev/null)" || continue
  while IFS= read -r u; do
    case "$u" in http://*|https://*|ftp://*) ;; *) continue ;; esac
    [[ -n "${SEEN[$u]:-}" ]] && continue
    SEEN[$u]=1
    if url_ok "$u"; then
      :
    else
      echo "DEAD URL [$spec]: $u"
      fail=1
    fi
  done < <(printf '%s\n' "$out" | awk '/^(Source|Patch)[0-9]*:/{print $NF}')
done

echo
if [[ $fail -ne 0 ]]; then
  echo "FAIL: one or more Source/Patch URLs do not resolve."
  echo "Fix the URL (upstream may have renamed/moved/retagged), or vendor the"
  echo "tarball to the repo / a lookaside cache and drop the URL."
  exit 1
fi
echo "OK: all Source/Patch URLs resolve."
exit 0
