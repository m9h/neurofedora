# Full documentation downloads 100+MB of data, so we'd rather users look at
# the upstream documentation at https://dipy.org/
%bcond docs 0

# Test suite is huge (many GB of upstream test data downloads), slow, and
# network-dependent. First COPR build skips it to get a green baseline;
# re-enable selectively once the package is known-good on F44.
%bcond tests 0

Name:           python-dipy
Version:        1.12.1
Release:        1%{?dist}
Summary:        Diffusion MRI Imaging in Python

%global forgeurl https://github.com/dipy/dipy/
%global tag %{version}
%forgemeta

License:        BSD-3-Clause
URL:            https://dipy.org/
Source:         %forgesource

BuildRequires:  python3-devel
BuildRequires:  gcc-c++
# dipy 1.12 switched its build backend from setuptools to meson-python
# (see pyproject.toml [build-system]). pyproject-rpm-macros handles
# the wheel build, but we need the underlying meson + ninja toolchain.
BuildRequires:  meson
BuildRequires:  ninja-build
# Cython>=3.0.4 required by dipy's build-system requires list
BuildRequires:  python3-Cython >= 3.0.4
%if %{with tests}
BuildRequires:  %{py3_dist pytest}
%endif

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

%global desc %{expand: \
DIPY is a python library for the analysis of MR diffusion imaging.

DIPY is for research only; please contact admins@dipy.org if you plan
to deploy in clinical settings. Provides tools for fiber tracking,
spherical deconvolution, DTI/DKI reconstruction, image registration,
and tractometry.

More information at https://dipy.org/}

%description
%{desc}

%package -n python3-dipy
Summary:        %{summary}
Suggests:       %{py3_dist ipython}

%description -n python3-dipy
%{desc}

%package doc
BuildArch:      noarch
Summary:        %{summary} - documentation

%description doc
Documentation pointer for %{name}. The full Sphinx docs are 100+ MB after
all the test datasets are downloaded; we recommend the live upstream
documentation at https://dipy.org/ instead.


%prep
%forgeautosetup -p1

# Fix any /usr/bin/env python shebangs — Fedora rejects unversioned ones
sed -i 's|#!/usr/bin/env python[0-9]*|#!/usr/bin/python3|' \
    doc/tools/docgen_cmd.py doc/tools/build_modref_templates.py 2>/dev/null || :
find tools/ -name '*.py' -exec \
    sed -i 's|#!/usr/bin/env python[0-9]*|#!/usr/bin/python3|' {} \; 2>/dev/null || :

# Strip shebangs from module files (they're libraries, not scripts)
find dipy/ -name '*.py' -exec sed -ri '/^#!.*python/d' {} +

# Drop execute bits on data files and non-script .py modules
find dipy/ -name '*.py' ! -path '*/workflows/*.py' -exec chmod a-x {} \; 2>/dev/null || :
chmod a-x doc/examples/*.py 2>/dev/null || :
chmod a-x dipy/data/files/func_coef.nii.gz 2>/dev/null || :

# Allow building with whatever numpy is installed (F44 ships 2.x).
# Upstream pins to 2.0.0rc1+ for wheel builds — relax for distro builds.
sed -ri 's/(numpy)[><=][^"]+"/\1"/g' pyproject.toml


%generate_buildrequires
%pyproject_buildrequires -p


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files dipy

# pyproject_install puts examples under /usr/doc; move them to %%_docdir.
if [[ -d %{buildroot}/usr/doc/dipy/examples ]]; then
    mkdir -p %{buildroot}%{_docdir}/%{name}-doc
    mv %{buildroot}/usr/doc/dipy/examples %{buildroot}%{_docdir}/%{name}-doc/
fi


%check
%if %{with tests}
# Mimic upstream: cd into an empty dir to test against the installed pkg,
# not the source tree. Exclude network-dependent tests (anything that
# tries to fetch_*() upstream test data).
mkdir test && cd test
%pytest -r fEs \
    -k "not test_io_fetch and not test_io_info \
        and not test_concatenate_flow \
        and not test_convert_tractogram_flow" \
    --pyargs dipy
%endif


%files -n python3-dipy -f %{pyproject_files}
%doc README.rst Changelog AUTHOR
%license LICENSE
%{_bindir}/dipy_*

%files doc
%license LICENSE
%dir %{_docdir}/%{name}-doc
%{_docdir}/%{name}-doc


%changelog
* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.12.1-1
- Initial COPR build (mhough/neurofedora), adapted from Fedora f41's
  python-dipy.spec (last live before retirement for orphan). Bumped
  from 1.11.0 → 1.12.1, switched to mesonpy build-system (was setuptools
  in 1.11), explicit Release/changelog instead of autorelease/autochangelog
  to match the COPR's house style. Tests disabled in first build.
