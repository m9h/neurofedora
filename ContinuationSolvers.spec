# BLT bundled at build time (build-time-only CMake macros; see other RADIUSS specs).
%global blt_version 0.7.2
# Snapshot pinned to the commit used by LLNL/smith (no usable upstream release).
%global commit 6917758451a45b5436816ae01da1642776f32c76
%global shortcommit 69177584
%global snapdate 20260211

# ContinuationSolvers forces ENABLE_MPI=ON and links blt::mpi; it is MPI-only,
# so only the -mpich/-openmpi variants are built (no serial library).
%bcond_without mpich
%bcond_without openmpi

Name:           ContinuationSolvers
Version:        0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Homotopy/interior-point continuation solvers for contact mechanics

License:        BSD-3-Clause
URL:            https://github.com/LLNL/ContinuationSolvers
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  metis-devel
%if %{with mpich}
BuildRequires:  mpich-devel
BuildRequires:  mfem-mpich-devel
BuildRequires:  hypre-mpich-devel
%endif
%if %{with openmpi}
BuildRequires:  openmpi-devel
BuildRequires:  mfem-openmpi-devel
BuildRequires:  hypre-openmpi-devel
%endif

Provides:       bundled(blt) = %{blt_version}

%description
ContinuationSolvers provides homotopy and interior-point continuation methods
for nonlinear mixed complementarity / optimization problems arising in contact
mechanics, built on MFEM. It is part of the LLNL Smith dependency stack.

%if %{with mpich}
%package mpich
Summary:        MPICH version of %{name}
Requires:       mpich%{?_isa}

%description mpich
This package contains the %{name} library compiled against MPICH.

%package mpich-devel
Summary:        Development files for the MPICH version of %{name}
Requires:       %{name}-mpich%{?_isa} = %{version}-%{release}
Requires:       mfem-mpich-devel%{?_isa}

%description mpich-devel
This package contains the headers needed to build MPICH applications against
%{name}.
%endif

%if %{with openmpi}
%package openmpi
Summary:        OpenMPI version of %{name}
Requires:       openmpi%{?_isa}

%description openmpi
This package contains the %{name} library compiled against OpenMPI.

%package openmpi-devel
Summary:        Development files for the OpenMPI version of %{name}
Requires:       %{name}-openmpi%{?_isa} = %{version}-%{release}
Requires:       mfem-openmpi-devel%{?_isa}

%description openmpi-devel
This package contains the headers needed to build OpenMPI applications against
%{name}.
%endif

%prep
%autosetup -n %{name}-%{commit}
tar -xf %{SOURCE1}

# Upstream assumes the 'mfem' CMake target is provided by a parent project (its
# FindMFEM include is commented out). Standalone, find MFEM explicitly so its
# headers/targets are available. MFEM_DIR is the MPI install prefix ($MPI_HOME).
sed -i '/set(continuation_sources/i\
if(NOT TARGET mfem)\
  find_package(MFEM REQUIRED CONFIG NO_DEFAULT_PATH PATHS ${MFEM_DIR}/lib/cmake/mfem)\
endif()' CMakeLists.txt

%build
OPTIONS=(
    -DBLT_SOURCE_DIR=%{_builddir}/%{name}-%{commit}/blt-%{blt_version}
    -DBLT_CXX_STD=c++17
    -DCMAKE_SKIP_RPATH=ON
    -DBUILD_SHARED_LIBS=ON
    -DENABLE_TESTS=OFF
)

%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake ${OPTIONS[@]} -DMFEM_DIR=$MPI_HOME \
    -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_INCLUDE}/hypre" \
    -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_mpich_unload}
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake ${OPTIONS[@]} -DMFEM_DIR=$MPI_HOME \
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
%{_libdir}/mpich/lib/libcontinuation_solver.so

%files mpich-devel
%{_libdir}/mpich/include/continuationsolver/
%endif

%if %{with openmpi}
%files openmpi
%license LICENSE
%{_libdir}/openmpi/lib/libcontinuation_solver.so

%files openmpi-devel
%{_libdir}/openmpi/include/continuationsolver/
%endif

%changelog
* Mon Jun 29 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.%{snapdate}git%{shortcommit}
- Initial package (snapshot pinned to smith's submodule commit; MPI-only)
