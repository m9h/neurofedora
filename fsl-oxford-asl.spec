%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-oxford-asl
Version:        4.0.29
Release:        1%{?dist}
Summary:        oxford_asl / BASIL - arterial spin labelling perfusion quantification

License:        Apache-2.0
URL:            https://github.com/physimals/oxford_asl
Source0:        %{url}/archive/v%{version}/oxford_asl-%{version}.tar.gz#/fsl-oxford-asl-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18
# The pipeline runs FABBER with the ASL models and the FSL registration tools.
Requires:       fsl-fabber-models-asl
Requires:       fsl-avwutils
Requires:       fsl-flirt
Requires:       fsl-bet2

%description
oxford_asl (with the BASIL Bayesian inference back-end) is the FSL pipeline for
quantifying perfusion from arterial spin labelling (ASL) MRI. It runs FABBER's
ASL kinetic models to produce calibrated cerebral blood flow maps. Ships the
asl_file utility and the oxford_asl / asl_calib / asl_reg / quasil driver
scripts.

%prep
%autosetup -p1 -n oxford_asl-%{version}

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
# NB: the upstream `make install` runs a `pyinstall` target that pip-installs
# the oxford_asl Python package (offline-fatal in mock). Install the compiled
# asl_file binary and the generated driver scripts directly instead.
mkdir -p %{buildroot}%{fsldir}/bin
install -m 0755 asl_file %{buildroot}%{fsldir}/bin/asl_file
for s in oxford_asl asl_calib asl_reg quasil toast; do
    install -m 0755 "$s" %{buildroot}%{fsldir}/bin/"$s"
done
chrpath -r '$ORIGIN/../lib' %{buildroot}%{fsldir}/bin/asl_file 2>/dev/null || :

%check
test -x %{buildroot}%{fsldir}/bin/asl_file
test -f %{buildroot}%{fsldir}/bin/oxford_asl

%files
%{fsldir}/bin/asl_file
%{fsldir}/bin/oxford_asl
%{fsldir}/bin/asl_calib
%{fsldir}/bin/asl_reg
%{fsldir}/bin/quasil
%{fsldir}/bin/toast

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.29-1
- Initial package: oxford_asl/BASIL ASL perfusion quantification (asl_file +
  oxford_asl/asl_calib/asl_reg scripts), on the fsl foundation; runs FABBER's
  ASL models (fsl-fabber-models-asl). Completes the FSL ASL chain.
