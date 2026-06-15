# FSL SIENA/SIENAX (brain atrophy / change analysis), layered on the fsl
# foundation and built against the installed relocatable $FSLDIR=/usr/lib/fsl.
# The siena/sienax driver scripts invoke bet2, flirt, fast4, fnirt and the
# avwutils image tools at runtime, so we depend on those FSL packages too.

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-siena
Version:        2111.1
Release:        1%{?dist}
Summary:        FSL SIENA/SIENAX - brain atrophy and change analysis

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/SIENA
Source0:        https://git.fmrib.ox.ac.uk/fsl/siena/-/archive/%{version}/siena-%{version}.tar.gz#/fsl-siena-%{version}.tar.gz

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
# siena/sienax orchestrate these FSL tools at runtime.
Requires:       fsl-bet2
Requires:       fsl-flirt
Requires:       fsl-fast4
Requires:       fsl-fnirt
Requires:       fsl-avwutils

%description
SIENA estimates percentage brain volume change between two time-points, and
SIENAX estimates cross-sectional normalised brain volume from a single image.
Ships the siena_diff binary and the siena / sienax driver scripts. Part of
the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n siena-%{version}

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
mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/
find %{buildroot}%{fsldir}/bin -xtype l -delete
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/siena_diff
test -f %{buildroot}%{fsldir}/bin/siena
test -f %{buildroot}%{fsldir}/bin/sienax
ldd %{buildroot}%{fsldir}/bin/siena_diff | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/siena_diff
%{fsldir}/bin/siena
%{fsldir}/bin/sienax
%{fsldir}/bin/siena_flirt
%{fsldir}/bin/siena_cal
%{fsldir}/bin/siena_flow2std
%{fsldir}/bin/viena_quant
%{fsldir}/bin/viena_createpng

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.1-1
- Initial package: SIENA/SIENAX brain atrophy analysis (siena_diff + siena/
  sienax driver scripts), layered on the fsl foundation; Requires the bet2/
  flirt/fast4/fnirt/avwutils tools the scripts invoke.
