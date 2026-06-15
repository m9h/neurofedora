%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-gps
Version:        2211.1
Release:        1%{?dist}
Summary:        FSL gps - generate diffusion gradient direction sets

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT
Source0:        https://git.fmrib.ox.ac.uk/fsl/gps/-/archive/%{version}/gps-%{version}.tar.gz#/fsl-gps-%{version}.tar.gz

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
gps (Gradient Permutation Search) generates optimised diffusion-weighted
gradient direction sets for diffusion MRI acquisition. Part of the FMRIB
Software Library (FSL).

%prep
%autosetup -p1 -n gps-%{version}

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
test -x %{buildroot}%{fsldir}/bin/gps
ldd %{buildroot}%{fsldir}/bin/gps | grep -q libfsl-miscmaths.so

%files
%{fsldir}/bin/gps

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2211.1-1
- Initial package: gps diffusion gradient direction-set generator, on the fsl
  foundation.
