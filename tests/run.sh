#!/usr/bin/env bash
# run.sh — orchestrator: install (if needed), regenerate tests, run smoke.
#
# Usage:
#   ./run.sh                # install + regen + bats
#   ./run.sh --no-install   # skip install (just regen + test)
#   ./run.sh --parallel N   # run bats with --jobs N (default: nproc)
#   ./run.sh --junit DIR    # write JUnit XML to DIR for CI ingestion
#   ./run.sh --tap          # plain TAP output (no pretty formatter)

set -euo pipefail

HERE="$(dirname "$(readlink -f "$0")")"
NO_INSTALL=0
JOBS=$(nproc)
JUNIT_DIR=""
FORMATTER="--pretty"

while (( $# > 0 )); do
    case "$1" in
        --no-install) NO_INSTALL=1; shift ;;
        --parallel)   JOBS="$2"; shift 2 ;;
        --junit)      JUNIT_DIR="$2"; FORMATTER="--formatter junit"; shift 2 ;;
        --tap)        FORMATTER="--formatter tap"; shift ;;
        -h|--help)    sed -n '2,11p' "$0"; exit 0 ;;
        *) echo "unknown flag: $1" >&2; exit 1 ;;
    esac
done

if (( NO_INSTALL == 0 )); then
    echo "==> install"
    "${HERE}/install.sh"
fi

echo "==> regenerate smoke.bats from packages.tsv"
"${HERE}/generate-tests.sh"

echo "==> bats (jobs=$JOBS)"
EXTRA=""
if [[ -n "$JUNIT_DIR" ]]; then
    mkdir -p "$JUNIT_DIR"
    EXTRA="--output $JUNIT_DIR"
fi
# Run every .bats file in this directory — smoke.bats (per-package),
# collisions.bats (file-conflict guard), and any future *.bats added.
# shellcheck disable=SC2086
exec bats --jobs "$JOBS" $FORMATTER $EXTRA "${HERE}"/*.bats
