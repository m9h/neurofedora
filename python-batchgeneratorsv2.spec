%global pypi_name batchgeneratorsv2
%global import_name batchgeneratorsv2

Name:           python-%{pypi_name}
Version:        0.3.5
Release:        1%{?dist}
Summary:        Torch-native rewrite of the batchgenerators augmentation framework

License:        Apache-2.0
URL:            https://github.com/MIC-DKFZ/batchgeneratorsv2
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
batchgeneratorsv2 is the second-generation rewrite of the DKFZ batchgenerators
augmentation framework, reimplementing the spatial and intensity transforms on
top of torch tensors so augmentation can run on the GPU and compose with torch
data loading. It is the augmentation path used by current nnU-Net versions.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
# Two modules cannot import in the buildroot and neither is part of the library's
# declared dependency set:
#   benchmarks.*                     - developer benchmark scripts
#   transforms.nnunet.remove_connected_components
#                                    - imports acvl_utils, which this package does
#                                      not declare as a dependency (and which sits
#                                      later in this build chain)
%pyproject_check_import -e '*.benchmarks.*' -e '*.transforms.nnunet.remove_connected_components'

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc readme.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.3.5-1
- Initial package. Augmentation path of current nnU-Net, part of the
  nnInteractive dependency chain.
