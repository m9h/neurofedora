%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^(libfsl-.*|libgdc)\\.so.*$

Name:           fsl-feat5
Version:        2201.7
Release:        1%{?dist}
Summary:        FSL FEAT - FMRI Expert Analysis Tool

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FEAT
Source0:        https://git.fmrib.ox.ac.uk/fsl/feat5/-/archive/%{version}/feat5-%{version}.tar.gz#/fsl-feat5-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
BuildRequires:  gd-devel
BuildRequires:  libpng-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18
# FEAT orchestrates the first-/higher-level modelling and registration tools.
Requires:       fsl-film
Requires:       fsl-flameo
Requires:       fsl-flirt
Requires:       fsl-avwutils
Requires:       fsl-melodic

%description
FEAT (FMRI Expert Analysis Tool) is FSL's high-level tool for model-based
FMRI analysis, covering first-level (within-run) and higher-level (group)
GLM analysis with FILM prewhitening, registration, and cluster/TFCE inference.
Ships the feat driver, the feat_model / featquery / easythresh utilities, the
PNM physiological-noise tools and the private libfsl-featlib.so. Part of the
FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n feat5-%{version}

%build
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
mkdir -p "${FSLDEVDIR}"
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{?build_ldflags}"
make %{?_smp_mflags}

%install
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
make install
mkdir -p %{buildroot}%{fsldir}/bin %{buildroot}%{fsldir}/lib
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/
cp -a "${FSLDEVDIR}/lib/libfsl-featlib.so" %{buildroot}%{fsldir}/lib/
find %{buildroot}%{fsldir}/bin -xtype l -delete
chrpath -r '$ORIGIN' %{buildroot}%{fsldir}/lib/libfsl-featlib.so 2>/dev/null || :
chmod 0755 %{buildroot}%{fsldir}/lib/libfsl-featlib.so
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/feat_model
test -f %{buildroot}%{fsldir}/bin/feat
test -e %{buildroot}%{fsldir}/lib/libfsl-featlib.so

%files
%{fsldir}/bin/cutoffcalc
%{fsldir}/bin/feat_model
%{fsldir}/bin/tsplot
%{fsldir}/bin/prewhiten
%{fsldir}/bin/generateConfounds
%{fsldir}/bin/popp
%{fsldir}/bin/pnm_evs
%{fsldir}/bin/easythresh
%{fsldir}/bin/feat
%{fsldir}/bin/mccutup
%{fsldir}/bin/renderhighres
%{fsldir}/bin/featregapply
%{fsldir}/bin/featquery
%{fsldir}/bin/fslerrorreport
%{fsldir}/bin/invfeatreg
%{fsldir}/bin/updatefeatreg
%{fsldir}/bin/estnoise
%{fsldir}/bin/perfusion_subtract
%{fsldir}/bin/match_smoothing
%{fsldir}/bin/fsl_motion_outliers
%{fsldir}/bin/feat_gm_prepare
%{fsldir}/bin/mp_diffpow.sh
%{fsldir}/bin/pnm_stage1
%{fsldir}/bin/mainfeatreg
%{fsldir}/bin/checkFEAT
%{fsldir}/bin/setFEAT
%{fsldir}/bin/autoaq
%{fsldir}/lib/libfsl-featlib.so

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2201.7-1
- Initial package: FEAT FMRI analysis suite (feat/feat_model/featquery/easythresh
  + PNM tools + private libfsl-featlib.so), on the fsl foundation; Requires
  film/flameo/flirt/avwutils/melodic.
