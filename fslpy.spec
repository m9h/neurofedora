Name:           python-fslpy
Version:        3.21.1
Release:        1%{?dist}
Summary:        FSL Python library

License:        Apache-2.0
URL:            https://git.fmrib.ox.ac.uk/fsl/fslpy
Source0:        %{pypi_source fslpy}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-h5py
BuildRequires:  python3-nibabel
BuildRequires:  python3-numpy
BuildRequires:  python3-scipy

%description
The fslpy project is a library of Python utilities for working with FSL
(FMRIB Software Library) data and metadata.

%package -n     python3-fslpy
Summary:        %{summary}
Requires:       python3-h5py
Requires:       python3-nibabel
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-indexed-gzip
Suggests:       dcm2niix

%description -n python3-fslpy
The fslpy project is a library of Python utilities for working with FSL
(FMRIB Software Library) data and metadata.

%prep
%autosetup -n fslpy-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fsl

%check
%{python3} -m fsl --version

%files -n python3-fslpy -f %{pyproject_files}
%doc README.rst

%changelog
* Mon May 04 2026 Morgan Hough <morgan.hough@gmail.com> - 3.21.1-1
- Initial package
