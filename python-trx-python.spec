Name:           python-trx-python
Version:        0.4.0
Release:        1%{?dist}
Summary:        Community-oriented file format for tractography

# Upstream pyproject says "BSD License" (SPDX: BSD-3-Clause per the
# LICENSE file shipped in the tarball).
License:        BSD-3-Clause
URL:            https://github.com/tee-ar-ex/trx-python
Source:         %{url}/archive/refs/tags/%{version}/trx-python-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools_scm

%global desc %{expand: \
TRX is a community-driven binary file format for storing tractography
streamlines (computed from diffusion MRI). The python-trx-python
package provides the reference reader/writer plus a `trx` CLI for
manipulating .trx files (concatenation, conversion, validation).

Required by dipy 1.12+ for its tractogram I/O. Upstream:
https://github.com/tee-ar-ex/trx-python}

%description
%{desc}

%package -n python3-trx-python
Summary:        %{summary}

%description -n python3-trx-python
%{desc}


%prep
%autosetup -n trx-python-%{version}

# Upstream uses setuptools_scm for version detection — provide a
# SETUPTOOLS_SCM_PRETEND_VERSION at build time so it doesn't try to
# read the git tag (the tarball has no .git/).


%generate_buildrequires
%pyproject_buildrequires


%build
SETUPTOOLS_SCM_PRETEND_VERSION=%{version} %pyproject_wheel


%install
SETUPTOOLS_SCM_PRETEND_VERSION=%{version} %pyproject_install
%pyproject_save_files trx


%files -n python3-trx-python -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/trx
%{_bindir}/trx_concatenate_tractograms


%changelog
* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.0-1
- Initial COPR build (mhough/neurofedora). Prerequisite for python-dipy
  1.12+ which added a hard dep on trx-python for tractogram I/O. Pure
  Python, setuptools build backend, BSD-3-Clause. All runtime deps
  (deepdiff, nibabel, numpy, typer) already in Fedora.
