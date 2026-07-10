#!/usr/bin/env bash
# Container entrypoint: one full CTest cycle (or loop) against the CURRENT COPR
# Slicer SRPM, submitting to my.cdash.org/neurofedora. Runs as root INSIDE the
# container — all mutations are contained; the host is untouched.
#
#   podman run --rm            ghcr.io/m9h/slicer-ctest-farm stable    # one cycle
#   podman run -d -e FARM_LOOP=1 ghcr.io/m9h/slicer-ctest-farm preview # 24/7
#   ... -h "$(hostname)"   -> report to CDash under the host's name
#   ... --device /dev/dri -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix  -> HW GL
set -euo pipefail
TRACK="${1:-stable}"
case "$TRACK" in
  stable)  PKG=3dslicer;       SPEC=3dslicer.spec ;;
  preview) PKG=slicer-preview; SPEC=slicer-preview.spec ;;
  *) echo "track must be stable|preview" >&2; exit 2 ;;
esac
MODEL="${SLICER_MODEL:-Nightly}"
export RPMBUILD="${RPMBUILD:-/root/rpmbuild}"
rpmdev-setuptree

run_cycle() {
  local t; t="$(mktemp -d)"; cd "$t"
  echo "--- fetching current $PKG SRPM from COPR ---"
  dnf download --source "$PKG"
  rpm -Uvh --nodeps --define "_topdir $RPMBUILD" ./"$PKG"-*.src.rpm
  if ! grep -q '%bcond.*testing' "$RPMBUILD/SPECS/$SPEC"; then
    echo "error: COPR $PKG predates the CTest 'testing' bcond — retry after the owner rebuilds it" >&2
    exit 1
  fi
  echo "--- builddep (inside container; host VTK untouched) ---"
  dnf -y builddep --allowerasing "$RPMBUILD/SPECS/$SPEC"
  SLICER_CTEST_SPEC="$SPEC" /opt/farm/run-slicer-ctest.sh "$MODEL"
  cd /; rm -rf "$t"
}

if [ "${FARM_LOOP:-0}" = 1 ]; then
  while true; do run_cycle || echo "[cycle failed; continuing]"; sleep "${FARM_COOLDOWN:-600}"; done
else
  run_cycle
fi
