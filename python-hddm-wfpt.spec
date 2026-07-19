%global pypi_name hddm-wfpt
%global dist_name hddm_wfpt

Name:           python-%{pypi_name}
Version:        0.1.7
Release:        1%{?dist}
Summary:        Wiener first-passage-time likelihoods for drift-diffusion models

# The bundled LICENSE file is the MIT License (the PyPI/Trove classifier
# erroneously lists BSD; the actual license text governs).
License:        MIT
URL:            https://github.com/lnccbrown/hddm-wfpt
Source0:        %{pypi_source %{dist_name}}

# Cython C/C++ extension modules (wfpt, cdfdif_wrapper), so this build is arch
# specific.
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
hddm-wfpt provides fast Cython implementations of the Wiener first-passage-time
(WFPT) distribution and related cumulative-distribution routines used to
compute drift-diffusion model likelihoods. It is a lightweight computational
core extracted from HDDM and used by the HSSM toolbox.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{dist_name}-%{version}
# Upstream caps requires-python at <3.15, which excludes rawhide's Python 3.15;
# the Cython sources build and import fine there, so relax the upper bound.
sed -i 's/,<3.15"/,<3.16"/' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# The package "hddm_wfpt" plus two top-level compiled extensions installed
# alongside it (wfpt, cdfdif_wrapper).
%pyproject_save_files hddm_wfpt wfpt cdfdif_wrapper

%check
%pyproject_check_import -t

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc Readme.rst

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.7-1
- Update to 0.1.7

* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.6-1
- Initial package (HSSM WFPT likelihood core; partial HSSM dependency stack)
