Name:           python-nitransforms
Version:        25.1.0
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        NiTransforms -- Neuroimaging spatial transforms in Python.

# No license information obtained, it's up to the packager to fill it in
License:        ...
URL:            https://github.com/nipy/nitransforms
Source:         %{pypi_source nitransforms}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'nitransforms' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-nitransforms
Summary:        %{summary}

%description -n python3-nitransforms %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras


%prep
%autosetup -p1 -n nitransforms-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l nitransforms


%check
%pyproject_check_import


%files -n python3-nitransforms -f %{pyproject_files}
%{_bindir}/nb-transform


%changelog
%autochangelog
