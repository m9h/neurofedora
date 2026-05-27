# Fedora Linux: The Medical Imaging & Surgical-Device Platform

**Mission**: Make Fedora Linux the default operating system for medical
imaging research, clinical-research computing, and medical-device
software development — by shipping a coherent, signed, reproducible
software stack that no other Linux distribution provides as cleanly.

---

## Why Fedora

The medical-imaging software ecosystem in 2026 is a sea of pain points:

- **Conda environments** that break every six months when CUDA/PyTorch/ITK
  release cycles diverge.
- **Custom Ubuntu PPAs** maintained by single PIs at single universities,
  often abandoned after grant cycles end.
- **3D Slicer's SuperBuild** that downloads and builds 30+ external
  projects, takes 4 hours, needs 32 GB RAM, and pins exact dependency
  versions that conflict with everything else on the host.
- **macOS/Windows binary installers** that don't compose, can't be
  audited, and break IEC 62304 software-of-unknown-provenance (SOUP)
  documentation requirements.
- **Cross-platform Python wrangling** between Slicer's PythonQt, system
  Python, and lab-specific virtual environments.

Fedora — with the COPR build service, signed RPMs, transactional updates
via `rpm-ostree`, and the Toolbx/Distrobox containerization story — is
uniquely positioned to solve all of this.

---

## Four user personas

| Persona | Need | Fedora's answer |
|---|---|---|
| **Clinical researcher** running an IRB-approved study | `dnf install 3dslicer slicer-dmri slicer-radiomics` and start analyzing patient DICOM data within 10 minutes | First-class RPMs in a stable COPR (eventually in Fedora itself) |
| **Medical-device R&D engineer** (surgical navigation, IGT, robotics) | Reproducible CI/CD with a documented runtime; compliance-friendly audit trail | `Fedora 44 + COPR mhough/neurofedora` pinned by version → IEC 62304 documentation in minutes |
| **Computer-vision / radiology ML researcher** | Slicer's PythonQt + system Python + PyTorch/MONAI all interop cleanly | Bundled-Python default + `slicer-fspython`-style uv-venv parallel for layering modern ML frameworks |
| **Educator / hospital researcher** | Pre-built containers, Jupyter integration, sample data, tutorials | Toolbx images, `3dslicer-jupyter` RPM, `slicer-tutorials` data package |

---

## The three-channel COPR model

```
mhough/neurofedora              ← stable Slicer 5.10.x + stable extensions
mhough/neurofedora-preview      ← Slicer main + tracking-edge extensions
mhough/neurofedora-research     ← experimental: CUDA, ROCm, MONAI integration
```

Each channel is a stable, citeable target. A clinical study can cite
"COPR mhough/neurofedora @ 3dslicer-5.10.0-1.fc44 + 3dslicer-dmri-1.x"
and that build is **reproducible five years later** by any researcher
with the same Fedora point release.

---

## Two-path Python strategy

| Path | When | How |
|---|---|---|
| **Bundled Python** (default) | Matches upstream Slicer behavior; Extension Manager works out of the box | `Slicer_USE_SYSTEM_python=OFF`, Slicer's own embedded interpreter |
| **System + uv venv** (opt-in) | When user wants PyTorch / MONAI / transformers in the runtime; reproducible CI; avoid Conda | `SLICER_USE_SYSTEM_PYTHON=1` + `slicer-fspython` package (same pattern as `freesurfer-fspython`) |

The uv-venv approach we already validated in the FreeSurfer work
sidesteps both Conda and Fedora's-unable-to-package-TensorFlow problems
without requiring new packaging machinery.

---

## Extension distribution: two coexisting models

| Path | When | Trust model |
|---|---|---|
| **Native RPM** (`3dslicer-dmri`, `3dslicer-elastix`, `3dslicer-rt`, ...) | Reproducible studies, hospital deployment, regulated CI, multi-user shared systems | Signed by Fedora COPR; matches `rpm-ostree` ideal; entire dep graph version-pinned |
| **Slicer Extension Manager** (built-in GUI) | Personal exploration, brand-new experimental modules, individual workstation | Slicer's own catalog; unsigned; pulled at runtime |

Document both clearly; let users pick per workload. The native-RPM path
is the *new* story Fedora can offer that no other distro does as cleanly.

---

## Compliance & medical-device angle

3D Slicer's license carries the standard "not FDA cleared, research-use
only" notice. **That's actually a feature for Fedora's positioning**:
medical-device companies need a *documented, reproducible build
environment* for IEC 62304 / 21 CFR Part 820 software-of-unknown-
provenance (SOUP) declarations.

Fedora + COPR provides exactly that out of the box:

- **Git → SRPM → RPM** audit trail (every spec change reviewable)
- **Signed metadata** via Fedora's signing infrastructure
- **Reproducible builds** (mock chroots, deterministic source pinning,
  documented dependency graph)
- **Long-term-stable point releases** (Fedora 44 → 45 → 46 with
  predictable rebase windows)

For a startup building a surgical-navigation product, citing "Fedora 44
+ COPR mhough/neurofedora as the development environment, frozen at
2026-Q3 commit X" in their 510(k) submission carries real regulatory
weight that competitors don't match for free.

---

## Hardware acceleration story

| Stack | Path |
|---|---|
| NVIDIA CUDA (most common in ML-medical workloads) | RPM Fusion non-free + NVIDIA's `cuda-fedora` repo + our `3dslicer-cuda` meta-package (see CUDA-RPM-FUSION.md) |
| AMD ROCm | Fedora's native `rocm-*` packages + our `3dslicer-rocm` meta-package |
| Apple Metal | Not applicable (Fedora is Linux-only); recommend dual-boot or container for those users |
| CPU-only | Default; everything works without GPU but slower for ML extensions |

---

## Near-term roadmap

| Sprint | Deliverable |
|---|---|
| **Now** (current sprint) | Stable 3dslicer 5.10.0 + 5 major extensions building in COPR |
| **+2 weeks** | Slicer Preview channel + 10 extensions building |
| **+1 month** | `slicer-fspython` uv-venv path + docs site |
| **+1 month** | `3dslicer-cuda` meta-package + RPM Fusion submission for CUDA-enabled bits |
| **+2 months** | Submit `qRestAPI`, `commontk-applauncher`, `ctk-qt6` to Fedora dist-git |
| **+3 months** | "Medical Imaging Lab" Fedora Spin (or Toolbx/Distrobox image with all extensions pre-installed) |
| **+6 months** | Slicer itself in Fedora dist-git — the long-tail goal; requires ITK/VTK/CTK packaging cleanup at the Fedora-review level |

---

## Community work to amplify

1. **Announce in the Slicer Forum** when the first stable RPM lands.
   The Slicer community will signal-boost.
2. **Partner with QIICR** (NCI Cancer Imaging) — they own DCMQI and
   several oncology workflows; collaborate on DICOM packaging.
3. **Submit incrementally to Fedora dist-git** — start with the
   satellites (`qRestAPI`, `commontk-applauncher`), then `ctk-qt6`,
   then someday Slicer itself. Each one in Fedora-proper makes the
   stack visible to a wider audience.
4. **Fedora Workstation Lab SIG** — push for a "Medical Imaging Lab"
   spin (Fedora's "Spin" model is purpose-built for this).
5. **Education**: NA-MIC training events, ISMRM tutorials, IEEE EMBC
   workshops, MICCAI demo sessions — show up with `dnf install` demos.

---

## What success looks like

Two years from now, this is real if any of these are true:

- A clinical fellow at a US academic medical center types
  `dnf install 3dslicer slicer-dmri` on a workstation laptop and is
  reading patient diffusion data within 15 minutes.
- A startup CTO building surgical-navigation software cites Fedora as
  their development OS in a regulatory submission.
- The Slicer documentation lists Fedora's RPM install as a
  recommended path alongside the upstream binary tarball.
- A new postdoc opens a Toolbx container with the full medical-imaging
  stack pre-installed and starts working without any compilation step.

---

## Why now

GCC 16, Qt 6.10, ITK 5.4, VTK 9.6, and Python 3.14 all converged in
Fedora 44 (2026). Slicer 5.10.0 supports system-installed versions of
all of the above (via `Slicer_USE_SYSTEM_*` cmake flags). For the first
time in Slicer's 20-year history, an entirely-system-package build is
feasible. This packaging effort captures that window.

The competing distributions (Ubuntu LTS, Debian) won't have these
versions until 2027-2028. Fedora has a 12-18-month lead — long enough
to establish the medical-imaging-on-Fedora story as the default.
