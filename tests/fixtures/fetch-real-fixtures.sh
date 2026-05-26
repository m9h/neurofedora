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

if [[ -f "$REAL/mni152_t1_2mm.nii.gz" && -f "$REAL/mni152_brain_mask_2mm.nii.gz" \
   && -f "$REAL/mni152_t1_2mm_moved.nii.gz" ]]; then
    echo "[real-fixtures] already present in $REAL — skipping fetch"
    exit 0
fi

echo "[real-fixtures] fetching MNI152 templates via nilearn (~15 MB on first run)"

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
print(f"[real-fixtures] wrote {n} NIfTI files, {total:.1f} MB total under {OUT}")
PY
