Name:           python-jsbeautifier
Version:        2.0.3
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        JavaScript unobfuscator and beautifier.

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        MIT
URL:            https://beautifier.io
Source:         %{pypi_source jsbeautifier}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'jsbeautifier' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-jsbeautifier
Summary:        %{summary}

%description -n python3-jsbeautifier %_description


%prep
%autosetup -p1 -n jsbeautifier-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files jsbeautifier


%check
%pyproject_check_import


%files -n python3-jsbeautifier -f %{pyproject_files}
%{_bindir}/js-beautify


%changelog
%autochangelog
