# nengo 4.1.0 is GPL v2 (see LICENSE.rst: "GPL v2 License"), confirmed against
# the bundled license file — despite ABR's non-commercial licensing of *other*
# Nengo components (nengo-dl, nengo-fpga, nengo-loihi). Core Nengo is free
# software, so this belongs in the FREE mhough/neurofedora COPR (not nonfree).
%global pypi_name nengo

Name:           python-%{pypi_name}
Version:        4.1.0
Release:        1%{?dist}
Summary:        Brain modeling with the Neural Engineering Framework

License:        GPL-2.0-only
URL:            https://www.nengo.ai/
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
Nengo is a Python library for building and simulating large-scale neural
models using the Neural Engineering Framework (NEF). It can model spiking
and non-spiking neurons, plasticity and learning rules, and scales from
single neurons to large functional brain models, with a deliberately small
dependency footprint (NumPy only at runtime).}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}
# Normalize CRLF line endings in shipped docs.
sed -i 's/\r$//' README.rst CHANGES.rst

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# Also package the top-level pytest_nengo plugin module (registered via a
# pytest11 entry point); it only loads under pytest, so it needs no runtime dep.
%pyproject_save_files -l %{pypi_name} pytest_nengo

%check
# Only verify the top-level import: numpy is Nengo's sole hard dependency,
# while various submodules lazily import optional deps (scipy, matplotlib,
# scikit-learn, IPython) and test modules import pytest plugins.
%pyproject_check_import -t -e pytest_nengo

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.rst CHANGES.rst

%changelog
* Sun Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 4.1.0-1
- Initial package (core Nengo, GPLv2)
