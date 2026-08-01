#!/usr/bin/env bash
#
# check-repo-contents.sh — does each spec actually produce an RPM in the COPR?
#
# The third member of the family. audit-sources.sh proves a spec's local sources
# are committed; check-source-urls.sh proves its remote sources still resolve;
# this one proves the whole thing came out the far end as an installable package.
#
# Why it exists: COPR's own status is not a usable answer here.
#   * A package shows a RED "latest build failed" badge if ANY chroot failed, so
#     five packages with perfectly good F44 RPMs look broken because rawhide is.
#   * Conversely `latest_succeeded_build == null` fires on those same healthy
#     packages, because COPR marks a *build* succeeded only when EVERY chroot
#     does. It is a per-build flag, not a per-package one.
# Neither tells you the thing you care about: is there an RPM a user can install?
#
# 3dslicer-dcmqi is the case that motivated this. It sat in the package list for
# months looking real. It had never built once — a BuildRequires naming a package
# that does not exist made its buildroot unsatisfiable — and because it never got
# as far as a chroot, it silently accumulated FIVE more independent defects
# (missing SlicerExecutionModel, missing git-core, a git-only version target, and
# a DCMTK API gap) that were each invisible until the one before it was fixed.
# A check on repo contents would have caught it on day one.
#
#   ci/check-repo-contents.sh [spec ...]     # default: all *.spec
#
# Needs the COPR repo enabled (the CI job does this) and network access.
# Exit 0 = every spec has at least one RPM; 1 = at least one produces nothing.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

# BOTH COPRs. The free repo alone is not the answer: the 2026-06 free/nonfree
# separation moved 43 specs (FSL, FreeSurfer, dsi-studio) into
# mhough/neurofedora-nonfree while their .spec files stayed in this one repo.
# Querying only the free repo reports every one of them as missing.
REPO_IDS="${REPO_IDS:-copr:copr.fedorainfracloud.org:mhough:neurofedora copr:copr.fedorainfracloud.org:mhough:neurofedora-nonfree}"
ALLOWLIST="ci/no-rpm-allowlist.txt"
RPMDEFS=(--define 'autorelease 1' --define 'autochangelog %{nil}')

specs=("$@")
if [[ ${#specs[@]} -eq 0 ]]; then shopt -s nullglob; specs=(*.spec); fi

# Deliberate exceptions, one bare spec name per line ("foo.spec"), # for comments.
declare -A ALLOWED=()
if [[ -f "$ALLOWLIST" ]]; then
  while read -r line; do
    line="${line%%#*}"; line="${line// /}"
    [[ -n "$line" ]] && ALLOWED["$line"]=1
  done < "$ALLOWLIST"
fi

# One repoquery for the whole repo beats one per package: ~230 specs would
# otherwise mean ~230 round trips.
# Only enable repo ids that are actually configured here. Passing --enablerepo
# for an absent repo makes dnf return an empty set rather than an error, which
# would look exactly like "every spec is missing".
# dnf5's repolist has no --qf, so take the first column and drop the header.
mapfile -t have_repos < <(dnf repolist --all 2>/dev/null | awk 'NR>1{print $1}')
enable_args=(--disablerepo='*'); used=(); absent=()
for r in $REPO_IDS; do
  if printf '%s\n' "${have_repos[@]}" | grep -qxF "$r"; then
    enable_args+=(--enablerepo="$r"); used+=("$r")
  else
    absent+=("$r")
  fi
done
if [[ ${#used[@]} -eq 0 ]]; then
  echo "ERROR: none of the expected repos are configured: ${REPO_IDS}" >&2
  echo "       enable them with: dnf copr enable mhough/neurofedora[-nonfree]" >&2
  exit 2
fi
if [[ ${#absent[@]} -gt 0 ]]; then
  echo "WARNING: not configured here, packages built there will read as missing:"
  for r in "${absent[@]}"; do echo "           $r"; done
fi
echo "Loading package lists from: ${used[*]}"
mapfile -t repo_pkgs < <(dnf repoquery "${enable_args[@]}" \
                           --qf '%{name}\n' --latest-limit 1 2>/dev/null | sort -u)
if [[ ${#repo_pkgs[@]} -eq 0 ]]; then
  echo "ERROR: repoquery returned nothing for ${REPO_IDS}." >&2
  echo "       Repo not enabled, or network is down. Refusing to report every" >&2
  echo "       spec as missing on the strength of an empty query." >&2
  exit 2
fi
declare -A INREPO=()
for p in "${repo_pkgs[@]}"; do INREPO["$p"]=1; done
echo "  ${#repo_pkgs[@]} binary package names in the repo"
echo

fail=0 missing=0 skipped=0 okc=0
for spec in "${specs[@]}"; do
  base="$(basename "$spec")"

  # Every binary package this spec would produce, main + subpackages. Comparing
  # on the SPEC name would be wrong: python-lapy.spec ships python3-lapy, and
  # nothing named python-lapy is ever in the repo.
  mapfile -t names < <(rpmspec -q --qf '%{name}\n' "${RPMDEFS[@]}" "$spec" 2>/dev/null | sort -u)
  if [[ ${#names[@]} -eq 0 ]]; then
    echo "SKIP  ${base} (rpmspec could not parse it; audit-sources covers that)"
    skipped=$((skipped + 1))
    continue
  fi

  found=""
  for n in "${names[@]}"; do
    [[ -n "${INREPO[$n]:-}" ]] && { found="$n"; break; }
  done

  if [[ -n "$found" ]]; then
    okc=$((okc + 1))
  elif [[ -n "${ALLOWED[$base]:-}" ]]; then
    echo "ALLOW ${base} (no RPM, listed in ${ALLOWLIST})"
    skipped=$((skipped + 1))
  else
    echo "MISS  ${base} -> produces no RPM in the repo"
    echo "        would build: ${names[*]}"
    missing=$((missing + 1))
    fail=1
  fi
done

echo
echo "checked ${#specs[@]} specs: ${okc} present, ${missing} missing, ${skipped} skipped"
if [[ $fail -ne 0 ]]; then
  cat <<'EOF'

A spec with no RPM anywhere in the repo has never produced an installable
package. That is a different and worse condition than "the latest build failed",
and COPR's UI does not distinguish them.

Fix the build, or add the spec to ci/no-rpm-allowlist.txt with a reason if it is
deliberately not yet submitted.
EOF
fi
exit $fail
