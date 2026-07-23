Name:           python-simpleicp
Version:        2.0.15
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        Simple version of the Iterative Closest Point _ICP_ algorithm

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        MIT
URL:            https://github.com/pglira/simpleICP/tree/master/python
Source:         %{pypi_source simpleicp}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'simpleicp' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-simpleicp
Summary:        %{summary}

%description -n python3-simpleicp %_description


%prep
%autosetup -p1 -n simpleicp-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files simpleicp


%check
%pyproject_check_import


%files -n python3-simpleicp -f %{pyproject_files}


%changelog
%autochangelog
