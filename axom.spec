# BLT is LLNL's build-time-only CMake macro framework (not Fedora's Tcl/Tk
# "blt"); bundled at build time. camp/umpire/RAJA/fmt are MPI-agnostic and taken
# from the serial system packages for every flavor; conduit and HDF5 are taken
# from the matching (serial or MPI) packages.
%global blt_version 0.7.2

# Axom's CMake project root is the src/ subdirectory.
%global _vpath_srcdir src

# Use the exact axom commit that LLNL/smith pins: its bundled sol2 supports Lua
# 5.4 (the v0.14.0 release's sol2 does not, and smith requires axom-with-Lua).
%global commit f81109cea1507cd9bbbd2f549c3fb33be18a3936
%global shortcommit f81109ce

%bcond_without mpich
%bcond_without openmpi

Name:           axom
Version:        0.14.0
Release:        5%{?dist}
Summary:        CS infrastructure components for HPC applications

License:        BSD-3-Clause
URL:            https://github.com/LLNL/axom
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  camp-devel
BuildRequires:  umpire-devel
BuildRequires:  RAJA-devel
BuildRequires:  conduit-devel
BuildRequires:  hdf5-devel
# Lua enables axom's inlet LuaReader + bundled sol2 (required by smith)
BuildRequires:  lua-devel
# MFEM enables sidre's MFEMSidreDataCollection (required by smith)
BuildRequires:  mfem-devel
BuildRequires:  hypre-devel
BuildRequires:  metis-devel
%if %{with mpich}
BuildRequires:  mpich-devel
BuildRequires:  conduit-mpich-devel
BuildRequires:  hdf5-mpich-devel
BuildRequires:  mfem-mpich-devel
BuildRequires:  hypre-mpich-devel
%endif
%if %{with openmpi}
BuildRequires:  openmpi-devel
BuildRequires:  conduit-openmpi-devel
BuildRequires:  hdf5-openmpi-devel
BuildRequires:  mfem-openmpi-devel
BuildRequires:  hypre-openmpi-devel
%endif

Provides:       bundled(blt) = %{blt_version}

%description
Axom is a collection of robust and flexible software components that serve as
building blocks for high-performance computing applications, developed as part
of the LLNL RADIUSS stack. Components include core, slic, slam, primal, mint,
spin, sidre, inlet, klee, and quest.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       camp-devel%{?_isa}
Requires:       umpire-devel%{?_isa}
Requires:       RAJA-devel%{?_isa}
Requires:       conduit-devel%{?_isa}
Requires:       lua-devel%{?_isa}
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
Requires:       camp-devel%{?_isa}
Requires:       umpire-devel%{?_isa}
Requires:       RAJA-devel%{?_isa}
Requires:       conduit-mpich-devel%{?_isa}
Requires:       lua-devel%{?_isa}
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
Requires:       camp-devel%{?_isa}
Requires:       umpire-devel%{?_isa}
Requires:       RAJA-devel%{?_isa}
Requires:       conduit-openmpi-devel%{?_isa}
Requires:       lua-devel%{?_isa}
Requires:       mfem-openmpi-devel%{?_isa}

%description openmpi-devel
This package contains the headers and CMake configuration files needed to
build OpenMPI applications against %{name}.
%endif

%prep
%autosetup -n %{name}-%{commit}
# Provide BLT at build time (see comment near %%blt_version above)
tar -xf %{SOURCE1}

# Upstream installs component libraries with unversioned sonames; add a
# versioned soname to each compiled component (scoped to axom_add_library; the
# SOURCES guard skips header-only components to avoid set_target_properties on
# INTERFACE libs).
sed -i '/^macro(axom_add_library)/,/^endmacro(axom_add_library)/{/arg_FOLDER})/a\
if(NOT "${arg_SOURCES}" STREQUAL "")\
set_target_properties(${arg_NAME} PROPERTIES VERSION %{version} SOVERSION 0)\
endif()
}' src/cmake/AxomMacros.cmake

%build
OPTIONS=(
    -DBLT_SOURCE_DIR=%{_builddir}/%{name}-%{commit}/blt-%{blt_version}
    -DCAMP_DIR=%{_libdir}/cmake/camp
    -DUMPIRE_DIR=%{_libdir}/cmake/umpire
    -Dfmt_DIR=%{_libdir}/cmake/fmt
    -DRAJA_DIR=%{_libdir}/cmake/raja
    -DLUA_DIR=%{_prefix}
    -DAXOM_ENABLE_MFEM_SIDRE_DATACOLLECTION=ON
    -DCMAKE_SKIP_RPATH=ON
    -DBUILD_SHARED_LIBS=ON
    -DENABLE_TESTS=OFF
    -DENABLE_EXAMPLES=OFF
    -DENABLE_DOCS=OFF
    -DAXOM_ENABLE_TOOLS=OFF
    -DENABLE_FORTRAN=OFF
    -DENABLE_OPENMP=OFF
)

# MPI variants first (pristine source installs the component libs under
# $MPI_HOME/lib via the default AXOM_INSTALL_LIB_DIR=lib).
%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON \
    -DCONDUIT_DIR=$MPI_HOME/lib/cmake/conduit -DHDF5_DIR=$MPI_HOME \
    -DMFEM_DIR=$MPI_HOME -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_INCLUDE}/hypre" \
    -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_mpich_unload}
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON \
    -DCONDUIT_DIR=$MPI_HOME/lib/cmake/conduit -DHDF5_DIR=$MPI_HOME \
    -DMFEM_DIR=$MPI_HOME -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_INCLUDE}/hypre" \
    -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_openmpi_unload}
%endif

# Serial last: redirect the hardcoded component-target / export "lib" to lib64.
sed -i -E 's|(DESTINATION[[:space:]]+)lib/cmake|\1%{_lib}/cmake|g' src/axom/CMakeLists.txt
sed -i -E 's|(DESTINATION[[:space:]]+)lib([)[:space:]]*)$|\1%{_lib}\2|' src/axom/CMakeLists.txt
%global _vpath_builddir %{_target_platform}
%cmake ${OPTIONS[@]} -DENABLE_MPI=OFF \
    -DCONDUIT_DIR=%{_libdir}/cmake/conduit -DHDF5_DIR=%{_prefix} \
    -DMFEM_DIR=%{_libdir} -DCMAKE_CXX_FLAGS="%{optflags} -I%{_includedir}/hypre" \
    -DAXOM_INSTALL_LIB_DIR=%{_lib} -DAXOM_INSTALL_CONFIG_DIR=%{_lib}
%cmake_build

%install
# --- serial ---
%global _vpath_builddir %{_target_platform}
%cmake_install
rm -rf %{buildroot}%{_prefix}/examples

# --- mpich ---
%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake_install
rm -rf %{buildroot}${MPI_HOME}/examples
%{_mpich_unload}
%endif

# --- openmpi ---
%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake_install
rm -rf %{buildroot}${MPI_HOME}/examples
%{_openmpi_unload}
%endif

%files
%license LICENSE
%doc README.md
%{_libdir}/libaxom_*.so.*

%files devel
%{_includedir}/axom/
%{_libdir}/libaxom_*.so
%{_libdir}/cmake/axom-*.cmake
%{_libdir}/cmake/BLT*.cmake

%if %{with mpich}
%files mpich
%license LICENSE
%{_libdir}/mpich/lib/libaxom_*.so.*

%files mpich-devel
%{_libdir}/mpich/include/axom/
%{_libdir}/mpich/lib/libaxom_*.so
%{_libdir}/mpich/lib/cmake/axom-*.cmake
%{_libdir}/mpich/lib/cmake/BLT*.cmake
%{_libdir}/mpich/lib/cmake/thirdparty/
%endif

%if %{with openmpi}
%files openmpi
%license LICENSE
%{_libdir}/openmpi/lib/libaxom_*.so.*

%files openmpi-devel
%{_libdir}/openmpi/include/axom/
%{_libdir}/openmpi/lib/libaxom_*.so
%{_libdir}/openmpi/lib/cmake/axom-*.cmake
%{_libdir}/openmpi/lib/cmake/BLT*.cmake
%{_libdir}/openmpi/lib/cmake/thirdparty/
%endif

%changelog
* Wed Jul 01 2026 Morgan Hough <morgan.hough@gmail.com> - 0.14.0-5
- Enable MFEM sidre DataCollection (MFEMSidreDataCollection.hpp), required by smith

* Tue Jun 30 2026 Morgan Hough <morgan.hough@gmail.com> - 0.14.0-4
- Switch to smith's pinned axom commit (f81109ce) for Lua 5.4-compatible sol2

* Tue Jun 30 2026 Morgan Hough <morgan.hough@gmail.com> - 0.14.0-3
- Enable Lua (inlet LuaReader + bundled sol2), required by LLNL/smith

* Mon Jun 29 2026 Morgan Hough <morgan.hough@gmail.com> - 0.14.0-2
- Add MPICH and OpenMPI variants (Fedora-correct MPI subpackages)

* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 0.14.0-1
- Initial package (RADIUSS dependency stack for LLNL/smith)
