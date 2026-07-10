#!/usr/bin/env bash
# container-entry.sh — ENTRYPOINT inside the neurofedora-farm image.
#
# Runs one (or a continuous loop of) Fedora-config Slicer CTest cycle(s) and
# submits to my.cdash.org/neurofedora, entirely inside the rootless container.
# It refreshes to the CURRENT COPR source RPM first (the image may have been
# built days ago) and then hands off to the SAME driver scripts the bare-metal
# farm uses — run-slicer-ctest.sh / slicer-ctest-loop.sh — so there is exactly
# one implementation of the build+test+submit logic.
#
# Driven entirely by env (set by farm-run.sh):
#   TRACK=stable|preview   MODE=oneshot|loop   SLICER_MODEL=Nightly|Experimental
#   SLICER_CTEST_SUBMIT=0  -> validate without publishing to CDash
#   SLICER_CTEST_J=N       -> parallelism (default: nproc-2)
#   SLICER_COOLDOWN=SECS   -> loop cooldown between cycles
set -euo pipefail

export RPMBUILD="${RPMBUILD:-/root/rpmbuild}"
DRIVER_DIR=/opt/cdash-driver
TRACK="${TRACK:-stable}"
MODE="${MODE:-oneshot}"

case "$TRACK" in
  preview) PKG=slicer-preview; SPEC=slicer-preview.spec ;;
  stable)  PKG=3dslicer;       SPEC=3dslicer.spec ;;
  *) echo "error: unknown TRACK=$TRACK (use stable|preview)" >&2; exit 2 ;;
esac

echo "=== container-entry: track=$TRACK pkg=$PKG mode=$MODE site=$(hostname) ==="

# --- refresh to the CURRENT COPR source RPM ---------------------------------
# The baked image pinned whatever SRPM existed at build time; pull the latest so
# a long-lived image still tests today's spec/commit without a rebuild.
mkdir -p "$RPMBUILD"/{SPECS,SOURCES,BUILD,BUILDROOT,RPMS,SRPMS}
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
( cd "$tmp"
  echo "--- fetching current $PKG source RPM from COPR ---"
  dnf download --source "$PKG" 2>/dev/null || {
    echo "error: 'dnf download --source $PKG' failed — is the COPR SRPM published" >&2
    echo "       for $(uname -m)/fc$(rpm -E %fedora)?" >&2; exit 1; }
  rpm -Uvh --nodeps --define "_topdir $RPMBUILD" ./"$PKG"-*.src.rpm )

[ -f "$RPMBUILD/SPECS/$SPEC" ] || { echo "error: $SPEC not installed from SRPM" >&2; exit 1; }
grep -q '%bcond.*testing' "$RPMBUILD/SPECS/$SPEC" || {
  echo "error: $SPEC has no 'testing' bcond — this COPR build predates CTest support." >&2
  exit 1; }

# Top up build deps in case the spec's BuildRequires shifted since the image was
# baked. No-op (fast) when already satisfied.
dnf -y builddep --allowerasing "$RPMBUILD/SPECS/$SPEC" >/dev/null 2>&1 || true

# --- hand off to the shared driver -----------------------------------------
export SLICER_CTEST_SPEC="$SPEC" SLICER_SPEC="$SPEC"
if [[ "$MODE" == loop ]]; then
  exec "$DRIVER_DIR/slicer-ctest-loop.sh"
else
  exec "$DRIVER_DIR/run-slicer-ctest.sh" "${SLICER_MODEL:-Nightly}"
fi
