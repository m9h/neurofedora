%global pypi_name nninteractive-client
%global dist_name nninteractive_client
# PEP 420 namespace: the client ships nnInteractive/inference/remote/ only, and
# shares the nnInteractive + nnInteractive.inference namespace dirs (no __init__.py)
# with the full nnInteractive distribution.
%global import_name nnInteractive

Name:           python-%{pypi_name}
Version:        2.5.1
Release:        1%{?dist}
Summary:        Thin HTTP client for the nnInteractive inference server

License:        Apache-2.0
URL:            https://github.com/MIC-DKFZ/nnInteractive
Source0:        %{pypi_source %{dist_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
The client half of nnInteractive: a small HTTP wrapper that submits images and
interaction prompts (points, scribbles, bounding boxes, lassos) to an
nnInteractive inference server and receives the resulting 3D segmentation.

It carries none of the model or deep-learning dependencies, so viewers and
scripts can drive a remote nnInteractive server without installing torch.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{dist_name}-%{version}

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

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.1-1
- Initial package. Client half of the nnInteractive stack; usable standalone
  against a remote inference server (no torch needed).
