%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-ptx2
Version:        2111.5
Release:        1%{?dist}
Summary:        FSL probtrackx2 - probabilistic tractography (v2)

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT
Source0:        https://git.fmrib.ox.ac.uk/fsl/ptx2/-/archive/%{version}/ptx2-%{version}.tar.gz#/fsl-ptx2-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
# Needs the newmesh (libfsl-newmeshclass) library added to the foundation at -7.
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
probtrackx2 is FSL's probabilistic tractography tool (version 2), tracing
white-matter pathways from the crossing-fibre models produced by bedpostx,
with surface- and volume-based seeding. Ships probtrackx2 and the surfmaths /
surf2surf / surf2volume surface utilities. This is the CPU build (the CUDA/GPU
variant is not included). Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n ptx2-%{version}

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
test -x %{buildroot}%{fsldir}/bin/probtrackx2
ldd %{buildroot}%{fsldir}/bin/probtrackx2 | grep -q libfsl-newmeshclass.so

%files
%{fsldir}/bin/probtrackx2
%{fsldir}/bin/surfmaths
%{fsldir}/bin/surf2surf
%{fsldir}/bin/surf2volume

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.5-1
- Initial package: probtrackx2 probabilistic tractography + surf utilities
  (CPU build), on the fsl foundation 6.0.7.18-7 (newmesh lib).
