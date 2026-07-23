Name:           python-pytransform3d
Version:        3.15.0
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        3D transformations for Python

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        BSD-3-Clause
URL:            https://github.com/dfki-ric/pytransform3d
Source:         %{pypi_source pytransform3d}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'pytransform3d' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-pytransform3d
Summary:        %{summary}

%description -n python3-pytransform3d %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n python3-pytransform3d all,doc,test


%prep
%autosetup -p1 -n pytransform3d-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires -x all,doc,test


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l pytransform3d


%check
%pyproject_check_import


%files -n python3-pytransform3d -f %{pyproject_files}


%changelog
%autochangelog
