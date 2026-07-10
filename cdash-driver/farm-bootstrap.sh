#!/usr/bin/env bash
# farm-bootstrap.sh — join the neurofedora Slicer CTest build farm.
#
# One command turns any Fedora 44+ box into a farm node: it builds the *Fedora*
# Slicer config with BUILD_TESTING=ON and submits the CTest results to
# my.cdash.org/index.php?project=neurofedora, continuously, as a systemd service.
#
# It needs only OUTBOUND https (to COPR + my.cdash.org) — no inbound access, no
# VPN, no shared LAN. This is the standard CDash distributed-dashboard model
# (how VTK/ITK/CMake collect nightly results from volunteers worldwide).
#
# Usage:
#   ./farm-bootstrap.sh [stable|preview]     # default: stable (3dslicer 5.12)
#   ./farm-bootstrap.sh preview              # slicer-preview 5.13 (main HEAD)
#
# Requirements: Fedora 44+ (x86_64 or aarch64), sudo, ~40 GB free, internet.
# Safe to re-run (idempotent-ish): re-enables the repo, refreshes the driver,
# restarts the service.
set -euo pipefail

TRACK="${1:-stable}"
case "$TRACK" in
  stable)  PKG=3dslicer;      SPEC=3dslicer.spec ;;
  preview) PKG=slicer-preview; SPEC=slicer-preview.spec ;;
  *) echo "usage: $0 [stable|preview]" >&2; exit 2 ;;
esac

RUN_USER="$(id -un)"
RUN_HOME="$HOME"
DRIVER_DIR="$RUN_HOME/rpmbuild/cdash-driver"

echo "=============================================================="
echo " neurofedora farm bootstrap — track=$TRACK pkg=$PKG"
echo " user=$RUN_USER host=$(hostname) arch=$(uname -m) fedora=$(rpm -E %fedora)"
echo "=============================================================="

# --- 0. preflight ----------------------------------------------------------
[ "$(rpm -E %fedora)" -ge 44 ] || { echo "error: need Fedora 44+"; exit 1; }
command -v sudo >/dev/null || { echo "error: sudo required"; exit 1; }
avail_gb=$(df -BG --output=avail "$RUN_HOME" | tail -1 | tr -dc '0-9')
[ "${avail_gb:-0}" -ge 30 ] || echo "warning: <30 GB free in $RUN_HOME; the build tree needs room"

# --- 1. COPR + build toolchain --------------------------------------------
echo "--- enabling mhough/neurofedora COPR + installing toolchain ---"
sudo dnf -y copr enable mhough/neurofedora
sudo dnf -y install rpm-build rpmdevtools cmake ninja-build gcc-c++ gcc-gfortran \
    git-core xorg-x11-server-Xvfb glx-utils chrpath mesa-dri-drivers dnf-plugins-core
rpmdev-setuptree

# --- 2. resolve the Fedora vtk 9.5 -> COPR 9.6 conflict --------------------
# COPR ships vtk 9.6 (same libvtk*.so.1 SONAME as Fedora 9.5 => cannot coinstall).
# vtk-java pins the 9.5 SONAMEs and has no COPR build, so it must be removed.
rpm -q vtk-java >/dev/null 2>&1 && sudo dnf -y remove vtk-java || true

# --- 3. fetch the CURRENT spec + sources from the COPR SRPM ----------------
# The SRPM bundles the spec (with the `--with testing` bcond), all Source
# tarballs, and patches. dnf download --source pulls the latest published SRPM.
echo "--- downloading $PKG source RPM from COPR ---"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
( cd "$tmp"
  if ! dnf download --source "$PKG" 2>/dev/null; then
    echo "error: 'dnf download --source $PKG' failed."
    echo "  The COPR $PKG SRPM may not be published for $(uname -m)/fc$(rpm -E %fedora)."
    echo "  Check https://copr.fedorainfracloud.org/coprs/mhough/neurofedora/"
    exit 1
  fi
  rpm -Uvh --nodeps ./"$PKG"-*.src.rpm )

# Verify the spec actually carries the testing bcond (older SRPMs don't).
if ! grep -q '%bcond.*testing' "$RUN_HOME/rpmbuild/SPECS/$SPEC"; then
  echo "error: $SPEC has no 'testing' bcond — the COPR build predates the CTest"
  echo "  support. Ask the farm owner to rebuild $PKG on COPR, then re-run this."
  exit 1
fi

# --- 4. build dependencies (swaps in COPR vtk 9.6, pulls ITK5/ctk/PythonQt) -
echo "--- installing build dependencies (this replaces Fedora vtk 9.5 with 9.6) ---"
sudo dnf -y builddep --allowerasing "$RUN_HOME/rpmbuild/SPECS/$SPEC"

# --- 5. runtime deps the tests need (mirror the shipped RPM's Requires) ----
# The CTest suite loads Slicer's Python; without these, a chunk of py_ tests fail
# on import (vtkAddonPython / dicomweb_client / cgi).
sudo dnf -y install python3-vtkAddon python3-dicomweb-client python3-highdicom \
    python3-legacy-cgi || true

# --- 6. install the CTest driver + loop + CDash config ---------------------
echo "--- installing driver into $DRIVER_DIR ---"
mkdir -p "$DRIVER_DIR"

cat > "$DRIVER_DIR/CTestConfig.cmake" <<'CTESTCONFIG'
set(CTEST_PROJECT_NAME "neurofedora")
set(CTEST_NIGHTLY_START_TIME "01:00:00 UTC")
set(CTEST_DROP_METHOD "https")
set(CTEST_DROP_SITE "my.cdash.org")
set(CTEST_DROP_LOCATION "/submit.php?project=neurofedora")
set(CTEST_DROP_SITE_CDASH TRUE)
CTESTCONFIG

# NOTE: the RUNCTEST/LOOP heredocs are quoted ('...') so they are written
# verbatim — the node's shell expands their $(...) / ${...} at run time, not now.
cat > "$DRIVER_DIR/run-slicer-ctest.sh" <<'RUNCTEST'
#!/usr/bin/env bash
# run-slicer-ctest.sh — one CTest cycle of the Fedora Slicer build -> CDash.
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
echo "=== Slicer CTest (spec=$(basename "$SPEC") model=$MODEL arch=$ARCH j=$J) ==="
rpmbuild -bc --with testing --define "_smp_mflags -j${J}" "$SPEC"
BT="$(find "$RPMBUILD/BUILD" -maxdepth 3 -type d -path '*/Slicer-*/redhat-linux-build' 2>/dev/null | sort | tail -1)"
[[ -n "$BT" && -f "$BT/CTestTestfile.cmake" ]] || { echo "no test build tree found" >&2; exit 1; }
echo "--- build tree: $BT ---"
cp -f "$DRIVER_DIR/CTestConfig.cmake" "$BT/CTestConfig.cmake"
CTEST_STEPS=(-D "${MODEL}Start" -D "${MODEL}Test" -D "${MODEL}Submit")
# Prefer real hardware GL on a live :0 session; else xvfb software GL.
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

cat > "$DRIVER_DIR/slicer-ctest-loop.sh" <<'LOOP'
#!/usr/bin/env bash
# slicer-ctest-loop.sh — run run-slicer-ctest.sh continuously (24/7).
set -uo pipefail
DRIVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${SLICER_MODEL:-Nightly}"; COOLDOWN="${SLICER_COOLDOWN:-600}"
STATE="$HOME/.local/state/slicer-ctest"; mkdir -p "$STATE"
if [[ -n "${SLICER_SPEC:-}" ]]; then SPEC="$SLICER_SPEC"
elif [[ -f "$HOME/rpmbuild/SPECS/slicer-preview.spec" ]]; then SPEC="slicer-preview.spec"
else SPEC="3dslicer.spec"; fi
echo "[loop] spec=$SPEC model=$MODEL cooldown=${COOLDOWN}s"
while true; do
  ts="$(date -u +%Y%m%dT%H%M%SZ)"; log="$STATE/cycle-$ts.log"
  echo "[loop] $ts starting cycle -> $log"
  SLICER_CTEST_SPEC="$SPEC" "$DRIVER_DIR/run-slicer-ctest.sh" "$MODEL" >"$log" 2>&1
  echo "[loop] $ts cycle exit=$?"
  ls -1t "$STATE"/cycle-*.log 2>/dev/null | tail -n +21 | xargs -r rm -f
  sleep "$COOLDOWN"
done
LOOP

chmod +x "$DRIVER_DIR"/*.sh

# --- 7. systemd service (unconfined SELinux + /bin/bash exec of a $HOME script) -
echo "--- installing + starting slicer-ctest.service ---"
sudo tee /etc/systemd/system/slicer-ctest.service >/dev/null <<UNIT
[Unit]
Description=neurofedora Slicer CTest farm node ($TRACK) -> my.cdash.org
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
# Dedicated build node: run unconfined so rpmbuild/ctest + the \$HOME driver
# script aren't blocked by SELinux service confinement (203/EXEC otherwise).
SELinuxContext=unconfined_u:unconfined_r:unconfined_t:s0
WorkingDirectory=$RUN_HOME/rpmbuild
Environment=SLICER_SPEC=$SPEC
Environment=SLICER_MODEL=Nightly
Environment=SLICER_COOLDOWN=600
Environment=ExternalData_OBJECT_STORES=$RUN_HOME/.cache/slicer-externaldata
# systemd cannot exec a user_home_t script directly; exec /bin/bash (bin_t) on it.
ExecStart=/bin/bash $RUN_HOME/rpmbuild/cdash-driver/slicer-ctest-loop.sh
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

echo
echo "=============================================================="
echo " JOINED. $(hostname) is now a $TRACK farm node building 24/7."
echo " Watch it:   journalctl -u slicer-ctest.service -f"
echo "             tail -f ~/.local/state/slicer-ctest/cycle-*.log"
echo " Results:    https://my.cdash.org/index.php?project=neurofedora"
echo "             (this host appears as site '$(hostname)')"
echo " First build takes ~7-9h; results post at the end of each cycle."
echo "=============================================================="
