Name:           python-hdf5plugin
Version:        6.0.0
Release:        1%{?dist}
Summary:        HDF5 Plugins for Windows, MacOS, and Linux

License:        MIT
URL:            https://github.com/silx-kit/hdf5plugin
Source0:        %pypi_source hdf5plugin

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-cpuinfo
BuildRequires:  hdf5-devel
BuildRequires:  gcc

%description
The hdf5plugin package provides HDF5 compression filters (plugins) for h5py
and PyTables.

%package -n python3-hdf5plugin
Summary:        %{summary}
Requires:       python3-h5py

%description -n python3-hdf5plugin
The hdf5plugin package provides HDF5 compression filters (plugins) for h5py
and PyTables.

%prep
%autosetup -n hdf5plugin-%{version}

%build
%pyproject_wheel

%install
%pyproject_install

%files -n python3-hdf5plugin
%license LICENSE
%doc README.rst
%{python3_sitearch}/hdf5plugin
%{python3_sitearch}/hdf5plugin-%{version}.dist-info

%changelog
* Sun Feb 01 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0-1
- Initial package
