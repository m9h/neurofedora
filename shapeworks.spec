# ShapeWorks is statically linked (huge unstripped binaries); debuginfo is not useful
%global debug_package %{nil}

# Bundled / vendored components (pinned commits)
%global gc_commit       8b20898f6c7be1eab827a9f720c8fd45e58ae63c
%global gc_short        8b20898
%global happly_commit   88f79725d32d78e0e637ebf42d8432d519e1c7d0
%global happly_short    88f7972
%global libigl_version  2.3.0
%global eigen_version   3.4.0

# ITK ships its bundled Eigen (itkeigen) here and force-injects it into every
# ITK-including translation unit; ShapeWorks must use that exact Eigen.
%global itkeigen_dir    %{_includedir}/ITK-5.4/itkeigen

Name:           shapeworks
Version:        6.7.0
Release:        1%{?dist}
Summary:        Statistical shape modeling: particle-based correspondence and PCA

# ShapeWorks core: MIT. Bundled: geometry-central (MIT), happly (MIT),
# libigl core (MPL-2.0) + its copyleft helpers (GPL-3.0-or-later), Eigen (MPL-2.0,
# compiled in), and in-tree ExternalLibs (trimesh2, tinyxml, robin_hood, optparse,
# ordered_map - BSD/MIT/Zlib).
License:        MIT AND MPL-2.0 AND GPL-3.0-or-later AND BSD-3-Clause AND Zlib
URL:            https://shapeworks.sci.utah.edu/
Source0:        https://github.com/SCIInstitute/ShapeWorks/archive/v%{version}/ShapeWorks-%{version}.tar.gz
# geometry-central pinned commit (ShapeWorks' FindGEOMETRYCENTRAL expects this old API)
Source1:        https://github.com/nmwsharp/geometry-central/archive/%{gc_commit}/geometry-central-%{gc_short}.tar.gz
# happly is a geometry-central git submodule, absent from the archive
Source2:        https://github.com/nmwsharp/happly/archive/%{happly_commit}/happly-%{happly_short}.tar.gz
# Eigen 3.4.0: built/staged for geometry-central, and supplies <unsupported/Eigen>
Source3:        https://gitlab.com/libeigen/eigen/-/archive/%{eigen_version}/eigen-%{eigen_version}.tar.gz
# libigl 2.3.0: bundled full source tree (ShapeWorks' FindLIBIGL needs its cmake module)
Source4:        https://github.com/libigl/libigl/archive/refs/tags/v%{libigl_version}/libigl-%{libigl_version}.tar.gz

# Use system libraries; disable Studio GUI (needs out-of-tree patched JKQTPlotter
# Qt5 fork); relax the Python 3.12 EXACT pin and move it after project(); skip the
# git-lfs sentinel; add geometry-central include dir globally. See patch comments.
Patch0:         shapeworks-cmake-system-libs.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  python3-devel
BuildRequires:  pybind11-devel
# Core ShapeWorks dependencies
BuildRequires:  InsightToolkit5-devel
BuildRequires:  InsightToolkit5-vtk-devel
BuildRequires:  vtk-devel
BuildRequires:  openvdb-devel
BuildRequires:  blosc-devel
BuildRequires:  imath-devel
BuildRequires:  tbb-devel
BuildRequires:  acvd-devel
BuildRequires:  xlnt-devel
BuildRequires:  boost-devel
BuildRequires:  json-devel
BuildRequires:  spdlog-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  libomp-devel
BuildRequires:  libminc-devel
# VTK find_package() transitively resolves these at configure time
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  hdf5-devel
BuildRequires:  double-conversion-devel
BuildRequires:  expat-devel
BuildRequires:  glew-devel
BuildRequires:  lz4-devel
BuildRequires:  libxml2-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libX11-devel
BuildRequires:  libXt-devel
BuildRequires:  libtheora-devel
BuildRequires:  libogg-devel
BuildRequires:  proj-devel
BuildRequires:  gdal-devel
BuildRequires:  netcdf-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  cli11-devel
BuildRequires:  viskores-devel
BuildRequires:  gl2ps-devel
BuildRequires:  gdcm-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel

# Vendored components compiled into the binaries
Provides:       bundled(geometry-central) = 0^git%{gc_short}
Provides:       bundled(happly) = 0^git%{happly_short}
Provides:       bundled(libigl) = %{libigl_version}
Provides:       bundled(eigen3) = %{eigen_version}
Provides:       bundled(trimesh2)
Provides:       bundled(tinyxml)
Provides:       bundled(robin_hood)

%description
ShapeWorks (SCI Institute, University of Utah) is a statistical shape modeling
toolkit. It builds compact statistical models of anatomical shape populations
using a particle-based optimization that places dense, corresponding landmarks
across a cohort, then performs population-level PCA. It is widely used for
subcortical shape analysis (complementing FSL FIRST), morphometrics, and
shape-based hypothesis testing.

This package provides the command-line tools and the Python API. The Qt Studio
GUI is not built (it depends on an out-of-tree patched Qt5 plotting library).

%package -n python3-shapeworks
Summary:        Python API for ShapeWorks
%{?python_provide:%python_provide python3-shapeworks}
Requires:       %{name} = %{version}-%{release}

%description -n python3-shapeworks
The shapeworks_py Python module exposing the ShapeWorks Image, Mesh, Optimize,
Groom and Analyze APIs for scripting shape-modeling pipelines.

%package devel
Summary:        Development headers and CMake config for ShapeWorks
Requires:       %{name} = %{version}-%{release}

%description devel
C++ headers and CMake package configuration for building against ShapeWorks.

%prep
%setup -q -n ShapeWorks-%{version}
%patch -P0 -p1

# --- Vendored source trees (kept out of the ShapeWorks source dir proper) ---
mkdir -p _vendor
# Eigen 3.4.0
tar -xzf %{SOURCE3} -C _vendor
# geometry-central (pinned commit) + its happly submodule
tar -xzf %{SOURCE1} -C _vendor
tar -xzf %{SOURCE2} -C _vendor
# place happly into geometry-central's deps/happly (submodule, absent from archive)
cp -a _vendor/happly-%{happly_commit}/. _vendor/geometry-central-%{gc_commit}/deps/happly/
# libigl 2.3.0 full source tree, laid out as FindLIBIGL expects: <dir>/libigl/...
mkdir -p _vendor/libigl-root/libigl
tar -xzf %{SOURCE4} -C _vendor/libigl-root/libigl --strip-components=1

# --- GCC15 fix: ShapeworksUtils.cpp uses unqualified cout/endl ---
sed -i '108s/cout/std::cout/; 108s/endl/std::endl/' Libs/Common/ShapeworksUtils.cpp

# --- Qt5 linkage: with Studio off, the Qt5 link dependency does not propagate to
#     the CLI exe or the Python module. Link Qt5 by plain library name (-lQt5*),
#     NOT the imported targets, to avoid a QT_MAJOR_VERSION clash with VTK's Qt6. ---
sed -i 's/^  pybind11::embed Project Image Groom Analyze Application/  pybind11::embed Project Image Groom Analyze Application\n  Qt5Widgets Qt5Gui Qt5Core/' \
    Applications/shapeworks/CMakeLists.txt
sed -i 's/^  ${DTAG_EXTRA_FLAGS}/  Qt5Widgets Qt5Gui Qt5Core\n  ${DTAG_EXTRA_FLAGS}/' \
    Libs/Python/CMakeLists.txt

# --- Bundled libigl vs ITK's Eigen (3.4.90, which removed DynamicSparseMatrix/
#     MappedSparseMatrix). libigl 2.3.0 targets stock Eigen <=3.4.0. ---
pushd _vendor/libigl-root/libigl/include/igl >/dev/null
# 1) the removed deprecated class -> modern SparseMatrix (reserve/coeffRef/convert)
for f in cat.cpp diag.cpp slice_into.cpp; do
    sed -i 's/DynamicSparseMatrix/SparseMatrix/g' "$f"
done
# 2) the <unsupported/Eigen/SparseExtra> umbrella drags in those removed classes;
#    none of these files use any SparseExtra-only feature, so use <Eigen/Sparse>
for f in cat.cpp cotmatrix.cpp diag.cpp min_quad_with_fixed.cpp slice_into.cpp \
         vector_area_matrix.cpp min_quad_with_fixed.h; do
    sed -i 's|#include *<unsupported/Eigen/SparseExtra>|#include <Eigen/Sparse>|' "$f"
done
popd >/dev/null

%build
vendor="$(pwd)/_vendor"

# (1) Stage stock Eigen 3.4.0 (header-only): provides Eigen3Config + unsupported/
%__cmake -S _vendor/eigen-%{eigen_version} -B _vendor/eigen-build \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_INSTALL_PREFIX=${vendor}/eigen-stage >/dev/null
%__cmake --install _vendor/eigen-build >/dev/null

# (2) Build geometry-central as a -fPIC static lib against stock Eigen 3.4.0
#     (the Python module is a shared object, so its static deps must be PIC).
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fPIC"
%__cmake -S _vendor/geometry-central-%{gc_commit} -B _vendor/gc-build -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DEigen3_DIR=${vendor}/eigen-stage/share/eigen3/cmake
%__cmake --build _vendor/gc-build --target geometry-central %{?_smp_mflags}
# stage geometry-central (no install rules at this commit)
mkdir -p _vendor/gc-stage/lib _vendor/gc-stage/include
cp _vendor/gc-build/src/libgeometry-central.a _vendor/gc-stage/lib/
cp -a _vendor/geometry-central-%{gc_commit}/include/geometrycentral _vendor/gc-stage/include/
cp _vendor/geometry-central-%{gc_commit}/deps/happly/happly.h _vendor/gc-stage/include/
cp -a _vendor/geometry-central-%{gc_commit}/deps/nanoflann/include/nanoflann _vendor/gc-stage/include/
cp -a _vendor/geometry-central-%{gc_commit}/deps/nanort/include/nanort _vendor/gc-stage/include/ 2>/dev/null || :

# (3) Eigen3 config shim: primary = ITK's itkeigen (3.4.90, matches ITK in every
#     ITK-including TU); stock 3.4.0 appended only to satisfy <unsupported/Eigen/...>.
mkdir -p _vendor/eigen-itk
cat > _vendor/eigen-itk/Eigen3Config.cmake <<EOF
set(EIGEN3_VERSION_STRING "3.4.90")
set(_itkeigen "%{itkeigen_dir}")
set(_eigen_unsupported "${vendor}/eigen-stage/include/eigen3")
set(EIGEN3_INCLUDE_DIR "\${_itkeigen}")
set(EIGEN3_INCLUDE_DIRS "\${_itkeigen};\${_eigen_unsupported}")
set(EIGEN3_ROOT_DIR "\${_itkeigen}")
if(NOT TARGET Eigen3::Eigen)
  add_library(Eigen3::Eigen INTERFACE IMPORTED)
  set_target_properties(Eigen3::Eigen PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "\${EIGEN3_INCLUDE_DIRS}")
endif()
set(Eigen3_FOUND TRUE)
EOF
cat > _vendor/eigen-itk/Eigen3ConfigVersion.cmake <<'EOF'
set(PACKAGE_VERSION "3.4.90")
if(PACKAGE_VERSION VERSION_LESS PACKAGE_FIND_VERSION)
  set(PACKAGE_VERSION_COMPATIBLE FALSE)
else()
  set(PACKAGE_VERSION_COMPATIBLE TRUE)
  if(PACKAGE_VERSION VERSION_EQUAL PACKAGE_FIND_VERSION)
    set(PACKAGE_VERSION_EXACT TRUE)
  endif()
endif()
EOF

# (4) Configure and build ShapeWorks (CLI + Python), all system libraries.
export GEOMETRYCENTRAL_DIR=${vendor}/gc-stage
export LIBIGL_DIR=${vendor}/libigl-root
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -include cassert -fPIC"
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DBUILD_STUDIO=OFF \
    -DBUILD_TESTS=OFF \
    -DBUILD_DOCUMENTATION=OFF \
    -DUSE_OPENMP=ON \
    -DITK_DIR=%{_libdir}/cmake/ITK-5.4 \
    -DVTK_DIR=%{_libdir}/cmake/vtk \
    -DOpenVDB_DIR=%{_libdir}/cmake/OpenVDB \
    -DEigen3_DIR=${vendor}/eigen-itk
%cmake_build

%install
%cmake_install

# Relocate the Python module out of %{_bindir} into the Python sitearch
mkdir -p %{buildroot}%{python3_sitearch}
mv %{buildroot}%{_bindir}/shapeworks_py*.so %{buildroot}%{python3_sitearch}/

# Strip any leftover RPATHs for Fedora compliance
chrpath --delete %{buildroot}%{_bindir}/shapeworks 2>/dev/null || :
chrpath --delete %{buildroot}%{python3_sitearch}/shapeworks_py*.so 2>/dev/null || :

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/shapeworks

%files -n python3-shapeworks
%license LICENSE.txt
%{python3_sitearch}/shapeworks_py*.so

%files devel
%{_includedir}/*
# ShapeWorks hardcodes CMAKE_INSTALL_LIBDIR=lib, so its libs/config land in /usr/lib
%{_prefix}/lib/*.a
%{_prefix}/lib/cmake/ShapeWorks/

%changelog
* Thu Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 6.7.0-1
- Initial package: ShapeWorks 6.7.0 CLI + Python API, no superbuild, all system
  libraries. Studio GUI disabled (out-of-tree patched JKQTPlotter Qt5 fork).
- Bundles geometry-central (pinned commit), happly, libigl 2.3.0 and Eigen 3.4.0;
  patches bundled libigl for Eigen >=3.4.90 (ITK's itkeigen removed
  DynamicSparseMatrix/MappedSparseMatrix).
