%global pypi_name formulaic

Name:           python-%{pypi_name}
Version:        1.2.2
Release:        1%{?dist}
Summary:        High-performance implementation of Wilkinson formulas for Python

License:        MIT
URL:            https://github.com/matthewwardrop/formulaic
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch

BuildRequires:  python3-devel

%global _description %{expand:
Formulaic is a high-performance implementation of Wilkinson formulas for
Python, used to translate concise model specifications (e.g. "y ~ x1 + x2*x3")
into model (design) matrices. It is a core dependency of pybids' statistical
modeling support.}

%description %{_description}

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %{_description}

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
# hatchling + hatch-vcs from pyproject [build-system]; -r adds runtime deps
# (interface-meta, narwhals, numpy, pandas, scipy, typing-extensions, wrapt)
# so the %%check import resolves.
%pyproject_buildrequires -r

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.2-1
- Initial package (hatchling backend). Core runtime blocker for python-pybids
  (design-matrix construction); deps interface-meta (Fedora) + narwhals (COPR).
