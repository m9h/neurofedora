%global pypi_name pyddm

Name:           python-%{pypi_name}
Version:        0.9.0
Release:        1%{?dist}
Summary:        Generalized drift-diffusion modeling for Python

License:        MIT
URL:            https://github.com/mwshinn/PyDDM
Source0:        %{pypi_source}

# PyDDM ships a C extension (pyddm.csolve), so this package is architecture
# specific.
BuildRequires:  gcc
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
PyDDM is a simulator and modeling framework for generalized drift-diffusion
models (GDDMs), aimed at cognitive neuroscience. It offers fast numerical
solutions of the drift-diffusion model and its generalizations, a flexible
syntax for defining drift rate, noise, bounds, starting position and
non-decision time as arbitrary Python functions, model fitting to reaction
time data, and a graphical model-exploration interface.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# PyDDM installs two top-level packages: the modern "pyddm" and a legacy
# backward-compatibility shim "ddm".
%pyproject_save_files pyddm ddm

%check
%pyproject_check_import -t

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE.txt
%doc README.md

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.9.0-1
- Initial package
