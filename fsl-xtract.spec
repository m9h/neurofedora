%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-xtract
Version:        2.0.7
Release:        1%{?dist}
Summary:        FSL XTRACT - cross-species automated tractography

# XTRACT is distributed as part of FSL (LicenseRef-FSL); upstream repo carries
# no separate SPDX license file.
License:        LicenseRef-FSL
URL:            https://github.com/SPMIC-UoN/XTRACT
# The maintained XTRACT lives in the SPMIC-UoN GitHub repo (the fsl/ GitLab copy
# is the older 1.6.x). Tag 2.0.7 matches FSL 6.0.7.x.
Source0:        %{url}/archive/%{version}/XTRACT-%{version}.tar.gz#/fsl-xtract-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  fsl-base = 6.0.7.18

Requires:       fsl-base = 6.0.7.18
# XTRACT drives probtrackx2 (fsl-ptx2) and uses the FSL image tools.
Requires:       fsl-ptx2
Requires:       fsl-avwutils
Requires:       fsl-bet2
Requires:       python3
Requires:       %{py3_dist numpy}
Requires:       %{py3_dist nibabel}
# The tract-protocol data the standard runs need.
Recommends:     fsl-xtract-data

%description
XTRACT (cross-species tractography) runs a standardised, automated
probabilistic tractography protocol to reconstruct a set of well-known white
matter tracts, in human or macaque brains. It also provides the blueprint,
stats, QC, divergence and viewer helper tools. XTRACT drives FSL's
probtrackx2. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n xtract-%{version}

%build
# Scripts only — nothing to compile.

%install
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
mkdir -p "${FSLDEVDIR}"
make install
mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/
find %{buildroot}%{fsldir}/bin -xtype l -delete

%check
test -f %{buildroot}%{fsldir}/bin/xtract
test -f %{buildroot}%{fsldir}/bin/xtract_blueprint

%files
%{fsldir}/bin/xtract
%{fsldir}/bin/xtract_viewer
%{fsldir}/bin/xtract_stats
%{fsldir}/bin/xtract_blueprint
%{fsldir}/bin/xtract_qc
%{fsldir}/bin/xtract_divergence
%{fsldir}/bin/create_blueprint
%{fsldir}/bin/get_wgb
%{fsldir}/bin/make_subcort_bp

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.7-1
- Initial package: XTRACT automated tractography (xtract + blueprint/stats/qc/
  viewer tools), on the fsl foundation; drives probtrackx2 (fsl-ptx2) and
  Recommends fsl-xtract-data.
