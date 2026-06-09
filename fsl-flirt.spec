# FLIRT (FMRIB's Linear Image Registration Tool) layered on the fsl
# foundation. Built with FSL's own make system against the installed
# relocatable $FSLDIR=/usr/lib/fsl. flirt links the registration libraries
# (warpfns, basisfield, meshclass) now shipped in fsl-libs.

%global fsldir          %{_prefix}/lib/fsl
# Drop auto-deps on the foundation's unversioned libfsl-*.so (depend on the
# fsl-libs package instead), and on /usr/bin/fslpython: aff2rigid uses
# "#!/usr/bin/env fslpython", which the dep generator rewrites to an absolute
# path that does not exist - fslpython is found via $FSLDIR/bin on PATH.
%global __requires_exclude ^(libfsl-.*\\.so.*|/usr/bin/fslpython)$

Name:           fsl-flirt
Version:        2111.4
Release:        1%{?dist}
Summary:        FSL FLIRT - linear image registration tool

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT
Source0:        https://git.fmrib.ox.ac.uk/fsl/flirt/-/archive/%{version}/flirt-%{version}.tar.gz#/fsl-flirt-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
FLIRT (FMRIB's Linear Image Registration Tool) is a robust and accurate tool
for affine (linear) intra- and inter-modal brain image registration. This
package also provides the supporting transform utilities (convert_xfm,
avscale, rmsdiff, the coordinate converters, applyxfm4D, pointflirt, makerot,
midtrans) and registration helper scripts (epi_reg, aff2rigid, pairreg and
others), plus the FLIRT cost-function schedule files in $FSLDIR/etc/flirtsch.
It is part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n flirt-%{version}

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
# Runs exeinstall (XFILES+SCRIPTS -> bin), tclinstall (RUNTCLS symlinks) and
# the project's custominstall (flirtsch/* -> etc/flirtsch).
make install

mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/
# FLIRT cost-function schedule files (referenced e.g. by FreeSurfer wrappers).
mkdir -p %{buildroot}%{fsldir}/etc/flirtsch
cp -a "${FSLDEVDIR}/etc/flirtsch/." %{buildroot}%{fsldir}/etc/flirtsch/
# custominstall makes the dir group-writable (g+w); restore standard perms.
chmod 0755 %{buildroot}%{fsldir}/etc/flirtsch

# RUNTCLS (Flirt/InvertXFM/ApplyXFM/ConcatXFM/Nudge + _gui) are symlinks to
# Runtcl from the unpackaged GUI helper fsl-misc_tcl; drop the dangling links.
find %{buildroot}%{fsldir}/bin -xtype l -delete

# Reset the leaked build-stage rpath on every compiled program (bin -> ../lib);
# the SCRIPTS are shell and are skipped.
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/flirt
test -x %{buildroot}%{fsldir}/bin/convert_xfm
test -e %{buildroot}%{fsldir}/bin/epi_reg
test -e %{buildroot}%{fsldir}/etc/flirtsch/bbr.sch
# flirt must resolve the FSL core libraries via the relocated rpath. (It links
# -lfsl-warpfns in its Makefile but, being linear-only, never references warp
# symbols, so -Wl,--as-needed prunes that NEEDED entry - do not assert it.)
ldd %{buildroot}%{fsldir}/bin/flirt | grep -q libfsl-newimage.so

%files
# Compiled programs (XFILES)
%{fsldir}/bin/flirt
%{fsldir}/bin/convert_xfm
%{fsldir}/bin/avscale
%{fsldir}/bin/rmsdiff
%{fsldir}/bin/std2imgcoord
%{fsldir}/bin/img2stdcoord
%{fsldir}/bin/img2imgcoord
%{fsldir}/bin/applyxfm4D
%{fsldir}/bin/pointflirt
%{fsldir}/bin/makerot
%{fsldir}/bin/midtrans
# Helper scripts (SCRIPTS)
%{fsldir}/bin/extracttxt
%{fsldir}/bin/pairreg
%{fsldir}/bin/standard_space_roi
%{fsldir}/bin/flirt_average
%{fsldir}/bin/epi_reg
%{fsldir}/bin/aff2rigid
# Cost-function schedule files
%dir %{fsldir}/etc/flirtsch
%{fsldir}/etc/flirtsch/*

%changelog
* Mon Jun 08 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.4-1
- Initial package: FLIRT linear registration + transform/helper utilities and
  the flirtsch schedule files, layered on the fsl foundation
- Built against the installed relocatable $FSLDIR=/usr/lib/fsl via FSL's make
- Drop the Flirt/InvertXFM/ApplyXFM/ConcatXFM/Nudge tcl-GUI symlinks (require
  the unpackaged fsl-misc_tcl)
