%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^(libfsl-.*|libgdc)\\.so.*$

Name:           fsl-filmbabe
Version:        2111.1
Release:        1%{?dist}
Summary:        FSL FILMBABE - Bayesian FMRI time-series modelling

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FEAT
Source0:        https://git.fmrib.ox.ac.uk/fsl/filmbabe/-/archive/%{version}/filmbabe-%{version}.tar.gz#/fsl-filmbabe-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
# Links the foundation miscplot/miscpic plotting libs (which pull gd/png).
BuildRequires:  gd-devel
BuildRequires:  libpng-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
FILMBABE (FMRIB's Improved Linear Model with a Bayesian Approach to model
Based Estimation) performs spatially-regularised Bayesian estimation of FMRI
time-series GLMs. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n filmbabe-%{version}

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
test -x %{buildroot}%{fsldir}/bin/filmbabe
test -x %{buildroot}%{fsldir}/bin/halfcosbasis

%files
%{fsldir}/bin/filmbabe
%{fsldir}/bin/halfcosbasis
%{fsldir}/bin/filmbabescript

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.1-1
- Initial package: FILMBABE Bayesian FMRI time-series modelling (filmbabe,
  halfcosbasis + script), on the fsl foundation.
