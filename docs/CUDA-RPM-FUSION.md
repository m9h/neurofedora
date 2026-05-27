# NVIDIA CUDA support for 3D Slicer on Fedora — RPM Fusion strategy

## Executive summary

**3D Slicer core does NOT depend on CUDA.** Slicer's "GPU" code paths
(vtkMRMLGPURayCastVolumeRenderingDisplayNode, qSlicerGPUMemoryComboBox)
all use VTK's OpenGL/GLSL pipeline — no CUDA calls in the C++ source.

**Every CUDA-using Slicer feature is a Python-level extension** that
talks to PyTorch / MONAI / TotalSegmentator / segment-anything-models at
runtime. The packaging problem is therefore not about compiling Slicer
itself with `-DSlicer_USE_CUDA=ON` — it's about making it easy for users
to install the right NVIDIA stack underneath an unmodified Slicer.

This document plans the **`3dslicer-cuda` meta-package** that bundles
those choices and how it integrates with RPM Fusion + NVIDIA's
developer CUDA repository.

---

## CUDA-using Slicer extensions (catalog)

| Extension | What it needs | How |
|---|---|---|
| **SlicerTotalSegmentator** (lassoan) | PyTorch + CUDA + TotalSegmentator pypi pkg | Loads TotalSegmentator at runtime; uses PyTorch's CUDA runtime |
| **SlicerMONAILabel** | MONAI Label server (external) | Slicer side is pure HTTP client; CUDA runs on the server |
| **SlicerMONAIAuto3DSeg** | MONAI + PyTorch + CUDA | Python scripted module; uses MONAI bundled models |
| **DeepInfer** | Docker + NVIDIA Container Toolkit | Pulls Docker images with CUDA baked in |
| **SlicerSAM** | PyTorch + segment-anything pip pkg | Python module loads SAM models on GPU |
| **SlicerLiver** | PyTorch / MONAI | Liver-specific deep-learning workflows |
| **pet-ct-annotate** | PyTorch | Annotation aided by ML models |
| **NVIDIA-AIAA** *(legacy)* | NVIDIA Clara AI-Assisted Annotation server | Slicer side is HTTP client |

**Common pattern**: every entry above is a *Python scripted module* in
Slicer that installs a PyPI package via `pip install` on first run (or
relies on a remote MONAI Label server). The CUDA dependency lives in
PyTorch, not in any Slicer-compiled binary.

---

## The Fedora landscape for NVIDIA CUDA

### Three repositories that ship NVIDIA software

| Source | What it ships | Licensing |
|---|---|---|
| **RPM Fusion nonfree** | NVIDIA proprietary kernel driver (`akmod-nvidia`, `xorg-x11-drv-nvidia`), some user-space libs | Redistributable per NVIDIA Linux driver license |
| **NVIDIA's developer.download.nvidia.com/.../cuda/fedora43/** | Full CUDA Toolkit 13.x (nvcc, cuFFT, cuBLAS, cuDNN, etc.) | NVIDIA's developer license — *not* redistributable in third-party repos |
| **Fedora native (mhough/neurofedora etc.)** | Anything CUDA-agnostic; CUDA-linked binaries are **not allowed** in Fedora/COPR | Free software only |

NVIDIA's CUDA SDK ships under a license that prohibits third-party
redistribution. Even RPM Fusion can't repackage it — they can only
ship the kernel driver. So the canonical Fedora-friendly stack is:

```
RPM Fusion (nonfree)       → NVIDIA kernel driver + libcuda.so
NVIDIA's CUDA repo (direct)→ CUDA toolkit, cuDNN, NCCL, libraries
Fedora/COPR (mhough/...)   → Slicer + extensions (CUDA-agnostic)
```

Users enable both external repos once; everything else is `dnf install`.

### What's currently in each repo (Fedora 44 / rawhide, May 2026)

**NVIDIA Fedora repo** ([developer.download.nvidia.com/compute/cuda/repos/fedora43/x86_64/](https://developer.download.nvidia.com/compute/cuda/repos/fedora43/x86_64/)):
- `cuda-toolkit-13` (meta package — nvcc, libraries, dev headers)
- `cuda-cudart-13`, `cuda-cudart-devel-13` (CUDA runtime)
- `cuda-libraries-13` (cuFFT, cuBLAS, cuSPARSE, etc.)
- `cuda-drivers-595` (driver — alternative to RPM Fusion's path)
- `cuda-compiler-13` (nvcc + ptxas)
- `libcudnn9-cuda-13` (cuDNN — separate license, must be downloaded)

**RPM Fusion nonfree** ([rpmfusion.org/Configuration](https://rpmfusion.org/Configuration)):
- `akmod-nvidia`, `kmod-nvidia` (kernel modules — auto-rebuild on kernel update)
- `xorg-x11-drv-nvidia`, `xorg-x11-drv-nvidia-libs` (X11/Wayland driver bits)
- `xorg-x11-drv-nvidia-cuda` (libcuda.so runtime for the userspace)
- Critically: **NOT** the CUDA toolkit, NOT cuDNN, NOT NCCL

Both repos provide `libcuda.so` — they conflict if both are installed.
The community-standard recommendation is: use RPM Fusion for the
*driver*, use NVIDIA's repo for the *toolkit* (`dnf module enable
nvidia-driver:open-dkms` or similar).

---

## The `3dslicer-cuda` meta-package plan

### Design

A small **noarch** RPM that:

1. **Requires** `3dslicer` (the main Slicer package).
2. **Recommends** `xorg-x11-drv-nvidia` from RPM Fusion (kernel driver).
3. **Recommends** `cuda-toolkit-13` from NVIDIA's CUDA repo (toolkit).
4. Ships `/usr/bin/slicer-cuda-setup` — a tool that:
   - Detects the installed NVIDIA driver version
   - Looks up the matching CUDA + cuDNN version
   - Installs PyTorch + MONAI + TotalSegmentator into Slicer's
     bundled Python via `pip install --user`, OR into a parallel uv venv
   - Writes a `slicer-cuda.conf` that the extension manager respects
5. Ships `/etc/profile.d/slicer-cuda.sh` — adds the right
   `LD_LIBRARY_PATH` and `CUDA_HOME` if both repos are enabled.

### Where the meta-package lives

| Component | Repo |
|---|---|
| `3dslicer` (core) | Fedora COPR `mhough/neurofedora` |
| `3dslicer-dmri`, `3dslicer-rt`, ... (CUDA-agnostic extensions) | same |
| `3dslicer-totalsegmentator`, `3dslicer-monailabel-client` (CUDA-using extensions) | same — they're CUDA-agnostic at compile time |
| **`3dslicer-cuda` meta** | **RPM Fusion nonfree** (because it depends on RPM Fusion's `xorg-x11-drv-nvidia`) |
| NVIDIA driver, libcuda.so | RPM Fusion nonfree |
| CUDA toolkit, cuDNN, PyTorch-cuda | NVIDIA's developer repo (or PyPI) |

The split lets the bulk of Slicer stay in standard Fedora/COPR while
the *one* nonfree-touching package lives in RPM Fusion where users
already trust nonfree content.

### User workflow

```bash
# One-time setup
sudo dnf install \
  https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf config-manager addrepo \
  --from-repofile=https://developer.download.nvidia.com/compute/cuda/repos/fedora43/x86_64/cuda-fedora43.repo
sudo dnf copr enable mhough/neurofedora

# Stack install
sudo dnf install 3dslicer 3dslicer-cuda
sudo reboot   # for the kernel driver

# Per-user PyTorch+MONAI setup (no sudo)
slicer-cuda-setup --interactive
```

After this, opening Slicer and loading the SlicerTotalSegmentator
extension should "just work" against the local GPU.

---

## What we'd submit to RPM Fusion vs keep in COPR

| Package | Where | Reason |
|---|---|---|
| `3dslicer-cuda` meta | RPM Fusion **nonfree** | Recommends nonfree drivers; nonfree is the Fedora-policy-correct home |
| `3dslicer-totalsegmentator` (scripted extension, no compiled CUDA code) | COPR `mhough/neurofedora` then Fedora | Pure Python; CUDA-agnostic at build time |
| `3dslicer-monaicore-client` (talks to MONAI server) | COPR `mhough/neurofedora` then Fedora | Pure Python; no CUDA at build |
| **Anything statically linking CUDA libraries** | Cannot ship anywhere in third-party repos | NVIDIA license — users must install from NVIDIA's own repo |

---

## Open questions / decisions before kickoff

1. **PyTorch path**: PyPI's pre-built `torch+cu13` wheels vs Anaconda's
   `pytorch-cuda` vs system-built. Recommendation: **PyPI wheels** —
   they're versioned to match CUDA cleanly and don't need conda. The
   `slicer-cuda-setup` tool can pin a known-good PyTorch + CUDA combo
   per Slicer release.
2. **AMD ROCm parallel**: should `3dslicer-rocm` exist for ROCm users?
   Yes, but lower priority — ROCm shareholder base in medical imaging
   is small. Stub spec deferred.
3. **Apple Silicon (MPS)**: not Linux; out of scope for Fedora story.
4. **AMDGPU compute via OpenCL**: legacy path; recommend ROCm route
   instead.
5. **Multi-GPU systems**: PyTorch handles multi-GPU; nothing extra in
   our packaging.

---

## Non-goals (explicitly out of scope)

- Repackaging CUDA toolkit or cuDNN in our COPR (license-prohibited)
- Forking PyTorch to add Fedora-specific patches (upstream is fine)
- Shipping container images via Quay/Docker Hub (separate project)
- NVIDIA Container Toolkit packaging (already in RPM Fusion / Docker)

---

## Implementation order

1. **First**: get base `3dslicer` building (current sprint)
2. **+1 month**: write `3dslicer-cuda` meta-package + `slicer-cuda-setup` script
3. **+1.5 months**: test on a workstation with NVIDIA GPU (Fedora 44 + RTX-class card)
4. **+2 months**: submit `3dslicer-cuda` to RPM Fusion nonfree review
5. **+3 months**: document the full workflow in our docs site (link from VISION.md)
6. **+3 months**: `3dslicer-totalsegmentator` and `3dslicer-monailabel-client` scripted-extension RPMs in main COPR (no CUDA at build time)

---

## References

- 3D Slicer issue tracker on CUDA / PyTorch:
  <https://discourse.slicer.org/search?q=CUDA>
- TotalSegmentator + 3D Slicer integration:
  <https://github.com/lassoan/SlicerTotalSegmentator>
- MONAI Label:
  <https://github.com/Project-MONAI/MONAILabel>
- RPM Fusion configuration:
  <https://rpmfusion.org/Configuration>
- NVIDIA CUDA Fedora repo metadata:
  <https://developer.download.nvidia.com/compute/cuda/repos/fedora43/x86_64/>
