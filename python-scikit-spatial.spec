Name:           python-scikit-spatial
Version:        9.0.1
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        Spatial objects and computations based on NumPy arrays.

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        BSD-3-Clause
URL:            https://github.com/ajhynes7/scikit-spatial
Source:         %{pypi_source scikit_spatial}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'scikit-spatial' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-scikit-spatial
Summary:        %{summary}

%description -n python3-scikit-spatial %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n python3-scikit-spatial plotting


%prep
%autosetup -p1 -n scikit_spatial-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires -x plotting


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l skspatial


%check
%pyproject_check_import


%files -n python3-scikit-spatial -f %{pyproject_files}


%changelog
%autochangelog
