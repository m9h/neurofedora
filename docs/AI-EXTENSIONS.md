# AI / Deep Learning extensions for 3D Slicer on Fedora

A companion to [CUDA-RPM-FUSION.md](CUDA-RPM-FUSION.md). That document
covers *the hardware substrate* (drivers, CUDA, cuDNN). This one covers
*the software ecosystem on top* — NVIDIA Clara, segmentation-for-ground-
truth tooling, DeepInfer, and the TensorFlow / MONAI compatibility story.

---

## Landscape (Q2 2026)

### NVIDIA Clara — current status

NVIDIA's "Clara" brand has gone through three eras:

| Era | Years | What it was | Status |
|---|---|---|---|
| **Clara Train SDK** | 2019–2022 | TensorFlow-based training framework with reference apps | **Deprecated** — superseded by MONAI |
| **Clara Deploy SDK** | 2020–2023 | Inference-pipeline runtime | **Deprecated** — superseded by MONAI Deploy |
| **NVIDIA-AIAA** (AI-Assisted Annotation) | 2019–2022 | HTTP server + Slicer extension for ML-assisted annotation | **Deprecated** — superseded by MONAI Label |
| **MONAI** (Medical Open Network for AI) | 2020–present | Open-source PyTorch-based medical imaging AI framework | **Current** — NVIDIA-led but open; what Clara users moved to |

**Action for Fedora packaging**: skip Clara. Target MONAI. Ship:
- `python-monai` (already available via PyPI; can wrap in COPR)
- `3dslicer-monailabel-client` (Slicer-side HTTP client for MONAI Label server)
- `3dslicer-monaiauto3dseg` (auto-3D segmentation extension wrapping MONAI Bundle)
- Optional: `3dslicer-nvidia-aiaa-legacy` as a transition aid for users
  with old Clara workflows (deprecated but works)

### Segmentation tools for ground truth training data

This is a *hot* area — generating ground truth at scale is the bottleneck
for every medical-imaging ML project. The Slicer ecosystem has several:

| Extension | Approach | Why it matters |
|---|---|---|
| **SegmentEditorExtraEffects** | Manual editing with extra brushes/tools | Pure-Python; the workhorse for human-curated ground truth |
| **MONAILabel** | Interactive: model proposes, human corrects, model retrains | The "active learning" loop — accelerates GT creation 5-10× |
| **SlicerSAM** | Segment Anything Model (Meta, 2023) | Zero-shot generic segmentation; great for diverse anatomies |
| **SlicerMedSAM** | MedSAM (medical SAM fine-tune) | SAM fine-tuned for medical imaging |
| **SlicerTotalSegmentator** | Pre-trained nnUNet for 100+ structures | Instant whole-body segmentation; great seed for editing |
| **SlicerNNUNet** | Train/use nnUNet models in-Slicer | When you need to train your own |
| **DCMQI** | DICOM-SEG export | Get GT *out* of Slicer in standard DICOM form |
| **SegmentationWizard** | Multi-modal workflow wrapper | Education / clinical-workflow scaffolding |

**Action for Fedora packaging**: ship all of these as separate RPMs
(`3dslicer-monailabel-client`, `3dslicer-sam`, `3dslicer-medsam`,
`3dslicer-totalsegmentator`, `3dslicer-nnunet`, `3dslicer-segeditor-extra`,
`3dslicer-segmentation-wizard`). Most are pure-Python scripted modules
— `noarch` RPMs, build in seconds, no CUDA at build time.

Group them under a meta-package `3dslicer-ai-segmentation` for users
who just want "give me the kitchen sink for ground-truth work".

### DeepInfer

[DeepInfer](https://github.com/DeepInfer/Slicer-DeepInfer) was an early
(2017–2020) effort to provide a generic "load any Docker container with
a model and run inference" mechanism inside Slicer. It works but is
largely abandoned upstream.

**Current state** (2026):
- The Slicer module side still loads in 5.10, but the Docker-image
  registry it depends on (`deepinfer.org`) is offline.
- Successor: **MONAI Label** + bundles, which handles the same
  use-case (remote model server) with active maintenance.

**Action for Fedora packaging**: ship `3dslicer-deepinfer` as a legacy
optional package for backwards compatibility with old study pipelines.
Add a README pointing users to MONAI Label as the replacement.

### TensorFlow + MONAI compatibility

The trickiest part of the AI story.

#### TensorFlow problem

**TensorFlow has been removed from Fedora** (and Fedora/EPEL never had a
clean story). The official upstream wheels (`pip install tensorflow`)
are the only practical path on Fedora. They ship with bundled CUDA libs
and pin specific CUDA + cuDNN versions.

**Slicer extensions that need TF**: SlicerLiver (some workflows), older
Clara extensions, some BraTS-era models. Increasingly rare — the field
has consolidated on PyTorch.

**Action**: provide TensorFlow via the same `slicer-fspython` uv-venv
mechanism we already use for FreeSurfer's SynthSeg/SynthSR. Specifically:

```bash
slicer-fspython-setup --backend tensorflow-cuda
```

writes a requirements file like:

```
tensorflow[and-cuda]==2.20.*
nibabel
SimpleITK
scikit-image
scikit-learn
```

and `uv pip install`s them into a parallel venv that Slicer's PythonQt
can `sys.path.insert(0, ...)` to import.

#### MONAI problem

MONAI is much cleaner. It's pure-Python, pip-installable, and works
with both PyTorch (default) and TensorFlow (legacy MONAI-TF, rare).
Fedora doesn't package MONAI directly, but PyPI ships clean wheels.

**Action**: ship a `3dslicer-monai-bundle` RPM that:
- Requires `slicer-fspython` (our uv-venv tool)
- On first run, `uv pip install monai monailabel` into the venv
- Provides `slicer-monai-setup` to refresh the venv when MONAI bumps

Pattern is **identical** to `freesurfer-fspython` — we already proved
this works.

---

## The full AI ecosystem RPM layout

Putting it all together:

```
3dslicer                                ← base Slicer (CUDA-agnostic)
├── 3dslicer-cuda                       ← meta: RPM Fusion driver + NVIDIA toolkit + venv setup
│                                          (lives in RPM Fusion nonfree)
├── 3dslicer-ai-segmentation            ← meta: pulls in the ground-truth-creation stack
│   ├── 3dslicer-monailabel-client      ← interactive AI annotation (replaces NVIDIA AIAA)
│   ├── 3dslicer-totalsegmentator       ← pre-trained whole-body segmentation
│   ├── 3dslicer-sam                    ← Segment Anything zero-shot
│   ├── 3dslicer-medsam                 ← MedSAM fine-tune
│   ├── 3dslicer-nnunet                 ← train your own models
│   ├── 3dslicer-segeditor-extra        ← manual editing power-tools
│   └── 3dslicer-segmentation-wizard    ← workflow scaffolding
├── 3dslicer-ai-inference               ← meta: post-training deployment
│   ├── 3dslicer-monai-bundle           ← Run MONAI Bundle .zip models
│   ├── 3dslicer-monaiauto3dseg         ← Auto3DSeg pipeline integration
│   └── 3dslicer-deepinfer              ← LEGACY: Docker-container models
├── 3dslicer-radiomics                  ← (already drafted) pyradiomics integration
└── slicer-fspython                     ← (parallel-named to freesurfer-fspython)
                                          uv-venv tool for PyTorch/TF/MONAI

mhough/neurofedora-research COPR        ← experimental: CUDA-pinned PyTorch RPMs,
                                          NVCC-built ITK-CUDA, VTK-CUDA backends
```

---

## Implementation phases

| Sprint | Deliverable |
|---|---|
| **Now** | 3dslicer base + 5 major extensions (current focus) |
| **+2 weeks** | `3dslicer-monailabel-client` (pure Python scripted; small) |
| **+2 weeks** | `3dslicer-totalsegmentator` (pure Python scripted; small) |
| **+1 month** | `slicer-fspython` (mirror of `freesurfer-fspython` pattern) |
| **+1 month** | `3dslicer-cuda` meta-package in RPM Fusion |
| **+1.5 months** | `3dslicer-sam`, `3dslicer-medsam`, `3dslicer-nnunet` |
| **+2 months** | `3dslicer-monai-bundle`, `3dslicer-monaiauto3dseg` |
| **+2 months** | `3dslicer-segeditor-extra`, `3dslicer-segmentation-wizard` |
| **+3 months** | `3dslicer-ai-segmentation` + `3dslicer-ai-inference` meta-packages |
| **+3 months** | `3dslicer-deepinfer` (legacy; low priority) |
| **+4 months** | Docs site walking through full GT-creation workflow on Fedora |

---

## A representative end-to-end user workflow

Once this is all shipped:

```bash
# Day 1 — enable the right repos
sudo dnf install \
  https://download1.rpmfusion.org/{free,nonfree}/fedora/\
rpmfusion-{free,nonfree}-release-$(rpm -E %fedora).noarch.rpm
sudo dnf config-manager addrepo \
  --from-repofile=https://developer.download.nvidia.com/compute/cuda/repos/fedora43/x86_64/cuda-fedora43.repo
sudo dnf copr enable mhough/neurofedora

# Day 1 — install the AI stack
sudo dnf install 3dslicer 3dslicer-cuda 3dslicer-ai-segmentation
sudo reboot   # for the NVIDIA driver

# Day 1 — set up PyTorch + MONAI in Slicer's Python env
slicer-fspython-setup --backend pytorch-cuda

# Day 1 — start work
slicer                              # opens 3D Slicer
# In Slicer: Modules → MONAILabel → Connect to remote MONAI server
# Or: Modules → TotalSegmentator → run automatic whole-body segmentation
# Or: Modules → Segment Editor → manual cleanup with extra effects
# Export GT: File → Export DICOM SEG (via DCMQI)
```

From `dnf install` to running interactive AI-assisted segmentation in
under 30 minutes. No Conda, no SuperBuild, no PPA wrangling, no Docker
host setup. **That's the Fedora medical-imaging story.**

---

## Why this matters strategically

The market for medical-imaging AI tools is exploding (every academic
medical center has at least one researcher building segmentation models
right now). The bottleneck is **environment setup** — typically
2-3 days of "make Conda + CUDA + PyTorch + MONAI + Slicer all play
nicely on Ubuntu LTS or macOS".

If Fedora collapses that to a single `dnf install` line, it becomes
the obvious choice for new research groups starting up — and once
they're on Fedora for the imaging stack, they tend to standardize
their whole lab on Fedora.

This is how Fedora wins the long-tail of academic computing.

---

## References

- MONAI: <https://monai.io>
- MONAI Label: <https://github.com/Project-MONAI/MONAILabel>
- TotalSegmentator: <https://github.com/wasserth/TotalSegmentator>
- SlicerSAM: <https://github.com/mazurowski-lab/SlicerSegmentWithSAM>
- NVIDIA-AIAA (deprecated reference):
  <https://github.com/NVIDIA/ai-assisted-annotation-client>
- Clara → MONAI migration:
  <https://developer.nvidia.com/blog/transitioning-from-clara-train-to-monai/>
- DeepInfer (legacy):
  <https://github.com/DeepInfer/Slicer-DeepInfer>
