Name:           python-babelviscofdtd
Version:        1.2.3
Release:        1%{?dist}
Summary:        GPU/CPU 3D FDTD solution of viscoelastic equation

License:        BSD-3-Clause
URL:            https://github.com/ProteusMRIgHIFU/BabelViscoFDTD
Source0:        https://github.com/ProteusMRIgHIFU/BabelViscoFDTD/archive/main.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-numpy
BuildRequires:  python3-scipy
BuildRequires:  python3-h5py
BuildRequires:  python3-hdf5plugin
BuildRequires:  python3-pydicom
BuildRequires:  python3-pyopencl
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  opencl-headers
BuildRequires:  ocl-icd-devel

%description
GPU/CPU 3D FDTD solution of viscoelastic equation.

%package -n python3-babelviscofdtd
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-h5py
Requires:       python3-hdf5plugin
Requires:       python3-pydicom
Requires:       python3-pyopencl

%description -n python3-babelviscofdtd
GPU/CPU 3D FDTD solution of viscoelastic equation.

%prep
%autosetup -n BabelViscoFDTD-main

%build
# setup.py calls cmake.
# We ensure cmake and build dependencies are present.
%pyproject_wheel

%install
%pyproject_install

%files -n python3-babelviscofdtd
%license LICENSE
%doc README.md
%{python3_sitearch}/BabelViscoFDTD
%{python3_sitearch}/_FDTDStaggered3D_with_relaxation_*.so
%{python3_sitearch}/babelviscofdtd-%{version}.dist-info

%changelog
* Sun Feb 01 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.6-1
- Initial package
