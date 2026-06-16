%global pypi_name pyfix

Name:           python-%{pypi_name}
Version:        0.10.0
Release:        1%{?dist}
Summary:        Python implementation of FSL's FIX ICA-based denoising tool

# Apache-2.0 (unlike the legacy R/MATLAB FIX, which is LicenseRef-FSL).
License:        Apache-2.0
URL:            https://git.fmrib.ox.ac.uk/fsl/pyfix
Source0:        %{url}/-/archive/%{version}/pyfix-%{version}.tar.gz#/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
pyfix is a pure-Python reimplementation of FSL's FIX (FMRIB's ICA-based
X-noiseifier) for automatic classification and removal of artefactual
components from single-subject ICA (MELODIC) decompositions of FMRI data.
It replaces the legacy FIX's MATLAB Compiler Runtime + R classifier stack
with scikit-learn, and bundles the standard trained models (Standard, HCP,
UK Biobank, macaque, ...).}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
# FIX operates on MELODIC ICA output and uses the FSL image tools at runtime.
Requires:       fsl-melodic
Requires:       fsl-avwutils
# Provide the legacy command name for discoverability.
Provides:       fsl-fix = %{version}-%{release}

%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
# setuptools-scm reads the version from git, absent in the release tarball.
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
# Version is derived from git via setuptools-scm; there is no .git in the
# release tarball, so pin it explicitly.
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_install
# The bundled .pyfix_model trained classifiers ship as package data.
%pyproject_save_files %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md
%{_bindir}/fix
%{_bindir}/convert_fix_model

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 0.10.0-1
- Initial package: pyfix, the pure-Python (scikit-learn) reimplementation of
  FSL FIX. Apache-2.0; bundles the standard trained models; no MATLAB Compiler
  Runtime or R required (a clean replacement for legacy FIX). Provides fsl-fix.
