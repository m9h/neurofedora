Name:           python-stanio
Version:        0.5.1
Release:        1%{?dist}
Summary:        Utilities for preparing Stan inputs and processing Stan outputs

License:        BSD-3-Clause
URL:            https://github.com/stan-dev/stanio
Source0:        %{pypi_source stanio}

BuildArch:      noarch
BuildRequires:  python3-devel

%description
Utilities for preparing Stan inputs and processing Stan outputs.

%package -n     python3-stanio
Summary:        %{summary}

%description -n python3-stanio
Utilities for preparing Stan inputs and processing Stan outputs.

%prep
%autosetup -n stanio-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files stanio

%check
%pyproject_check_import

%files -n python3-stanio -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Thu Feb 19 2026 Morgan G Hough <morgan.hough@gmail.com> - 0.5.1-1
- Initial package
