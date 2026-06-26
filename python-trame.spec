Name:           python-trame
Version:        3.13.2
Release:        2%{?dist}
Summary:        Python framework for building reactive web applications

License:        Apache-2.0
URL:            https://github.com/Kitware/trame
Source:         %{pypi_source trame}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-trame-server
BuildRequires:  python3-trame-client
BuildRequires:  python3-trame-common
BuildRequires:  python3-wslink
BuildRequires:  python3-pyyaml

%global _description %{expand:
trame is a Python framework for building reactive web applications.
This meta package wires together the trame-server, trame-client, and
trame-common runtimes so applications only need to depend on trame
itself. Used by every trame-* downstream application including
trame-slicer.}

%description %_description

%package -n     python3-trame
Summary:        %{summary}
Requires:       python3-trame-server >= 3.12.2
Requires:       python3-trame-client >= 3.12.2
Requires:       python3-trame-common >= 1.2.3
Requires:       python3-wslink >= 2.5.6
Requires:       python3-pyyaml

%description -n python3-trame %_description

%prep
%autosetup -p1 -n trame-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files trame

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Thu Jun 26 2026 Morgan Hough <morgan.hough@gmail.com> - 3.13.2-2
- Rebuild against Python 3.15 (rawhide). Release bump so the py3.15
  build strictly supersedes the lingering same-NVR py3.14 RPM that
  was still winning in the COPR buildroot repo.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 3.13.2-1
- Initial package for the trame-slicer dependency chain.
