Name:           python-trame-common
Version:        1.2.4
Release:        1%{?dist}
Summary:        Dependency-less helpers shared across trame packages

License:        Apache-2.0
URL:            https://github.com/Kitware/trame-common
Source:         %{pypi_source trame_common}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
trame-common holds the small set of dependency-free classes and helpers
shared by trame-server, trame-client, trame-rca, and trame itself. It
has no runtime deps of its own and is loaded by every trame component
at import time.}

%description %_description

%package -n     python3-trame-common
Summary:        %{summary}

%description -n python3-trame-common %_description

%prep
%autosetup -p1 -n trame_common-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files trame_common

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame-common -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.4-1
- Update to 1.2.4 (current upstream; freshness sweep 2026-06-14)

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.3-1
- Initial package for the trame-slicer dependency chain.
