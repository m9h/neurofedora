%define debug_package %{nil}

%global pypi_name fmm3dpy

Name:           python-%{pypi_name}
Version:        2.1.0
Release:        1%{?dist}
Summary:        Fast Multipole Method in Python (FMM3D wrapper)

License:        Apache-2.0
URL:            https://fmm3d.readthedocs.io/
Source0:        %{pypi_source}

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
BuildRequires:  python3-meson-python

%description
fmm3dpy provides Python bindings for the Flatiron Institute's FMM3D library.
It offers Fast Multipole Method (FMM) implementations for the Laplace,
Helmholtz, Stokes, and Maxwell equations.

%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy

%description -n python3-%{pypi_name}
This package provides the Python 3 library for fmm3dpy.

%prep
%autosetup -n %{pypi_name}-%{version}

# Allow building with -fallow-argument-mismatch for legacy Fortran
sed -i "s/f_args = fc.get_supported_arguments(\['-w', '-std=legacy'\])/f_args = fc.get_supported_arguments(['-w', '-std=legacy', '-fallow-argument-mismatch'])/" meson.build

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fmm3dpy

%check
export PYTHONPATH=%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}
%{python3} -c "import fmm3dpy; print('fmm3dpy imported successfully')"

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE

%changelog
* Wed Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 2.1.0-1
- Update to 2.1.0 (major version bump, now uses meson-python build system)
- Switch source from GitHub FMM3D repo to PyPI sdist
- Remove manual f2py build process (upstream now handles via meson.build)

* Tue Mar 10 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.3-2
- Add meson BuildRequires (numpy.f2py uses meson backend on Python 3.14+)

* Tue Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.3-1
- Update to 1.0.3 and use improved build process
