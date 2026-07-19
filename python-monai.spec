# MONAI (Medical Open Network for AI) — PyTorch-based deep-learning
# framework for healthcare imaging. Pure-Python, noarch.
#
# VENUE NOTE: MONAI is Apache-2.0 and its only hard deps are torch + numpy,
# both already in Fedora proper (python3-torch 2.9.1, python3-numpy). It
# therefore does NOT belong in / need RPM Fusion (which exists for nonfree
# or patent-encumbered software). This spec targets the mhough/neurofedora
# COPR for immediate use; it is equally eligible for Fedora proper.
#
# MONAI optionally compiles C++/CUDA extensions, gated by the BUILD_MONAI
# env var (default "0" -> pure-Python). We leave it off: the resulting wheel
# is the upstream-published py3-none-any (noarch). GPU acceleration is a
# *torch* concern (Fedora ships CPU torch); MONAI runs on whatever torch is
# installed, so no MONAI-side change is needed for it.

%global pypi_name monai

# Pure-Python noarch — no debuginfo.
%global debug_package %{nil}

%global _description %{expand:
MONAI is a PyTorch-based, open-source framework for deep learning in
healthcare imaging, part of the PyTorch Ecosystem. It provides
domain-optimized, reproducible building blocks for medical image
analysis: flexible multi-dimensional transforms and I/O (NIfTI, DICOM,
NRRD), networks and loss functions for segmentation/classification/
registration/generation, sliding-window inference, metrics, and
composable training/evaluation engines built on PyTorch Ignite.

It is developed by the MONAI Consortium (King's College London, NVIDIA,
and a broad academic-clinical community) and is widely used as the model
layer behind tools such as MONAI Label and 3D Slicer's AI extensions.}

Name:           python-%{pypi_name}
Version:        1.6.0
Release:        1%{?dist}
Summary:        AI toolkit for healthcare imaging (PyTorch-based)

License:        Apache-2.0
URL:            https://monai.io
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch

BuildRequires:  python3-devel

%description %{_description}

%package -n python3-%{pypi_name}
Summary:        %{summary}

# Optional features. MONAI's only hard runtime deps are torch + numpy
# (auto-generated from project metadata); these weak deps light up the
# common extras and are all packaged in Fedora.
Recommends:     %{py3_dist nibabel}
Recommends:     %{py3_dist scikit-image}
Recommends:     %{py3_dist pillow}
Recommends:     %{py3_dist einops}
Recommends:     %{py3_dist tqdm}
Recommends:     %{py3_dist pandas}
Recommends:     %{py3_dist scipy}
Recommends:     %{py3_dist pyyaml}
Recommends:     %{py3_dist psutil}
Recommends:     %{py3_dist lmdb}
Recommends:     %{py3_dist matplotlib}
Recommends:     %{py3_dist h5py}
Recommends:     %{py3_dist pydicom}
Recommends:     %{py3_dist tensorboardX}

%description -n python3-%{pypi_name} %{_description}

%prep
%autosetup -p1 -n %{pypi_name}-%{version}

%generate_buildrequires
# Default includes runtime requirements (torch, numpy) so %%check can import
# MONAI against Fedora's torch — that import is the real feasibility proof.
%pyproject_buildrequires

%build
# Leave the C++/CUDA extension off -> upstream's noarch py3 wheel.
export BUILD_MONAI=0
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
# Smoke test: import the package (and a few core submodules) against the
# system PyTorch. Proves MONAI 1.5.2 runs on Fedora's python3-torch.
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.6.0-1
- Update to 1.6.0

* Tue Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.2-1
- Initial package for the mhough/neurofedora COPR.
- Pure-Python noarch build (BUILD_MONAI=0); hard deps torch + numpy are
  satisfied by Fedora proper (python3-torch 2.9.1). Apache-2.0, so no
  RPM Fusion needed.
- %%check imports MONAI against the system PyTorch as a feasibility proof.
