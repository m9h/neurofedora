#!/usr/bin/env bash
# cc3d-install.sh — install the COMPLETE CompuCell3D stack from the
# mhough/neurofedora COPR on Fedora 44, including the network-solver and
# model-authoring chain that ships only as weak deps (Recommends).
#
# Why this script exists (two traps a plain `dnf install compucell3d` hits):
#
#   1. The SBML/MaBoSS solvers (python3-roadrunner, python3-cc3dext,
#      python3-simservice) are Recommends on python3-compucell3d. dnf can
#      silently skip weak deps (e.g. --setopt=install_weak_deps=0, or a prior
#      depsolve hiccup), and then every MaBoSS/SBML demo fails at runtime with
#      AttributeError / NoMaBoSSExtensionError. We install them EXPLICITLY.
#
#   2. VTK ABI split. Fedora ships vtk 9.5.2; the COPR ships 9.6.2. They share
#      the libvtk*.so.1 SONAME, so a CC3D built against 9.6.2 silently links
#      the wrong one and dies at import with:
#        undefined symbol: _ZN16vtkCartesianGrid13GetDimensionsEPi
#      The COPR's 9.6.2 has no vtk-java/-data/-doc/-examples subpackages, and
#      Fedora's (already installed) ones pin `vtk = 9.5.2`, blocking the swap.
#      We remove those ancillary subpackages and force vtk >= 9.6.2.
#
# Idempotent: re-running only does the work still needed. Needs sudo.

set -uo pipefail

HERE="$(dirname "$(readlink -f "$0")")"
LOG="${HERE}/cc3d-install-$(date +%Y%m%d-%H%M%S).log"
VTK_FLOOR="9.6.2"

log()  { printf '[cc3d-install] %s\n' "$*" | tee -a "$LOG"; }
die()  { printf '[cc3d-install] ERROR: %s\n' "$*" >&2; exit 1; }
have() { rpm -q --quiet "$1" 2>/dev/null; }
# ver_lt A B  -> true if A < B  (rpm version compare via sort -V)
ver_lt() { [ "$1" != "$2" ] && [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -1)" = "$1" ]; }

[ "$(id -u)" -eq 0 ] || command -v sudo >/dev/null || die "need root or sudo"
SUDO=""; [ "$(id -u)" -eq 0 ] || SUDO="sudo"

# --- The complete CompuCell3D package set ----------------------------------
# Core engine + Python bindings + GUIs:
CORE_PKGS=(
    compucell3d
    python3-compucell3d
    compucell3d-devel
    cc3d-player5
    cc3d-twedit5
)
# Network solvers + model authoring (Recommends — installed explicitly here):
SOLVER_PKGS=(
    python3-roadrunner     # SBML continuous kinetics (CVODE)
    libroadrunner          # the shared lib (python3-roadrunner is self-contained,
                           # but install it so other consumers can link it)
    python3-cc3dext        # bundled MaBoSS Boolean-network engine (cc3dext.MaBoSSCC3DPy)
    python3-simservice     # CC3D service mode
    antimony               # human-readable <-> SBML translators (CLI)
    python3-antimony       # antimony Python bindings
    libsbmlnetwork         # SBML layout/render lib antimony links
)
# Test prerequisites (headless GUI + demo sweep):
TEST_PKGS=(
    xorg-x11-server-Xvfb
)

# --- 1. Enable + activate the COPR -----------------------------------------
REPO_ID="copr:copr.fedorainfracloud.org:mhough:neurofedora"
log "ensuring $REPO_ID is enabled"
$SUDO dnf copr enable -y mhough/neurofedora 2>&1 | tee -a "$LOG" || true
REPO_FILE=$(ls /etc/yum.repos.d/_copr*mhough*neurofedora*.repo 2>/dev/null | head -1)
[ -n "$REPO_FILE" ] && $SUDO sed -i 's/^enabled=0/enabled=1/' "$REPO_FILE"
$SUDO dnf config-manager setopt "${REPO_ID}.enabled=1" 2>/dev/null \
    || $SUDO dnf config-manager --set-enabled "$REPO_ID" 2>/dev/null || true
dnf repolist --enabled 2>/dev/null | grep -qi 'mhough.*neurofedora' \
    || die "COPR not enabled. Run: sudo dnf config-manager --set-enabled '$REPO_ID'"
log "refreshing dnf metadata"
$SUDO dnf makecache --refresh >/dev/null 2>&1 || true

# --- 2. VTK preflight: force the COPR's 9.6.2 ------------------------------
CUR_VTK=$(rpm -q --qf '%{VERSION}' vtk 2>/dev/null || echo "")
if [ -z "$CUR_VTK" ]; then
    log "vtk not installed yet — dnf will pull the COPR's >= $VTK_FLOOR with CC3D"
elif ver_lt "$CUR_VTK" "$VTK_FLOOR"; then
    log "vtk $CUR_VTK installed (< $VTK_FLOOR) — switching to the COPR build"
    # These ancillary subpackages exist only in Fedora's 9.5.2 and hard-pin
    # vtk = 9.5.2, blocking the upgrade. CC3D needs none of them. Remove first.
    ANCILLARY=(vtk-java vtk-data vtk-doc vtk-examples vtk-testing)
    DROP=()
    for p in "${ANCILLARY[@]}"; do have "$p" && DROP+=("$p"); done
    if (( ${#DROP[@]} > 0 )); then
        log "removing Fedora-only ancillary VTK subpackages (not used by CC3D): ${DROP[*]}"
        $SUDO dnf remove -y "${DROP[@]}" 2>&1 | tee -a "$LOG" || true
    fi
    log "upgrading vtk/python3-vtk/vtk-qt to >= $VTK_FLOOR (--allowerasing)"
    log "  >>> REVIEW the 'Removing' list: it must be only vtk-* subpackages."
    log "  >>> If dnf wants to remove a real app (paraview, mrtrix3, ...), abort"
    log "  >>> and rebuild that app against vtk $VTK_FLOOR first."
    $SUDO dnf install --refresh --allowerasing -y \
        vtk python3-vtk vtk-qt 2>&1 | tee -a "$LOG" \
        || die "VTK upgrade failed — see $LOG"
else
    log "vtk $CUR_VTK already >= $VTK_FLOOR — good"
fi

# --- 3. Install the CC3D stack ---------------------------------------------
ALL_PKGS=("${CORE_PKGS[@]}" "${SOLVER_PKGS[@]}" "${TEST_PKGS[@]}")
log "installing the complete CompuCell3D stack (${#ALL_PKGS[@]} packages):"
printf '  - %s\n' "${ALL_PKGS[@]}" | tee -a "$LOG"
# --skip-unavailable: tolerate a package temporarily absent from the COPR.
# No --skip-broken here: a broken depsolve on the CORE set is a real failure
# we want to see, not silently paper over.
$SUDO dnf install --skip-unavailable --allowerasing -y \
    "${ALL_PKGS[@]}" 2>&1 | tee -a "$LOG" || true

# --- 4. Verify --------------------------------------------------------------
log "---------------------------------------------------------------"
FAIL=0
NEW_VTK=$(rpm -q --qf '%{VERSION}' vtk 2>/dev/null || echo "none")
if [ "$NEW_VTK" = none ] || ver_lt "$NEW_VTK" "$VTK_FLOOR"; then
    log "FAIL: vtk is $NEW_VTK (need >= $VTK_FLOOR) — CC3D will not import"
    FAIL=1
else
    log "OK:   vtk $NEW_VTK (from $(rpm -q --qf '%{VENDOR}' vtk 2>/dev/null))"
fi
MISSING=()
for p in "${CORE_PKGS[@]}" "${SOLVER_PKGS[@]}"; do
    have "$p" && log "OK:   $(rpm -q "$p")" || { MISSING+=("$p"); log "FAIL: $p not installed"; FAIL=1; }
done
log "---------------------------------------------------------------"
if (( FAIL == 0 )); then
    log "SUCCESS: complete CompuCell3D stack installed."
    log "Next: run  bash ${HERE}/cc3d-network-solvers-smoke.sh"
    log "      then  bash ${HERE}/cc3d-demo-sweep.sh   (runs every shipped demo)"
else
    (( ${#MISSING[@]} > 0 )) && log "Missing: ${MISSING[*]}"
    log "See $LOG for the full transaction."
fi
log "log: $LOG"
exit $FAIL
