%global pypi_name pyjpegls

Name:           python-%{pypi_name}
Version:        1.5.1
Release:        1%{?dist}
Summary:        Python interface to the CharLS JPEG-LS library, with pydicom integration

# pyjpegls itself is MIT; it bundles and statically compiles CharLS (BSD-3-Clause)
License:        MIT AND BSD-3-Clause
URL:            https://github.com/pydicom/pyjpegls
Source0:        %{pypi_source %{pypi_name} %{version}}

# CharLS is bundled in lib/charls and compiled into the _CharLS extension;
# upstream setup.py has no system-library option.
Provides:       bundled(charls)

BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-Cython
BuildRequires:  python3-numpy

%description
pyjpegls is a Python interface to the CharLS JPEG-LS (ISO/IEC 14495-1)
compression library. It provides the JPEG-LS pixel-data handler used by
pydicom (and therefore highdicom and 3D Slicer's DICOM tooling) to decode
and encode JPEG-LS compressed DICOM images.

%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy

%description -n python3-%{pypi_name}
Python interface to the CharLS JPEG-LS library, providing pydicom's
JPEG-LS pixel-data handler.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files jpeg_ls _CharLS

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
# Upstream ships no standalone license file; pyjpegls is MIT (declared in
# project metadata), bundled CharLS is BSD-3-Clause.
%doc README.md

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.1-1
- Initial package (JPEG-LS handler for pydicom/highdicom; bundled CharLS)
