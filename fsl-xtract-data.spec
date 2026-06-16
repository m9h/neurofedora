%global fsldir          %{_prefix}/lib/fsl

Name:           fsl-xtract-data
Version:        2.1.0
Release:        1%{?dist}
Summary:        XTRACT tract-protocol definitions and atlases for FSL

License:        LicenseRef-FSL
URL:            https://git.fmrib.ox.ac.uk/fsl/xtract_data
# ~76 MB of tract-protocol masks/seeds (human + macaque). Repackaged from the
# installed fsl-data_xtract 2.1.0 (the FMRIB GitLab tags lag at 2.0.x).
Source0:        fsl-xtract-data-2.1.0.tar.gz

BuildArch:      noarch
Requires:       fsl-base
Requires:       fsl-xtract

%description
The XTRACT data: tract-protocol definitions (seed/target/exclusion masks and
stop criteria) and the associated atlases for the standardised white-matter
tracts XTRACT reconstructs, for human and macaque brains. Installed under
$FSLDIR/data/xtract_data where XTRACT expects them.

%prep
%autosetup -c -n %{name}-%{version}

%install
mkdir -p %{buildroot}%{fsldir}/data
cp -rp xtract_data %{buildroot}%{fsldir}/data/

%check
test -d %{buildroot}%{fsldir}/data/xtract_data

%files
%dir %{fsldir}/data
%{fsldir}/data/xtract_data

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.1.0-1
- Initial package: XTRACT tract-protocol data + atlases (~76 MB) under
  $FSLDIR/data/xtract_data; fsl-xtract Recommends it.
