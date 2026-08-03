# STRUMPACK is used (via MFEM_USE_STRUMPACK) by LLNL/smith's contact solver.
# MPI-only (MFEM's STRUMPACK support and smith need the distributed solver).
%bcond_without mpich
%bcond_without openmpi

Name:           STRUMPACK
Version:        8.0.0
Release:        1%{?dist}
Summary:        Sparse direct solver and preconditioner using low-rank structure

License:        BSD-3-Clause-LBNL
URL:            https://github.com/pghysels/STRUMPACK
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  flexiblas-devel
BuildRequires:  metis-devel
%if %{with mpich}
BuildRequires:  mpich-devel
BuildRequires:  scalapack-mpich-devel
%endif
%if %{with openmpi}
BuildRequires:  openmpi-devel
BuildRequires:  scalapack-openmpi-devel
%endif

%description
STRUMPACK (STRUctured Matrix PACKage) is a software library providing sparse
direct solvers and preconditioners based on hierarchical/low-rank matrix
structure, for large sparse linear systems.

%if %{with mpich}
%package mpich
Summary:        MPICH version of %{name}
Requires:       mpich%{?_isa}

%description mpich
This package contains the %{name} library compiled against MPICH.

%package mpich-devel
Summary:        Development files for the MPICH version of %{name}
Requires:       %{name}-mpich%{?_isa} = %{version}-%{release}
Requires:       scalapack-mpich-devel%{?_isa}
Requires:       metis-devel%{?_isa}

%description mpich-devel
Headers and CMake config for the MPICH build of %{name}.
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
Requires:       scalapack-openmpi-devel%{?_isa}
Requires:       metis-devel%{?_isa}

%description openmpi-devel
Headers and CMake config for the OpenMPI build of %{name}.
%endif

%prep
%autosetup -n %{name}-%{version}

%build
OPTIONS=(
    -DSTRUMPACK_USE_MPI=ON
    -DSTRUMPACK_USE_OPENMP=ON
    -DTPL_ENABLE_SLATE=OFF
    -DTPL_ENABLE_PARMETIS=OFF
    -DTPL_ENABLE_BPACK=OFF
    -DTPL_ENABLE_ZFP=OFF
    -DTPL_ENABLE_PTSCOTCH=OFF
    -DTPL_ENABLE_SCOTCH=OFF
    -DTPL_ENABLE_METIS=ON
    -DSTRUMPACK_BUILD_TESTS=OFF
    -DBUILD_SHARED_LIBS=ON
    -DCMAKE_SKIP_RPATH=ON
    -DCMAKE_INSTALL_LIBDIR=lib
)

# Fedora's serial scalapack CMake config is broken (references a nonexistent
# serial lib; scalapack is MPI-only), so bypass find_package by passing the MPI
# ScaLAPACK library explicitly via TPL_SCALAPACK_LIBRARIES.
%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake ${OPTIONS[@]} -DCMAKE_INSTALL_PREFIX=$MPI_HOME \
    -DTPL_SCALAPACK_LIBRARIES=${MPI_LIB}/libscalapack.so
%cmake_build
%{_mpich_unload}
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake ${OPTIONS[@]} -DCMAKE_INSTALL_PREFIX=$MPI_HOME \
    -DTPL_SCALAPACK_LIBRARIES=${MPI_LIB}/libscalapack.so
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
%{_libdir}/mpich/lib/libstrumpack.so.*

%files mpich-devel
%{_libdir}/mpich/include/
%{_libdir}/mpich/lib/libstrumpack.so
%{_libdir}/mpich/lib/cmake/
%endif

%if %{with openmpi}
%files openmpi
%license LICENSE
%{_libdir}/openmpi/lib/libstrumpack.so.*

%files openmpi-devel
%{_libdir}/openmpi/include/
%{_libdir}/openmpi/lib/libstrumpack.so
%{_libdir}/openmpi/lib/cmake/
%endif

%changelog
* Thu Jul 02 2026 Morgan Hough <morgan.hough@gmail.com> - 8.0.0-1
- Initial package (MPI-only; STRUMPACK dependency for LLNL/smith via MFEM)
