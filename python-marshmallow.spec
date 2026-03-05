%global pypi_name marshmallow

Name:           python-%{pypi_name}
Version:        4.2.2
Release:        1%{?dist}
Summary:        A lightweight library for converting complex objects to and from simple Python datatypes

License:        MIT
URL:            https://github.com/marshmallow-code/marshmallow
Source0:        %{pypi_source %{pypi_name}}
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-pytest

%description
marshmallow is an ORM/ODM/framework-agnostic library for converting 
complex datatypes, such as objects, to and from native Python datatypes.

%package -n     python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name}
marshmallow is an ORM/ODM/framework-agnostic library for converting 
complex datatypes, such as objects, to and from native Python datatypes.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
%pytest

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 4.2.2-1
- Initial package for fury dependency
