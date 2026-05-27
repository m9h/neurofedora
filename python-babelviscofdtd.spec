Name:           python-babelviscofdtd
Version:        1.2.6
Release:        2%{?dist}
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
# The cython-built .so extensions live INSIDE BabelViscoFDTD/ (per the
# upstream layout), so the directory listing covers them. Don't list
# top-level _FDTDStaggered*.so — they don't exist there.
%{python3_sitearch}/BabelViscoFDTD
# The dist-info version drifts because Source0 fetches main.tar.gz (not a tag);
# the wheel build uses whatever pyproject.toml says in that snapshot. Glob it.
%{python3_sitearch}/babelviscofdtd-*.dist-info

%changelog

* Tue May 26 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.6-2
- Glob the .dist-info path: Source0 fetches main.tar.gz which
  drifts between pyproject.toml versions, so a literal version
  in %%files breaks reproducibility.

* Tue May 26 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.6-1
- Bump to 1.2.6 (upstream pyproject.toml metadata version; the v1.2.3
  GitHub tag actually contains 1.2.6 in setup.cfg).
- Drop erroneous top-level _FDTDStaggered*.so glob from %%files —
  the cython extensions are inside BabelViscoFDTD/ (already covered).
* Sun Feb 01 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.6-1
- Initial package
