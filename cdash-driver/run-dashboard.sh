#!/usr/bin/env bash
# run-dashboard.sh — submit neurofedora smoke tests to CDash.
#
# Usage:
#   ./run-dashboard.sh [Experimental|Continuous|Nightly]   # default: Experimental
#
# Runs VTK then ITK serially. Caps parallelism at 8 cores per the
# legion resource policy (one build at a time, half the box).
#
# Prerequisites:
#   - vtk-devel, InsightToolkit5-devel installed (skipped if absent)
#   - A "neurofedora" project on https://my.cdash.org or override CDASH_HOST below
#   - Network reachability to the CDash submission endpoint

set -euo pipefail

MODEL="${1:-Experimental}"
DRIVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARALLEL="${CDASH_PARALLEL:-8}"

case "$MODEL" in
  Experimental|Continuous|Nightly) ;;
  *) echo "error: model must be Experimental, Continuous, or Nightly" >&2
     exit 2 ;;
esac

run_one() {
  local name="$1" devel_pkg="$2" script="$3"
  if ! rpm -q "$devel_pkg" >/dev/null 2>&1; then
    printf '\n[skip] %s: %s not installed\n' "$name" "$devel_pkg"
    return 0
  fi
  printf '\n=== %s dashboard (model=%s, j=%s) ===\n' "$name" "$MODEL" "$PARALLEL"
  ctest -V -S "${DRIVER_DIR}/${script}" \
        -DDASHBOARD_MODEL="$MODEL" \
        -DPARALLEL="$PARALLEL"
}

cd "$DRIVER_DIR"

run_one VTK          vtk-devel                  neurofedora-vtk.cmake
run_one ITK          InsightToolkit5-devel      neurofedora-itk.cmake
run_one ITK6         InsightToolkit6-devel      neurofedora-itk6.cmake
run_one SimpleITK    python3-simpleitk          neurofedora-simpleitk.cmake
run_one ANTs         ANTs                       neurofedora-ants.cmake
run_one elastix      elastix                    neurofedora-elastix.cmake
run_one vmtk         python3-vmtk               neurofedora-vmtk.cmake
run_one ParaView     paraview                   neurofedora-paraview.cmake
run_one VTK-extended vtk-testing                neurofedora-vtk-extended.cmake
run_one ITK-examples InsightToolkit5-examples   neurofedora-itk-examples.cmake
run_one Slicer       3dslicer                   neurofedora-slicer.cmake

printf '\nAll done.\n'
