%global pypi_name spectrum

Name:           python-spectrum
Version:        0.10.0
Release:        1%{?dist}
Summary:        Spectral analysis tools for Python

License:        BSD-3-Clause
URL:            https://github.com/cokelaer/spectrum
Source0:        %{pypi_source %{pypi_name}}

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  gcc

%description
spectrum is a Python library providing tools to estimate power spectral
densities (periodogram, multitapers/DPSS, parametric AR/ARMA methods,
correlograms, windowing functions and more).

%package -n python3-spectrum
Summary:        %{summary}

%description -n python3-spectrum
spectrum provides spectral-analysis (power spectral density) estimators
for Python.

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
%pyproject_check_import

%files -n python3-spectrum -f %{pyproject_files}
%doc README.rst

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 0.10.0-1
- Initial package (pyfix dependency chain, via easydev).
