%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-bianca
Version:        2209.3
Release:        1%{?dist}
Summary:        FSL BIANCA - automated white-matter lesion segmentation

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BIANCA
Source0:        https://git.fmrib.ox.ac.uk/fsl/bianca/-/archive/%{version}/bianca-%{version}.tar.gz#/fsl-bianca-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  fsl-base = 6.0.7.18

Requires:       fsl-base = 6.0.7.18
# BIANCA's classifier is implemented in Python (scikit-learn k-NN).
Requires:       python3
Requires:       %{py3_dist scikit-learn}
Requires:       %{py3_dist numpy}
# Driver scripts call these FSL tools.
Requires:       fsl-avwutils
Requires:       fsl-fast4
Requires:       fsl-flirt

%description
BIANCA (Brain Intensity AbNormality Classification Algorithm) is FSL's
automated, supervised method for white-matter hyperintensity / lesion
segmentation, based on a k-nearest-neighbour classifier. Ships the bianca
driver and the cluster-stats / overlap-measures / mask-making helper scripts.
Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n bianca-%{version}

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
test -f %{buildroot}%{fsldir}/bin/bianca
test -f %{buildroot}%{fsldir}/bin/make_bianca_mask

%files
%{fsldir}/bin/bianca
%{fsldir}/bin/bianca_cluster_stats
%{fsldir}/bin/bianca_overlap_measures
%{fsldir}/bin/make_bianca_mask
%{fsldir}/bin/bianca_perivent_deep

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2209.3-1
- Initial package: BIANCA white-matter lesion segmentation (Python/scikit-learn
  classifier scripts), on the fsl foundation.
