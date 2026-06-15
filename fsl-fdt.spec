%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-fdt
Version:        2202.11
Release:        1%{?dist}
Summary:        FSL FDT - FMRIB's Diffusion Toolbox (dtifit, bedpostx, probtrackx)

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT
Source0:        https://git.fmrib.ox.ac.uk/fsl/fdt/-/archive/%{version}/fdt-%{version}.tar.gz#/fsl-fdt-%{version}.tar.gz

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
# bedpostx/probtrack drivers call other FSL tools at runtime.
Requires:       fsl-avwutils
Requires:       fsl-bet2
Requires:       fsl-flirt

%description
FDT (FMRIB's Diffusion Toolbox) is a suite for analysing diffusion-weighted
MRI: tensor fitting (dtifit), Bayesian estimation of crossing fibres
(bedpostx/xfibres), probabilistic tractography (probtrackx), and supporting
utilities. This is the CPU build (the optional CUDA/GPU variants are not
included). Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n fdt-%{version}

%build
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
mkdir -p "${FSLDEVDIR}"
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{?build_ldflags}"
# Default gpu=0 -> CPU build (no CUDA).
make %{?_smp_mflags}

%install
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
make install
mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/

# Drop the FX/feeds-test helper binaries (not part of the shipped toolbox) and
# any dangling tcl-GUI symlinks.
for f in reord_OM sausages replacevols fdt_matrix_ops indexer rubix basgen; do
    rm -f %{buildroot}%{fsldir}/bin/$f
done
# This is the CPU build: drop the GPU-path helpers that get built/installed
# regardless (the *_gpu binaries are CPU stubs only useful with the CUDA build).
for f in bedpostx_gpu bedpostx_postproc_gpu.sh merge_parts_gpu split_parts_gpu \
         xfibres_gpu; do
    rm -f %{buildroot}%{fsldir}/bin/$f
done
find %{buildroot}%{fsldir}/bin -xtype l -delete

for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/dtifit
test -x %{buildroot}%{fsldir}/bin/xfibres
test -x %{buildroot}%{fsldir}/bin/probtrackx
# (no ldd assertion: -Wl,--as-needed prunes unreferenced NEEDED entries.)

%files
%{fsldir}/bin/dtifit
%{fsldir}/bin/ccops
%{fsldir}/bin/medianfilter
%{fsldir}/bin/make_dyadic_vectors
%{fsldir}/bin/vecreg
%{fsldir}/bin/xfibres
%{fsldir}/bin/probtrackx
%{fsldir}/bin/pvmfit
%{fsldir}/bin/dtigen
%{fsldir}/bin/eddy_combine
%{fsldir}/bin/fdt_rotate_bvecs
%{fsldir}/bin/select_dwi_vols
%{fsldir}/bin/eddy_correct
%{fsldir}/bin/zeropad
%{fsldir}/bin/maskdyads
%{fsldir}/bin/probtrack
%{fsldir}/bin/bedpost
%{fsldir}/bin/bedpostx
%{fsldir}/bin/bedpostx_postproc.sh
%{fsldir}/bin/bedpostx_preproc.sh
%{fsldir}/bin/bedpostx_single_slice.sh
%{fsldir}/bin/bedpostx_datacheck

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2202.11-1
- Initial package: FDT diffusion toolbox CPU build (dtifit, xfibres, bedpostx,
  probtrackx, vecreg + driver scripts), on the fsl foundation. GPU/CUDA variants
  excluded.
