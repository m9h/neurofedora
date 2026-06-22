%global pypi_name bsmschema

Name:           python-%{pypi_name}
Version:        0.1.1
Release:        2%{?dist}
Summary:        Pydantic schema for BIDS Stats Models

License:        Apache-2.0
URL:            https://github.com/bids-standard/stats-models
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch

BuildRequires:  python3-devel

%global _description %{expand:
bsmschema provides a Pydantic schema for the BIDS Stats Models specification —
the standard for describing statistical models over Brain Imaging Data
Structure (BIDS) datasets. It is a build dependency of pybids' model-parsing
support.}

%description %{_description}

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %{_description}

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
# hatchling + hatch-vcs come from pyproject [build-system]; -r adds the runtime
# deps (pydantic >=2) so the %%check import works.
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
* Sat Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.1-2
- Rebuild at Release 2 to escape Fedora's fedora-obsolete-packages obsoletion of
  python3-bsmschema < 0.1.1-2 (Fedora retired the package). The COPR 0.1.1-1 was
  itself obsoleted, leaving python3-pybids+test (which Requires bsmschema) with no
  provider. 0.1.1-2 is not < 0.1.1-2, so it survives and satisfies pybids again.

* Fri Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.1-1
- Initial package (hatchling backend; runtime dep pydantic >=2). Unblocks the
  python-pybids resubmit, which BuildRequires bsmschema for stats-model parsing.
