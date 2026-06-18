#!/usr/bin/env bash
#
# install-smoke.sh — "built ≠ installable ≠ functional" gate.
#
# A green COPR build only proves the RPM compiled. It does NOT prove the package
# installs from a clean repo (missing Requires), that the newest build actually
# superseded in the repo (the %autorelease-stuck-at-N trap), or that its binaries
# even start (missing runtime libs). The paraview saga hit all three. This script
# checks the whole chain in a throwaway mock chroot.
#
# Usage:
#   ci/smoke/install-smoke.sh <pkg> [<pkg> ...]
#   ci/smoke/install-smoke.sh --manifest ci/smoke/manifest.txt
#
# Env:
#   CHROOT   mock config (default fedora-44-x86_64)
#   COPR     COPR repo base URL to --addrepo
#
# Per package it asserts:
#   1. INSTALL   — `dnf install <pkg>` resolves from COPR+Fedora alone.
#   2. NVR-DEPLOY— installed NVR == latest COPR build NVR (catches stale/stuck).
#   3. SMOKE     — each /usr/bin binary it ships starts (no loader/"not found"
#                  error) under `--help`/`--version`/`-h`; or a manifest override.
#   4. RPMLINT   — informational rpmlint on the installed package.
#
# Exit 0 only if every package passes INSTALL + NVR-DEPLOY + SMOKE.

set -uo pipefail

CHROOT="${CHROOT:-fedora-44-x86_64}"
COPR="${COPR:-https://download.copr.fedorainfracloud.org/results/mhough/neurofedora/${CHROOT}/}"
MANIFEST=""
declare -a PKGS=()
declare -A OVERRIDE=()   # pkg -> explicit smoke command

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest) MANIFEST="$2"; shift 2 ;;
    --chroot)   CHROOT="$2"; shift 2 ;;
    *)          PKGS+=("$1"); shift ;;
  esac
done

if [[ -n "$MANIFEST" ]]; then
  while IFS='|' read -r pkg cmd; do
    pkg="$(echo "$pkg" | xargs)"; [[ -z "$pkg" || "$pkg" == \#* ]] && continue
    PKGS+=("$pkg")
    [[ -n "${cmd:-}" ]] && OVERRIDE["$pkg"]="$(echo "$cmd" | xargs)"
  done < "$MANIFEST"
fi

[[ ${#PKGS[@]} -eq 0 ]] && { echo "no packages given"; exit 2; }

latest_nvr() {  # echo "<version>-<release>" of the latest COPR build for $1
  curl -s "https://copr.fedorainfracloud.org/api_3/package/get?ownername=mhough&projectname=neurofedora&packagename=$1&with_latest_build=true" 2>/dev/null \
    | python3 -c 'import sys,json;b=(json.load(sys.stdin).get("latest_build") or {});print((b.get("source_package") or {}).get("version") or "")' 2>/dev/null
}

overall=0
declare -a SUMMARY=()
for pkg in "${PKGS[@]}"; do
  ue="smoke-${pkg//[^a-zA-Z0-9]/_}"
  root="/var/lib/mock/${CHROOT}-${ue}/root"
  echo "==================== $pkg ===================="
  mock -r "$CHROOT" --uniqueext="$ue" --addrepo="$COPR" --init   >/tmp/$ue-init.log 2>&1
  mock -r "$CHROOT" --uniqueext="$ue" --no-clean --addrepo="$COPR" --install "$pkg" >/tmp/$ue-inst.log 2>&1
  inst_rc=$?

  status="PASS"; detail=""
  if [[ $inst_rc -ne 0 ]]; then
    status="FAIL"; detail="INSTALL: dnf could not install (unmet deps?) — see /tmp/$ue-inst.log"
    echo "  INSTALL: FAIL"; SUMMARY+=("$pkg: FAIL ($detail)"); overall=1
    mock -r "$CHROOT" --uniqueext="$ue" --scrub=all >/dev/null 2>&1 &
    continue
  fi
  echo "  INSTALL: ok"

  # 2. NVR-deploy: does the installed NVR match the latest COPR build?
  inst_ver="$(mock -r "$CHROOT" --uniqueext="$ue" --no-clean --shell "rpm -q --qf '%{VERSION}-%{RELEASE}\n' $pkg" 2>/dev/null \
              | grep -E '^[0-9].*-' | head -1)"
  want="$(latest_nvr "$pkg")"
  inst_short="${inst_ver%.fc*}"; want_short="${want%.fc*}"
  if [[ -n "$want_short" && -n "$inst_short" && "$inst_short" != "$want_short" ]]; then
    status="FAIL"; detail="NVR-DEPLOY: installed $inst_short != latest build $want_short (stale/stuck NVR)"
    echo "  NVR-DEPLOY: FAIL (installed $inst_short, latest $want_short)"; overall=1
  else
    echo "  NVR-DEPLOY: ok ($inst_short)"
  fi

  # 3. smoke
  if [[ -n "${OVERRIDE[$pkg]:-}" ]]; then
    if mock -r "$CHROOT" --uniqueext="$ue" --no-clean --shell "${OVERRIDE[$pkg]}" >/tmp/$ue-smoke.log 2>&1; then
      echo "  SMOKE(override): ok"
    else
      status="FAIL"; detail="SMOKE override failed: ${OVERRIDE[$pkg]} — see /tmp/$ue-smoke.log"; echo "  SMOKE(override): FAIL"; overall=1
    fi
  else
    # auto-smoke every /usr/bin binary the package ships
    bins="$(mock -r "$CHROOT" --uniqueext="$ue" --no-clean --shell "rpm -ql $pkg | grep '^/usr/bin/' | head -40" 2>/dev/null | grep '^/usr/bin/')"
    if [[ -z "$bins" ]]; then
      echo "  SMOKE: (no /usr/bin binaries — library/data package; install+NVR only)"
    else
      smoke_script='ok=0; bad=""; for b in '"$(echo $bins)"'; do
        out=$(timeout 25 "$b" --help 2>&1 || timeout 25 "$b" --version 2>&1 || timeout 25 "$b" -h 2>&1);
        if echo "$out" | grep -qiE "error while loading shared lib|cannot open shared object|No such file or directory|command not found|undefined symbol"; then
          bad="$bad $b"; else ok=$((ok+1)); fi;
      done;
      echo "SMOKE_OK=$ok"; [ -n "$bad" ] && echo "SMOKE_BAD=$bad"'
      smres="$(mock -r "$CHROOT" --uniqueext="$ue" --no-clean --shell "$smoke_script" 2>/dev/null)"
      if echo "$smres" | grep -q "SMOKE_BAD="; then
        bad="$(echo "$smres" | grep -o 'SMOKE_BAD=.*')"
        status="FAIL"; detail="SMOKE: binaries fail to start: ${bad#SMOKE_BAD=}"; echo "  SMOKE: FAIL ($detail)"; overall=1
      else
        echo "  SMOKE: ok ($(echo "$smres" | grep -o 'SMOKE_OK=[0-9]*') binaries start)"
      fi
    fi
  fi

  # 4. rpmlint (informational)
  mock -r "$CHROOT" --uniqueext="$ue" --no-clean --shell "command -v rpmlint >/dev/null || (dnf -y install rpmlint >/dev/null 2>&1); rpmlint $pkg 2>/dev/null | tail -1" 2>/dev/null | grep -E "packages and|badness" | sed 's/^/  RPMLINT: /' || true

  SUMMARY+=("$pkg: $status${detail:+ — $detail}")
  mock -r "$CHROOT" --uniqueext="$ue" --scrub=all >/dev/null 2>&1 &
done

echo
echo "==================== SUMMARY ===================="
printf '%s\n' "${SUMMARY[@]}"
wait 2>/dev/null
exit $overall
