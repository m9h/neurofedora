%global pypi_name dicomweb-client
%global pypi_dist dicomweb_client

Name:           python-%{pypi_name}
Version:        0.61.0
Release:        1%{?dist}
Summary:        Python client for DICOMweb RESTful services

License:        MIT
URL:            https://github.com/ImagingDataCommons/dicomweb-client
Source0:        %{pypi_source %{pypi_dist} %{version}}

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-hatchling

%description
dicomweb-client provides client interfaces for DICOMweb RESTful services
(QIDO-RS, WADO-RS, STOW-RS) to search, retrieve and store DICOM objects
over the web. It is a runtime dependency of 3D Slicer's DICOM tooling.

%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-pillow
Requires:       python3-pydicom >= 3.0.0
Requires:       python3-requests
Requires:       python3-retrying

%description -n python3-%{pypi_name}
Python client for DICOMweb RESTful services (QIDO-RS, WADO-RS, STOW-RS).

%prep
%autosetup -n %{pypi_dist}-%{version}

# Drop uv-dynamic-versioning (reads the version from git, absent in the sdist and
# not packaged in Fedora). Pin the static version so a plain hatchling build works
# offline.
sed -i 's/^dynamic = \["version"\]/version = "%{version}"/' pyproject.toml
sed -i '/^\[tool.hatch.version\]/d' pyproject.toml
sed -i '/^source = "uv-dynamic-versioning"/d' pyproject.toml
sed -i 's/, "uv-dynamic-versioning"//' pyproject.toml

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_dist}

# No %%check import: dicomweb_client imports python3-retrying, which is brand new
# (built in the same COPR batch) and not assumable as a BuildRequires here. The
# import is exercised at install/runtime via the slicer.bats DICOM smoke instead.

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.61.0-1
- Initial package (3D Slicer DICOM module runtime dependency)
- Pin static version to drop the unpackaged uv-dynamic-versioning build plugin
