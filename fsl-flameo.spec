%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-flameo
Version:        2111.2
Release:        1%{?dist}
Summary:        FSL FLAME - higher-level FMRI mixed-effects modelling

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FEAT
Source0:        https://git.fmrib.ox.ac.uk/fsl/flameo/-/archive/%{version}/flameo-%{version}.tar.gz#/fsl-flameo-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
BuildRequires:  ciftilib-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
FLAMEO implements FMRIB's Local Analysis of Mixed Effects (FLAME) for
higher-level (group) FMRI analysis, performing mixed-effects GLM inference
across sessions/subjects. It is the modelling engine used by FEAT's
higher-level analyses. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n flameo-%{version}

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
test -x %{buildroot}%{fsldir}/bin/flameo
ldd %{buildroot}%{fsldir}/bin/flameo | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/flameo

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.2-1
- Initial package: FLAME higher-level FMRI mixed-effects (flameo), on the fsl
  foundation; links CiftiLib.
