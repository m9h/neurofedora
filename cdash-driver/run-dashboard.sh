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
  # Tolerate component failure: a configure/build error makes `ctest -S` exit
  # non-zero, which under `set -e` would abort the ENTIRE nightly and blank the
  # rest of the dashboard. The failure is already recorded on CDash, so log it
  # locally and keep going. (Using `if` disables errexit for this command.)
  if ! ctest -V -S "${DRIVER_DIR}/${script}" \
        -DDASHBOARD_MODEL="$MODEL" \
        -DPARALLEL="$PARALLEL"; then
    printf '[warn] %s: ctest exited non-zero (configure/build error — see CDash); continuing\n' "$name"
  fi
}

# Like run_one, but loads an MPI environment-modules flavour first so
# find_package(VTK) resolves the MPI VTK config and the matching mpiexec is on
# PATH. Runs in a subshell so the module state doesn't leak to later components.
run_one_mpi() {
  local name="$1" devel_pkg="$2" script="$3" flavour="${4:-mpich}"
  local arch; arch="$(uname -m)"
  if ! rpm -q "$devel_pkg" >/dev/null 2>&1; then
    printf '\n[skip] %s: %s not installed\n' "$name" "$devel_pkg"
    return 0
  fi
  printf '\n=== %s dashboard (model=%s, flavour=%s, j=%s) ===\n' \
         "$name" "$MODEL" "$flavour" "$PARALLEL"
  # Same failure-tolerance as run_one (see note there): don't let one component
  # abort the nightly. The subshell isolates the module env.
  if ! (
    # shellcheck disable=SC1091
    source /etc/profile.d/modules.sh
    module load "mpi/${flavour}-${arch}"
    ctest -V -S "${DRIVER_DIR}/${script}" \
          -DDASHBOARD_MODEL="$MODEL" \
          -DPARALLEL="$PARALLEL" \
          -DMPI_FLAVOUR="$flavour"
  ); then
    printf '[warn] %s: ctest exited non-zero (configure/build error — see CDash); continuing\n' "$name"
  fi
}

cd "$DRIVER_DIR"

run_one VTK          vtk-devel                  neurofedora-vtk.cmake
run_one VTK-python   python3-vtk                neurofedora-vtk-python.cmake
run_one_mpi VTK-MPI  vtk-mpich-devel            neurofedora-vtk-mpi.cmake   mpich
run_one ITK          InsightToolkit5-devel      neurofedora-itk.cmake
run_one ITK6         InsightToolkit6-devel      neurofedora-itk6.cmake
run_one SimpleITK    python3-simpleitk          neurofedora-simpleitk.cmake
run_one ANTs         ANTs                       neurofedora-ants.cmake
run_one elastix      elastix                    neurofedora-elastix.cmake
run_one vmtk         python3-vmtk               neurofedora-vmtk.cmake
run_one ParaView     paraview                   neurofedora-paraview.cmake
run_one VTK-extended vtk-testing                neurofedora-vtk-extended.cmake
run_one ITK-examples InsightToolkit5-examples   neurofedora-itk-examples.cmake
# Extension-module expectations for the Slicer smoke component (slicer_smoke.py
# section 6): one ';'-separated GROUP per INSTALLED 3dslicer-<ext>, '|' alternatives
# within a group. The Slicer smoke then fails if an installed extension's module does
# not register. Keep this map in sync with the BATS canonical copy in
# neurofedora/tests/slicer/run-slicer-selftest.sh.
declare -A _SLICER_EXT_MODULES=(
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
_slicer_expect=""
for _rn in "${!_SLICER_EXT_MODULES[@]}"; do
    rpm -q --quiet "$_rn" 2>/dev/null || continue
    _slicer_expect+="${_slicer_expect:+;}${_SLICER_EXT_MODULES[$_rn]}"
done
export SLICER_EXPECT_MODULES="$_slicer_expect"
printf '\n[info] Slicer smoke expecting extension modules: %s\n' "${_slicer_expect:-<none installed>}"
run_one Slicer       3dslicer                   neurofedora-slicer.cmake

printf '\nAll done.\n'
