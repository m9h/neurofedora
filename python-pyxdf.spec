%global pypi_name pyxdf

# Example-files commit used for the playback test data.  Contents (MIT)
# are not installed and do not contribute to binary RPM licenses.
%global ex_commit 387ba537c3a0dd5da2c9a51c578c8f1296e3edeb

Name:           python-%{pypi_name}
Version:        1.17.4
Release:        1%{?dist}
Summary:        Python package for importing XDF (Extensible Data Format) files

License:        BSD-2-Clause
URL:            https://github.com/xdf-modules/pyxdf
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
Source1:        https://github.com/xdf-modules/example-files/archive/%{ex_commit}/example-files-%{ex_commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  %{py3_dist pytest}


%global _description %{expand:
pyXDF is a Python importer for XDF (Extensible Data Format) files used by
the Lab Streaming Layer (LSL) ecosystem.}

%description %{_description}


%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %{_description}

See python3-pyxdf-examples for the command-line examples (pyxdf.cli).


%package -n python3-%{pypi_name}-examples
Summary:        %{summary}
Requires:       python3-%{pypi_name} = %{version}-%{release}
# Imported by the example code.
Requires:       %{py3_dist numpy}
# pyxdf.cli.playback_lsl uses pylsl at runtime.
Requires:       python3-pylsl

%description -n python3-%{pypi_name}-examples %{_description}

This package contains the examples (pyxdf.cli):

  * pyxdf.cli.print_metadata — print basic metadata about each found stream.
  * pyxdf.cli.playback_lsl — open an XDF file then replay its data as an LSL
    stream (requires python3-pylsl).


%prep
%autosetup -n %{pypi_name}-%{version} -p1
%setup -q -n %{pypi_name}-%{version} -T -D -b 1
ln -s ../example-files-%{ex_commit}/ example-files


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}


%check
# Skip pyxdf.cli.playback_lsl in the import check — it imports pylsl, which
# is in a separate spec and not necessarily installed in the build chroot.
%pyproject_check_import -e pyxdf.cli.playback_lsl
# Run the unit tests (these do not require pylsl); they read fixtures
# from example-files (Source1, symlinked above).
%pytest


%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc CHANGELOG.md
%doc README.md
%exclude %{python3_sitelib}/pyxdf/cli/


%files -n python3-%{pypi_name}-examples
%{python3_sitelib}/pyxdf/cli/


%changelog
* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.17.4-1
- Rebase from Fedora dist-git (orphaned, retired) onto 1.17.4 for the
  mhough/neurofedora COPR. Add python3-pyxdf-examples Requires:
  python3-pylsl since the upstream pylsl package is now packaged here.
