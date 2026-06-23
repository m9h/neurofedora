# Dependency of python-pyactr (not currently in Fedora). Pure-Python, MIT.
%global pypi_name simpy

Name:           python-%{pypi_name}
Version:        4.1.2
Release:        1%{?dist}
Summary:        Discrete-event simulation framework for Python

License:        MIT
URL:            https://simpy.readthedocs.io/
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
SimPy is a process-based discrete-event simulation framework based on
standard Python. Processes are defined by Python generator functions and
can model active components such as customers, vehicles or agents.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files -l %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.rst AUTHORS.rst

%changelog
* Sun Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 4.1.2-1
- Initial package (dependency for pyactr)
