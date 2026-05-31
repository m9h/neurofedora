# Pure-Python package; no debuginfo to generate
%global debug_package %{nil}

%global pypi_name dicom-anonymizer
%global tarball_name dicom_anonymizer
%global module_name dicomanonymizer

Name:           dicomanonymizer
Version:        1.0.13.post1
Release:        1%{?dist}
Summary:        Program to anonymize DICOM files with default and custom rules

# SPDX — LICENSE file is BSD-3-Clause (Copyright Kitware Europe)
License:        BSD-3-Clause
URL:            https://github.com/KitwareMedical/dicom-anonymizer
Source0:        https://files.pythonhosted.org/packages/source/d/%{pypi_name}/%{tarball_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  %{py3_dist setuptools}
BuildRequires:  %{py3_dist wheel}

%global _description %{expand:
dicom-anonymizer is a Python tool to anonymize DICOM files using configurable
rules. It ships a console entry point (dicom-anonymizer) for batch processing
of DICOM datasets and a Python API (dicomanonymizer module) for use in
neuroimaging pipelines. Default rules implement common PII-stripping policies;
custom rules can be supplied to override or extend the defaults.}

%description %{_description}


%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       %{py3_dist pydicom} < 3
Requires:       %{py3_dist tqdm}

%description -n python3-%{pypi_name} %{_description}


%prep
%autosetup -n %{tarball_name}-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files %{module_name}


%check
%pyproject_check_import


%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/dicom-anonymizer


%changelog
* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.13.post1-1
- Initial COPR packaging of dicom-anonymizer 1.0.13.post1 (PyPI, KitwareMedical fork)
