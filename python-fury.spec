%global pypi_name fury

Name:           python-%{pypi_name}
Version:        0.12.0
Release:        1%{?dist}
Summary:        Free Unified Rendering in Python

License:        BSD-3-Clause
URL:            https://fury.gl
Source0:        %{pypi_source %{pypi_name}}
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-numpy
BuildRequires:  python3-scipy
BuildRequires:  python3-vtk
BuildRequires:  python3-pillow
BuildRequires:  python3-pygltflib

%description
FURY is a free and open-source software library for scientific 
visualization and 3D animations in Python.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-vtk
Requires:       python3-pillow
Requires:       python3-pygltflib

%description -n python3-%{pypi_name}
FURY is a free and open-source software library for scientific 
visualization and 3D animations in Python.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fury

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.12.0-1
- Initial package for dipy ecosystem
