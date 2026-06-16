%global commit      99c29e6b80d2ebd4a1ac398346a6ee74443e4948
%global shortcommit %(c=%{commit}; echo ${c:0:12})

%global fsldir          %{_prefix}/lib/fsl
# Exclude auto-deps on the foundation libs AND fabber's own private libs.
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-fabber-core
Version:        4.0.11
Release:        1%{?dist}
Summary:        FABBER - fast Bayesian model fitting for quantitative MRI

License:        Apache-2.0
URL:            https://github.com/physimals/fabber_core
# Pin to a recent master commit: tagged releases (<= v4.0.10) still use the old
# unprefixed FSL link names; master uses -lfsl-* matching our foundation.
Source0:        %{url}/archive/%{commit}/fabber_core-%{shortcommit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
BuildRequires:  boost-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
FABBER is a tool for fast Bayesian (variational) inference of nonlinear
forward models applied voxelwise to quantitative MRI data (ASL, CEST, DCE,
DSC, dual-echo, dwi, etc.). This is the core inference engine; model libraries
(e.g. fabber_models_asl) plug in on top. Ships the fabber and mvntool
executables and the fabbercore/fabberexec shared libraries.

%prep
%autosetup -p1 -n fabber_core-%{commit}

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
cp -a "${FSLDEVDIR}/lib/libfsl-fabbercore.so" %{buildroot}%{fsldir}/lib/
cp -a "${FSLDEVDIR}/lib/libfsl-fabberexec.so" %{buildroot}%{fsldir}/lib/
find %{buildroot}%{fsldir}/bin -xtype l -delete
for so in %{buildroot}%{fsldir}/lib/*.so; do
    chrpath -r '$ORIGIN' "$so" 2>/dev/null || :
    chmod 0755 "$so"
done
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/fabber
test -e %{buildroot}%{fsldir}/lib/libfsl-fabbercore.so

%files
%{fsldir}/bin/fabber
%{fsldir}/bin/mvntool
%{fsldir}/bin/fabber_var
%{fsldir}/lib/libfsl-fabbercore.so
%{fsldir}/lib/libfsl-fabberexec.so

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.11-1
- Initial package: FABBER Bayesian inference engine (fabber/mvntool + the
  fabbercore/fabberexec libraries), on the fsl foundation. Root of the ASL
  (oxford_asl/basil) chain.
