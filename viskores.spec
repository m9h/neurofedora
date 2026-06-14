%global _lto_cflags %{nil}
%define debug_package %{nil}
%global _smp_mflags -j8

Name:           viskores
Version:        1.1.1
Release:        1%{?dist}
Summary:        Toolkit of scientific visualization algorithms for emerging processor architectures

License:        BSD-3-Clause
URL:            https://github.com/Viskores/viskores
Source0:        https://github.com/Viskores/viskores/archive/refs/tags/v%{version}.tar.gz#/viskores-v%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath

# Viskores can use OpenMP for parallelism on host CPUs — cheap win, no extra
# runtime deps beyond libgomp. CUDA/Kokkos/TBB are intentionally disabled
# (deferred to dedicated subpackages if a consumer ever needs them).

%description
Viskores (formerly VTK-m) is a toolkit of scientific visualization
algorithms designed for emerging processor architectures with many
integrated cores. It offers a unified data and execution model for
algorithms that can be portably accelerated on multi-core CPUs and GPUs.

This COPR build is configured to interoperate with VTK 9.6+: it uses
VTK-compatible default types (`Viskores_USE_DEFAULT_TYPES_FOR_VTK=ON`)
and matches the build flags VTK's internal-bundled Viskores uses. Once
this package is installed, VTK can be rebuilt with
`-DVTK_MODULE_USE_EXTERNAL_vtkviskores=ON` to drop the bundled copy.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake

%description devel
Headers and cmake configuration for building applications against Viskores.

%prep
%autosetup -p1 -n viskores-%{version}

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DViskores_BUILD_ALL_LIBRARIES:BOOL=ON \
    `# VTK compatibility — match the flags VTK 9.6.2's bundled build sets in` \
    `# ThirdParty/viskores/vtkviskores/CMakeLists.txt so a downstream` \
    `# find_package(Viskores) from VTK produces a compatible binding.` \
    -DViskores_USE_DEFAULT_TYPES_FOR_VTK:BOOL=ON \
    -DViskores_USE_DEFAULT_SYMBOL_VISIBILITY:BOOL=OFF \
    -DViskores_USE_DOUBLE_PRECISION:BOOL=OFF \
    -DViskores_USE_64BIT_IDS:BOOL=ON \
    -DViskores_ADD_XGC_TO_DEFAULT_TYPES_VTK:BOOL=OFF \
    -DViskores_USE_DEFAULT_TYPES_FOR_ASCENT:BOOL=OFF \
    -DViskores_ENABLE_LOGGING:BOOL=ON \
    -DViskores_ENABLE_RENDERING:BOOL=OFF \
    -DViskores_ENABLE_TESTING_LIBRARY:BOOL=ON \
    -DViskores_ENABLE_HDF5_IO:BOOL=OFF \
    -DViskores_ENABLE_OPENMP:BOOL=ON \
    -DViskores_ENABLE_TBB:BOOL=OFF \
    -DViskores_ENABLE_CUDA:BOOL=OFF \
    -DViskores_ENABLE_KOKKOS:BOOL=OFF \
    -DViskores_ENABLE_MPI:BOOL=OFF \
    -DViskores_ENABLE_DOCUMENTATION:BOOL=OFF \
    -DViskores_ENABLE_EXAMPLES:BOOL=OFF \
    -DViskores_ENABLE_TUTORIALS:BOOL=OFF \
    -DViskores_ENABLE_TESTING:BOOL=OFF \
    -DViskores_ENABLE_BENCHMARKS:BOOL=OFF \
    -DViskores_ENABLE_CPACK:BOOL=OFF \
    -DViskores_NO_ASSERT:BOOL=OFF \
    -DViskores_INSTALL_LIB_DIR:PATH=%{_lib} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install

# Strip any residual build-tree RPATHs from installed libraries.
find %{buildroot}%{_libdir} -name 'libviskores*.so*' -exec chrpath --delete {} \; 2>/dev/null || true

%ldconfig_scriptlets

%files
%license LICENSE.txt
%doc README.md
%{_libdir}/libviskores*.so.*
%{_datadir}/viskores-1.1/

%files devel
%{_includedir}/viskores-1.1/
%{_libdir}/libviskores*.so
%{_libdir}/cmake/viskores-1.1/
%{_libdir}/pkgconfig/viskores.pc

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.1-1
- Update to 1.1.1 (current upstream; freshness sweep 2026-06-14)

* Tue Jun  2 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.0-3
- Flip Viskores_USE_64BIT_IDS:BOOL=ON to match VTK 9.6.2's default
  (VTK_USE_64BIT_IDS=ON by upstream default). vtk -11 build 10533571
  failed at compile with `#error VTK was defined with 64-bit ids but
  Viskores with 32-bit ids` because viskores -2 was built with 32-bit.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.0-2
- Add %%{_libdir}/pkgconfig/viskores.pc to %%files devel. Build 10528870
  compiled cleanly (69 min) but failed the unpackaged-files check.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.0-1
- Initial standalone packaging of upstream Viskores 1.1.0 for the
  neurofedora COPR. Matches the build flags VTK 9.6.2's internal-bundled
  copy uses (Viskores_USE_DEFAULT_TYPES_FOR_VTK=ON,
  Viskores_USE_DEFAULT_SYMBOL_VISIBILITY=OFF, etc.) so that VTK can be
  rebuilt with -DVTK_MODULE_USE_EXTERNAL_vtkviskores=ON and drop its
  Provides: bundled(viskores).
- OpenMP enabled; CUDA/Kokkos/TBB/MPI/Rendering disabled (deferred —
  separate subpackages if a future consumer needs them, mirroring
  vtk-mpi for MPI variants).
