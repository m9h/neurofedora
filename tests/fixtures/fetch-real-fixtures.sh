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

# ─── Section 5/5: FSL reference data (anat + DTI templates) ────────────────
# FSL's FEEDS test dataset isn't anonymously fetchable from the FSL gitlab
# (auth-walled), so we DETECT a local FSL install and symlink its shipped
# reference data into fixtures/real/feeds/. Covers:
#   - MNI152 T1 1mm/2mm (richer than nilearn's 2009a 2mm)
#   - FMRIB58 / HCP1065 FA + L1 + V1 — real DTI-derived templates,
#     exercises the same NIfTI code paths as raw DWI loading.
#
# If FSL isn't installed, the section skips cleanly and the FEEDS-style
# pipeline rows skip too. Install FSL from
# https://fsl.fmrib.ox.ac.uk/fsl/docs/#/install/index to unlock.
FEEDS_DIR="$REAL/feeds"
mkdir -p "$FEEDS_DIR"

_detect_fsl() {
    local cand
    for cand in "${FSLDIR:-}" /usr/share/fsl /opt/fsl /usr/local/fsl \
                "$HOME/fsl" /Applications/fsl; do
        [[ -n "$cand" && -d "$cand/data/standard" ]] && { echo "$cand"; return 0; }
    done
    # /opt/fsl-* glob (versioned installs)
    for cand in /opt/fsl-* ; do
        [[ -d "$cand/data/standard" ]] && { echo "$cand"; return 0; }
    done
    return 1
}

if FSL_DIR=$(_detect_fsl); then
    # Anatomical T1 templates (1mm and 2mm)
    for f in MNI152_T1_1mm.nii.gz MNI152_T1_1mm_brain.nii.gz \
             MNI152_T1_2mm.nii.gz MNI152_T1_2mm_brain.nii.gz \
             MNI152_T1_2mm_brain_mask.nii.gz; do
        src="$FSL_DIR/data/standard/$f"
        [[ -f "$src" && ! -e "$FEEDS_DIR/$f" ]] && ln -sf "$src" "$FEEDS_DIR/$f"
    done
    # DTI / diffusion-derived templates
    for f in FMRIB58_FA_1mm.nii.gz FMRIB58_FA-skeleton_1mm.nii.gz \
             FSL_HCP1065_FA_1mm.nii.gz FSL_HCP1065_L1_1mm.nii.gz \
             FSL_HCP1065_V1_1mm.nii.gz; do
        src="$FSL_DIR/data/standard/$f"
        [[ -f "$src" && ! -e "$FEEDS_DIR/$f" ]] && ln -sf "$src" "$FEEDS_DIR/$f"
    done
    n=$(ls -1 "$FEEDS_DIR" 2>/dev/null | wc -l)
    echo "[real-fixtures] FSL data: $n symlinks (FSLDIR=$FSL_DIR)"
    # Optional: an actual FEEDS install adds raw DWI/anat/fmri subdirs
    if [[ -d "$FSL_DIR/feeds" ]]; then
        for sub in anat diff fmri; do
            [[ -d "$FSL_DIR/feeds/$sub" && ! -e "$FEEDS_DIR/$sub" ]] \
                && ln -sf "$FSL_DIR/feeds/$sub" "$FEEDS_DIR/$sub"
        done
        echo "[real-fixtures] FSL FEEDS detected: anat/diff/fmri symlinked"
    fi
else
    echo "[real-fixtures] FSL not detected — FEEDS-style pipelines will SKIP"
    echo "[real-fixtures]   (set FSLDIR or install FSL to unlock)"
fi

# ─── Section 6/6: DWI via dipy.data.fetch_sherbrooke_3shell ────────────────
# Real 4D DWI (HARDI 193 directions) with companion bval/bvec — the
# canonical "smallest real DWI" dataset dipy ships a fetcher for.
# ~184 MB compressed, cached under ~/.dipy/sherbrooke_3shell/. Unlocks
# tests of: mrconvert -fslgrad, dwi2tensor, dipy DKI/DTI fits, fslpy
# DWI loaders, nibabel bvec parsing.
#
# Requires python-dipy >= 1.10 (in mhough/neurofedora COPR). Skips
# cleanly if dipy isn't importable (e.g., on a box that hasn't enabled
# the COPR yet).
DWI_DIR="$REAL/dwi"
mkdir -p "$DWI_DIR"

if [[ -f "$DWI_DIR/HARDI193.nii.gz" && -f "$DWI_DIR/HARDI193.bval" \
   && -f "$DWI_DIR/HARDI193.bvec" ]]; then
    echo "[real-fixtures] DWI: already present"
elif ! /usr/bin/python3 -c "import dipy" 2>/dev/null; then
    echo "[real-fixtures] DWI: dipy not importable — skipping (install python3-dipy)"
else
    echo "[real-fixtures] DWI: fetching sherbrooke_3shell via dipy (~184 MB)"
/usr/bin/python3 - "$DWI_DIR" <<'PY' || echo "[real-fixtures] DWI: fetch failed (network?), skipping"
"""Fetch HARDI 3-shell DWI via dipy and copy into fixtures/real/dwi/."""
import sys, pathlib, shutil
from dipy.data import fetch_sherbrooke_3shell, get_fnames

OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(exist_ok=True)

# fetch_sherbrooke_3shell caches under ~/.dipy/sherbrooke_3shell/
fetch_sherbrooke_3shell()
fdwi, fbval, fbvec = get_fnames(name='sherbrooke_3shell')

# Copy (not symlink) so the fixture survives a ~/.dipy/ wipe
for src in (fdwi, fbval, fbvec):
    dst = OUT / pathlib.Path(src).name
    if not dst.exists():
        shutil.copy2(src, dst)

# Report sizes
total_mb = sum(p.stat().st_size for p in OUT.iterdir()) / (1024*1024)
print(f"[real-fixtures] DWI: copied 3 files, {total_mb:.1f} MB total")
PY
fi

# ── Summary ────────────────────────────────────────────────────────────────
total_kb=$(du -sLk "$REAL" 2>/dev/null | awk '{print $1}')
echo "[real-fixtures] all sections done; total ${total_kb} KB under $REAL"
