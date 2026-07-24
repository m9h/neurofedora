Name:           python-concurrent-log-handler
Version:        0.9.29
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        RotatingFileHandler replacement with concurrency, gzip and Windows support. Size and time based rotation.

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        Apache-2.0
URL:            https://github.com/Preston-Landers/concurrent-log-handler
Source:         %{pypi_source concurrent_log_handler}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'concurrent-log-handler' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-concurrent-log-handler
Summary:        %{summary}

%description -n python3-concurrent-log-handler %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras


%prep
%autosetup -p1 -n concurrent_log_handler-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l concurrent_log_handler


%check
%pyproject_check_import


%files -n python3-concurrent-log-handler -f %{pyproject_files}


%changelog
%autochangelog
