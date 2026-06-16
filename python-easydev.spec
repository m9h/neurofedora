%global pypi_name easydev

Name:           python-easydev
Version:        0.14.0
Release:        1%{?dist}
Summary:        Common utilities to ease the development of Python packages

License:        BSD-3-Clause
URL:            https://github.com/cokelaer/easydev
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
easydev provides miscellaneous functions and utilities that are commonly
reused across Python projects (configuration handling, console tools,
decorators, multiprocessing helpers and more).

%package -n python3-easydev
Summary:        %{summary}

%description -n python3-easydev
easydev provides miscellaneous functions and utilities reused across
Python projects.

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

%files -n python3-easydev -f %{pyproject_files}
%doc README.rst

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 0.14.0-1
- Initial package (pyfix dependency chain, via spectrum).
