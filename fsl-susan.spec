# SUSAN (Smallest Univalue Segment Assimilating Nucleus) nonlinear noise-
# reduction filter, layered on the fsl foundation. Built with FSL's own make
# system against the installed relocatable $FSLDIR=/usr/lib/fsl.

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-susan
Version:        2111.0
Release:        1%{?dist}
Summary:        FSL SUSAN - structure-preserving noise reduction filter

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/SUSAN
Source0:        https://git.fmrib.ox.ac.uk/fsl/susan/-/archive/%{version}/susan-%{version}.tar.gz#/fsl-susan-%{version}.tar.gz

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
SUSAN is a structure-preserving noise-reduction filter used throughout FSL
(e.g. by FEAT for spatial smoothing). It reduces image noise while keeping
underlying structure (edges) intact. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n susan-%{version}

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
# RUNTCLS (Susan -> Runtcl) is a tcl-GUI symlink to the unpackaged fsl-misc_tcl.
find %{buildroot}%{fsldir}/bin -xtype l -delete

for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/susan
ldd %{buildroot}%{fsldir}/bin/susan | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/susan

%changelog
* Tue Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.0-1
- Initial package: the SUSAN noise-reduction filter, layered on the fsl
  foundation and built against the installed relocatable $FSLDIR=/usr/lib/fsl
