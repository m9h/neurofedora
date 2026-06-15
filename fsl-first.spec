# FSL FIRST (model-based subcortical segmentation), layered on the fsl
# foundation. Built with FSL's own make system against the installed
# relocatable $FSLDIR=/usr/lib/fsl. Links the foundation's shapeModel,
# first_lib and vtkio libraries (added to fsl-libs at 6.0.7.18-6).
#
# NOTE: the subcortical model files (data/first/models/*.bmv) are a large
# separate FSL data download, NOT shipped here; FIRST needs them at runtime.

%global fsldir          %{_prefix}/lib/fsl
# Depend on fsl-libs for the foundation's unversioned libfsl-*.so (not on
# auto-generated soname Requires).
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-first
Version:        2203.1
Release:        2%{?dist}
Summary:        FSL FIRST - model-based subcortical segmentation

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIRST
Source0:        https://git.fmrib.ox.ac.uk/fsl/first/-/archive/%{version}/first-%{version}.tar.gz#/fsl-first-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
# Foundation 6.0.7.18-6 adds the shapeModel/first_lib/vtkio libraries FIRST links.
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18
# FIRST cannot segment without its shape/appearance models; pull them by
# default but keep the tool installable lean (soft dependency).
Recommends:     fsl-first-data

%description
FIRST is a model-based segmentation/registration tool for the subcortical
structures of the brain (thalamus, caudate, putamen, pallidum, hippocampus,
amygdala, accumbens, brainstem). It ships the first, first_utils and
first_mult_bcorr binaries plus the run_first/run_first_all driver scripts.
Part of the FMRIB Software Library (FSL).

The shape/appearance models FIRST fits are a separate FSL data download and
are not included in this package.

%prep
%autosetup -p1 -n first-%{version}

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

# Drop any dangling tcl-GUI symlinks to the unpackaged fsl-misc_tcl.
find %{buildroot}%{fsldir}/bin -xtype l -delete

# Strip the leaked build-stage rpath; binaries find the foundation libs via
# $ORIGIN/../lib ($FSLDIR/lib).
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/first
test -x %{buildroot}%{fsldir}/bin/first_utils
test -x %{buildroot}%{fsldir}/bin/first_mult_bcorr
# first links the foundation core; assert a stable dependency (newimage).
ldd %{buildroot}%{fsldir}/bin/first | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/first
%{fsldir}/bin/first_utils
%{fsldir}/bin/first_mult_bcorr
%{fsldir}/bin/run_first
%{fsldir}/bin/run_first_all
%{fsldir}/bin/first_flirt
%{fsldir}/bin/concat_bvars
%{fsldir}/bin/first_roi_slicesdir
%{fsldir}/bin/first_boundary_corr
%{fsldir}/bin/surface_fdr
%{fsldir}/bin/first3Dview

%changelog
* Sun Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2203.1-2
- Recommends fsl-first-data (the 336 shape/appearance models FIRST needs at
  runtime); the tool installs lean but dnf pulls the models by default.

* Sun Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2203.1-1
- Initial package: FSL FIRST subcortical segmentation (first, first_utils,
  first_mult_bcorr + run_first/run_first_all scripts), layered on the fsl
  foundation 6.0.7.18-6 which adds the shapeModel/first_lib/vtkio libraries.
