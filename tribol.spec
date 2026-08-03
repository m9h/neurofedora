# BLT bundled at build time (build-time-only CMake macros; see other RADIUSS specs).
%global blt_version 0.7.2
# Snapshot pinned to the commit used by LLNL/smith (no usable upstream release).
%global commit 48a9dd6c7dba8efd690768f2ce3437e52487f662
%global shortcommit 48a9dd6c
%global snapdate 20260415

%bcond_without mpich
%bcond_without openmpi

Name:           tribol
Version:        0.1.0
Release:        0.2.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Contact mechanics library for HPC finite element codes

License:        BSD-3-Clause
URL:            https://github.com/LLNL/Tribol
Source0:        %{url}/archive/%{commit}/Tribol-%{commit}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  axom-devel
BuildRequires:  mfem-devel
BuildRequires:  hypre-devel
# mfem's exported target links serial metis (no metis-mpich in Fedora)
BuildRequires:  metis-devel
%if %{with mpich}
BuildRequires:  mpich-devel
BuildRequires:  axom-mpich-devel
BuildRequires:  mfem-mpich-devel
BuildRequires:  hypre-mpich-devel
%endif
%if %{with openmpi}
BuildRequires:  openmpi-devel
BuildRequires:  axom-openmpi-devel
BuildRequires:  mfem-openmpi-devel
BuildRequires:  hypre-openmpi-devel
%endif

Provides:       bundled(blt) = %{blt_version}

%description
Tribol is a contact mechanics library that provides interface physics models
and computational methods for finite element simulations, built on the LLNL
RADIUSS stack (Axom) and MFEM.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       axom-devel%{?_isa}
Requires:       mfem-devel%{?_isa}

%description devel
This package contains the headers and CMake configuration files needed to
build serial applications against %{name}.

%if %{with mpich}
%package mpich
Summary:        MPICH version of %{name}
Requires:       mpich%{?_isa}

%description mpich
This package contains the %{name} libraries compiled against MPICH.

%package mpich-devel
Summary:        Development files for the MPICH version of %{name}
Requires:       %{name}-mpich%{?_isa} = %{version}-%{release}
Requires:       axom-mpich-devel%{?_isa}
Requires:       mfem-mpich-devel%{?_isa}

%description mpich-devel
This package contains the headers and CMake configuration files needed to
build MPICH applications against %{name}.
%endif

%if %{with openmpi}
%package openmpi
Summary:        OpenMPI version of %{name}
Requires:       openmpi%{?_isa}

%description openmpi
This package contains the %{name} libraries compiled against OpenMPI.

%package openmpi-devel
Summary:        Development files for the OpenMPI version of %{name}
Requires:       %{name}-openmpi%{?_isa} = %{version}-%{release}
Requires:       axom-openmpi-devel%{?_isa}
Requires:       mfem-openmpi-devel%{?_isa}

%description openmpi-devel
This package contains the headers and CMake configuration files needed to
build OpenMPI applications against %{name}.
%endif

%prep
%autosetup -n Tribol-%{commit}
# Provide BLT at build time
tar -xf %{SOURCE1}

# Versioned soname for the tribol libraries.
sed -i '/install( TARGETS tribol/i set_target_properties(tribol PROPERTIES VERSION %{version} SOVERSION 0)' cmake/TribolMacros.cmake

# Install tribol's CMake config + BLT helper files into a per-package subdir so
# they do not conflict with axom's files installed directly in <libdir>/cmake/.
sed -i 's|DESTINATION lib/cmake|DESTINATION lib/cmake/tribol|' cmake/TribolMacros.cmake

%build
OPTIONS=(
    -DBLT_SOURCE_DIR=%{_builddir}/Tribol-%{commit}/blt-%{blt_version}
    -Dcamp_DIR=%{_libdir}/cmake/camp
    -Dumpire_DIR=%{_libdir}/cmake/umpire
    -DRAJA_DIR=%{_libdir}/cmake/raja
    -Dfmt_DIR=%{_libdir}/cmake/fmt
    -DCMAKE_SKIP_RPATH=ON
    -DBUILD_SHARED_LIBS=ON
    -DENABLE_TESTS=OFF
    -DENABLE_EXAMPLES=OFF
    -DENABLE_DOCS=OFF
    -DENABLE_FORTRAN=OFF
    -DENABLE_OPENMP=OFF
)

# MPI variants first (pristine source: Axom/MFEM are under $MPI_HOME/lib/cmake,
# tribol installs under $MPI_HOME/lib).
%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON -DBUILD_REDECOMP=ON \
    -DAXOM_DIR=$MPI_HOME -DMFEM_DIR=$MPI_HOME \
    -Daxom_DIR=$MPI_HOME/lib/cmake -Dconduit_DIR=$MPI_HOME/lib/cmake/conduit \
    -DHDF5_DIR=$MPI_HOME \
    -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_INCLUDE}/hypre" \
    -DTRIBOL_INSTALL_CMAKE_MODULE_DIR=lib/cmake/tribol \
    -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_mpich_unload}
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON -DBUILD_REDECOMP=ON \
    -DAXOM_DIR=$MPI_HOME -DMFEM_DIR=$MPI_HOME \
    -Daxom_DIR=$MPI_HOME/lib/cmake -Dconduit_DIR=$MPI_HOME/lib/cmake/conduit \
    -DHDF5_DIR=$MPI_HOME \
    -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_INCLUDE}/hypre" \
    -DTRIBOL_INSTALL_CMAKE_MODULE_DIR=lib/cmake/tribol \
    -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_openmpi_unload}
%endif

# Serial last: redirect external-dep lib/cmake lookups and tribol's own install
# destinations to Fedora's libdir.
sed -i 's|${AXOM_DIR}/lib/cmake|${AXOM_DIR}/%{_lib}/cmake|' cmake/SetupThirdParty.cmake
sed -i 's|${MFEM_DIR}/lib/cmake/mfem|${MFEM_DIR}/%{_lib}/cmake/mfem|' cmake/thirdparty/SetupMFEM.cmake
sed -i 's|lib/cmake|%{_lib}/cmake|g' cmake/TribolMacros.cmake
sed -i -E 's@(LIBRARY|ARCHIVE)( +DESTINATION )lib$@\1\2%{_lib}@' cmake/TribolMacros.cmake
# tribol_shared is installed by src/shared with its own hardcoded "lib"
sed -i -E 's@(DESTINATION[[:space:]]+)lib$@\1%{_lib}@' src/shared/CMakeLists.txt
%global _vpath_builddir %{_target_platform}
%cmake ${OPTIONS[@]} -DENABLE_MPI=OFF -DBUILD_REDECOMP=OFF \
    -DAXOM_DIR=%{_prefix} -DMFEM_DIR=%{_prefix} \
    -Daxom_DIR=%{_libdir}/cmake -Dconduit_DIR=%{_libdir}/cmake/conduit \
    -DHDF5_DIR=%{_prefix} \
    -DCMAKE_CXX_FLAGS="%{optflags} -I%{_includedir}/hypre" \
    -DTRIBOL_INSTALL_LIB_DIR=%{_lib} -DTRIBOL_INSTALL_CONFIG_DIR=%{_lib} \
    -DTRIBOL_INSTALL_CMAKE_MODULE_DIR=%{_lib}/cmake/tribol
%cmake_build

%install
# --- serial ---
%global _vpath_builddir %{_target_platform}
%cmake_install

# --- mpich ---
%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake_install
%{_mpich_unload}
%endif

# --- openmpi ---
%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake_install
%{_openmpi_unload}
%endif

# Note: tribol_shared and redecomp are unversioned helper libraries (upstream
# does not version them); they are runtime components and go in the main package.
%files
%license LICENSE
%doc README.md
%{_libdir}/libtribol.so.*
%{_libdir}/libtribol_shared.so

%files devel
%{_includedir}/tribol/
%{_includedir}/shared/
%{_libdir}/libtribol.so
%{_libdir}/cmake/tribol/

%if %{with mpich}
%files mpich
%license LICENSE
%{_libdir}/mpich/lib/libtribol.so.*
%{_libdir}/mpich/lib/libtribol_shared.so
%{_libdir}/mpich/lib/libredecomp.so

%files mpich-devel
%{_libdir}/mpich/include/tribol/
%{_libdir}/mpich/include/shared/
%{_libdir}/mpich/include/redecomp/
%{_libdir}/mpich/lib/libtribol.so
%{_libdir}/mpich/lib/cmake/tribol/
%endif

%if %{with openmpi}
%files openmpi
%license LICENSE
%{_libdir}/openmpi/lib/libtribol.so.*
%{_libdir}/openmpi/lib/libtribol_shared.so
%{_libdir}/openmpi/lib/libredecomp.so

%files openmpi-devel
%{_libdir}/openmpi/include/tribol/
%{_libdir}/openmpi/include/shared/
%{_libdir}/openmpi/include/redecomp/
%{_libdir}/openmpi/lib/libtribol.so
%{_libdir}/openmpi/lib/cmake/tribol/
%endif

%changelog
* Mon Jun 29 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-0.2.%{snapdate}git%{shortcommit}
- Add MPICH and OpenMPI variants (Fedora-correct MPI subpackages)

* Mon Jun 29 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-0.1.%{snapdate}git%{shortcommit}
- Initial package (snapshot pinned to smith's submodule commit)
