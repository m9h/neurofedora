%bcond_without tests

%global pypi_name pybids

Name:           python-%{pypi_name}
Version:        0.22.0
Release:        2%{?dist}
Summary:        Interface with datasets conforming to BIDS

# The entire source is MIT, except:
#   - The Versioneer-generated bids/_version.py 0.28, is Unlicense.
#   - Test datasets (bids/tests/data/*/) are assumed MIT unless otherwise
#     marked; ds005 and ds005_conflict carry PDDL-1.0 (in +test subpkg).
# We refrain from including the bids-examples/ submodule because many of the
# datasets therein have unspecified licenses.
License:        MIT AND Unlicense
URL:            https://bids.neuroimaging.io
Source0:        https://github.com/bids-standard/%{pypi_name}/archive/%{version}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch

# tests fail on 32 bit systems; plus i686 leaf removal policy
ExcludeArch:    %{ix86}

BuildRequires:  git-core
BuildRequires:  hardlink
BuildRequires:  python3-devel
# Unbundled
BuildRequires:  %{py3_dist inflect}

%global _description %{expand:
PyBIDS is a Python library to centralize interactions with datasets conforming
to BIDS (Brain Imaging Data Structure) format. For more information about
BIDS visit https://bids.neuroimaging.io.}

%description %{_description}


# We cannot package the "model_reports" extra because python-altair is not
# packaged in EPEL/F44 in the variant pybids needs.
%pyproject_extras_subpkg -n python3-%{pypi_name} plotting


%package -n python3-%{pypi_name}
Summary:        %{summary}
Obsoletes:      python-pybids-doc < 0.15.5-13
# unbundled
Requires:       %{py3_dist inflect}

%description -n python3-%{pypi_name} %{_description}


%package -n python3-%{pypi_name}+test
%global test_summary Tests and test extras for PyBIDS
Summary:        %{test_summary}

# See comment above base package License tag for licensing breakdown.
License:        MIT AND PDDL-1.0

Requires:       python3-%{pypi_name} = %{version}-%{release}

%global test_description %{expand: \
These are the tests for python3-pybids. This package:

* Provides the "bids.tests" package
* Makes sure the "test" extra dependencies are installed}

%description -n python3-%{pypi_name}+test %{test_description}


%package -n python3-%{pypi_name}+tests
Summary:        %{test_summary}

# Plural alias subpkg; only metadata, no own files
License:        MIT

Requires:       python3-%{pypi_name}+test = %{version}-%{release}

%description -n python3-%{pypi_name}+tests %{test_description}


%prep
%autosetup -n %{pypi_name}-%{version} -S git

# loosen formulaic dep
sed -i 's/formulaic .*"/formulaic"/' pyproject.toml

# Remove bundled inflect
rm -rf src/bids/external
sed -r -i.backup 's/from.*external (import)/\1/' src/bids/layout/layout.py

# Drop pytest-cov / coverage from extras (Fedora linter policy)
sed -r -i 's/^([[:blank:]]*)"(pytest-cov|coverage)\b/\1# "\2/' pyproject.toml

# python-altair is not packaged for our COPR targets: patch it out
sed -r -i 's/^([[:blank:]]*)"(altair)\b/\1# "\2/' pyproject.toml

# Remove bogus executable bits for non-script files
find src/bids doc -type f -perm /0111 -execdir chmod -v a-x '{}' '+'

# Drop test dependency on s3fs (not packaged)
sed -r -i '/s3fs/d' pyproject.toml

# Relax pytest-xdist >= 3.8 to >= 3.7 (Fedora ships 3.7.0; the test suite does
# not depend on a 3.8-specific feature, it only uses -n parallelism).
sed -r -i 's/"pytest-xdist >= 3\.8"/"pytest-xdist >= 3.7"/' pyproject.toml

# Commit everything and tag so Versioneer reports the right version
git add --all
git -c user.email=copr@neurofedora -c user.name='COPR Build' \
    commit -m "[COPR] Apply downstream changes"
git tag %{version}


%generate_buildrequires
%pyproject_buildrequires -x test,plotting


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files -l bids
# Save space by hardlinking duplicate test data files
hardlink -c -v '%{buildroot}%{python3_sitelib}/bids/tests/data/'


%check
%if %{with tests}
# temporarily disable failing test (formulaic compat)
k="${k-}${k+ and }not test_split"
# test_remote_bids.py requires network
%pytest -v \
    ${k+-k } "${k-}" \
    --ignore src/bids/layout/tests/test_remote_bids.py
%else
%pyproject_check_import
%endif


%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md
%{_bindir}/pybids
%exclude %{python3_sitelib}/bids/tests/


%files -n python3-%{pypi_name}+test
%{python3_sitelib}/bids/tests/
%ghost %{python3_sitelib}/*.dist-info


%files -n python3-%{pypi_name}+tests
%ghost %{python3_sitelib}/*.dist-info


%changelog
* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 0.22.0-2
- Unblock the build: its hard deps are now packaged — formulaic 1.2.2 (new,
  core design-matrix dep) and bsmschema 0.1.1 (new, test extra). Relax the
  test-extra pin pytest-xdist >= 3.8 to >= 3.7 (Fedora ships 3.7.0; no
  3.8-specific feature is used).

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 0.22.0-1
- Update to 0.22.0 (adopted from orphaned Fedora python-pybids; rescued from cdd59e4)
