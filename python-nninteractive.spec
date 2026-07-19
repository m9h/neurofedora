%global pypi_name nninteractive
%global dist_name nninteractive
# PEP 420 namespace shared with the lightweight nninteractive-client package.
%global import_name nnInteractive

Name:           python-%{pypi_name}
Version:        2.5.1
Release:        1%{?dist}
Summary:        Promptable 3D interactive segmentation for medical images

License:        Apache-2.0
URL:            https://github.com/MIC-DKFZ/nnInteractive
Source0:        %{pypi_source %{dist_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
nnInteractive is a promptable 3D segmentation framework from the DKFZ Division
of Medical Image Computing. Rather than segmenting a fixed set of structures, it
takes user interactions -- points, scribbles, bounding boxes and lassos -- and
produces a full 3D segmentation from them, refining as further prompts arrive.

This package provides the in-process inference engine, model management, and the
nninteractive-server HTTP server that image viewers connect to. To drive a
remote server without pulling in torch, install python3-nninteractive-client
instead.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-nninteractive-client = %{version}-%{release}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{dist_name}-%{version}

# See python-nnunetv2.spec for the full rationale: upstream's `!=2.9.*` torch
# exclusion is a CUDA/cuDNN performance guard (torch 2.9 disabled fast conv
# implementations after a cuDNN bug), not a correctness constraint, and it does
# not apply to Fedora's CPU-only torch 2.9.1. Relax it so the dependency
# resolves.
sed -i 's/"torch>=2\.1\.2,!=2\.9\.\*"/"torch>=2.1.2"/' pyproject.toml
grep -q '!=2.9' pyproject.toml && exit 1 || :

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc readme.md
%{_bindir}/nninteractive-server
%{_bindir}/nninteractive-available-models
%{_bindir}/nninteractive-download-model

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.1-1
- Initial package. Gives ITK-SNAP 4.4 (which already exposes nnInteractive
  point/scribble/lasso modes) a local inference backend to talk to. Relaxes the
  upstream torch != 2.9.* exclusion, a CUDA/cuDNN performance guard that does
  not apply to Fedora's CPU-only torch (see the comment in %%prep).
