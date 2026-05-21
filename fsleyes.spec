Name:           fsleyes
Version:        1.13.0
Release:        1%{?dist}
Summary:        FSL image viewer

License:        Apache-2.0
URL:            https://git.fmrib.ox.ac.uk/fsl/fsleyes/fsleyes
Source0:        %{pypi_source fsleyes}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-fslpy >= 3.21.1
BuildRequires:  python3-fsleyes-props >= 1.11.0
BuildRequires:  python3-fsleyes-widgets >= 0.14.3
BuildRequires:  python3-wxpython >= 4.0.0
BuildRequires:  python3-nibabel
BuildRequires:  python3-numpy
BuildRequires:  python3-matplotlib
BuildRequires:  python3-scipy

%description
FSLeyes is the FSL image viewer.

%package -n     python3-fsleyes
Summary:        %{summary}
Requires:       python3-fslpy >= 3.21.1
Requires:       python3-fsleyes-props >= 1.11.0
Requires:       python3-fsleyes-widgets >= 0.14.3
Requires:       python3-wxpython >= 4.0.0
Requires:       python3-nibabel
Requires:       python3-numpy
Requires:       python3-matplotlib
Requires:       python3-scipy
Requires:       python3-h5py

%description -n python3-fsleyes
FSLeyes is the FSL image viewer.

%prep
%autosetup -n fsleyes-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fsleyes

%files -n python3-fsleyes -f %{pyproject_files}
%{_bindir}/fsleyes
%doc README.rst

%changelog
* Mon May 04 2026 Morgan Hough <morgan.hough@gmail.com> - 1.13.0-1
- Initial package
