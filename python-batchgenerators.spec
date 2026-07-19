%global pypi_name batchgenerators
%global import_name batchgenerators

Name:           python-%{pypi_name}
Version:        0.25.3
Release:        1%{?dist}
Summary:        Framework for data augmentation of 2D and 3D medical images

License:        Apache-2.0
URL:            https://github.com/MIC-DKFZ/batchgenerators
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
batchgenerators is the data-augmentation framework developed at the DKFZ
Division of Medical Image Computing. It provides multi-threaded data loading
and a large library of spatial, intensity, noise, resampling and cropping
transforms that operate on 2D and 3D images, designed for the memory and
dimensionality constraints of medical imaging rather than natural images.

It underpins the nnU-Net family of segmentation frameworks.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

# Drop two Python 2 era runtime dependencies that Fedora no longer ships and
# that this code does not actually need on Python 3:
#
#   future    - only provides the `builtins` module as a Python 2 backport. The
#               package does `from builtins import range/object`, which on
#               Python 3 resolves to the stdlib `builtins` module. (verified: no
#               `from future`/`past.` imports anywhere in the package)
#   unittest2 - a Python 2 backport of unittest. Not imported anywhere in the
#               package or its tests, which use plain `import unittest`; it is
#               listed as a runtime dependency in error (it is a test-only tool
#               at most).
sed -i -e '/^    "future",$/d' -e '/^    "unittest2",$/d' pyproject.toml
grep -q 'unittest2\|"future"' pyproject.toml && exit 1 || :

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
# batchgenerators/examples/* are standalone demo scripts shipped inside the
# package; they import torch and SimpleITK, which the library itself does not
# depend on (it is numpy-based). Exclude them from the import check.
%pyproject_check_import -e '*.examples.*'

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.25.3-1
- Initial package. Augmentation backbone of the nnU-Net stack, part of the
  nnInteractive dependency chain. Drops the vestigial Python 2 era future and
  unittest2 runtime dependencies (neither is packaged in Fedora and neither is
  needed on Python 3; see the comment in %%prep).
