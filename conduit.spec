# BLT is LLNL's build-time-only CMake macro framework (not Fedora's Tcl/Tk
# "blt"); bundled at build time. Conduit also embeds several third-party
# parsers/helpers in src/thirdparty_builtin that are compiled directly into its
# libraries and cannot be cleanly unbundled; these are disclosed below.
%global blt_version 0.7.2

# Conduit's CMake project root is the src/ subdirectory.
%global _vpath_srcdir src

%bcond_without mpich
%bcond_without openmpi

Name:           conduit
Version:        0.9.7
Release:        2%{?dist}
Summary:        Intuitive model for describing hierarchical scientific data

License:        BSD-3-Clause
URL:            https://github.com/LLNL/conduit
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hdf5-devel
BuildRequires:  zlib-devel
%if %{with mpich}
BuildRequires:  mpich-devel
BuildRequires:  hdf5-mpich-devel
%endif
%if %{with openmpi}
BuildRequires:  openmpi-devel
BuildRequires:  hdf5-openmpi-devel
%endif

Provides:       bundled(blt) = %{blt_version}
Provides:       bundled(fmt) = 12.1.0
Provides:       bundled(yyjson)
Provides:       bundled(libb64) = 1.2.1
Provides:       bundled(libyaml)

%description
Conduit provides an intuitive model for describing hierarchical scientific
data in C++, C, Fortran, and Python. It is used for data coupling between
packages in-core, serialization, and I/O tasks, and is part of the LLNL
RADIUSS stack.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
# ConduitConfig.cmake does find_dependency(HDF5) and find_dependency(ZLIB)
Requires:       hdf5-devel%{?_isa}
Requires:       zlib-devel%{?_isa}

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
Requires:       hdf5-mpich-devel%{?_isa}
Requires:       zlib-devel%{?_isa}

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
Requires:       hdf5-openmpi-devel%{?_isa}
Requires:       zlib-devel%{?_isa}

%description openmpi-devel
This package contains the headers and CMake configuration files needed to
build OpenMPI applications against %{name}.
%endif

%prep
%autosetup -n %{name}-%{version}
# Provide BLT at build time (see comment near %%blt_version above)
tar -xf %{SOURCE1}

# Upstream ships its libraries with unversioned sonames; version them all via
# the shared add_compiled_library macro.
sed -i 's|        # install our lib|        set_target_properties(${args_NAME} PROPERTIES VERSION ${PROJECT_VERSION} SOVERSION ${PROJECT_VERSION_MAJOR})\n        # install our lib|' src/cmake/CMakeBasics.cmake

%build
OPTIONS=(
    -DBLT_SOURCE_DIR=%{_builddir}/%{name}-%{version}/blt-%{blt_version}
    -DCMAKE_SKIP_RPATH=ON
    -DBUILD_SHARED_LIBS=ON
    -DENABLE_TESTS=OFF
    -DENABLE_EXAMPLES=OFF
    -DENABLE_DOCS=OFF
    -DENABLE_UTILS=OFF
    -DENABLE_RELAY_WEBSERVER=OFF
    -DENABLE_PYTHON=OFF
    -DENABLE_FORTRAN=OFF
)

# Build the MPI variants first, against the pristine source: each installs under
# its own $MPI_HOME prefix, so the upstream-hardcoded "lib" becomes $MPI_HOME/lib.
%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON -DHDF5_DIR=$MPI_HOME -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_mpich_unload}
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake ${OPTIONS[@]} -DENABLE_MPI=ON -DHDF5_DIR=$MPI_HOME -DCMAKE_INSTALL_PREFIX=$MPI_HOME
%cmake_build
%{_openmpi_unload}
%endif

# Serial build last: redirect the hardcoded "lib" to Fedora's libdir so the
# exported CMake targets record the correct lib64 location.
sed -i -E 's|(LIBRARY\|ARCHIVE) DESTINATION lib$|\1 DESTINATION %{_lib}|' src/cmake/CMakeBasics.cmake
%global _vpath_builddir %{_target_platform}
%cmake ${OPTIONS[@]} -DENABLE_MPI=OFF -DHDF5_DIR=%{_prefix}
%cmake_build

%install
# --- serial ---
%global _vpath_builddir %{_target_platform}
%cmake_install
# Relocate conduit's serial CMake package files from the hardcoded <prefix>/lib.
%if "%{_lib}" != "lib"
mkdir -p %{buildroot}%{_libdir}/cmake
mv %{buildroot}%{_prefix}/lib/cmake/conduit %{buildroot}%{_libdir}/cmake/conduit
rmdir %{buildroot}%{_prefix}/lib/cmake %{buildroot}%{_prefix}/lib 2>/dev/null || :
%endif
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
%{_libdir}/libconduit*.so.*

%files devel
%{_includedir}/conduit/
%{_libdir}/libconduit*.so
%{_libdir}/cmake/conduit/
%{_datadir}/conduit/

%if %{with mpich}
%files mpich
%license LICENSE
%{_libdir}/mpich/lib/libconduit*.so.*

%files mpich-devel
%{_libdir}/mpich/include/conduit/
%{_libdir}/mpich/lib/libconduit*.so
%{_libdir}/mpich/lib/cmake/conduit/
%{_libdir}/mpich/share/conduit/
%endif

%if %{with openmpi}
%files openmpi
%license LICENSE
%{_libdir}/openmpi/lib/libconduit*.so.*

%files openmpi-devel
%{_libdir}/openmpi/include/conduit/
%{_libdir}/openmpi/lib/libconduit*.so
%{_libdir}/openmpi/lib/cmake/conduit/
%{_libdir}/openmpi/share/conduit/
%endif

%changelog
* Mon Jun 29 2026 Morgan Hough <morgan.hough@gmail.com> - 0.9.7-2
- Add MPICH and OpenMPI variants (Fedora-correct MPI subpackages)

* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 0.9.7-1
- Initial package (RADIUSS dependency stack for LLNL/smith)
