%global pypi_name dataclasses-json

Name:           python-%{pypi_name}
Version:        0.6.7
Release:        1%{?dist}
Summary:        Easily serialize Data Classes to and from JSON

License:        MIT
URL:            https://github.com/lidatong/dataclasses-json
Source0:        %{pypi_source %{pypi_name}}
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-marshmallow
BuildRequires:  python3-typing-inspect

%description
This library provides a simple API for encoding and decoding Data Classes 
to and from JSON.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-marshmallow
Requires:       python3-typing-inspect

%description -n python3-%{pypi_name}
This library provides a simple API for encoding and decoding Data Classes 
to and from JSON.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files dataclasses_json

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.6.7-1
- Initial package for fury dependency
