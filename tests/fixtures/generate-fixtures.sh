#!/usr/bin/env bash
# generate-fixtures.sh — synthesize the small, license-clean dataset used
# by pipelines.bats. Idempotent: re-run any time to refresh fixtures.
#
# Why synthesize rather than ship a tarball?
#   • zero licensing concerns — fully synthetic, no patient data
#   • tiny: total fixture size < 200 KB
#   • deterministic: numpy RNG seeded, same bits every time
#   • no network at test time
#
# Requirements: python3 + numpy + nibabel + pydicom + SimpleITK
# (installed by tests/install.sh as part of the test prerequisites).

set -euo pipefail

HERE="$(dirname "$(readlink -f "$0")")"
cd "$HERE"

# Bail loudly if Python deps are missing — install.sh should have grabbed them.
python3 - <<'PY' || { echo "fixture generation skipped: missing Python deps" >&2; exit 0; }
import sys
missing = []
for m in ("numpy", "nibabel", "pydicom", "SimpleITK"):
    try: __import__(m)
    except ImportError: missing.append(m)
if missing:
    print("missing:", " ".join(missing), file=sys.stderr); sys.exit(1)
PY

echo "[fixtures] generating in $HERE"

python3 - "$HERE" <<'PY'
"""Synthesize the neurofedora pipeline test corpus."""
import os, sys, pathlib, datetime
import numpy as np
import nibabel as nib

OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

# --- 1) T1-like volume: 32³ with a centered bright sphere + noise -----------
SIZE = 32
zz, yy, xx = np.indices((SIZE, SIZE, SIZE), dtype=np.float32)
center = SIZE / 2.0
r = np.sqrt((xx - center) ** 2 + (yy - center) ** 2 + (zz - center) ** 2)
t1 = np.where(r < 10, 800.0, 200.0).astype(np.float32)
t1 += rng.normal(0, 20, t1.shape).astype(np.float32)
affine = np.diag([1.0, 1.0, 1.0, 1.0])  # 1 mm isotropic
nib.save(nib.Nifti1Image(t1, affine), OUT / "t1.nii.gz")

# --- 2) Binary mask of the sphere -------------------------------------------
mask = (r < 10).astype(np.uint8)
nib.save(nib.Nifti1Image(mask, affine), OUT / "mask.nii.gz")

# --- 3) Translated T1 for registration tests --------------------------------
t1_moved = np.roll(t1, shift=(2, 1, 0), axis=(0, 1, 2))
nib.save(nib.Nifti1Image(t1_moved, affine), OUT / "t1_moved.nii.gz")

# --- 4) Minimal DWI: 1 b0 + 6 directions, same 32³ grid ---------------------
dwi_dir = OUT / "dwi"; dwi_dir.mkdir(exist_ok=True)
n_vols = 7
dwi = np.zeros((SIZE, SIZE, SIZE, n_vols), dtype=np.float32)
dwi[..., 0] = t1                            # b0
for i in range(1, n_vols):                  # diffusion-weighted: attenuated
    dwi[..., i] = t1 * (0.7 + 0.05 * i)
nib.save(nib.Nifti1Image(dwi, affine), dwi_dir / "dwi.nii.gz")
bvecs = np.array([
    [0.0, 1, 0, 0,  0.707,  0.707, 0],
    [0.0, 0, 1, 0,  0.707,  0.0,    0.707],
    [0.0, 0, 0, 1,  0.0,    0.707,  0.707],
])  # 3×7
np.savetxt(dwi_dir / "bvecs", bvecs, fmt="%.3f")
bvals = np.array([0, 1000, 1000, 1000, 1000, 1000, 1000])
np.savetxt(dwi_dir / "bvals", bvals.reshape(1, -1), fmt="%d")

# --- 5) Synthetic 10-slice DICOM series -------------------------------------
import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid, CTImageStorage
dcm_dir = OUT / "dicom"; dcm_dir.mkdir(exist_ok=True)
study_uid  = generate_uid()
series_uid = generate_uid()
for i in range(10):
    fm = FileMetaDataset()
    fm.MediaStorageSOPClassUID    = CTImageStorage
    fm.MediaStorageSOPInstanceUID = generate_uid()
    fm.TransferSyntaxUID          = ExplicitVRLittleEndian
    fn = dcm_dir / f"slice_{i:03d}.dcm"
    ds = FileDataset(str(fn), {}, file_meta=fm, preamble=b"\0" * 128)
    ds.PatientName       = "Synthetic^Test"
    ds.PatientID         = "NEUROFEDORA-TEST"
    ds.Modality          = "CT"
    ds.Manufacturer      = "neurofedora-fixtures"
    ds.StudyInstanceUID  = study_uid
    ds.SeriesInstanceUID = series_uid
    ds.SOPClassUID       = CTImageStorage
    ds.SOPInstanceUID    = fm.MediaStorageSOPInstanceUID
    ds.SeriesNumber      = 1
    ds.InstanceNumber    = i + 1
    ds.ContentDate       = datetime.date.today().strftime("%Y%m%d")
    ds.ContentTime       = "000000"
    ds.Rows, ds.Columns  = SIZE, SIZE
    ds.BitsAllocated     = 16
    ds.BitsStored        = 16
    ds.HighBit           = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel   = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    arr = (t1[i * 3].astype(np.uint16))
    ds.PixelData = arr.tobytes()
    ds.is_little_endian = True
    ds.is_implicit_VR  = False
    ds.save_as(fn, write_like_original=False)

# --- 6) NRRD copy of the T1 — Fedora's teem (v1.11, 2012) can't read NIfTI -
nrrd_path = OUT / "t1.nrrd"
hdr_text = (
    "NRRD0001\n"
    "type: float\n"
    "dimension: 3\n"
    f"sizes: {SIZE} {SIZE} {SIZE}\n"
    "encoding: raw\n"
    "endian: little\n"
    "\n"
)
nrrd_path.write_bytes(hdr_text.encode() + t1.tobytes())

# --- 7) Tiny mesh (.vtp) via VTK in SimpleITK is awkward; use raw XML --------
# Sphere mesh, 8 vertices (cube corners) + 12 triangles
verts = [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]
tris = [(0,1,2),(0,2,3),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
        (2,3,7),(2,7,6),(1,2,6),(1,6,5),(0,3,7),(0,7,4)]
mesh_path = OUT / "mesh.vtp"
with mesh_path.open("w") as f:
    f.write('<?xml version="1.0"?>\n<VTKFile type="PolyData" version="1.0">\n<PolyData>\n')
    f.write(f'<Piece NumberOfPoints="{len(verts)}" NumberOfPolys="{len(tris)}">\n')
    f.write('<Points><DataArray type="Float32" NumberOfComponents="3" format="ascii">\n')
    f.write(" ".join(f"{x} {y} {z}" for x,y,z in verts)); f.write("\n</DataArray></Points>\n")
    f.write('<Polys>\n<DataArray type="Int32" Name="connectivity" format="ascii">\n')
    f.write(" ".join(f"{a} {b} {c}" for a,b,c in tris)); f.write("\n</DataArray>\n")
    f.write('<DataArray type="Int32" Name="offsets" format="ascii">\n')
    f.write(" ".join(str(3*(i+1)) for i in range(len(tris)))); f.write("\n</DataArray>\n</Polys>\n")
    f.write('</Piece></PolyData></VTKFile>\n')

print(f"[fixtures] wrote {len(list(OUT.rglob('*')))} files in {OUT}")
PY

# Manifest of fixtures (helps users see what's available without running ls -R)
{
    echo "# Auto-generated fixture manifest"
    echo "# Re-generate with: ./generate-fixtures.sh"
    echo
    find "$HERE" -type f ! -name "*.sh" ! -name "MANIFEST" -printf '%P\t%s bytes\n' | sort
} > "$HERE/MANIFEST"

echo "[fixtures] manifest written to $HERE/MANIFEST"
