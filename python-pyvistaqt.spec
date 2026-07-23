Name:           python-pyvistaqt
Version:        0.12.0
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        pyvista qt plotter

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        MIT
URL:            https://github.com/pyvista/pyvistaqt
Source:         %{pypi_source pyvistaqt}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'pyvistaqt' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-pyvistaqt
Summary:        %{summary}

%description -n python3-pyvistaqt %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n python3-pyvistaqt dev,docs,test


%prep
%autosetup -p1 -n pyvistaqt-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires -x dev,docs,test


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l pyvistaqt


%check
%pyproject_check_import


%files -n python3-pyvistaqt -f %{pyproject_files}


%changelog
%autochangelog
