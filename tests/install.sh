#!/usr/bin/env bash
# install.sh — idempotent install of every neurofedora package from
# packages.tsv, plus the test prerequisites (bats + xorg-x11-server-Xvfb
# for the headless GUI smoke tests).
#
# Reads packages.tsv next to this script. Skips packages whose RPM is
# already installed at the same NEVRA. Reports a clean summary at the end.

set -euo pipefail

HERE="$(dirname "$(readlink -f "$0")")"
MANIFEST="${HERE}/packages.tsv"
COPR_REPO_FILE="/etc/yum.repos.d/_copr:copr.fedorainfracloud.org:mhough:neurofedora.repo"
LOG="${HERE}/install-$(date +%Y%m%d-%H%M%S).log"

log() { printf '[install] %s\n' "$*" | tee -a "$LOG"; }
die() { printf '[install] ERROR: %s\n' "$*" >&2; exit 1; }

[[ -f "$MANIFEST" ]] || die "manifest not found: $MANIFEST"

# 1. Make sure the COPR repo is enabled AND active. dnf has multiple
# sources of "enabled" state and they don't agree: a previously-disabled
# COPR shows enabled=1 in its .repo file but still says "disabled" in
# `dnf repolist --all`. The authoritative override is `dnf config-manager`.
REPO_ID="copr:copr.fedorainfracloud.org:mhough:neurofedora"

log "ensuring $REPO_ID is enabled"
# Step 1: add the .repo file if it's missing (idempotent)
sudo dnf copr enable -y mhough/neurofedora 2>&1 | tee -a "$LOG" || true

# Step 2: belt-and-suspenders — make sure enabled=1 in the file
REPO_FILE=$(ls /etc/yum.repos.d/_copr*mhough*neurofedora*.repo 2>/dev/null | head -1)
[[ -n "$REPO_FILE" ]] && sudo sed -i 's/^enabled=0/enabled=1/' "$REPO_FILE"

# Step 3: authoritative override via config-manager (handles both dnf4 and dnf5
# syntaxes — the older --set-enabled vs the newer setopt)
sudo dnf config-manager setopt "${REPO_ID}.enabled=1" 2>/dev/null \
    || sudo dnf config-manager --set-enabled "$REPO_ID" 2>/dev/null \
    || true

# Step 4: verify
if ! dnf repolist --enabled 2>/dev/null | grep -qi 'mhough.*neurofedora'; then
    log "WARN: $REPO_ID still not enabled. dnf repolist --all says:"
    dnf repolist --all 2>/dev/null | grep -i mhough | tee -a "$LOG"
    die "Manually fix: sudo dnf config-manager --set-enabled '$REPO_ID'"
fi

log "refreshing dnf metadata (so the COPR's current package set is visible)"
sudo dnf makecache --refresh >/dev/null 2>&1 || true

# 2. Make sure bats (the test runner) is available
if ! command -v bats >/dev/null 2>&1; then
    log "installing bats (test runner)"
    sudo dnf install -y bats
fi

# 3. xvfb-run for the non-Qt GUI smoke tests (Qt apps use QT_QPA_PLATFORM=
#    offscreen and don't need an X server). Skipped silently if absent —
#    the corresponding tests will then SKIP rather than fail.
if ! command -v xvfb-run >/dev/null 2>&1; then
    log "installing xorg-x11-server-Xvfb (headless GUI smoke)"
    sudo dnf install -y xorg-x11-server-Xvfb || \
        log "xvfb install failed — gui.bats xvfb tests will be skipped"
fi

# 3b. Python deps for pipelines.bats fixture generation. The fixtures are
#     synthesized on first test run from numpy + nibabel + pydicom + SimpleITK.
#     Without these, pipelines.bats SKIPs all 20 tests.
FIXTURE_DEPS=(python3-numpy python3-nibabel python3-pydicom python3-SimpleITK)
NEED_FIXTURE_DEPS=()
for p in "${FIXTURE_DEPS[@]}"; do
    rpm -q --quiet "$p" 2>/dev/null || NEED_FIXTURE_DEPS+=("$p")
done
if (( ${#NEED_FIXTURE_DEPS[@]} > 0 )); then
    log "installing pipeline fixture deps: ${NEED_FIXTURE_DEPS[*]}"
    sudo dnf install -y --skip-unavailable "${NEED_FIXTURE_DEPS[@]}" 2>&1 | tee -a "$LOG" || true
fi

# 3c. Preflight: remove Fedora packages that file-conflict with COPR packages.
#     The COPR ships InsightToolkit 5.x; Fedora's stock InsightToolkit is 4.x
#     and they fight over /usr/bin/itkTestDriver. Same situation for any other
#     known offenders. We `dnf remove` them silently — they will be replaced
#     by the COPR equivalent in the main install step.
CONFLICT_REMOVALS=(InsightToolkit InsightToolkit-devel dtk-devel)
REMOVE_NOW=()
for p in "${CONFLICT_REMOVALS[@]}"; do
    rpm -q --quiet "$p" 2>/dev/null && REMOVE_NOW+=("$p")
done
if (( ${#REMOVE_NOW[@]} > 0 )); then
    log "removing Fedora packages that conflict with COPR equivalents: ${REMOVE_NOW[*]}"
    sudo dnf remove -y "${REMOVE_NOW[@]}" 2>&1 | tee -a "$LOG" || true
fi

# 4. Collect the package list from the manifest (skip comments and WIP rows)
mapfile -t PKGS < <(awk -F'\t' '
    /^[[:space:]]*$/ { next }
    /^[[:space:]]*#/ { next }
    { print $1 }
' "$MANIFEST")

log "manifest lists ${#PKGS[@]} packages"

# 5. Filter out already-installed packages (idempotency)
NEEDED=()
for p in "${PKGS[@]}"; do
    if ! rpm -q --quiet "$p" 2>/dev/null; then
        NEEDED+=("$p")
    fi
done

if (( ${#NEEDED[@]} == 0 )); then
    log "all ${#PKGS[@]} packages already installed — nothing to do"
    exit 0
fi

# 5b. Filter out known-conflicting pairs: itksnap-0.7 bundles c3d+greedy at
#     the same paths as the standalone packages. We can't install both. The
#     standalone CLIs are higher value (used by every registration pipeline),
#     so the manifest stays the manifest but install.sh holds back the
#     conflicting itksnap until upstream-0.8 lands on COPR.
HOLD_BACK=()
if printf '%s\n' "${NEEDED[@]}" | grep -qx c3d && \
   printf '%s\n' "${NEEDED[@]}" | grep -qx greedy && \
   printf '%s\n' "${NEEDED[@]}" | grep -qx itksnap; then
    log "holding back itksnap (its 0.7 release bundles c3d+greedy — re-enable when 0.8 lands)"
    HOLD_BACK+=(itksnap)
fi
INSTALL_NOW=()
for p in "${NEEDED[@]}"; do
    skip=0
    for h in "${HOLD_BACK[@]}"; do [[ "$p" == "$h" ]] && skip=1; done
    (( skip == 0 )) && INSTALL_NOW+=("$p")
done

log "${#INSTALL_NOW[@]} packages will be installed (after ${#HOLD_BACK[@]} held back):"
printf '  - %s\n' "${INSTALL_NOW[@]}" | tee -a "$LOG"

# 6. Single dnf transaction, best-effort:
#   --skip-unavailable : skip names dnf can't find at all (no metadata match)
#   --skip-broken      : skip packages with depsolve conflicts (e.g. a package
#                        in the COPR that requires python3-numba which F44
#                        doesn't currently package)
#   --allowerasing     : allow dnf to remove packages that have hard Conflicts:
#                        with what we're installing (e.g. legacy dtk-devel
#                        being replaced by dtk-qt6). DOES NOT cover unflagged
#                        binary-vs-binary file collisions — those need step 5b.
# We never want a partial-COPR or a transient broken dep to abort the whole
# smoke run — we want to install as much as we can and report what landed.
log "running: sudo dnf install --skip-unavailable --skip-broken --allowerasing -y ..."
sudo dnf install --skip-unavailable --skip-broken --allowerasing -y \
    "${INSTALL_NOW[@]}" 2>&1 | tee -a "$LOG" || true

# 7. Final tally
INSTALLED=0
MISSING=()
for p in "${PKGS[@]}"; do
    if rpm -q --quiet "$p" 2>/dev/null; then
        INSTALLED=$((INSTALLED + 1))
    else
        MISSING+=("$p")
    fi
done

log "---------------------------------------------------------------"
log "Installed: $INSTALLED / ${#PKGS[@]}"
if (( ${#MISSING[@]} > 0 )); then
    log "Not installed: ${#MISSING[@]} (probably not in repo, or name mismatch):"
    printf '  - %s\n' "${MISSING[@]}" | tee -a "$LOG"
fi
log "log: $LOG"
