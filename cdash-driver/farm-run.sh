#!/usr/bin/env bash
# farm-run.sh — run a neurofedora Slicer CTest node on ANY host, ROOTLESS.
#
# The host-neutral counterpart to farm-bootstrap.sh. Where farm-bootstrap.sh is
# a DEDICATED-BOX action (it swaps the host's system VTK, removes vtk-java, and
# installs a 24/7 root systemd service), this runs the entire build+test+submit
# inside a rootless podman container. The host is never modified — it only needs
# `podman`. Default mode is a SINGLE cycle; nothing persists.
#
# Usage:
#   ./farm-run.sh [--track stable|preview] [--oneshot|--loop] [options]
#
#   --track T        stable = 3dslicer 5.12 (default) ; preview = slicer-preview 5.13
#   --oneshot        run one CTest cycle and exit (DEFAULT)
#   --loop           run continuously (like the bare-metal service); implies --detach unless -f
#   -f, --foreground keep --loop attached to this terminal instead of detaching
#   --no-submit      run tests but do NOT publish to my.cdash.org (local validation)
#   --site NAME      dashboard site name (default: <hostname>-container)
#   --model M        Nightly (default) | Experimental
#   -j N             build/test parallelism (default inside container: nproc-2)
#   --build-image    (re)build the image even if it already exists
#   --pull           pass --pull=newer to the image build (refresh the Fedora base)
#   -n, --dry-run    print the podman build/run commands, do nothing
#   -h, --help       this help
#
# First run builds the image (base + COPR VTK 9.6 + all Slicer BuildRequires,
# baked once). The first BUILD CYCLE is long (~7-9 h). Subsequent --oneshot runs
# reuse the image and just recompile.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_REPO="localhost/neurofedora-farm"

TRACK=stable
MODE=oneshot
DETACH=auto            # for --loop: auto -> detach; -f forces foreground
SUBMIT=1
SITE=""
MODEL="${SLICER_MODEL:-Nightly}"
JOBS="${SLICER_CTEST_J:-}"
COOLDOWN="${SLICER_COOLDOWN:-600}"
FORCE_BUILD=0
PULL=0
DRY=0

die(){ echo "error: $*" >&2; exit 2; }
usage(){ sed -n '2,/^set -euo/p' "$0" | sed '$d;s/^# \{0,1\}//'; exit "${1:-0}"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --track)   TRACK="${2:?}"; shift 2 ;;
    --oneshot) MODE=oneshot; shift ;;
    --loop)    MODE=loop; shift ;;
    -f|--foreground) DETACH=no; shift ;;
    --no-submit) SUBMIT=0; shift ;;
    --site)    SITE="${2:?}"; shift 2 ;;
    --model)   MODEL="${2:?}"; shift 2 ;;
    -j)        JOBS="${2:?}"; shift 2 ;;
    --build-image) FORCE_BUILD=1; shift ;;
    --pull)    PULL=1; shift ;;
    -n|--dry-run) DRY=1; shift ;;
    -h|--help) usage 0 ;;
    *) die "unknown argument: $1 (see --help)" ;;
  esac
done

case "$TRACK" in stable|preview) ;; *) die "--track must be stable or preview" ;; esac
command -v podman >/dev/null || die "podman is required (this is the whole point — no host RPMs touched)"
[ -f "$HERE/Containerfile" ] || die "Containerfile not found next to farm-run.sh"

IMG="$IMAGE_REPO:$TRACK"
[ -n "$SITE" ] || SITE="$(hostname)-container"

run(){ echo "+ $*"; [ "$DRY" = 1 ] || "$@"; }

# --- 1. build the image if missing (or forced) ------------------------------
if [ "$FORCE_BUILD" = 1 ] || ! podman image exists "$IMG" 2>/dev/null; then
  echo "=== building $IMG (base + COPR VTK 9.6 + Slicer BuildRequires) ==="
  build_args=(build --build-arg "TRACK=$TRACK" -t "$IMG" -f "$HERE/Containerfile")
  [ "$PULL" = 1 ] && build_args+=(--pull=newer)
  build_args+=("$HERE")
  run podman "${build_args[@]}"
else
  echo "=== reusing existing image $IMG (use --build-image to rebuild) ==="
fi

# --- 2. run the cycle rootless ----------------------------------------------
# --hostname sets the CTest/CDash SITE name (CTest defaults SITE to the hostname).
# The driver dir is bind-mounted read-only so image never goes stale on tweaks.
podman_args=(run --rm
  --hostname "$SITE"
  -e "TRACK=$TRACK" -e "MODE=$MODE" -e "SLICER_MODEL=$MODEL"
  -e "SLICER_CTEST_SUBMIT=$SUBMIT" -e "SLICER_COOLDOWN=$COOLDOWN"
  -v "$HERE:/opt/cdash-driver:ro,Z")
[ -n "$JOBS" ] && podman_args+=(-e "SLICER_CTEST_J=$JOBS")

if [ "$MODE" = loop ] && [ "$DETACH" != no ]; then
  podman_args+=(--detach --name "neurofedora-farm-$TRACK" --restart=always)
fi

echo "=== running $TRACK node: mode=$MODE site=$SITE submit=$SUBMIT model=$MODEL ==="
run podman "${podman_args[@]}" "$IMG"

if [ "$MODE" = loop ] && [ "$DETACH" != no ] && [ "$DRY" != 1 ]; then
  cat <<EOF

detached loop node started: container 'neurofedora-farm-$TRACK'
  watch:  podman logs -f neurofedora-farm-$TRACK
  stop:   podman rm -f neurofedora-farm-$TRACK
  results: https://my.cdash.org/index.php?project=neurofedora  (site $SITE)
EOF
fi
