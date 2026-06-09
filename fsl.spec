# FSL is built from independently-versioned upstream modules. This SRPM
# builds the build-system root (fsl-base) plus the core C++ libraries in
# dependency order into a relocatable $FSLDIR (/usr/lib/fsl), mirroring the
# /usr/lib/freesurfer layout already used in this repo.
#
# This is the FOUNDATION package: fsl-base + the leaf libraries that almost
# every other FSL tool links (utils, miscmaths, znz, NewNifti, newimage,
# cprob, meshclass) and the spline/warp registration libraries (basisfield,
# warpfns) plus their build-time deps (armawrap headers, newran). Tools are
# layered on top in later packages.

%global fsldir          %{_prefix}/lib/fsl
%global __provides_exclude_from ^%{fsldir}/lib/.*\\.so$
%global __requires_exclude       ^libfsl-.*\\.so.*$

# Per-module upstream versions (the self-consistent set shipped in FSL 6.0.7.x)
%global ver_base        2504.3
%global ver_armawrap    0.7.0
%global ver_znzlib      2111.0
%global ver_cprob       2111.0
%global ver_newran      2111.0
%global ver_newnifti    4.1.0
%global ver_utils       2412.1
%global ver_miscmaths   2412.4
%global ver_newimage    2501.4
%global ver_meshclass   2111.0
%global ver_basisfield  2203.4
%global ver_warpfns     2501.0

Name:           fsl
Version:        6.0.7.18
Release:        4%{?dist}
Summary:        FMRIB Software Library - core libraries and build system

# FSL itself is non-commercial (LicenseRef-FSL); armawrap bundles Armadillo
# (Apache-2.0 OR MIT); cprob derives from Cephes (BSD-ish/public domain).
License:        LicenseRef-FSL AND Apache-2.0 AND BSD-3-Clause
URL:            https://fsl.fmrib.ox.ac.uk

Source0:        https://git.fmrib.ox.ac.uk/fsl/base/-/archive/%{ver_base}/base-%{ver_base}.tar.gz#/fsl-base-%{ver_base}.tar.gz
Source1:        https://git.fmrib.ox.ac.uk/fsl/armawrap/-/archive/%{ver_armawrap}/armawrap-%{ver_armawrap}.tar.gz#/fsl-armawrap-%{ver_armawrap}.tar.gz
Source2:        https://git.fmrib.ox.ac.uk/fsl/znzlib/-/archive/%{ver_znzlib}/znzlib-%{ver_znzlib}.tar.gz#/fsl-znzlib-%{ver_znzlib}.tar.gz
Source3:        https://git.fmrib.ox.ac.uk/fsl/cprob/-/archive/%{ver_cprob}/cprob-%{ver_cprob}.tar.gz#/fsl-cprob-%{ver_cprob}.tar.gz
Source4:        https://git.fmrib.ox.ac.uk/fsl/newran/-/archive/%{ver_newran}/newran-%{ver_newran}.tar.gz#/fsl-newran-%{ver_newran}.tar.gz
Source5:        https://git.fmrib.ox.ac.uk/fsl/newnifti/-/archive/%{ver_newnifti}/newnifti-%{ver_newnifti}.tar.gz#/fsl-newnifti-%{ver_newnifti}.tar.gz
Source6:        https://git.fmrib.ox.ac.uk/fsl/utils/-/archive/%{ver_utils}/utils-%{ver_utils}.tar.gz#/fsl-utils-%{ver_utils}.tar.gz
Source7:        https://git.fmrib.ox.ac.uk/fsl/miscmaths/-/archive/%{ver_miscmaths}/miscmaths-%{ver_miscmaths}.tar.gz#/fsl-miscmaths-%{ver_miscmaths}.tar.gz
Source8:        https://git.fmrib.ox.ac.uk/fsl/newimage/-/archive/%{ver_newimage}/newimage-%{ver_newimage}.tar.gz#/fsl-newimage-%{ver_newimage}.tar.gz
Source9:        https://git.fmrib.ox.ac.uk/fsl/meshclass/-/archive/%{ver_meshclass}/meshclass-%{ver_meshclass}.tar.gz#/fsl-meshclass-%{ver_meshclass}.tar.gz
Source10:       fsl-profile.sh
Source11:       fsl-profile.csh
Source12:       fsl-ld.so.conf
Source13:       https://git.fmrib.ox.ac.uk/fsl/basisfield/-/archive/%{ver_basisfield}/basisfield-%{ver_basisfield}.tar.gz#/fsl-basisfield-%{ver_basisfield}.tar.gz
Source14:       https://git.fmrib.ox.ac.uk/fsl/warpfns/-/archive/%{ver_warpfns}/warpfns-%{ver_warpfns}.tar.gz#/fsl-warpfns-%{ver_warpfns}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
# znzlib does #include "zlib.h" (classic zlib API); on Fedora that header and
# pkgconfig(zlib) come from the zlib-ng *compat* devel package, not zlib-ng-devel.
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  blas-devel
BuildRequires:  lapack-devel

Requires:       fsl-base = %{version}-%{release}
Requires:       fsl-libs = %{version}-%{release}

%description
The FMRIB Software Library (FSL) is a comprehensive library of analysis
tools for FMRI, MRI and diffusion brain imaging data.

This metapackage pulls in the FSL core: the build-system/runtime environment
(fsl-base) and the shared libraries (fsl-libs). It also installs the system
environment (profile.d and ld.so.conf.d entries) so that $FSLDIR is set and
the FSL libraries are visible to the dynamic linker.

%package base
Summary:        FSL build system, configuration and runtime environment
BuildArch:      noarch
Provides:       bundled(fsl-base) = %{ver_base}

%description base
The FSL Makefile build system (FSLCONFDIR), the fslconf environment scripts
and supporting configuration. Required to build and run all other FSL
components.

%package libs
Summary:        FSL core shared libraries
Requires:       fsl-base = %{version}-%{release}
Provides:       bundled(fsl-armawrap) = %{ver_armawrap}
Provides:       bundled(fsl-znzlib) = %{ver_znzlib}
Provides:       bundled(fsl-cprob) = %{ver_cprob}
Provides:       bundled(fsl-newran) = %{ver_newran}
Provides:       bundled(fsl-newnifti) = %{ver_newnifti}
Provides:       bundled(fsl-utils) = %{ver_utils}
Provides:       bundled(fsl-miscmaths) = %{ver_miscmaths}
Provides:       bundled(fsl-newimage) = %{ver_newimage}
Provides:       bundled(fsl-meshclass) = %{ver_meshclass}
Provides:       bundled(fsl-basisfield) = %{ver_basisfield}
Provides:       bundled(fsl-warpfns) = %{ver_warpfns}

%description libs
The core FSL shared libraries that nearly every FSL tool links against:
znz, NewNifti, cprob, newran, utils, miscmaths, newimage, meshclass,
basisfield and warpfns (the spline/warp-field registration libraries).

%package libs-devel
Summary:        Headers for the FSL core libraries
Requires:       fsl-libs = %{version}-%{release}
Requires:       blas-devel
Requires:       lapack-devel
Requires:       zlib-ng-compat-devel

%description libs-devel
Header files (including the bundled armawrap/Armadillo headers) needed to
compile FSL components against the core libraries.

%prep
# Heterogeneous archive top-dirs; normalise everything to fsl-<module>/.
setup_mod() {
    topdir=$(tar tf "$1" | head -1 | cut -d/ -f1)
    tar xf "$1"
    mv "$topdir" "fsl-$2"
}
rm -rf %{_builddir}/%{name}-%{version}
mkdir -p %{_builddir}/%{name}-%{version}
cd %{_builddir}/%{name}-%{version}
setup_mod %{SOURCE0} base
setup_mod %{SOURCE1} armawrap
setup_mod %{SOURCE2} znzlib
setup_mod %{SOURCE3} cprob
setup_mod %{SOURCE4} newran
setup_mod %{SOURCE5} newnifti
setup_mod %{SOURCE6} utils
setup_mod %{SOURCE7} miscmaths
setup_mod %{SOURCE8} newimage
setup_mod %{SOURCE9} meshclass
setup_mod %{SOURCE13} basisfield
setup_mod %{SOURCE14} warpfns

%build
cd %{_builddir}/%{name}-%{version}

# Stage into a private $FSLDIR so inter-module builds resolve headers/libs
# via FSL's own -isystem $FSLDIR/include / -L $FSLDIR/lib (no rpath embedded).
export FSLDIR=%{_builddir}/%{name}-%{version}/_stage
export FSLDEVDIR="${FSLDIR}"
export FSLCONFDIR="${FSLDIR}/config"
mkdir -p "${FSLDIR}"

# Seed the build system from fsl-base (skip its pip/python install, which the
# C++ core does not need).
mkdir -p "${FSLDIR}/config" "${FSLDIR}/etc/fslconf"
cp -a fsl-base/config/*               "${FSLDIR}/config/"
cp -a fsl-base/etc/fslconf/*          "${FSLDIR}/etc/fslconf/"
install -m 0644 fsl-base/LICENCE.FSL  "${FSLDIR}/LICENCE.FSL"
# fslconf scripts read $FSLDIR/etc/fslversion; provide it (also useful at runtime).
echo "%{version}" > "${FSLDIR}/etc/fslversion"

# Pass Fedora's hardening/optflags through FSL's flag machinery (it appends
# its own ARCH* flags after these).
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{?build_ldflags}"

# Build the libraries in dependency order. armawrap is header-only.
# meshclass links newimage/miscmaths/NewNifti/cprob/utils/znz; basisfield links
# miscmaths/newimage/utils; warpfns links basisfield/meshclass/newimage/... so
# the registration libraries come after the leaf libraries they depend on.
for mod in znzlib cprob newran armawrap newnifti utils miscmaths newimage meshclass basisfield warpfns; do
    echo "=== building fsl-${mod} ==="
    make -C "fsl-${mod}" %{?_smp_mflags}
    make -C "fsl-${mod}" install
done

%install
ST=%{_builddir}/%{name}-%{version}/_stage

# Relocatable FSL tree under %{fsldir}
mkdir -p %{buildroot}%{fsldir}
cp -a "${ST}/config"        %{buildroot}%{fsldir}/
cp -a "${ST}/etc"           %{buildroot}%{fsldir}/
cp -a "${ST}/include"       %{buildroot}%{fsldir}/
cp -a "${ST}/lib"           %{buildroot}%{fsldir}/
install -m 0644 "${ST}/LICENCE.FSL" %{buildroot}%{fsldir}/LICENCE.FSL

# FSL embeds an rpath of '$ORIGIN:<build-stage>/lib'. Drop the absolute
# build-stage component, keeping only $ORIGIN so the libraries locate their
# siblings relative to their own install dir (%{fsldir}/lib) after relocation.
for so in %{buildroot}%{fsldir}/lib/*.so; do
    chrpath -r '$ORIGIN' "$so"
    # FSL's makefiles install a couple of libraries 0644; normalise every
    # shared object to 0755 (rpmlint: shared-library-not-executable).
    chmod 0755 "$so"
done

# System integration: env + dynamic linker path
install -D -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/profile.d/fsl.sh
install -D -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/profile.d/fsl.csh
install -D -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/ld.so.conf.d/fsl.conf

%check
# Core libraries present and dynamically sound.
test -e %{buildroot}%{fsldir}/lib/libfsl-newimage.so
test -e %{buildroot}%{fsldir}/lib/libfsl-miscmaths.so
test -e %{buildroot}%{fsldir}/lib/libfsl-meshclass.so
test -e %{buildroot}%{fsldir}/lib/libfsl-basisfield.so
test -e %{buildroot}%{fsldir}/lib/libfsl-warpfns.so
test -e %{buildroot}%{fsldir}/include/newimage/newimageall.h
test -e %{buildroot}%{fsldir}/include/meshclass/meshclass.h

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%license %{fsldir}/LICENCE.FSL
%{_sysconfdir}/profile.d/fsl.sh
%{_sysconfdir}/profile.d/fsl.csh
%{_sysconfdir}/ld.so.conf.d/fsl.conf

%files base
%dir %{fsldir}
%{fsldir}/config
%{fsldir}/etc

%files libs
%{fsldir}/lib

%files libs-devel
%{fsldir}/include

%changelog
* Mon Jun 08 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.7.18-4
- Strip the leaked build-stage rpath with chrpath instead of patchelf (keeps
  the $ORIGIN runpath; chrpath is already in the buildroot tooling set)
- chmod 0755 every libfsl-*.so (FSL installs warpfns/znz 0644), clearing the
  rpmlint shared-library-not-executable errors

* Mon Jun 08 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.7.18-3
- Add the registration libraries fsl-basisfield (2203.4) and fsl-warpfns
  (2501.0) to fsl-libs: libfsl-basisfield.so / libfsl-warpfns.so + headers,
  needed by flirt (and fnirt, fugue and other registration/warp tools)

* Mon Jun 08 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.7.18-2
- Add fsl-meshclass (2111.0) to the core libraries: libfsl-meshclass.so +
  headers are needed by bet2 and other tools layered on the foundation
  (drawmesh/selfintersection mesh utilities are not installed)

* Sun Jun 07 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.7.18-1
- Initial FSL foundation package: fsl-base build system + 6 core libraries
- Relocatable $FSLDIR=/usr/lib/fsl with profile.d and ld.so.conf.d integration
  (parallels the /usr/lib/freesurfer layout for a merged neuro stack)
- Builds modules in dependency order via FSL's own make system; no conda
