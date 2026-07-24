Name:           python-pyshortcuts
Version:        1.9.9
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        Create desktop and Start Menu shortcuts for python scripts

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        MIT
URL:            https://github.com/newville/pyshortcuts/
Source:         %{pypi_source pyshortcuts}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'pyshortcuts' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-pyshortcuts
Summary:        %{summary}

%description -n python3-pyshortcuts %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras


%prep
%autosetup -p1 -n pyshortcuts-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l pyshortcuts


%check
%pyproject_check_import


%files -n python3-pyshortcuts -f %{pyproject_files}
%{_bindir}/pyshortcut


%changelog
%autochangelog
