%global fsldir          %{_prefix}/lib/fsl

Name:           fsl-first-data
Version:        2006.0
Release:        1%{?dist}
Summary:        FSL FIRST subcortical shape/appearance models (336-vertex set)

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIRST
# Upstream: git.fmrib.ox.ac.uk/fsl/data_first_models_336_bin @ 2006.0 (conda
# fsl-data_first_models_336_bin-2006.0). The .bmv files are large binary models
# committed directly to the FSL data repo; this tarball is the identical content
# (~1 GB). Source kept as a tarball rather than the streamed GitLab archive.
Source0:        fsl-first-data-336-2006.0.tar.gz

BuildArch:      noarch
# Installs under $FSLDIR (fsl-base provides %dir %{fsldir}); the models are only
# useful together with the FIRST tool.
Requires:       fsl-base
Requires:       fsl-first

%description
The trained Bayesian Appearance Models used by FSL FIRST for model-based
segmentation of the subcortical structures (336-vertex model set): brainstem,
left/right hippocampus, amygdala, caudate, putamen, pallidum, thalamus,
accumbens and the lateral ventricles, plus the 0.5 mm high-resolution models
and the intensity-reference data. Installed under $FSLDIR/data/first where
FIRST expects them.

FIRST cannot perform segmentation without these models; the fsl-first tool
package Recommends this data package.

%prep
%autosetup -c -n %{name}-%{version}

%install
mkdir -p %{buildroot}%{fsldir}/data/first
cp -rp models_336_bin %{buildroot}%{fsldir}/data/first/

%check
test -f %{buildroot}%{fsldir}/data/first/models_336_bin/L_Hipp_bin.bmv
test -f %{buildroot}%{fsldir}/data/first/models_336_bin/BrStem_bin.bmv

%files
%dir %{fsldir}/data
%dir %{fsldir}/data/first
%{fsldir}/data/first/models_336_bin/

%changelog
* Sun Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2006.0-1
- Initial package: FSL FIRST 336-vertex subcortical shape/appearance models
  (the .bmv data FIRST needs at runtime), installed under $FSLDIR/data/first.
  fsl-first Recommends this package. Ships the standard + 0.5 mm models.
