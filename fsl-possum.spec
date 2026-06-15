%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-possum
Version:        2111.3
Release:        1%{?dist}
Summary:        FSL POSSUM - MRI image acquisition simulator

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/POSSUM
Source0:        https://git.fmrib.ox.ac.uk/fsl/possum/-/archive/%{version}/possum-%{version}.tar.gz#/fsl-possum-%{version}.tar.gz

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
# possum_interpmot.py / possum_plot.py are Python helpers.
Requires:       python3

%description
POSSUM (Physics-Oriented Simulated Scanner for Understanding MRI) simulates
realistic MRI image acquisition, including the effects of pulse sequences,
B0 inhomogeneity, motion and noise. Ships the possum/pulse/signal2image core
binaries and the possumX driver scripts. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n possum-%{version}

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
test -x %{buildroot}%{fsldir}/bin/possum
test -x %{buildroot}%{fsldir}/bin/pulse
ldd %{buildroot}%{fsldir}/bin/possum | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/possum
%{fsldir}/bin/spharm_rm
%{fsldir}/bin/signal2image
%{fsldir}/bin/pulse
%{fsldir}/bin/systemnoise
%{fsldir}/bin/possum_sum
%{fsldir}/bin/b0calc
%{fsldir}/bin/possum_matrix
%{fsldir}/bin/tcalc
%{fsldir}/bin/possumX
%{fsldir}/bin/possumX_postproc.sh
%{fsldir}/bin/generate_b0
%{fsldir}/bin/generate_brain
%{fsldir}/bin/generate_b0calc
%{fsldir}/bin/possum_interpmot.py
%{fsldir}/bin/possum_plot.py

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.3-1
- Initial package: POSSUM MRI acquisition simulator (possum/pulse/signal2image
  + possumX scripts), on the fsl foundation.
