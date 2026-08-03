# BLT bundled at build time (build-time-only CMake macros; see other RADIUSS specs).
%global blt_version 0.7.2
# Smith snapshot (pre-alpha; develop as of the pinned commit).
%global commit 292e743bf9ad593aa12df53fb2b7029f09c7bfca
%global shortcommit 292e743b
%global snapdate 20260618
# Bundled submodules that smith only consumes via add_subdirectory (source):
%global gretl_commit d9f26d2b809e8af2d6a57effac39609f2124d566
%global continuation_commit 6917758451a45b5436816ae01da1642776f32c76

# Smith requires MPI (hard FATAL_ERROR without MPI compilers): MPI-only package.
%bcond_without mpich
%bcond_without openmpi

Name:           smith
Version:        0.1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        3D implicit nonlinear thermal-structural finite element simulation code

License:        BSD-3-Clause
URL:            https://github.com/LLNL/smith
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz
# gretl (LLNL solver-state util; name/file-collides with Fedora's econometrics
# gretl, so it is bundled here rather than packaged separately).
Source2:        https://github.com/LLNL/gretl/archive/%{gretl_commit}/gretl-%{gretl_commit}.tar.gz
# ContinuationSolvers (smith only supports it via add_subdirectory).
Source3:        https://github.com/LLNL/ContinuationSolvers/archive/%{continuation_commit}/ContinuationSolvers-%{continuation_commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  metis-devel
BuildRequires:  lua-devel
# camp/umpire/RAJA are MPI-agnostic (serial packages used by every flavor)
BuildRequires:  camp-devel
BuildRequires:  umpire-devel
BuildRequires:  RAJA-devel
%if %{with mpich}
BuildRequires:  mpich-devel
BuildRequires:  conduit-mpich-devel
BuildRequires:  axom-mpich-devel
BuildRequires:  tribol-mpich-devel
BuildRequires:  mfem-mpich-devel
BuildRequires:  hdf5-mpich-devel
BuildRequires:  hypre-mpich-devel
BuildRequires:  STRUMPACK-mpich-devel
BuildRequires:  superlu_dist-mpich-devel
%endif
%if %{with openmpi}
BuildRequires:  openmpi-devel
BuildRequires:  conduit-openmpi-devel
BuildRequires:  axom-openmpi-devel
BuildRequires:  tribol-openmpi-devel
BuildRequires:  mfem-openmpi-devel
BuildRequires:  hdf5-openmpi-devel
BuildRequires:  hypre-openmpi-devel
BuildRequires:  STRUMPACK-openmpi-devel
BuildRequires:  superlu_dist-openmpi-devel
%endif

Provides:       bundled(blt) = %{blt_version}
Provides:       bundled(gretl)
Provides:       bundled(ContinuationSolvers)

%description
Smith is a 3D implicit nonlinear thermal-structural simulation code for
investigating abstraction strategies and implicit finite-element algorithm
development on emerging architectures. It is built on the LLNL RADIUSS stack
(Axom, MFEM, Tribol). This is a pre-alpha release.

%if %{with mpich}
%package mpich
Summary:        MPICH version of %{name}
Requires:       mpich%{?_isa}

%description mpich
This package contains the %{name} libraries and drivers compiled against MPICH.

%package mpich-devel
Summary:        Development files for the MPICH version of %{name}
Requires:       %{name}-mpich%{?_isa} = %{version}-%{release}

%description mpich-devel
This package contains the headers and CMake configuration files for the MPICH
build of %{name}.
%endif

%if %{with openmpi}
%package openmpi
Summary:        OpenMPI version of %{name}
Requires:       openmpi%{?_isa}

%description openmpi
This package contains the %{name} libraries and drivers compiled against OpenMPI.

%package openmpi-devel
Summary:        Development files for the OpenMPI version of %{name}
Requires:       %{name}-openmpi%{?_isa} = %{version}-%{release}

%description openmpi-devel
This package contains the headers and CMake configuration files for the OpenMPI
build of %{name}.
%endif

%prep
%autosetup -n %{name}-%{commit}
tar -xf %{SOURCE1}
# Vendor the gretl and ContinuationSolvers submodules where smith expects them.
# The GitHub archive ships submodule paths as empty placeholder dirs, so remove
# them before moving the real sources in (otherwise mv nests inside them).
rm -rf gretl ContinuationSolvers
tar -xf %{SOURCE2}
mv gretl-%{gretl_commit} gretl
tar -xf %{SOURCE3}
mv ContinuationSolvers-%{continuation_commit} ContinuationSolvers

# Examples and the partitioner tool are added unconditionally upstream
# (ENABLE_EXAMPLES=OFF is not honored). They are the only consumers of the
# smith/physics.hpp umbrella, which pulls in solid_mechanics_contact.hpp;
# that header names smith::StrumpackSolver outside the #ifdef
# MFEM_USE_STRUMPACK guard used everywhere else, and GCC 15's -Wtemplate-body
# rejects it at template definition time. Demo binaries are not shipped.
sed -i '/^add_subdirectory(examples)/d' CMakeLists.txt
sed -i '/^add_subdirectory(tools)/d' src/CMakeLists.txt

%build
OPTIONS=(
    -DBLT_SOURCE_DIR=%{_builddir}/%{name}-%{commit}/blt-%{blt_version}
    -DBLT_CXX_STD=c++20
    -DCAMP_DIR=%{_libdir}/cmake/camp
    -Dcamp_DIR=%{_libdir}/cmake/camp
    -DUMPIRE_DIR=%{_libdir}/cmake/umpire
    -Dumpire_DIR=%{_libdir}/cmake/umpire
    -DRAJA_DIR=%{_libdir}/cmake/raja
    -Dfmt_DIR=%{_libdir}/cmake/fmt
    -DLUA_DIR=%{_prefix}
    -DGRETL_SOURCE_DIR=%{_builddir}/%{name}-%{commit}/gretl
    -DCONTINUATION_SOURCE_DIR=%{_builddir}/%{name}-%{commit}/ContinuationSolvers
    -DCMAKE_SKIP_RPATH=ON
    -DBUILD_SHARED_LIBS=ON
    -DENABLE_TESTS=OFF
    -DENABLE_EXAMPLES=OFF
    -DENABLE_DOCS=OFF
)

%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON \
    -DMPI_C_COMPILER=$MPI_BIN/mpicc -DMPI_CXX_COMPILER=$MPI_BIN/mpicxx \
    -DCONDUIT_DIR=$MPI_HOME -Dconduit_DIR=$MPI_HOME/lib/cmake/conduit \
    -DAXOM_DIR=$MPI_HOME -Daxom_DIR=$MPI_HOME/lib/cmake \
    -DTRIBOL_DIR=$MPI_HOME -DMFEM_DIR=$MPI_HOME -DHDF5_DIR=$MPI_HOME \
    -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_INCLUDE}/hypre" \
    -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_mpich_unload}
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON \
    -DMPI_C_COMPILER=$MPI_BIN/mpicc -DMPI_CXX_COMPILER=$MPI_BIN/mpicxx \
    -DCONDUIT_DIR=$MPI_HOME -Dconduit_DIR=$MPI_HOME/lib/cmake/conduit \
    -DAXOM_DIR=$MPI_HOME -Daxom_DIR=$MPI_HOME/lib/cmake \
    -DTRIBOL_DIR=$MPI_HOME -DMFEM_DIR=$MPI_HOME -DHDF5_DIR=$MPI_HOME \
    -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_INCLUDE}/hypre" \
    -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_openmpi_unload}
%endif

%install
%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake_install
%{_mpich_unload}
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake_install
%{_openmpi_unload}
%endif

%if %{with mpich}
%files mpich
%license LICENSE
# Upstream builds all libraries unversioned (no SOVERSION), so the bare .so
# files are the runtime libraries and belong in the main subpackage.
%{_libdir}/mpich/lib/lib*.so

%files mpich-devel
%{_libdir}/mpich/include/
%{_libdir}/mpich/lib/cmake/
%endif

%if %{with openmpi}
%files openmpi
%license LICENSE
%{_libdir}/openmpi/lib/lib*.so

%files openmpi-devel
%{_libdir}/openmpi/include/
%{_libdir}/openmpi/lib/cmake/
%endif

%changelog
* Fri Jul 03 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-0.1.20260618git292e743b
- Drop upstream examples and the partitioner tool: they fail to build with GCC 15
  (-Wtemplate-body) because solid_mechanics_contact.hpp uses StrumpackSolver
  outside its #ifdef guard. Libraries and headers are unaffected.
- Add STRUMPACK + superlu_dist MPI BuildRequires (mfem contact solver links them)
- Initial package (pre-alpha snapshot; MPI-only; bundles gretl + ContinuationSolvers)
