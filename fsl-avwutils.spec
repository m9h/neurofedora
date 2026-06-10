# FSL image utilities (avwutils) layered on the fsl foundation. Built with
# FSL's own make system against the installed relocatable $FSLDIR=/usr/lib/fsl.
# This is the workhorse command set every FSL pipeline uses: fslmaths, fslstats,
# fslroi, fslmerge, fslsplit, fslhd, fslswapdim, fslreorient2std and friends.

%global fsldir          %{_prefix}/lib/fsl
# Drop auto-deps on the foundation's unversioned libfsl-*.so (depend on the
# fsl-libs package instead), and on /usr/bin/fslpython: fsladd uses
# "#!/usr/bin/env fslpython", which the dep generator rewrites to an absolute
# path that does not exist - fslpython is found via $FSLDIR/bin on PATH.
%global __requires_exclude ^(libfsl-.*\\.so.*|/usr/bin/fslpython)$

Name:           fsl-avwutils
Version:        2209.3
Release:        1%{?dist}
Summary:        FSL image utilities (fslmaths, fslstats, fslroi, ...)

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk
Source0:        https://git.fmrib.ox.ac.uk/fsl/avwutils/-/archive/%{version}/avwutils-%{version}.tar.gz#/fsl-avwutils-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
# fslstats.cc #includes <nlohmann/json.hpp> directly (header-only library)
BuildRequires:  json-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
The FSL "avwutils" command-line image utilities, the most frequently used
tools in any FSL pipeline. Includes fslmaths (image arithmetic/filtering),
fslstats (image statistics), fslroi, fslmerge, fslsplit, fslselectvols,
fslhd/fslinfo/fslval (header inspection), fslorient/fslswapdim/fslreorient2std
(orientation), fslcomplex/fslfft/fslpspec (complex/spectral), fslmeants,
fslcc, fslinterleave, fslslice, fslsmoothfill, distancemap and the
header-editing helper scripts. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n avwutils-%{version}

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
# exeinstall (XFILES -> bin) + scriptinstall (SCRIPTS -> bin)
make install

mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/

# Drop any dangling symlinks (none expected for avwutils, but be safe).
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
test -x %{buildroot}%{fsldir}/bin/fslmaths
test -x %{buildroot}%{fsldir}/bin/fslstats
test -x %{buildroot}%{fsldir}/bin/fslroi
test -e %{buildroot}%{fsldir}/bin/fslinfo
# The compiled tools must resolve the FSL core libraries via the relocated rpath.
ldd %{buildroot}%{fsldir}/bin/fslmaths | grep -q libfsl-newimage.so

%files
# Compiled programs (XFILES)
%{fsldir}/bin/fslorient
%{fsldir}/bin/fslstats
%{fsldir}/bin/fslmerge
%{fsldir}/bin/fslpspec
%{fsldir}/bin/fslroi
%{fsldir}/bin/fslnvols
%{fsldir}/bin/fsl2ascii
%{fsldir}/bin/fslascii2img
%{fsldir}/bin/fslsplit
%{fsldir}/bin/fslcc
%{fsldir}/bin/fslinterleave
%{fsldir}/bin/fslhd
%{fsldir}/bin/fslcpgeom
%{fsldir}/bin/fslcreatehd
%{fsldir}/bin/fslmaths
%{fsldir}/bin/fslcomplex
%{fsldir}/bin/fslfft
%{fsldir}/bin/fslmeants
%{fsldir}/bin/fslslice
%{fsldir}/bin/fslswapdim_exe
%{fsldir}/bin/fslchfiletype_exe
%{fsldir}/bin/calc_grad_perc_dev
%{fsldir}/bin/fslsmoothfill
%{fsldir}/bin/fslselectvols
%{fsldir}/bin/distancemap
# Helper scripts (SCRIPTS)
%{fsldir}/bin/fslval
%{fsldir}/bin/fslchpixdim
%{fsldir}/bin/fslsize
%{fsldir}/bin/fslinfo
%{fsldir}/bin/fsledithd
%{fsldir}/bin/avw2fsl
%{fsldir}/bin/fslswapdim
%{fsldir}/bin/fslchfiletype
%{fsldir}/bin/fslreorient2std
%{fsldir}/bin/fslmodhd
%{fsldir}/bin/fsladd

%changelog
* Mon Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 2209.3-1
- Initial package: the avwutils image-utility command set (fslmaths, fslstats,
  fslroi, fslmerge, fslhd, fslswapdim, fslreorient2std and the rest), layered
  on the fsl foundation and built against the installed relocatable
  $FSLDIR=/usr/lib/fsl via FSL's make system
