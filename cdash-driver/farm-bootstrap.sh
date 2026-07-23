#!/usr/bin/env bash
# farm-bootstrap.sh — join the neurofedora Slicer CTest build farm.
#
# One command turns a Fedora 44+ box into a farm node: it builds the *Fedora*
# Slicer config with BUILD_TESTING=ON and submits the CTest results to
# my.cdash.org/index.php?project=neurofedora, continuously, as a systemd service.
# Outbound https only (COPR + my.cdash.org) — no inbound access / VPN / shared LAN.
#
# READ THIS FIRST — it makes SYSTEM-WIDE and PUBLIC changes and is meant for a
# DEDICATED build box, not a workstation you rely on:
#   * It SWAPS SYSTEM VTK: removes vtk-java and replaces Fedora VTK 9.5 with COPR
#     VTK 9.6 (same libvtk*.so.1 soname → cannot coexist). Every VTK consumer on
#     the box (paraview, python3-vtk, opencascade, …) then links COPR 9.6.
#   * It installs a 24/7 unconfined systemd service (Restart=always, ~7-9 h first
#     build, loops forever). Permanent background load; contends with mock.
#   * It PUBLISHES each cycle to the PUBLIC my.cdash.org/neurofedora under this
#     host's name (cached/indexed even if later removed).
# It does NOT touch ~/rpmbuild — it uses an isolated tree under
# ~/.local/share/neurofedora-farm so your packaging work is never overwritten.
#
# Usage:
#   ./farm-bootstrap.sh [stable|preview] [--dry-run] [--yes]
#     stable  = 3dslicer 5.12 (default) ; preview = slicer-preview 5.13 (main)
#     --dry-run  print exactly what it would do, change nothing
#     --yes      skip the interactive confirmation (for automation)
set -euo pipefail

TRACK=stable; ASSUME_YES=0; DRY_RUN=0
for a in "$@"; do
  case "$a" in
    stable|preview) TRACK="$a" ;;
    -y|--yes)       ASSUME_YES=1 ;;
    -n|--dry-run)   DRY_RUN=1 ;;
    *) echo "usage: $0 [stable|preview] [--dry-run] [--yes]" >&2; exit 2 ;;
  esac
done
case "$TRACK" in
  stable)  PKG=3dslicer;       SPEC=3dslicer.spec ;;
  preview) PKG=slicer-preview; SPEC=slicer-preview.spec ;;
esac

RUN_USER="$(id -un)"; RUN_HOME="$HOME"
FARM_ROOT="$RUN_HOME/.local/share/neurofedora-farm"   # isolated — NOT ~/rpmbuild
RPMTREE="$FARM_ROOT/rpmbuild"
DRIVER_DIR="$FARM_ROOT/cdash-driver"

# --- preflight: show exactly what will change, and get consent ---------------
cat <<EOF
==============================================================================
 neurofedora CTest farm bootstrap
   host=$(hostname)  user=$RUN_USER  arch=$(uname -m)  fedora=$(rpm -E %fedora)
   track=$TRACK ($PKG)   isolated build tree: $RPMTREE
------------------------------------------------------------------------------
 This will, on THIS machine:
   1. SWAP SYSTEM VTK  — remove vtk-java, and 'dnf builddep --allowerasing'
      replaces Fedora VTK 9.5 with COPR VTK 9.6 (system-wide; every VTK
      consumer relinks). Only appropriate on a DEDICATED build box.
   2. Install a 24/7 unconfined systemd service (Restart=always; ~7-9 h first
      build; loops forever). Permanent background load; contends with mock.
   3. PUBLISH results to PUBLIC my.cdash.org/neurofedora as site "$(hostname)".
 It will NOT touch ~/rpmbuild (uses $RPMTREE).
==============================================================================
EOF
if [ "$DRY_RUN" = 1 ]; then echo "[--dry-run] no changes made."; exit 0; fi
if [ "$ASSUME_YES" != 1 ]; then
  # Read from the controlling terminal so `curl … | bash` still prompts (stdin is
  # the pipe there). If there is no TTY at all, don't silently abort — explain.
  if [ -r /dev/tty ]; then
    read -rp "This is a dedicated-node action. Type 'yes' to proceed: " _ans < /dev/tty
  else
    echo "aborted: no terminal for the confirmation prompt." >&2
    echo "  Re-run with --yes to skip it (you've already seen the plan above):" >&2
    echo "    curl -sSL <url>/farm-bootstrap.sh | bash -s -- $TRACK --yes" >&2
    exit 1
  fi
  [ "$_ans" = yes ] || { echo "aborted — nothing changed."; exit 1; }
fi

# --- 0. preflight checks -----------------------------------------------------
[ "$(rpm -E %fedora)" -ge 44 ] || { echo "error: need Fedora 44+"; exit 1; }
command -v sudo >/dev/null || { echo "error: sudo required"; exit 1; }
avail_gb=$(df -BG --output=avail "$RUN_HOME" | tail -1 | tr -dc '0-9')
[ "${avail_gb:-0}" -ge 30 ] || echo "warning: <30 GB free in $RUN_HOME"

# isolated tree — never the user's ~/rpmbuild
mkdir -p "$RPMTREE"/{SPECS,SOURCES,BUILD,BUILDROOT,RPMS,SRPMS} "$DRIVER_DIR"

# --- 1. COPR + build toolchain ----------------------------------------------
echo "--- enabling mhough/neurofedora COPR + toolchain ---"
sudo dnf -y copr enable mhough/neurofedora
sudo dnf -y install rpm-build rpmdevtools cmake ninja-build gcc-c++ gcc-gfortran \
    git-core xorg-x11-server-Xvfb glx-utils chrpath mesa-dri-drivers dnf-plugins-core

# --- 2. Fedora vtk 9.5 -> COPR 9.6 (vtk-java has no COPR build; must go) -----
rpm -q vtk-java >/dev/null 2>&1 && sudo dnf -y remove vtk-java || true

# --- 3. fetch CURRENT spec + sources into the ISOLATED tree ------------------
echo "--- downloading $PKG source RPM from COPR into $RPMTREE ---"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
( cd "$tmp"
  dnf download --source "$PKG" 2>/dev/null || {
    echo "error: 'dnf download --source $PKG' failed — is the COPR SRPM published for $(uname -m)/fc$(rpm -E %fedora)?"; exit 1; }
  rpm -Uvh --nodeps --define "_topdir $RPMTREE" ./"$PKG"-*.src.rpm )

if ! grep -q '%bcond.*testing' "$RPMTREE/SPECS/$SPEC"; then
  echo "error: $SPEC has no 'testing' bcond — the COPR $PKG build predates CTest"
  echo "  support. Ask the farm owner to rebuild $PKG on COPR, then re-run."; exit 1
fi

# --- 4. build deps (swaps in COPR vtk 9.6; pulls ITK5/ctk/PythonQt/…) --------
echo "--- builddep (replaces Fedora vtk 9.5 with COPR 9.6) ---"
sudo dnf -y builddep --allowerasing "$RPMTREE/SPECS/$SPEC"

# --- 5. runtime deps the tests import ---------------------------------------
sudo dnf -y install python3-vtkAddon python3-dicomweb-client python3-highdicom \
    python3-legacy-cgi || true

# --- 6. driver + loop + CDash config (into the isolated tree) ----------------
cat > "$DRIVER_DIR/CTestConfig.cmake" <<'CTESTCONFIG'
set(CTEST_PROJECT_NAME "neurofedora")
set(CTEST_NIGHTLY_START_TIME "01:00:00 UTC")
set(CTEST_DROP_METHOD "https")
set(CTEST_DROP_SITE "my.cdash.org")
set(CTEST_DROP_LOCATION "/submit.php?project=neurofedora")
set(CTEST_DROP_SITE_CDASH TRUE)
CTESTCONFIG

cat > "$DRIVER_DIR/run-slicer-ctest.sh" <<'RUNCTEST'
#!/usr/bin/env bash
# One CTest cycle of the Fedora Slicer build -> CDash. Honors RPMBUILD (isolated
# tree) via --define _topdir so it never uses ~/rpmbuild unless told to.
set -euo pipefail
MODEL="${1:-Nightly}"
case "$MODEL" in Nightly|Experimental) ;; *) echo "model must be Nightly|Experimental" >&2; exit 2;; esac
DRIVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RPMBUILD="${RPMBUILD:-$HOME/rpmbuild}"
ARCH="$(uname -m)"
if [[ -n "${SLICER_CTEST_SPEC:-}" ]]; then
  case "$SLICER_CTEST_SPEC" in /*) SPEC="$SLICER_CTEST_SPEC";; *) SPEC="$RPMBUILD/SPECS/$SLICER_CTEST_SPEC";; esac
elif [[ -f "$RPMBUILD/SPECS/slicer-preview.spec" ]]; then SPEC="$RPMBUILD/SPECS/slicer-preview.spec"
else SPEC="$RPMBUILD/SPECS/3dslicer.spec"; fi
[[ -f "$SPEC" ]] || { echo "spec not found: $SPEC" >&2; exit 2; }
if [[ -n "${SLICER_CTEST_J:-}" ]]; then J="$SLICER_CTEST_J"; else J=$(( $(nproc) - 2 )); (( J < 1 )) && J=1; fi
echo "=== Slicer CTest (spec=$(basename "$SPEC") model=$MODEL arch=$ARCH j=$J topdir=$RPMBUILD) ==="
rpmbuild -bc --with testing --define "_topdir $RPMBUILD" --define "_smp_mflags -j${J}" "$SPEC"
BT="$(find "$RPMBUILD/BUILD" -maxdepth 3 -type d -path '*/Slicer-*/redhat-linux-build' 2>/dev/null | sort | tail -1)"
[[ -n "$BT" && -f "$BT/CTestTestfile.cmake" ]] || { echo "no test build tree found" >&2; exit 1; }
echo "--- build tree: $BT ---"
cp -f "$DRIVER_DIR/CTestConfig.cmake" "$BT/CTestConfig.cmake"
CTEST_STEPS=(-D "${MODEL}Start" -D "${MODEL}Test" -D "${MODEL}Submit")
_xw="$(ls -1t /run/user/$(id -u)/.mutter-Xwaylandauth.* 2>/dev/null | head -1)"
[[ -z "$_xw" && -f "$HOME/.Xauthority" ]] && _xw="$HOME/.Xauthority"
_hw=0
if [[ -e /tmp/.X11-unix/X0 && -n "$_xw" ]] && \
   DISPLAY=:0 XAUTHORITY="$_xw" glxinfo 2>/dev/null | grep -iE "OpenGL renderer" | grep -qivE "llvmpipe|softpipe|swrast"; then _hw=1; fi
if [[ "$_hw" == 1 ]]; then
  echo "--- hardware GL on :0 ($(DISPLAY=:0 XAUTHORITY="$_xw" glxinfo 2>/dev/null | grep -i 'OpenGL renderer' | sed 's/.*: //')) ---"
  DISPLAY=:0 XAUTHORITY="$_xw" ctest --test-dir "$BT" "${CTEST_STEPS[@]}" -j "$J" || true
else
  echo "--- xvfb software GL ---"
  xvfb-run -a -s "-screen 0 1920x1080x24" ctest --test-dir "$BT" "${CTEST_STEPS[@]}" -j "$J" || true
fi
ARCH_DIR="$HOME/.local/state/slicer-ctest/triage"; mkdir -p "$ARCH_DIR"; ts="$(date -u +%Y%m%dT%H%M%SZ)"
_lt="$(find "$BT/Testing" -name LastTest.log 2>/dev/null | head -1)"
_lf="$(find "$BT/Testing" -name LastTestsFailed.log 2>/dev/null | head -1)"
[[ -n "$_lt" ]] && cp "$_lt" "$ARCH_DIR/LastTest-$ts.log"
[[ -n "$_lf" ]] && cp "$_lf" "$ARCH_DIR/LastTestsFailed-$ts.log"
ls -1t "$ARCH_DIR"/LastTest-*.log 2>/dev/null | tail -n +11 | xargs -r rm -f
ls -1t "$ARCH_DIR"/LastTestsFailed-*.log 2>/dev/null | tail -n +11 | xargs -r rm -f
echo "=== done -> my.cdash.org/index.php?project=neurofedora ==="
RUNCTEST

cat > "$DRIVER_DIR/slicer-ext-smoke.sh" <<'EXTSMOKE'
#!/usr/bin/env bash
# slicer-ext-smoke.sh — per-node 3D Slicer *extension* load-smoke for the farm.
#
# The farm's main job (run-slicer-ctest.sh) BUILDS core Slicer and runs its
# built-in ctest against the build tree — it never validates the packaged
# EXTENSION set. This closes that gap on EVERY farm node: install the COPR Slicer
# + extension packages, launch Slicer headless, and assert each installed
# extension registers at least one of its modules (catches an extension that
# built green but installed into a stale Slicer-X.Y path the launcher never scans,
# or whose scripted module raised on load).
#
# SELF-CONTAINED: the module check is inline, so this runs on a bare container /
# curl|bash node with nothing but the driver script. If the CDash driver files
# (neurofedora-slicer.cmake + tests-slicer/) are ALSO present (legion), it
# additionally submits the richer smoke to my.cdash.org/neurofedora.
#
# Network is required (COPR install) — this runs on the host, OUTSIDE mock.
#   slicer-ext-smoke.sh [Experimental|Nightly]      (default Experimental)
set -uo pipefail

MODEL="${1:-Experimental}"
DRIVER_DIR="$(dirname "$(readlink -f "$0")")"

# Which Slicer track: match whatever the farm builds, else stable.
CORE=3dslicer
case "${SLICER_CTEST_SPEC:-}" in *preview*) CORE=slicer-preview ;; esac

# Canonical package->module map (keep in sync with
# neurofedora/tests/slicer/run-slicer-selftest.sh). '|' = alternatives; a group
# passes if ANY alternative registers.
declare -A MAP=(
    [3dslicer-elastix]="Elastix"
    [3dslicer-totalsegmentator]="TotalSegmentator"
    [3dslicer-monailabel]="MONAILabelReviewer|MONAILabel"
    [3dslicer-openlifu]="OpenLIFUHome|OpenLIFUData"
    [3dslicer-spharm-pdm]="ShapeAnalysisModule|SPHARM-PDM"
    [3dslicer-srep]="SRep|SRepCreator"
    [3dslicer-openigtlink]="OpenIGTLinkIF|OpenIGTLinkRemote"
    [3dslicer-dmri]="TractographyDisplay|DWIToDTIEstimation"
    [3dslicer-igt]="FiducialRegistrationWizard|Watchdog|PivotCalibration|VolumeResliceDriver|BreachWarning"
    [3dslicer-rt]="DicomRtImportExport|DoseVolumeHistogram"
    [3dslicer-jupyter]="JupyterKernel"
)

echo "==> ext-smoke: ensuring COPR + installing $CORE + available extensions" >&2
sudo dnf -y copr enable mhough/neurofedora 2>/dev/null || true
inst=("$CORE")
for e in "${!MAP[@]}"; do
    dnf -q info "$e" >/dev/null 2>&1 && inst+=("$e")
done
echo "==> installing: ${inst[*]}" >&2
sudo dnf -y install "${inst[@]}" || { echo "ext-smoke: install failed" >&2; exit 1; }

# Expected-module groups for whatever actually installed.
expect=""
for r in "${!MAP[@]}"; do
    rpm -q --quiet "$r" 2>/dev/null || continue
    expect+="${expect:+;}${MAP[$r]}"
done
export SLICER_EXPECT_MODULES="$expect"
echo "==> ext-smoke expecting: ${expect:-<none installed>}" >&2

LAUNCHER="$(command -v Slicer || true)"
[[ -z "$LAUNCHER" ]] && { echo "ext-smoke: Slicer launcher not found after install" >&2; exit 1; }

# Inline, self-contained headless check (no external smoke files needed).
tmp_py="$(mktemp --suffix=.py)"
trap 'rm -f "$tmp_py"' EXIT
cat > "$tmp_py" <<'PYEOF'
import os, sys, slicer
reg = set(slicer.app.moduleManager().modulesNames())
fails = []
def chk(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""), flush=True)
    if not ok: fails.append(label)
chk("loadable-modules-present", len(reg) > 0, f"{len(reg)} modules")
for core in ("Data", "Volumes", "Models"):
    chk(f"core-module-{core}", core in reg)
for group in [g for g in os.environ.get("SLICER_EXPECT_MODULES", "").split(";") if g]:
    alts = [m for m in group.split("|") if m]
    hit = next((m for m in alts if m in reg), None)
    chk(f"extension-group-{alts[0]}", hit is not None,
        f"matched {hit}" if hit else f"none of {alts} registered")
print(f"\n[SLICER-EXT-SMOKE] {'FAIL' if fails else 'PASS'} ({len(fails)} failure(s))"
      + (": " + ", ".join(fails) if fails else ""), flush=True)
sys.exit(1 if fails else 0)
PYEOF

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
timeout "${SLICER_SELFTEST_TIMEOUT:-300}" "$LAUNCHER" \
    --no-splash --no-main-window --ignore-slicerrc \
    --python-script "$tmp_py" --exit-after-startup
rc=$?

# Bonus: if the full CDash smoke driver is present (legion), submit the richer
# extension-aware smoke to my.cdash.org/neurofedora too.
if [[ -f "$DRIVER_DIR/neurofedora-slicer.cmake" && -d "$DRIVER_DIR/tests-slicer" ]]; then
    echo "==> ext-smoke: submitting CDash extension smoke" >&2
    ctest -V -S "$DRIVER_DIR/neurofedora-slicer.cmake" \
          -DDASHBOARD_MODEL="$MODEL" -DPARALLEL="${SLICER_CTEST_J:-4}" || true
fi

exit "$rc"
EXTSMOKE

cat > "$DRIVER_DIR/slicer-ctest-loop.sh" <<'LOOP'
#!/usr/bin/env bash
set -uo pipefail
DRIVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RPMBUILD="${RPMBUILD:-$HOME/rpmbuild}"
MODEL="${SLICER_MODEL:-Nightly}"; COOLDOWN="${SLICER_COOLDOWN:-600}"
STATE="$HOME/.local/state/slicer-ctest"; mkdir -p "$STATE"
if [[ -n "${SLICER_SPEC:-}" ]]; then SPEC="$SLICER_SPEC"
elif [[ -f "$RPMBUILD/SPECS/slicer-preview.spec" ]]; then SPEC="slicer-preview.spec"
else SPEC="3dslicer.spec"; fi
echo "[loop] spec=$SPEC model=$MODEL cooldown=${COOLDOWN}s topdir=$RPMBUILD"
while true; do
  ts="$(date -u +%Y%m%dT%H%M%SZ)"; log="$STATE/cycle-$ts.log"
  echo "[loop] $ts starting cycle -> $log"
  SLICER_CTEST_SPEC="$SPEC" "$DRIVER_DIR/run-slicer-ctest.sh" "$MODEL" >"$log" 2>&1
  echo "[loop] $ts cycle exit=$?"
  # Per-node extension load-smoke (install COPR Slicer+extensions, assert modules
  # register). Non-fatal — must not stop the 24/7 build loop.
  if [[ -x "$DRIVER_DIR/slicer-ext-smoke.sh" ]]; then
    ext_log="$STATE/extsmoke-$ts.log"
    SLICER_CTEST_SPEC="$SPEC" "$DRIVER_DIR/slicer-ext-smoke.sh" "$MODEL" >"$ext_log" 2>&1
    echo "[loop] $ts ext-smoke exit=$?"
  fi
  ls -1t "$STATE"/cycle-*.log 2>/dev/null | tail -n +21 | xargs -r rm -f
  ls -1t "$STATE"/extsmoke-*.log 2>/dev/null | tail -n +21 | xargs -r rm -f
  sleep "$COOLDOWN"
done
LOOP
chmod +x "$DRIVER_DIR"/*.sh

# --- 7. systemd service (isolated RPMBUILD, unconfined, /bin/bash exec) -------
echo "--- installing + starting slicer-ctest.service ---"
sudo tee /etc/systemd/system/slicer-ctest.service >/dev/null <<UNIT
[Unit]
Description=neurofedora Slicer CTest farm node ($TRACK) -> my.cdash.org
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
SELinuxContext=unconfined_u:unconfined_r:unconfined_t:s0
WorkingDirectory=$FARM_ROOT
Environment=RPMBUILD=$RPMTREE
Environment=SLICER_SPEC=$SPEC
Environment=SLICER_MODEL=Nightly
Environment=SLICER_COOLDOWN=600
Environment=ExternalData_OBJECT_STORES=$RUN_HOME/.cache/slicer-externaldata
ExecStart=/bin/bash $DRIVER_DIR/slicer-ctest-loop.sh
Restart=always
RestartSec=30
Nice=10
IOSchedulingClass=idle

[Install]
WantedBy=multi-user.target
UNIT

mkdir -p "$RUN_HOME/.cache/slicer-externaldata"
sudo systemctl daemon-reload
sudo systemctl enable --now slicer-ctest.service

cat <<EOF

==============================================================================
 JOINED. $(hostname) is now a $TRACK farm node building 24/7 (isolated tree).
   watch:    journalctl -u slicer-ctest.service -f
             tail -f ~/.local/state/slicer-ctest/cycle-*.log
   results:  https://my.cdash.org/index.php?project=neurofedora  (site $(hostname))
   stop:     sudo systemctl disable --now slicer-ctest.service
 First build ~7-9 h; results post at the end of each cycle.
==============================================================================
EOF
