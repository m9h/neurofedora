Name:           python-darkdetect
Version:        0.8.0
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        Detect OS Dark Mode from Python

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        BSD-3-Clause
URL:            http://github.com/albertosottile/darkdetect
Source:         %{pypi_source darkdetect}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'darkdetect' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-darkdetect
Summary:        %{summary}

%description -n python3-darkdetect %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n python3-darkdetect macos-listener


%prep
%autosetup -p1 -n darkdetect-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires -x macos-listener


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l darkdetect


%check
%pyproject_check_import


%files -n python3-darkdetect -f %{pyproject_files}


%changelog
%autochangelog
