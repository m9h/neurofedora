%global pypi_name pylsl

Name:           python-%{pypi_name}
Version:        1.18.2
Release:        1%{?dist}
Summary:        Python library for LSL (lab streaming layer)

License:        MIT
URL:            https://github.com/labstreaminglayer/pylsl
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# setuptools-scm reads PKG-INFO from the sdist; no .git needed.

# Runtime: pylsl uses ctypes.find_library("lsl") to locate liblsl at runtime.
# We Require liblsl so the .so is on the system.
Requires:       liblsl >= 1.17.0

%global _description %{expand:
pylsl is a Python interface to the Lab Streaming Layer (LSL). LSL is an
open-source networked middleware ecosystem for real-time streaming, recording,
and analysis of time-series data measured from any sensor or device.

This package provides Python bindings around the upstream liblsl C/C++
library; liblsl itself ships separately and is loaded at runtime via
ctypes.find_library("lsl").}

%description %{_description}


%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %{_description}


%prep
%autosetup -n %{pypi_name}-%{version} -p1


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}


%check
# %%pyproject_check_import would try to dlopen liblsl via ctypes
# (pylsl.lib.__init__ runs find_liblsl_libraries at import). That works
# only if liblsl is installed in the build chroot — which we cannot
# assume without a BuildRequires on liblsl. Skip the import check; the
# Requires: liblsl on the binary package ensures runtime correctness.
:


%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md


%changelog
* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.18.2-1
- Initial package for the mhough/neurofedora COPR.
- Pure-Python noarch wheel; liblsl resolved at runtime via ctypes.
