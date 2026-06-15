# FSL randomise (permutation-based nonparametric inference on neuroimaging
# data), layered on the fsl foundation and built against the installed
# relocatable $FSLDIR=/usr/lib/fsl.

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-randomise
Version:        2203.3
Release:        1%{?dist}
Summary:        FSL randomise - permutation-based nonparametric inference

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/randomise
Source0:        https://git.fmrib.ox.ac.uk/fsl/randomise/-/archive/%{version}/randomise-%{version}.tar.gz#/fsl-randomise-%{version}.tar.gz

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
randomise performs permutation-based nonparametric statistical inference on
neuroimaging data, supporting voxelwise and cluster/TFCE spatial statistics,
flexible GLM designs and exchangeability blocks, with FWER correction. Ships
randomise plus the fdr and unconfound utilities and the randomise_parallel /
design helper scripts. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n randomise-%{version}

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
test -x %{buildroot}%{fsldir}/bin/randomise
test -x %{buildroot}%{fsldir}/bin/fdr
ldd %{buildroot}%{fsldir}/bin/randomise | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/randomise
%{fsldir}/bin/fdr
%{fsldir}/bin/unconfound
%{fsldir}/bin/design_ttest2
%{fsldir}/bin/randomise_parallel
%{fsldir}/bin/tfce_support
%{fsldir}/bin/randomise_combine
%{fsldir}/bin/setup_masks

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2203.3-1
- Initial package: randomise permutation inference (+ fdr/unconfound and the
  randomise_parallel/design scripts), layered on the fsl foundation.
