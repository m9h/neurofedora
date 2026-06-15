%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-tbss
Version:        2111.2
Release:        1%{?dist}
Summary:        FSL TBSS - Tract-Based Spatial Statistics

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS
Source0:        https://git.fmrib.ox.ac.uk/fsl/tbss/-/archive/%{version}/tbss-%{version}.tar.gz#/fsl-tbss-%{version}.tar.gz

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
# The tbss_* pipeline scripts orchestrate these FSL tools.
Requires:       fsl-flirt
Requires:       fsl-fnirt
Requires:       fsl-avwutils
Requires:       fsl-randomise

%description
TBSS (Tract-Based Spatial Statistics) projects every subject's diffusion FA
(or other) data onto a mean FA white-matter skeleton, enabling voxelwise
cross-subject statistics on the skeleton. Ships the tbss_skeleton binary, the
swap utilities and the full tbss_1..4 / fsl_reg pipeline scripts. Part of the
FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n tbss-%{version}

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
find %{buildroot}%{fsldir}/bin -xtype l -delete
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/tbss_skeleton
test -f %{buildroot}%{fsldir}/bin/tbss_1_preproc

%files
%{fsldir}/bin/tbss_skeleton
%{fsldir}/bin/swap_voxelwise
%{fsldir}/bin/swap_subjectwise
%{fsldir}/bin/tbss_1_preproc
%{fsldir}/bin/tbss_2_reg
%{fsldir}/bin/tbss_3_postreg
%{fsldir}/bin/tbss_4_prestats
%{fsldir}/bin/fsl_reg
%{fsldir}/bin/tbss_non_FA
%{fsldir}/bin/tbss_fill
%{fsldir}/bin/tbss_deproject
%{fsldir}/bin/tbss_sym
%{fsldir}/bin/tbss_x

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.2-1
- Initial package: TBSS Tract-Based Spatial Statistics (tbss_skeleton + swap
  utilities + tbss_1..4/fsl_reg scripts), on the fsl foundation; Requires
  flirt/fnirt/avwutils/randomise.
