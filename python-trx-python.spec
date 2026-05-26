Name:           python-trx-python
Version:        0.4.0
Release:        4%{?dist}
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

# Upstream pyproject sets [tool.setuptools_scm] fallback_version="0.0",
# so when the release tarball (no .git/) is built, setuptools_scm yields
# "0.0", which trips Fedora's _python_dist_allow_version_zero check.
#
# Set SETUPTOOLS_SCM_PRETEND_VERSION to override. CRUCIAL: must be set
# with `export` on its own line — `VAR=value %%pyproject_wheel` does NOT
# work because %%pyproject_wheel expands to a multi-line shell block, so
# bash treats `VAR=value` as a plain shell assignment (not exported to
# subprocesses), and the Python wheel-build subprocess never sees it.
# -2 hit this exact trap. (% in comments MUST be doubled to prevent
# RPM macro expansion — -3 ran %%pyproject_wheel's expansion inside
# %prep when the bare % expanded the macro right here.)


%generate_buildrequires
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_buildrequires


%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_wheel


%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files trx


%files -n python3-trx-python -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/trx
%{_bindir}/trx_concatenate_tractograms


%changelog
* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.0-4
- Escape bare %% in %%prep comments — -3's comment said `%%pyproject_wheel`
  with single %%, and RPM dutifully expanded the macro right there inside
  %%prep, dumping the wheel-build pipeline mid-comment. Build died with
  "No module named pip" because pip isn't installed in the %%prep BR set.
  Doubled every %% in the explanatory comment.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.0-3
- Use `export SETUPTOOLS_SCM_PRETEND_VERSION` on its own line instead of
  the `VAR=value %%pyproject_*` prefix form. %%pyproject_wheel et al expand
  to multi-line shell blocks, so the prefix form sets a shell var but
  doesn't export it — the Python wheel-build subprocess never saw the
  override, and setuptools_scm fell back to "0.0" again. -2 logs show the
  trap: every "+ SETUPTOOLS_SCM_PRETEND_VERSION=0.4.0" was followed by
  "creating .../trx_python-0.0.dist-info".

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.0-2
- Set SETUPTOOLS_SCM_PRETEND_VERSION in %%generate_buildrequires too —
  -1 only set it for %%build and %%install but the wheel-metadata
  extraction in %%pyproject_buildrequires also needs it. Without it,
  setuptools_scm fell back to "0.0" and Fedora's version-zero check
  refused to ship the wheel.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.0-1
- Initial COPR build (mhough/neurofedora). Prerequisite for python-dipy
  1.12+ which added a hard dep on trx-python for tractogram I/O. Pure
  Python, setuptools build backend, BSD-3-Clause. All runtime deps
  (deepdiff, nibabel, numpy, typer) already in Fedora.
