# FSL libvis command-line visualisation tools (slicer, overlay, pngappend,
# fsl_tsplot, ...), layered on the fsl foundation. The miscplot/miscpic shared
# libraries these link are shipped by the foundation (fsl-libs, 6.0.7.18-6);
# this package ships only the binaries + the render LUTs.

%global fsldir          %{_prefix}/lib/fsl
# Depend on fsl-libs for the foundation libfsl-*.so / libgdc.so (not on the
# auto-generated soname Requires).
%global __requires_exclude ^(libfsl-.*|libgdc)\\.so.*$

Name:           fsl-libvis
Version:        2111.2
Release:        1%{?dist}
Summary:        FSL command-line visualisation tools (slicer, overlay, pngappend, ...)

License:        LicenseRef-FSL
URL:            https://fsl.fmrib.ox.ac.uk
Source0:        https://git.fmrib.ox.ac.uk/fsl/libvis/-/archive/%{version}/libvis-%{version}.tar.gz#/fsl-libvis-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
# The plotting tools link GDChart (libgdc, in fsl-libs) + system gd/png.
BuildRequires:  gd-devel
BuildRequires:  libpng-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18

%description
The FSL libvis command-line image-visualisation utilities: slicer (snapshot
montages from volumes), overlay (combine statistical overlays with structural
images), pngappend (compose PNGs), wpng, and the fsl_tsplot / fsl_boxplot /
fsl_histogram plotting tools. Part of the FMRIB Software Library (FSL).

The miscplot/miscpic libraries these tools use are provided by the FSL core
(fsl-libs); this package adds the binaries and the rendering colour LUTs.

%prep
%autosetup -p1 -n libvis-%{version}

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

# Ship only the binaries and the render LUTs. The libfsl-miscplot.so /
# libfsl-miscpic.so libraries are owned by the foundation (fsl-libs); do NOT
# repackage them here.
mkdir -p %{buildroot}%{fsldir}/bin
cp -a "${FSLDEVDIR}/bin/." %{buildroot}%{fsldir}/bin/
if [ -d "${FSLDEVDIR}/etc/luts" ]; then
    mkdir -p %{buildroot}%{fsldir}/etc/luts
    cp -a "${FSLDEVDIR}/etc/luts/." %{buildroot}%{fsldir}/etc/luts/
fi

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
test -x %{buildroot}%{fsldir}/bin/slicer
test -x %{buildroot}%{fsldir}/bin/overlay
test -x %{buildroot}%{fsldir}/bin/pngappend
ldd %{buildroot}%{fsldir}/bin/slicer | grep -q libfsl-miscpic.so

%files
%{fsldir}/bin/slicer
%{fsldir}/bin/overlay
%{fsldir}/bin/wpng
%{fsldir}/bin/pngappend
%{fsldir}/bin/fsl_tsplot
%{fsldir}/bin/fsl_boxplot
%{fsldir}/bin/fsl_histogram
%{fsldir}/bin/create_lut
%dir %{fsldir}/etc/luts
%{fsldir}/etc/luts/*

%changelog
* Sun Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.2-1
- Initial package: FSL libvis visualisation tools (slicer, overlay, pngappend,
  wpng, fsl_tsplot, fsl_boxplot, fsl_histogram, create_lut) + render LUTs,
  layered on the fsl foundation. The miscplot/miscpic libraries are provided by
  fsl-libs (foundation 6.0.7.18-6); this package ships only the binaries.
