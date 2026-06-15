%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^(libfsl-.*|libgdc)\\.so.*$

Name:           fsl-mm
Version:        2111.1
Release:        1%{?dist}
Summary:        FSL MM - mixture-model spatial activation maps

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki
Source0:        https://git.fmrib.ox.ac.uk/fsl/mm/-/archive/%{version}/mm-%{version}.tar.gz#/fsl-mm-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
BuildRequires:  gd-devel
BuildRequires:  libpng-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
MM performs mixture-modelling of statistic images to produce probabilistic
spatial activation maps (an alternative to fixed thresholding), as used by
MELODIC and FEAT. Ships the mm binary and its private libfsl-mm.so. Part of
the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n mm-%{version}

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
# Private shared library used by mm.
mkdir -p %{buildroot}%{fsldir}/lib
cp -a "${FSLDEVDIR}/lib/libfsl-mm.so" %{buildroot}%{fsldir}/lib/
find %{buildroot}%{fsldir}/bin -xtype l -delete
chrpath -r '$ORIGIN' %{buildroot}%{fsldir}/lib/libfsl-mm.so 2>/dev/null || :
chmod 0755 %{buildroot}%{fsldir}/lib/libfsl-mm.so
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/mm
test -e %{buildroot}%{fsldir}/lib/libfsl-mm.so

%files
%{fsldir}/bin/mm
%{fsldir}/lib/libfsl-mm.so

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.1-1
- Initial package: MM mixture-model activation maps (mm + private libfsl-mm.so),
  on the fsl foundation.
