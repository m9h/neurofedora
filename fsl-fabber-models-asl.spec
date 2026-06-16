%global fabber_commit 99c29e6b80d2ebd4a1ac398346a6ee74443e4948

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-fabber-models-asl
Version:        2.0.8
Release:        1%{?dist}
Summary:        FABBER ASL forward-model library (arterial spin labelling)

License:        Apache-2.0
URL:            https://github.com/physimals/fabber_models_asl
Source0:        %{url}/archive/v%{version}/fabber_models_asl-%{version}.tar.gz#/fsl-fabber-models-asl-%{version}.tar.gz
# The model build needs fabber_core's headers (referenced as ../fabber_core).
# It links the installed libfsl-fabbercore.so from the fsl-fabber-core package.
Source1:        https://github.com/physimals/fabber_core/archive/%{fabber_commit}/fabber_core-%{fabber_commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  git-core
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  fsl-fabber-core
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
BuildRequires:  boost-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18
Requires:       fsl-fabber-core

%description
The FABBER arterial-spin-labelling (ASL) forward-model library: the kinetic
models (resting-state, multiphase, GRASE) used by FABBER to fit perfusion
(ASL) data. Provides the fabber_asl executable (FABBER with the ASL models
built in) and the libfsl-fabber_models_asl.so plugin. Underpins oxford_asl
and BASIL.

%prep
%autosetup -p1 -n fabber_models_asl-%{version}
# Provide fabber_core's headers as the sibling ../fabber_core the Makefile expects.
tar xzf %{SOURCE1} -C ..
mv ../fabber_core-%{fabber_commit} ../fabber_core

%build
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
mkdir -p "${FSLDEVDIR}"
export CFLAGS="%{optflags}"
# The model sources #include "fabber_core/<hdr>"; -I.. resolves them against the
# bundled ../fabber_core source (the modern Makefile path omits the -I.. that
# the legacy path had).
export CXXFLAGS="%{optflags} -I.."
export LDFLAGS="%{?build_ldflags}"
make %{?_smp_mflags}

%install
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
make install
mkdir -p %{buildroot}%{fsldir}/bin %{buildroot}%{fsldir}/lib
cp -a "${FSLDEVDIR}/bin/fabber_asl" %{buildroot}%{fsldir}/bin/
cp -a "${FSLDEVDIR}/lib/libfsl-fabber_models_asl.so" %{buildroot}%{fsldir}/lib/
find %{buildroot}%{fsldir}/bin -xtype l -delete
chrpath -r '$ORIGIN' %{buildroot}%{fsldir}/lib/libfsl-fabber_models_asl.so 2>/dev/null || :
chmod 0755 %{buildroot}%{fsldir}/lib/libfsl-fabber_models_asl.so
chrpath -r '$ORIGIN/../lib' %{buildroot}%{fsldir}/bin/fabber_asl 2>/dev/null || :

%check
test -x %{buildroot}%{fsldir}/bin/fabber_asl
test -e %{buildroot}%{fsldir}/lib/libfsl-fabber_models_asl.so

%files
%{fsldir}/bin/fabber_asl
%{fsldir}/lib/libfsl-fabber_models_asl.so

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.8-1
- Initial package: FABBER ASL forward-model library (fabber_asl +
  libfsl-fabber_models_asl.so), on the fsl foundation + fsl-fabber-core.
