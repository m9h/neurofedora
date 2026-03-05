%global pypi_name pygltflib

Name:           python-%{pypi_name}
Version:        1.16.5
Release:        1%{?dist}
Summary:        Python library for reading, writing and handling GLTF v2 files

License:        MIT
URL:            https://gitlab.com/dodgyville/pygltflib
Source0:        %{pypi_source %{pypi_name}}
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-dataclasses-json
BuildRequires:  python3-deprecated

%description
pygltflib is a Python library for reading, writing and handling GLTF v2 files.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-dataclasses-json
Requires:       python3-deprecated

%description -n python3-%{pypi_name}
pygltflib is a Python library for reading, writing and handling GLTF v2 files.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pygltflib

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.5-1
- Initial package for fury dependency
