# FSL cluster (cluster-based thresholding / local maxima of statistic images),
# layered on the fsl foundation and built against the installed relocatable
# $FSLDIR=/usr/lib/fsl. Upstream renames the main binary to "fsl-cluster" to
# avoid the system "cluster" (graphviz) name clash.

%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^libfsl-.*\\.so.*$

Name:           fsl-cluster
Version:        2201.0
Release:        1%{?dist}
Summary:        FSL cluster - cluster-based thresholding of statistic images

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Cluster
Source0:        https://git.fmrib.ox.ac.uk/fsl/cluster/-/archive/%{version}/cluster-%{version}.tar.gz#/fsl-cluster-%{version}.tar.gz
# cluster.cc #includes "misc_c/ztop_function.h" (compile-time only — misc_c is
# NOT in cluster's link line). The misc_c module is not shipped by the
# foundation, so provide its headers from the source archive at build time.
Source1:        https://git.fmrib.ox.ac.uk/fsl/misc_c/-/archive/2111.0/misc_c-2111.0.tar.gz#/fsl-misc_c-2111.0.tar.gz

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
The FSL cluster tools find and characterise clusters and local maxima in
statistic images (fsl-cluster), estimate image smoothness for cluster-based
thresholding (smoothest), and label connected components (connectedcomp).
Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n cluster-%{version}
# Unpack misc_c alongside (for its headers only).
tar xzf %{SOURCE1}

%build
export FSLDIR=%{fsldir}
export FSLCONFDIR=%{fsldir}/config
export FSLDEVDIR=%{_builddir}/_stage
mkdir -p "${FSLDEVDIR}"
# Make misc_c's headers resolvable as "misc_c/<hdr>.h" via -I${FSLDEVDIR}/include
# (FSL's build adds that to the include path). misc_c links nothing here.
mkdir -p "${FSLDEVDIR}/include/misc_c"
cp -p misc_c-2111.0/*.h "${FSLDEVDIR}/include/misc_c/"
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
test -x %{buildroot}%{fsldir}/bin/fsl-cluster
test -x %{buildroot}%{fsldir}/bin/smoothest
ldd %{buildroot}%{fsldir}/bin/fsl-cluster | grep -q libfsl-newimage.so

%files
%{fsldir}/bin/fsl-cluster
%{fsldir}/bin/smoothest
%{fsldir}/bin/connectedcomp
%{fsldir}/bin/cluster2html

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2201.0-1
- Initial package: FSL cluster tools (fsl-cluster, smoothest, connectedcomp +
  cluster2html), layered on the fsl foundation.
