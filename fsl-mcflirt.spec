# FSL MCFLIRT (intra-modal motion correction for fMRI), layered on the fsl
# foundation and built against the installed relocatable $FSLDIR=/usr/lib/fsl.

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-mcflirt
Version:        2111.0
Release:        1%{?dist}
Summary:        FSL MCFLIRT - intra-modal motion correction for fMRI

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/MCFLIRT
Source0:        https://git.fmrib.ox.ac.uk/fsl/mcflirt/-/archive/%{version}/mcflirt-%{version}.tar.gz#/fsl-mcflirt-%{version}.tar.gz

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
MCFLIRT is an intra-modal motion correction tool, designed for use on
time-series of fMRI images and based on optimisation and registration
techniques from FLIRT. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n mcflirt-%{version}

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
test -x %{buildroot}%{fsldir}/bin/mcflirt
ldd %{buildroot}%{fsldir}/bin/mcflirt | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/mcflirt

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.0-1
- Initial package: MCFLIRT fMRI motion correction, layered on the fsl foundation.
