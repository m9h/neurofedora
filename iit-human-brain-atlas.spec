Name:           iit-human-brain-atlas
Version:        5.0
Release:        1%{?dist}
Summary:        IIT Human Brain Atlas (MRI templates and labels)

# Non-commercial research/educational use only.
# No redistribution allowed without permission.
# Because of this, the source cannot be automatically downloaded.
License:        Restrictive
URL:            https://www.nitrc.org/projects/iit/

# The user must download this file manually from NITRC:
# https://www.nitrc.org/frs/download.php/11141/IIT_Atlas_v5.0.zip
Source0:        IIT_Atlas_v5.0.zip

BuildArch:      noarch
BuildRequires:  unzip

%description
The IIT Human Brain Atlas is a suite of MRI templates and labels of the 
human brain. It includes anatomical (T1, T2), DTI, and HARDI templates, 
as well as probabilistic gray matter and white matter labels.

The templates are provided in MNI152 space and are compatible with FSL, 
MRtrix, DTI-TK, and other neuroimaging analysis packages.

Note: This package requires the source zip to be manually downloaded from NITRC
due to licensing and download restrictions.

%prep
%autosetup -c -n %{name}-%{version}

%build
# No compilation needed for data package

%install
mkdir -p %{buildroot}%{_datadir}/neurofedora/atlases/iit
cp -rp * %{buildroot}%{_datadir}/neurofedora/atlases/iit/

# Move documentation to standard location
mkdir -p %{buildroot}%{_docdir}/%{name}
mv %{buildroot}%{_datadir}/neurofedora/atlases/iit/*.pdf %{buildroot}%{_docdir}/%{name}/ || true

%check
# Verify that key files are present
test -f %{buildroot}%{_datadir}/neurofedora/atlases/iit/IITmean_FA.nii.gz

%files
%doc %{_docdir}/%{name}/*
%{_datadir}/neurofedora/

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 5.0-1
- Initial IIT Human Brain Atlas data package
- Saves data to /usr/share/neurofedora/atlases/iit for cross-package use
