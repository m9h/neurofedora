# FUGUE (FMRIB's Utility for Geometrically Unwarping EPIs) and its companion
# warp utilities, layered on the fsl foundation. Built with FSL's own make
# system against the installed relocatable $FSLDIR=/usr/lib/fsl.

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-fugue
Version:        2201.5
Release:        1%{?dist}
Summary:        FSL FUGUE - EPI fieldmap-based geometric unwarping

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FUGUE
Source0:        https://git.fmrib.ox.ac.uk/fsl/fugue/-/archive/%{version}/fugue-%{version}.tar.gz#/fsl-fugue-%{version}.tar.gz

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
FUGUE performs geometric unwarping of echo-planar (EPI) images using B0
fieldmaps to correct susceptibility-induced distortions. This package also
provides the associated warp-field utilities: prelude (phase unwrapping),
applywarp, convertwarp, sigloss (signal-loss estimation), fnirtfileutils and
the fsl_prepare_fieldmap / extractfidparams helper scripts. Part of the FMRIB
Software Library (FSL).

%prep
%autosetup -p1 -n fugue-%{version}

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
# RUNTCLS (Fsl_prepare_fieldmap -> Runtcl) is a tcl-GUI symlink to the
# unpackaged fsl-misc_tcl; drop the dangling link.
find %{buildroot}%{fsldir}/bin -xtype l -delete

for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/fugue
test -x %{buildroot}%{fsldir}/bin/prelude
test -e %{buildroot}%{fsldir}/bin/fsl_prepare_fieldmap
# fugue links -lfsl-warpfns in its Makefile but, like flirt, never references
# warp symbols, so -Wl,--as-needed prunes that NEEDED entry; assert the core
# image library it actually uses instead.
ldd %{buildroot}%{fsldir}/bin/fugue | grep -q libfsl-newimage.so

%files
# Compiled programs (XFILES)
%{fsldir}/bin/prelude
%{fsldir}/bin/fugue
%{fsldir}/bin/applywarp
%{fsldir}/bin/convertwarp
%{fsldir}/bin/sigloss
%{fsldir}/bin/fnirtfileutils
# Helper scripts (SCRIPTS)
%{fsldir}/bin/fsl_prepare_fieldmap
%{fsldir}/bin/extractfidparams

%changelog
* Tue Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 2201.5-1
- Initial package: FUGUE EPI fieldmap unwarping plus the prelude/applywarp/
  convertwarp/sigloss/fnirtfileutils warp utilities and the fsl_prepare_fieldmap
  helper scripts, layered on the fsl foundation and built against the installed
  relocatable $FSLDIR=/usr/lib/fsl via FSL's make system
