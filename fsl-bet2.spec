# BET (Brain Extraction Tool) is the first end-user FSL tool layered on the
# foundation package (fsl-libs / fsl-libs-devel). It is built with FSL's own
# make system against the *installed* relocatable $FSLDIR=/usr/lib/fsl, which
# supplies the headers (fsl-libs-devel) and link libraries (fsl-libs).

%global fsldir          %{_prefix}/lib/fsl
# The foundation deliberately does not version or export libfsl-*.so symbols,
# so do not let the auto-dep generator emit Requires on them; depend on the
# fsl-libs package explicitly instead.
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-bet2
Version:        2111.9
Release:        1%{?dist}
Summary:        FSL Brain Extraction Tool (BET)

# bet2 carries the FSL non-commercial licence.
License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BET
Source0:        https://git.fmrib.ox.ac.uk/fsl/bet2/-/archive/%{version}/bet2-%{version}.tar.gz#/fsl-bet2-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
# Foundation: build system (FSLCONFDIR), headers and link libraries.
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
# FSL's buildSettings.mk auto-appends -llapack -lblas -lz to every link.
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel

# Runtime: the shared libraries it links and the fslconf environment.
Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
BET (Brain Extraction Tool) deletes non-brain tissue from an image of the
whole head. It can also estimate the inner and outer skull surfaces and the
outer scalp surface when given good-quality T1- and T2-weighted input.

This package provides the bet/bet2 brain-extraction programs, betsurf,
bet4animal and the robustfov field-of-view cropping tool. It is part of the
FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n bet2-%{version}

%build
# Point the FSL build at the installed foundation: FSLDIR supplies headers
# (-isystem $FSLDIR/include) and link libs (-L $FSLDIR/lib); FSLCONFDIR is the
# foundation's make system. Install lands in FSLDEVDIR, a private stage dir.
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

# Relocate the staged tree into the buildroot's $FSLDIR.
mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/

# RUNTCLS=Bet creates Bet/Bet_gui symlinks to Runtcl, which is shipped by the
# (unpackaged) GUI helper fsl-misc_tcl. Drop the dangling links; the headless
# command-line tools do not need them.
rm -f %{buildroot}%{fsldir}/bin/Bet %{buildroot}%{fsldir}/bin/Bet_gui

# FSL embeds an rpath of '$ORIGIN:$FSLDEVDIR/lib:$FSLDIR/lib'; the staging
# component leaks an absolute build path. Reset to locate the foundation libs
# relative to the binaries (bin -> ../lib).
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
# The compiled programs and the user-facing wrapper script must be present...
test -x %{buildroot}%{fsldir}/bin/bet2
test -x %{buildroot}%{fsldir}/bin/betsurf
test -x %{buildroot}%{fsldir}/bin/robustfov
test -e %{buildroot}%{fsldir}/bin/bet
# ...and bet2 must resolve its FSL libraries via the relocated rpath.
LD_LIBRARY_PATH=%{buildroot}%{fsldir}/lib \
    ldd %{buildroot}%{fsldir}/bin/bet2 | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/bet
%{fsldir}/bin/bet2
%{fsldir}/bin/bet4animal
%{fsldir}/bin/betsurf
%{fsldir}/bin/old_betall
%{fsldir}/bin/robustfov

%changelog
* Mon Jun 08 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.9-1
- Initial package: first FSL tool layered on the fsl foundation libraries
- Built against the installed relocatable $FSLDIR=/usr/lib/fsl via FSL's make
- Drop the Bet/Bet_gui tcl-GUI symlinks (require the unpackaged fsl-misc_tcl)
