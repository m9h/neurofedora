Name:           python-trame-server
Version:        3.12.4
Release:        1%{?dist}
Summary:        Internal server-side implementation of trame

License:        Apache-2.0
URL:            https://github.com/Kitware/trame-server
Source:         %{pypi_source trame_server}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-more-itertools
BuildRequires:  python3-trame-common
BuildRequires:  python3-wslink

%global _description %{expand:
trame-server holds the Python-side runtime of a trame application:
the state machine, controller, and protocol implementations that
wslink uses to push updates to the browser. Required by every trame
application but normally pulled in transitively via the trame meta
package.}

%description %_description

%package -n     python3-trame-server
Summary:        %{summary}
Requires:       python3-more-itertools
Requires:       python3-trame-common >= 1.2.3
Requires:       python3-wslink >= 2.5.7

%description -n python3-trame-server %_description

%prep
%autosetup -p1 -n trame_server-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files trame_server

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame-server -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 3.12.4-1
- Initial package for the trame-slicer dependency chain.
