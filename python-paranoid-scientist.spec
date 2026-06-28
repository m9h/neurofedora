%global pypi_name paranoid-scientist
%global dist_name paranoid_scientist
# The importable top-level module is "paranoid" (not paranoid_scientist).
%global import_name paranoid

Name:           python-%{pypi_name}
Version:        0.2.3
Release:        1%{?dist}
Summary:        Runtime verification and automated testing for scientific code

License:        MIT
URL:            https://github.com/mwshinn/paranoidscientist
Source0:        %{pypi_source %{dist_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
Paranoid Scientist is a Python library for verifying the correctness of
scientific software. It provides runtime verification through function
contracts that check arguments and return values against a rich type system,
together with automated property-based testing, helping ensure numerical and
scientific code behaves as intended.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{dist_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE.txt
%doc README.md

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.3-1
- Initial package (dependency of PyDDM)
