# FSL MELODIC (probabilistic ICA for FMRI), layered on the fsl foundation.
# Built with FSL's own make system against the installed relocatable
# $FSLDIR=/usr/lib/fsl. Links the foundation's miscplot/miscpic plotting
# libraries (from libvis, added to fsl-libs at 6.0.7.18-6) and CiftiLib.
# Ships its own private shared library (libfsl-ggmix.so), like topup.

%global fsldir          %{_prefix}/lib/fsl
# Exclude auto-deps on the foundation's unversioned libfsl-*.so (depend on
# fsl-libs) AND the package's own libfsl-ggmix.so (resolved via the binaries'
# $ORIGIN/../lib rpath) AND the bundled GDChart libgdc.so (in fsl-libs).
%global __requires_exclude ^(libfsl-.*|libgdc)\\.so.*$

Name:           fsl-melodic
Version:        2111.3
Release:        1%{?dist}
Summary:        FSL MELODIC - probabilistic independent component analysis for FMRI

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/MELODIC
Source0:        https://git.fmrib.ox.ac.uk/fsl/melodic/-/archive/%{version}/melodic-%{version}.tar.gz#/fsl-melodic-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
# Foundation 6.0.7.18-6 adds the miscplot/miscpic (libvis) + libgdc libraries.
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
# miscplot/miscpic (and thus melodic) link GDChart + system gd/png.
BuildRequires:  gd-devel
BuildRequires:  libpng-devel
# CiftiLib (pkg-config CiftiLib) for the CIFTI I/O paths.
BuildRequires:  ciftilib-devel
BuildRequires:  hdf5-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
MELODIC performs Probabilistic Independent Component Analysis (PICA) to
decompose single- or multi-session FMRI data into spatial and temporal
components. This package ships melodic together with the related fsl_glm,
fsl_sbca, fsl_mvlm, fsl_regfilt and fsl_schurprod utilities, the melodicreport
and dual_regression scripts, and the private libfsl-ggmix.so mixture-model
library. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n melodic-%{version}

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
# Private shared library (libfsl-ggmix.so) used by melodic.
mkdir -p %{buildroot}%{fsldir}/lib
cp -a "${FSLDEVDIR}/lib/libfsl-ggmix.so" %{buildroot}%{fsldir}/lib/

# Drop dangling tcl-GUI symlinks (RUNTCLS Melodic -> unpackaged fsl-misc_tcl).
find %{buildroot}%{fsldir}/bin -xtype l -delete

# Strip the leaked build-stage rpath: the private lib finds its foundation
# siblings via $ORIGIN ($FSLDIR/lib); the binaries find ../lib.
chrpath -r '$ORIGIN' %{buildroot}%{fsldir}/lib/libfsl-ggmix.so 2>/dev/null || :
chmod 0755 %{buildroot}%{fsldir}/lib/libfsl-ggmix.so
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/melodic
test -x %{buildroot}%{fsldir}/bin/fsl_glm
test -x %{buildroot}%{fsldir}/bin/fsl_regfilt
test -e %{buildroot}%{fsldir}/lib/libfsl-ggmix.so
# melodic links the foundation miscplot/miscpic; assert a stable dependency.
ldd %{buildroot}%{fsldir}/bin/melodic | grep -q libfsl-miscplot.so

%files
%{fsldir}/bin/melodic
%{fsldir}/bin/fsl_glm
%{fsldir}/bin/fsl_sbca
%{fsldir}/bin/fsl_mvlm
%{fsldir}/bin/fsl_regfilt
%{fsldir}/bin/fsl_schurprod
%{fsldir}/bin/dual_regression
%{fsldir}/lib/libfsl-ggmix.so

%changelog
* Sun Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.3-1
- Initial package: FSL MELODIC probabilistic ICA (melodic + fsl_glm/fsl_sbca/
  fsl_mvlm/fsl_regfilt/fsl_schurprod + dual_regression script and the private
  libfsl-ggmix.so), layered on the fsl foundation 6.0.7.18-6 which
  adds the miscplot/miscpic (libvis) + GDChart libraries. Links CiftiLib.
