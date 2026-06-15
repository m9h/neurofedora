%global fsldir          %{_prefix}/lib/fsl
%global __requires_exclude ^(libfsl-.*|libgdc)\\.so.*$

Name:           fsl-mist
Version:        2111.6
Release:        1%{?dist}
Summary:        FSL MIST - Model-based Integration of Shape and Texture (subcortical seg)

License:        LicenseRef-FSL
URL:            https://git.fmrib.ox.ac.uk/fsl/mist
Source0:        https://git.fmrib.ox.ac.uk/fsl/mist/-/archive/%{version}/mist-%{version}.tar.gz#/fsl-mist-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  fsl-base = 6.0.7.18
BuildRequires:  fsl-libs-devel = 6.0.7.18
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  json-devel
# mist links VTK directly, plus boost, nlopt, gd/GDChart (libgdc from fsl-libs),
# libpng and sqlite.
BuildRequires:  vtk-devel
BuildRequires:  boost-devel
BuildRequires:  NLopt-devel
BuildRequires:  gd-devel
BuildRequires:  libpng-devel
BuildRequires:  sqlite-devel

Requires:       fsl-libs = 6.0.7.18
Requires:       fsl-base = 6.0.7.18
# The training/fitting drivers are Python.
Requires:       python3

%description
MIST (Model-based Integration of Shape and Texture) performs subcortical
structure segmentation by jointly modelling shape and image appearance.
Ships the mist engine, the mist_1_train / mist_2_fit driver scripts and the
shape model/mask data. Part of the FMRIB Software Library (FSL).

%prep
%autosetup -p1 -n mist-%{version}

# mist hardcodes VTK 9.3 (VTKSUFFIX=-9.3, -I$FSLDIR/include/vtk-9.3). Fedora
# ships VTK 9.5 with UNsuffixed libnames and headers under %{_includedir}/vtk.
# Clear the suffix and repoint the include path to the system VTK.
sed -i 's/^VTKSUFFIX = -9.3/VTKSUFFIX =/' Makefile
sed -i 's|\${FSLDIR}/include/vtk\${VTKSUFFIX}|%{_includedir}/vtk|' Makefile

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
# Shape-model / mask data.
if [ -d "${FSLDEVDIR}/data/mist" ]; then
    mkdir -p %{buildroot}%{fsldir}/data
    cp -a "${FSLDEVDIR}/data/mist" %{buildroot}%{fsldir}/data/
fi
find %{buildroot}%{fsldir}/bin -xtype l -delete
for exe in %{buildroot}%{fsldir}/bin/*; do
    [ -f "$exe" ] || continue
    if head -c4 "$exe" | grep -q ELF; then
        chrpath -r '$ORIGIN/../lib' "$exe" 2>/dev/null || :
    fi
done

%check
test -x %{buildroot}%{fsldir}/bin/mist

%files
%{fsldir}/bin/mist
%{fsldir}/bin/mist_1_train
%{fsldir}/bin/mist_2_fit
%{fsldir}/bin/mist_FA_reg
%{fsldir}/bin/mist_display
%{fsldir}/bin/mist_mesh_utils
%dir %{fsldir}/data
%{fsldir}/data/mist

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2111.6-1
- Initial package: MIST subcortical shape+texture segmentation, on the fsl
  foundation. Adapt the hardcoded VTK 9.3 build to the system VTK 9.5
  (unsuffixed libs + %{_includedir}/vtk). Links boost/nlopt/gd/sqlite.
