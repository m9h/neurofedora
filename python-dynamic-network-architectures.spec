%global pypi_name dynamic-network-architectures
%global dist_name dynamic_network_architectures
%global import_name dynamic_network_architectures

Name:           python-%{pypi_name}
Version:        0.4.4
Release:        1%{?dist}
Summary:        Dynamically configurable network architectures for medical segmentation

License:        Apache-2.0
URL:            https://github.com/MIC-DKFZ/dynamic-network-architectures
Source0:        %{pypi_source %{dist_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
A library of torch network architectures whose topology is built at runtime from
a configuration rather than hard-coded: encoders, decoders, residual and
convolutional U-Nets, plus transformer based designs (EVA, Primus, DINOv2).

nnU-Net uses it to instantiate the architecture chosen by its dataset
fingerprint, which is why the network shape can adapt per dataset.}

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
%doc README.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.4-1
- Initial package. Architecture library of nnU-Net v2, part of the
  nnInteractive dependency chain.
