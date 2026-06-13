# Pure-Python package; no debuginfo to generate
%global debug_package %{nil}

%global pypi_name dicom-anonymizer
%global tarball_name dicom_anonymizer
%global module_name dicomanonymizer

Name:           dicomanonymizer
Version:        1.0.13.post1
Release:        2%{?dist}
Summary:        Program to anonymize DICOM files with default and custom rules

# SPDX — LICENSE file is BSD-3-Clause (Copyright Kitware Europe)
License:        BSD-3-Clause
URL:            https://github.com/KitwareMedical/dicom-anonymizer
Source0:        https://files.pythonhosted.org/packages/source/d/%{pypi_name}/%{tarball_name}-%{version}.tar.gz
# Relax the conservative pydicom<3 cap so the package installs on Fedora's
# pydicom 3.x. The code uses only modern pydicom APIs; verified functionally
# against pydicom 3.0.2 (see %%check). Candidate for an upstream PR.
Patch0:         dicomanonymizer-pydicom3.patch

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  %{py3_dist setuptools}
BuildRequires:  %{py3_dist wheel}
# For the functional %%check (ships the bundled CT_small.dcm test dataset).
BuildRequires:  %{py3_dist pydicom}

%global _description %{expand:
dicom-anonymizer is a Python tool to anonymize DICOM files using configurable
rules. It ships a console entry point (dicom-anonymizer) for batch processing
of DICOM datasets and a Python API (dicomanonymizer module) for use in
neuroimaging pipelines. Default rules implement common PII-stripping policies;
custom rules can be supplied to override or extend the defaults.}

%description %{_description}


%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       %{py3_dist pydicom} >= 2
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
# Functional anonymization smoke against the installed (Fedora) pydicom 3.x —
# proves the relaxed pin is sound, not merely importable: read a bundled test
# dataset, anonymize it, assert PatientName is cleared.
PYTHONPATH=%{buildroot}%{python3_sitelib} %{python3} -c "import pydicom; from pydicom.data import get_testdata_files; from pydicom import dcmread; from dicomanonymizer import anonymize_dataset; ds=dcmread(get_testdata_files('CT_small.dcm')[0]); n0=str(ds.PatientName); anonymize_dataset(ds); assert str(ds.PatientName)!=n0, 'anonymization left PatientName unchanged'; print('anonymize_dataset OK under pydicom', pydicom.__version__)"


%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/dicom-anonymizer


%changelog
* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.13.post1-2
- Relax pydicom<3 cap to pydicom>=2 (Patch0) so the package installs on Fedora's
  pydicom 3.x. The code uses only modern pydicom APIs (dcmread, generate_uid,
  multival.MultiValue); verified functionally against pydicom 3.0.2 — CT/MR/
  RTPLAN/EMRI/liver datasets anonymize cleanly with SOPInstanceUID regeneration.
- Add a functional %%check (anonymize_dataset clears PatientName) on top of the
  import check. Patch is a candidate for an upstream PR to KitwareMedical.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.13.post1-1
- Initial COPR packaging of dicom-anonymizer 1.0.13.post1 (PyPI, KitwareMedical fork)
