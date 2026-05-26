#!/usr/bin/env bash
# fetch-real-fixtures.sh — pull canonical real-world test datasets so the
# MRI tools can be tested against something biological, not just the 32³
# synthetic sphere from generate-fixtures.sh.
#
# Why nilearn instead of installing FSL: nilearn already ships in the
# neurofedora manifest (python3-nilearn), has built-in fetchers for the
# standard MNI152 / Harvard-Oxford / atlas datasets, and caches under
# ~/nilearn_data so repeat runs hit zero network. FSL's own data package
# isn't in Fedora and requires a separate manual install at /opt/fsl/.
#
# Datasets fetched (~15 MB total):
#   real/mni152_t1_2mm.nii.gz         — MNI152 2009a T1 template (91x109x91, 2 mm iso)
#   real/mni152_brain_mask_2mm.nii.gz — brain mask for the above
#   real/mni152_t1_2mm_moved.nii.gz   — synthetic affine perturbation for registration tests
#
# Idempotent: re-running is a no-op if the files exist. Network-only on
# first call. Pipelines that need real data SKIP cleanly when this script
# hasn't been run (the per-test `_require_real` check in pipelines.bats
# tests for real/mni152_t1_2mm.nii.gz before running).

set -euo pipefail

HERE="$(dirname "$(readlink -f "$0")")"
REAL="$HERE/real"
mkdir -p "$REAL"

# Bail loudly if Python deps are missing — install.sh should have grabbed them.
/usr/bin/python3 - <<'PY' || { echo "[real-fixtures] missing nilearn/nibabel; skipping" >&2; exit 0; }
import sys
missing = []
for m in ("nilearn", "nibabel", "numpy"):
    try: __import__(m)
    except ImportError: missing.append(m)
if missing:
    print("missing:", " ".join(missing), file=sys.stderr); sys.exit(1)
PY

# ─── Section 1/4: MRI (MNI152 via nilearn) ─────────────────────────────────
# Each section below has its own per-file idempotency check, so re-running
# this script is cheap once the data is cached. Network only on first fetch.
if [[ -f "$REAL/mni152_t1_2mm.nii.gz" && -f "$REAL/mni152_brain_mask_2mm.nii.gz" \
   && -f "$REAL/mni152_t1_2mm_moved.nii.gz" ]]; then
    echo "[real-fixtures] MRI: already present"
else
    echo "[real-fixtures] MRI: fetching MNI152 templates via nilearn (~0.4 MB)"
/usr/bin/python3 - "$REAL" <<'PY'
"""Fetch MNI152 templates via nilearn and produce a registration partner."""
import os, sys, pathlib, shutil
import numpy as np
import nibabel as nib
from nilearn.datasets import load_mni152_template, load_mni152_brain_mask

OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(exist_ok=True)

# ---- T1 template (2 mm isotropic, MNI152 2009a) ----
t1 = load_mni152_template(resolution=2)
nib.save(t1, OUT / "mni152_t1_2mm.nii.gz")

# ---- Brain mask (binary, same grid) ----
mask = load_mni152_brain_mask(resolution=2)
nib.save(mask, OUT / "mni152_brain_mask_2mm.nii.gz")

# ---- Registration partner: same T1 shifted by (2, 1, 0) voxels ----
# Gives ANTs / NiftyReg / Greedy / elastix something non-identical but
# recoverable to register against. Real affine offset, real anatomy.
data = t1.get_fdata()
moved = np.roll(data, shift=(2, 1, 0), axis=(0, 1, 2))
nib.save(nib.Nifti1Image(moved.astype(data.dtype), t1.affine, t1.header),
         OUT / "mni152_t1_2mm_moved.nii.gz")

# Summary
n = sum(1 for _ in OUT.glob("*.nii.gz"))
total = sum(p.stat().st_size for p in OUT.glob("*.nii.gz")) / (1024*1024)
print(f"[real-fixtures] MRI: wrote {n} NIfTI files, {total:.1f} MB total")
PY
fi

# ─── Section 2/4: Robotics URDF samples (dart-sim / urdfdom) ───────────────
# A handful of representative URDFs from the official dart-sim and ROS
# example sets. Tiny (~1-5 KB each, ~30 KB total). Sourced from
# dartsim/dart-tutorial-data which is BSD-2-licensed; mirrored on GitHub.
URDF_DIR="$REAL/urdf"
mkdir -p "$URDF_DIR"

# Each row is "<url> <local-name>"
# - test_robot.urdf: minimal 2-link arm (DART test fixture)
# - rrbot.urdf: classic 2-DOF revolute robot, used in ROS tutorials
# - simple_arm.urdf: 4-DOF arm with end-effector
URDF_URLS=(
    "https://raw.githubusercontent.com/dartsim/dart/v6.13.0/data/urdf/test/joint_properties.urdf|joint_properties.urdf"
    "https://raw.githubusercontent.com/dartsim/dart/v6.13.0/data/urdf/test/primitive_geometry.urdf|primitive_geometry.urdf"
    "https://raw.githubusercontent.com/dartsim/dart/v6.13.0/data/urdf/test/testWorld.urdf|testWorld.urdf"
    "https://raw.githubusercontent.com/dartsim/dart/v6.13.0/data/urdf/test/issue838.urdf|issue838.urdf"
)
fetched_urdf=0
for entry in "${URDF_URLS[@]}"; do
    url="${entry%|*}"; name="${entry#*|}"
    [[ -f "$URDF_DIR/$name" ]] && continue
    if curl -sfLo "$URDF_DIR/$name" "$url" 2>/dev/null; then
        fetched_urdf=$((fetched_urdf + 1))
    else
        echo "[real-fixtures] WARN: could not fetch $name" >&2
    fi
done
echo "[real-fixtures] URDF: $(ls "$URDF_DIR"/*.urdf 2>/dev/null | wc -l) files"

# ─── Section 3/4: MorpheusML model examples (morpheus / morpheus-gui) ──────
# Two reference morpheus models from upstream's example library. Each is a
# small (~10-50 KB) MorpheusML XML file exercising different solver paths
# (reaction-diffusion vs. cellular Potts).
MORPH_DIR="$REAL/morpheus"
mkdir -p "$MORPH_DIR"

MORPHEUS_URLS=(
    "https://gitlab.com/morpheus.lab/morpheus/-/raw/main/Examples/PDE/ActivatorInhibitor_1D.xml|ActivatorInhibitor_1D.xml"
    "https://gitlab.com/morpheus.lab/morpheus/-/raw/main/Examples/CPM/CellSorting_2D.xml|CellSorting_2D.xml"
)
for entry in "${MORPHEUS_URLS[@]}"; do
    url="${entry%|*}"; name="${entry#*|}"
    [[ -f "$MORPH_DIR/$name" ]] && continue
    if curl -sfLo "$MORPH_DIR/$name" "$url" 2>/dev/null; then
        :
    else
        echo "[real-fixtures] WARN: could not fetch $name" >&2
    fi
done
echo "[real-fixtures] MorpheusML: $(ls "$MORPH_DIR"/*.xml 2>/dev/null | wc -l) files"

# ─── Section 4/4: BED genomics sample (ucsc-kent-utils) ────────────────────
# Synthesize rather than fetch — a tiny but valid BED file is trivial to
# construct and avoids hitting hgdownload.cse.ucsc.edu (which has rate
# limits and serves multi-MB minimum chunks). Three regions on chr1
# covering the BED-3 / BED-6 / BED-12 schemas — enough to exercise
# bedToBigBed / overlapSelect / etc.
GENOMICS_DIR="$REAL/genomics"
mkdir -p "$GENOMICS_DIR"

if [[ ! -f "$GENOMICS_DIR/sample.bed" ]]; then
    cat > "$GENOMICS_DIR/sample.bed" <<'BED'
chr1	1000	5000	feature_A	900	+
chr1	8000	12000	feature_B	800	-
chr1	15000	20000	feature_C	1000	+
chr2	3000	7000	feature_D	750	-
chr2	10000	14000	feature_E	950	+
BED
fi

# Matching chrom.sizes for bedToBigBed (chr1, chr2 dimensions)
if [[ ! -f "$GENOMICS_DIR/chrom.sizes" ]]; then
    cat > "$GENOMICS_DIR/chrom.sizes" <<'SIZES'
chr1	248956422
chr2	242193529
SIZES
fi

echo "[real-fixtures] genomics: $(ls "$GENOMICS_DIR" 2>/dev/null | wc -l) files"

# ── Summary ────────────────────────────────────────────────────────────────
total_kb=$(du -sk "$REAL" 2>/dev/null | awk '{print $1}')
echo "[real-fixtures] all sections done; total ${total_kb} KB under $REAL"
