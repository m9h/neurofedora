%global pypi_name highdicom

Name:           python-%{pypi_name}
Version:        0.27.0
Release:        1%{?dist}
Summary:        High-level DICOM abstractions for Python

License:        MIT
URL:            https://github.com/ImagingDataCommons/highdicom
Source0:        %{pypi_source %{pypi_name} %{version}}

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools >= 64
BuildRequires:  python3-wheel
# Needed for the %%check import (highdicom imports them at module load)
BuildRequires:  python3-numpy
BuildRequires:  python3-pillow
BuildRequires:  python3-pydicom >= 3.0.1
BuildRequires:  python3-typing-extensions

%description
highdicom provides high-level abstractions for reading and writing DICOM
objects (segmentations, structured reports, parametric maps, presentation
states, ...) on top of pydicom. It is a runtime dependency of 3D Slicer's
DICOM tooling.

%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-pillow
Requires:       python3-pydicom >= 3.0.1
Requires:       python3-typing-extensions
# JPEG-LS support is via pydicom's pixel-data plugin; highdicom does not import
# it directly, so make it a weak dependency (image read/write works without it,
# only JPEG-LS transfer syntaxes need it).
Recommends:     python3-pyjpegls

%description -n python3-%{pypi_name}
High-level DICOM abstractions for Python, built on pydicom.

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
%license LICENSE
%doc README.md

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.27.0-1
- Initial package (3D Slicer DICOM module runtime dependency)
