%global pypi_name leanclient

Name:           python-leanclient
Version:        0.12.1
Release:        1%{?dist}
Summary:        Fast Python client for the Lean 4 language server

License:        MIT
URL:            https://github.com/oOo0oOo/leanclient
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
leanclient is a fast, thin Python client for interacting with the Lean 4
theorem prover through its language server (LSP). It opens files and runs
requests against lean/lake, exposing goal state, diagnostics, hovers, symbols
and completions, which makes it a convenient substrate for programmatic and
machine-learning-driven interaction with Lean projects.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md

%changelog
* Wed Jun 24 2026 Morgan Hough <morgan.hough@gmail.com> - 0.11.0-1
- Initial package
