%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-swe
Version:        1.1.0
Release:        1%{?dist}
Summary:        FSL SwE - Sandwich Estimator for longitudinal/repeated-measures neuroimaging

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/SwE
Source0:        https://git.fmrib.ox.ac.uk/fsl/swe/-/archive/v%{version}/swe-v%{version}.tar.gz#/fsl-swe-%{version}.tar.gz

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

%description
The Sandwich Estimator (SwE) toolbox performs non-iterative marginal
modelling of longitudinal and repeated-measures neuroimaging data, with
the sandwich variance estimator and Wild Bootstrap inference. Ships the swe
binary and its private libfsl-swe.so. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n swe-v%{version}

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
cp -a "${FSLDEVDIR}/lib/libfsl-swe.so" %{buildroot}%{fsldir}/lib/
find %{buildroot}%{fsldir}/bin -xtype l -delete
chrpath -r '$ORIGIN' %{buildroot}%{fsldir}/lib/libfsl-swe.so 2>/dev/null || :
chmod 0755 %{buildroot}%{fsldir}/lib/libfsl-swe.so
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/swe
test -e %{buildroot}%{fsldir}/lib/libfsl-swe.so

%files
%{fsldir}/bin/swe
%{fsldir}/lib/libfsl-swe.so

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.0-1
- Initial package: SwE Sandwich Estimator (swe + private libfsl-swe.so), on the
  fsl foundation.
