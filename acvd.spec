Name:           acvd
Version:        4.0
Release:        1%{?dist}
Summary:        Fast simplification and remeshing of 3D surface meshes (VTK-based)

# CeCILL-B is a permissive BSD-like French free-software license (Fedora-allowed).
License:        CECILL-B
URL:            https://github.com/valette/ACVD
Source0:        %{url}/archive/refs/tags/v%{version}/ACVD-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  chrpath
BuildRequires:  vtk-devel
# IOMINC component requested by ACVD's find_package(VTK)
BuildRequires:  libminc-devel
# OpenMP (optional acceleration in the remeshing examples; harmless for the libs)
BuildRequires:  libomp-devel
# VTK cmake config resolves all module deps at find_package time
BuildRequires:  hdf5-devel json-devel jsoncpp-devel utf8cpp-devel fmt-devel
BuildRequires:  freetype-devel pugixml-devel PEGTL-devel libglvnd-devel
BuildRequires:  libtheora-devel libogg-devel libjpeg-turbo-devel libpng-devel
BuildRequires:  libtiff-devel fontconfig-devel expat-devel lz4-devel xz-devel
BuildRequires:  zlib-devel sqlite-devel libxml2-devel netcdf-devel proj-devel
BuildRequires:  tbb-devel libharu-devel gl2ps-devel double-conversion-devel
BuildRequires:  gdal-devel libpq-devel libX11-devel libXt-devel libGL-devel
BuildRequires:  cli11-devel boost-devel

%description
ACVD provides fast, high-quality simplification and isotropic/anisotropic
remeshing of 3D triangular surface meshes, based on Approximated Centroidal
Voronoi Diagrams (Valette et al.). It is built on top of VTK and provides the
vtkSurface and vtkVolumeProcessing shared libraries plus a header-only discrete
remeshing module, used by statistical-shape-modeling pipelines (e.g. ShapeWorks)
for surface correspondence preprocessing.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vtk-devel

%description    devel
Headers and CMake package configuration for developing against %{name}
(ACVD: vtkSurface, vtkDiscreteRemeshing, vtkVolumeProcessing).

%prep
%autosetup -n ACVD-%{version}

%build
# ACVD's sources use unqualified cout/cin/cerr/endl with neither <iostream> nor
# `using namespace std` — they relied on transitive availability that newer VTK
# headers / GCC 15 no longer provide. Force-include a small prelude that supplies
# both, restoring the environment the code was written for.
cat > _acvd_prelude.h <<'EOF'
#include <iostream>
using namespace std;
EOF
export CXXFLAGS="%{optflags} -include $PWD/_acvd_prelude.h"

# Library-only build: the bundled Examples produce many generically-named CLI
# binaries (viewer, icp, sampleMesh, ...) that would collide in %{_bindir};
# downstreams (ShapeWorks) need only the libraries + headers + cmake config.
# ACVD uses its own INSTALL_*_DIR vars (not CMAKE_INSTALL_LIBDIR), so set lib64.
%cmake -GNinja \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DBUILD_DOCUMENTATION:BOOL=OFF \
    -DINSTALL_LIB_DIR:PATH=%{_lib} \
    -DINSTALL_INCLUDE_DIR:PATH=include \
    -DINSTALL_CMAKE_DIR:PATH=%{_lib}/cmake/ACVD
%cmake_build

%install
%cmake_install
# Drop any build-tree RPATHs.
find %{buildroot} -type f \( -name '*.so' -o -name '*.so.*' \) \
    -exec chrpath --delete {} \; 2>/dev/null || :

%files
%license LICENSE.txt
%doc Readme.md
%{_libdir}/libvtkSurface.so.4.0*
%{_libdir}/libvtkVolumeProcessing.so.4.0*

%files devel
%{_includedir}/ACVD/
%{_libdir}/libvtkSurface.so
%{_libdir}/libvtkVolumeProcessing.so
%{_libdir}/cmake/ACVD/

%changelog
* Wed Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0-1
- Initial package (stock upstream valette/ACVD v4.0). Library-only build
  (BUILD_EXAMPLES=OFF) against system VTK; provides vtkSurface /
  vtkVolumeProcessing / vtkDiscreteRemeshing for the ShapeWorks dependency chain.
