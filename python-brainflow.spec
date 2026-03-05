%global pypi_name brainflow

Name:           python-%{pypi_name}
Version:        5.19.0
Release:        1%{?dist}
Summary:        Python bindings for BrainFlow

License:        MIT
URL:            https://brainflow.org/
Source0:        https://files.pythonhosted.org/packages/source/b/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-numpy
BuildRequires:  gcc-c++
BuildRequires:  cmake
# Links against the package you just built
BuildRequires:  brainflow-devel = %{version}

%description
Python bindings for BrainFlow, intended to obtain, parse and analyze 
EEG, EMG, ECG and other kinds of data from biosensors.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Requires:       brainflow%{?_isa} = %{version}
Requires:       python3-numpy
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
Python bindings for BrainFlow.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
# Force it to use the system installed libraries we just built
export BRAINFLOW_SYSTEM_LIBS=1
%py3_build

%install
export BRAINFLOW_SYSTEM_LIBS=1
%py3_install

%files -n python3-%{pypi_name}
%{python3_sitearch}/%{pypi_name}/
%{python3_sitearch}/%{pypi_name}-%{version}-py%{python3_version}.egg-info/

%changelog
* Wed Jan 07 2026 Morgan Hough <morgan.hough@gmail.com> - 5.19.0-1
- Initial Python bindings for BrainFlow linked against system libs
