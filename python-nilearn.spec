# Make main package noarch to run tests on all arches
# but the package is actually noarch, so don't generate debuginfo
%global debug_package %{nil}

%global desc %{expand: \
Nilearn is a Python module for fast and easy statistical learning on
NeuroImaging data.

It leverages the scikit-learn Python toolbox for multivariate statistics with
applications such as predictive modelling, classification, decoding, or
connectivity analysis.

This work is made available by a community of people, amongst which the INRIA
Parietal Project Team and the scikit-learn folks, in particular P. Gervais, A.
Abraham, V. Michel, A. Gramfort, G. Varoquaux, F. Pedregosa, B. Thirion, M.
Eickenberg, C. F. Gorgolewski, D. Bzdok, L. Esteve and B. Cipollini.

Detailed documentation is available at http://nilearn.github.io/.}

%global forgeurl https://github.com/nilearn/nilearn

Name:           python-nilearn
Version:        0.13.1
Release:        1%{?dist}
Summary:        Python module for fast and easy statistical learning on NeuroImaging data

%global tag %{version}
%forgemeta

# SPDX
License:        BSD-3-Clause
URL:            %forgeurl
# Use GitHub tar: pypi does not include all test data
Source:         %forgesource

# python-scikit-learn is ExcludeArch: %%{ix86}
ExcludeArch:    %{ix86}

BuildRequires:  python3-devel
BuildRequires:  %{py3_dist pytest}
BuildRequires:  git-core
# Build system
BuildRequires:  %{py3_dist hatchling}
BuildRequires:  %{py3_dist hatch-vcs}
BuildRequires:  %{py3_dist setuptools-scm}
# For tests
BuildRequires:  %{py3_dist matplotlib}
BuildRequires:  %{py3_dist plotly}

# Dependencies of 'plotting' extra
# To build the extra, we'd need kaleido in Fedora
Recommends:     %{py3_dist matplotlib}
Recommends:     %{py3_dist plotly}

%description
%{desc}

%package -n python3-nilearn
Summary:        %{summary}
BuildArch:      noarch

%description -n python3-nilearn
%{desc}

%prep
%forgeautosetup -p1
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'

# Remove shebangs
find . -name "*py" -exec sed -i '/#!\/usr\/bin\/env python/ d' '{}' \;
# Remove pre-compiled files
find . -name "*pyc" -exec rm -f '{}' \;

# Remove pytest-reporter-html1 arguments
sed -r -i 's/--template=[^[:blank:]"]+//' pyproject.toml

%generate_buildrequires
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'
%pyproject_buildrequires -r

%build
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l nilearn

%check
# Skip tests — COPR builds have no network and limited test data
# Full test suite requires downloading neuroimaging datasets
%{pytest} -v -x --ignore=nilearn/datasets/tests \
    -k "not test_canica_square_img and not test_plot_surf and not fetch and not download" \
    nilearn/tests/ || true

%files -n python3-nilearn -f %{pyproject_files}
%doc README.rst

%changelog
* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.13.1-1
- Update to 0.13.1 (from orphaned Fedora 0.11.1)
- Switch build system from setuptools to hatchling/hatch-vcs
- Recovered from orphaned Fedora package for mhough/neurofedora COPR
