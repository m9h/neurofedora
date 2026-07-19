# scikit-build-core builds the .so via CMake; the debug sources are not tracked
# into debugsourcefiles.list (empty -> FTBFS), so disable the debug package.
%global debug_package %{nil}

Name:           python-babelviscofdtd
Version:        1.2.7
Release:        1%{?dist}
Summary:        GPU/CPU 3D FDTD solution of viscoelastic equation

License:        BSD-3-Clause
URL:            https://github.com/ProteusMRIgHIFU/BabelViscoFDTD
Source0:        https://github.com/ProteusMRIgHIFU/BabelViscoFDTD/archive/main.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-pip
# pyproject.toml uses build-backend = scikit_build_core.build (not setuptools),
# which drives cmake via the ninja generator.
BuildRequires:  python3-scikit-build-core
BuildRequires:  ninja-build
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
# The scikit-build-core backend nests the compiled _FDTDStaggered*.so
# extensions inside the package dir (wheel.packages = ["BabelViscoFDTD"]), so
# this dir entry captures them; the old top-level .so glob no longer applies.
%{python3_sitearch}/BabelViscoFDTD
# The dist-info version drifts because Source0 fetches main.tar.gz (not a tag);
# the wheel build uses whatever pyproject.toml says in that snapshot. Glob it.
%{python3_sitearch}/babelviscofdtd-*.dist-info

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.7-1
- Update to 1.2.7

* Wed Jun 10 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.6-4
- Fix BackendUnavailable FTBFS: pyproject.toml uses
  build-backend = scikit_build_core.build, but the spec only BuildRequired
  setuptools/wheel. BuildRequire python3-scikit-build-core (+ ninja-build, its
  default cmake generator) so %%pyproject_wheel can load the backend. Unblocks
  BabelBrain (BabelViscoFDTD is its core solver)

* Tue May 26 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.6-3
- Restore _FDTDStaggered*.so glob in %%files: the wheel actually
  installs the cython extensions at BOTH top-level sitearch AND
  inside BabelViscoFDTD/. The -2 removal was wrong.

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
