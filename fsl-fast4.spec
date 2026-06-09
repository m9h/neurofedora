# FAST (FMRIB's Automated Segmentation Tool) layered on the fsl foundation.
# Built with FSL's own make system against the installed relocatable
# $FSLDIR=/usr/lib/fsl (headers from fsl-libs-devel, link libs from fsl-libs).
# Upstream names the project "fast4"; the installed program is "fast".

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-fast4
Version:        2111.3
Release:        1%{?dist}
Summary:        FSL FAST - automated tissue segmentation tool

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FAST
Source0:        https://git.fmrib.ox.ac.uk/fsl/fast4/-/archive/%{version}/fast4-%{version}.tar.gz#/fsl-fast4-%{version}.tar.gz

# Users know this tool as "fast", not by its upstream project name "fast4".
Provides:       fsl-fast = %{version}-%{release}

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
FAST (FMRIB's Automated Segmentation Tool) segments a 3D image of the brain
into different tissue types (grey matter, white matter, CSF, etc.) while
correcting for the spatial intensity bias field. It is part of the FMRIB
Software Library (FSL).

%prep
%autosetup -p1 -n fast4-%{version}

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

# RUNTCLS=Fast creates Fast/Fast_gui symlinks to Runtcl (shipped by the
# unpackaged GUI helper fsl-misc_tcl); drop the resulting dangling links.
find %{buildroot}%{fsldir}/bin -xtype l -delete

# Reset the leaked build-stage rpath so the program finds the foundation libs
# relative to itself (bin -> ../lib).
chrpath -r '$ORIGIN/../lib' %{buildroot}%{fsldir}/bin/fast

%check
test -x %{buildroot}%{fsldir}/bin/fast
ldd %{buildroot}%{fsldir}/bin/fast | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/fast

%changelog
* Mon Jun 08 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.3-1
- Initial package: FAST tissue segmentation, layered on the fsl foundation
- Built against the installed relocatable $FSLDIR=/usr/lib/fsl via FSL's make
- Drop the Fast/Fast_gui tcl-GUI symlinks (require the unpackaged fsl-misc_tcl)
