%global pypi_name pygpc
%global commit 51c975354b8c4db0c579cd30b284d5bdc7b3f7f7
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           python-%{pypi_name}
Version:        0.4.4
Release:        1%{?dist}
Summary:        Sensitivity and uncertainty analysis of simulation-based models

License:        GPL-3.0-only
URL:            https://github.com/pygpc-polynomial-chaos/pygpc
Source0:        %{url}/archive/%{commit}/%{pypi_name}-%{shortcommit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-Cython
BuildRequires:  python3-numpy
BuildRequires:  python3-scipy
BuildRequires:  python3-pytest
BuildRequires:  python3-matplotlib
BuildRequires:  python3-h5py
BuildRequires:  python3-pillow

%description
pygpc is a Python toolbox for sensitivity and uncertainty analysis of
simulation-based models using generalized Polynomial Chaos (gPC).

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-matplotlib
Requires:       python3-h5py
Requires:       python3-pillow

%description -n python3-%{pypi_name}
pygpc is a Python toolbox for sensitivity and uncertainty analysis of
simulation-based models using generalized Polynomial Chaos (gPC).

%prep
%autosetup -n %{pypi_name}-%{commit}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
# Basic import test
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.4-1
- Initial package for SimNIBS dependency
