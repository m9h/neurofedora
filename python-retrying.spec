%global pypi_name retrying

Name:           python-%{pypi_name}
Version:        1.4.2
Release:        1%{?dist}
Summary:        General-purpose retrying library

License:        Apache-2.0
URL:            https://github.com/groodt/retrying
Source0:        %{pypi_source %{pypi_name} %{version}}

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip

%description
Retrying is a general-purpose retrying library to simplify the task of
adding retry behavior to just about anything. It provides a decorator to
retry a function on exceptions or unexpected return values with
configurable stop conditions, wait strategies and backoff.

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name}
Retrying is a general-purpose retrying library to simplify the task of
adding retry behavior to just about anything.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE.txt
%doc README.md

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.4.2-1
- Initial package (dependency of python-dicomweb-client for 3D Slicer DICOM)
