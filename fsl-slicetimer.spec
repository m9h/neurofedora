# FSL slicetimer (slice-timing correction for fMRI), layered on the fsl
# foundation and built against the installed relocatable $FSLDIR=/usr/lib/fsl.

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-slicetimer
Version:        2111.0
Release:        1%{?dist}
Summary:        FSL slicetimer - slice-timing correction for fMRI

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/slicetimer
Source0:        https://git.fmrib.ox.ac.uk/fsl/slicetimer/-/archive/%{version}/slicetimer-%{version}.tar.gz#/fsl-slicetimer-%{version}.tar.gz

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
slicetimer corrects fMRI time-series data for differences in slice
acquisition times by Hanning-windowed sinc interpolation along the time
axis. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n slicetimer-%{version}

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
test -x %{buildroot}%{fsldir}/bin/slicetimer
ldd %{buildroot}%{fsldir}/bin/slicetimer | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/slicetimer

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.0-1
- Initial package: slicetimer fMRI slice-timing correction, on the fsl foundation.
