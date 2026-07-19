%global pypi_name acvl-utils
%global dist_name acvl_utils
%global import_name acvl_utils

Name:           python-%{pypi_name}
Version:        0.2.6
Release:        1%{?dist}
Summary:        Utility library of the DKFZ Applied Computer Vision Lab

License:        Apache-2.0
URL:            https://github.com/MIC-DKFZ/acvl_utils
Source0:        %{pypi_source %{dist_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
Shared helper code from the DKFZ Applied Computer Vision Lab: bounding-box and
cropping arithmetic, connected-component and instance-segmentation helpers,
morphology, array manipulation and general imaging utilities used across the
lab's segmentation projects, including nnU-Net and nnInteractive.}

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
# Upstream spells it LICENCE.
%license LICENCE
%doc README.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.6-1
- Initial package. Utility layer of nnU-Net / nnInteractive, part of the
  nnInteractive dependency chain.
