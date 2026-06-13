# FSL topup (susceptibility-induced distortion estimation/correction), layered
# on the fsl foundation. Built with FSL's own make system against the installed
# relocatable $FSLDIR=/usr/lib/fsl. Unlike the simpler tools, topup ships its
# own private shared library (libfsl-topup.so) used by both binaries, plus the
# b02b0 config schedules into etc/flirtsch.

%global fsldir          %{_prefix}/lib/fsl
# Exclude auto-deps on the foundation's unversioned libfsl-*.so (depend on
# fsl-libs instead) AND the package's own libfsl-topup.so (resolved via the
# binaries' $ORIGIN/../lib rpath, not a system Requires).
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-topup
Version:        2203.5
Release:        1%{?dist}
Summary:        FSL topup - estimation and correction of EPI susceptibility distortions

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup
Source0:        https://git.fmrib.ox.ac.uk/fsl/topup/-/archive/%{version}/topup-%{version}.tar.gz#/fsl-topup-%{version}.tar.gz

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
topup estimates and corrects susceptibility-induced (B0) distortions in
echo-planar (EPI) images, such as diffusion and fMRI data, from pairs of
images acquired with opposing phase-encode directions. Ships the topup and
applytopup command-line tools and the standard b02b0 configuration schedules.
Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n topup-%{version}

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
# Private shared library (libfsl-topup.so) shared by topup + applytopup.
mkdir -p %{buildroot}%{fsldir}/lib
cp -a "${FSLDEVDIR}/lib/libfsl-topup.so" %{buildroot}%{fsldir}/lib/
# b02b0 config schedules (co-located with the FLIRT schedules).
mkdir -p %{buildroot}%{fsldir}/etc/flirtsch
cp -a "${FSLDEVDIR}/etc/flirtsch/." %{buildroot}%{fsldir}/etc/flirtsch/
chmod 0755 %{buildroot}%{fsldir}/etc/flirtsch

# Drop any dangling tcl-GUI symlinks to the unpackaged fsl-misc_tcl.
find %{buildroot}%{fsldir}/bin -xtype l -delete

# Strip the leaked build-stage rpath: the private lib finds its foundation
# siblings via $ORIGIN ($FSLDIR/lib); the binaries find ../lib.
chrpath -r '$ORIGIN' %{buildroot}%{fsldir}/lib/libfsl-topup.so 2>/dev/null || :
chmod 0755 %{buildroot}%{fsldir}/lib/libfsl-topup.so
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/topup
test -x %{buildroot}%{fsldir}/bin/applytopup
test -e %{buildroot}%{fsldir}/lib/libfsl-topup.so
test -e %{buildroot}%{fsldir}/etc/flirtsch/b02b0.cnf
ldd %{buildroot}%{fsldir}/bin/topup | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/topup
%{fsldir}/bin/applytopup
%{fsldir}/lib/libfsl-topup.so
# b02b0 schedules; the flirtsch dir is co-owned with fsl-flirt/fsl-fnirt so
# topup is installable independently.
%dir %{fsldir}/etc/flirtsch
%{fsldir}/etc/flirtsch/b02b0.cnf
%{fsldir}/etc/flirtsch/b02b0_1.cnf
%{fsldir}/etc/flirtsch/b02b0_2.cnf
%{fsldir}/etc/flirtsch/b02b0_4.cnf
%{fsldir}/etc/flirtsch/b02b0_7T.cnf
%{fsldir}/etc/flirtsch/test_acqp.cnf

%changelog
* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 2203.5-1
- Initial package: topup + applytopup (EPI susceptibility distortion correction)
  with the private libfsl-topup.so and b02b0 config schedules, layered on the
  fsl foundation and built against the installed relocatable $FSLDIR=/usr/lib/fsl
