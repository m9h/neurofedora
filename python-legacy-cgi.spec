%global pypi_name legacy-cgi
%global pypi_dist legacy_cgi

Name:           python-%{pypi_name}
Version:        2.6.4
Release:        1%{?dist}
Summary:        Fork of the standard library cgi and cgitb modules (removed in Python 3.13)

License:        PSF-2.0
URL:            https://github.com/jackrosenthal/legacy-cgi
Source0:        %{pypi_source %{pypi_dist} %{version}}

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pip
# hatchling build backend
BuildRequires:  python3-hatchling

%description
This is a fork of the standard library cgi and cgitb modules, which were
deprecated in Python 3.11 and removed in Python 3.13. It provides those
modules unchanged for code (such as 3D Slicer's DICOM scripted modules)
that still imports them on modern Python.

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name}
A fork of the standard library cgi and cgitb modules (removed in Python 3.13).

%prep
%autosetup -n %{pypi_dist}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files cgi cgitb

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.4-1
- Initial package (restores cgi/cgitb for 3D Slicer scripted modules on Py3.14)
