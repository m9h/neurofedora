%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-eddy
Version:        2401.2
Release:        1%{?dist}
Summary:        FSL eddy - correction of eddy-current and movement distortions in dMRI

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy
Source0:        https://git.fmrib.ox.ac.uk/fsl/eddy/-/archive/%{version}/eddy-%{version}.tar.gz#/fsl-eddy-%{version}.tar.gz
# eddy links -lfsl-topup and includes topup's headers, which the fsl-topup
# package ships as a runtime lib only (no -devel). Build topup into the dev
# stage for its headers + libfsl-topup.so; the runtime lib comes from fsl-topup.
Source1:        https://git.fmrib.ox.ac.uk/fsl/topup/-/archive/2203.5/topup-2203.5.tar.gz#/fsl-topup-2203.5.tar.gz

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
# eddy_cpu has a NEEDED entry on libfsl-topup.so (shipped by fsl-topup).
Requires:       fsl-topup

%description
eddy corrects for eddy-current-induced distortions and subject movement in
diffusion-weighted MRI, and can detect and replace outlier slices. This is the
CPU build (eddy_cpu); the optional CUDA/GPU variant is not included. Part of
the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n eddy-%{version}
# Unpack topup alongside (for headers + libfsl-topup.so at build time).
tar xzf %{SOURCE1}

%build
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
mkdir -p "${FSLDEVDIR}"
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{?build_ldflags}"
# Build + stage-install topup first so eddy resolves topup/*.h and -lfsl-topup.
make -C topup-2203.5 %{?_smp_mflags}
make -C topup-2203.5 install
# eddy: default gpu unset -> CPU build (eddy_cpu).
make %{?_smp_mflags}

%install
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
make install
# The stage bin also contains topup/applytopup (built above) — ship ONLY eddy.
mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/eddy_cpu" %{buildroot}%{fsldir}/bin/
cp -a "${FSLDEVDIR}/bin/eddy"     %{buildroot}%{fsldir}/bin/
find %{buildroot}%{fsldir}/bin -xtype l -delete
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/eddy_cpu
test -f %{buildroot}%{fsldir}/bin/eddy
ldd %{buildroot}%{fsldir}/bin/eddy_cpu | grep -q libfsl-topup.so

%files
%{fsldir}/bin/eddy_cpu
%{fsldir}/bin/eddy

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2401.2-1
- Initial package: eddy diffusion eddy-current/movement correction (CPU build,
  eddy_cpu + eddy wrapper), on the fsl foundation; links the topup library
  (built from bundled topup source; runtime from fsl-topup).
