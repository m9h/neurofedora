%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-film
Version:        2111.1
Release:        1%{?dist}
Summary:        FSL FILM - FMRIB's Improved Linear Model for FMRI time-series

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FEAT
Source0:        https://git.fmrib.ox.ac.uk/fsl/film/-/archive/%{version}/film-%{version}.tar.gz#/fsl-film-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
# Needs the surface library added to the foundation at 6.0.7.18-7.
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
BuildRequires:  expat-devel
BuildRequires:  ciftilib-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
FILM (FMRIB's Improved Linear Model) carries out the first-level (within-run)
time-series GLM estimation for FMRI with prewhitening to account for temporal
autocorrelation, as used by FEAT. Ships film_gls, contrast_mgr and the
ttoz/ftoz/ttologp statistic utilities, plus the private libfsl-film.so. Part
of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n film-%{version}

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
cp -a "${FSLDEVDIR}/lib/libfsl-film.so" %{buildroot}%{fsldir}/lib/
find %{buildroot}%{fsldir}/bin -xtype l -delete
chrpath -r '$ORIGIN' %{buildroot}%{fsldir}/lib/libfsl-film.so 2>/dev/null || :
chmod 0755 %{buildroot}%{fsldir}/lib/libfsl-film.so
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/film_gls
test -e %{buildroot}%{fsldir}/lib/libfsl-film.so

%files
%{fsldir}/bin/film_gls
%{fsldir}/bin/contrast_mgr
%{fsldir}/bin/ttoz
%{fsldir}/bin/ftoz
%{fsldir}/bin/ttologp
%{fsldir}/bin/film_cifti
%{fsldir}/lib/libfsl-film.so

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.1-1
- Initial package: FILM first-level FMRI GLM (film_gls/contrast_mgr + stat utils
  + private libfsl-film.so), on the fsl foundation 6.0.7.18-7 (surface lib).
