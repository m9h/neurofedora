# FNIRT (FMRIB's Non-linear Image Registration Tool) layered on the fsl
# foundation. Built with FSL's own make system against the installed
# relocatable $FSLDIR=/usr/lib/fsl. fnirt links the spline/warp registration
# libraries (warpfns, basisfield, meshclass) shipped in fsl-libs.

%global fsldir          %{_prefix}/lib/fsl
# Depend on the fsl-libs package rather than the unversioned libfsl-*.so.
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-fnirt
Version:        2203.2
Release:        1%{?dist}
Summary:        FSL FNIRT - non-linear image registration tool

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT
Source0:        https://git.fmrib.ox.ac.uk/fsl/fnirt/-/archive/%{version}/fnirt-%{version}.tar.gz#/fsl-fnirt-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
# newimage headers transitively pull in <nlohmann/json.hpp>.
BuildRequires:  json-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
FNIRT (FMRIB's Non-linear Image Registration Tool) performs non-linear
registration of brain images, typically used after an affine FLIRT
registration to warp images into a standard space. This package provides the
fnirt and invwarp programs plus the standard FNIRT configuration files
(fnirtcnf, installed alongside the FLIRT schedules in $FSLDIR/etc/flirtsch).
Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n fnirt-%{version}

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
# exeinstall (XFILES -> bin) + custominstall (fnirtcnf/* -> etc/flirtsch)
make install

mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/
mkdir -p %{buildroot}%{fsldir}/etc/flirtsch
cp -a "${FSLDEVDIR}/etc/flirtsch/." %{buildroot}%{fsldir}/etc/flirtsch/
# custominstall makes the dir group-writable; restore standard perms.
chmod 0755 %{buildroot}%{fsldir}/etc/flirtsch

find %{buildroot}%{fsldir}/bin -xtype l -delete

# Reset the leaked build-stage rpath on every compiled program (bin -> ../lib).
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/fnirt
test -x %{buildroot}%{fsldir}/bin/invwarp
test -e %{buildroot}%{fsldir}/etc/flirtsch/T1_2_MNI152_2mm.cnf
ldd %{buildroot}%{fsldir}/bin/fnirt | grep -q libfsl-warpfns.so

%files
%{fsldir}/bin/fnirt
%{fsldir}/bin/invwarp
# FNIRT configuration files (co-located with the FLIRT schedules; the dir is
# co-owned with fsl-flirt so fnirt is installable independently).
%dir %{fsldir}/etc/flirtsch
%{fsldir}/etc/flirtsch/FA_2_FMRIB58_1mm.cnf
%{fsldir}/etc/flirtsch/GM_2_MNI152GM_2mm.cnf
%{fsldir}/etc/flirtsch/T1_2_MNI152_2mm.cnf

%changelog
* Tue Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 2203.2-1
- Initial package: FNIRT non-linear registration (fnirt + invwarp) and the
  standard FNIRT configuration files, layered on the fsl foundation and built
  against the installed relocatable $FSLDIR=/usr/lib/fsl via FSL's make system
