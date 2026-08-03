## START: Set by rpmautospec
## (rpmautospec version 0.8.3)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 2;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%bcond_without openmpi
%bcond_without mpich
%bcond_with check 0

%global forgeurl https://github.com/mfem/mfem
Version:        4.9
%global sover   %{version}.0
%forgemeta

Name:           mfem
Release:        2.4%{?dist}
Summary:        Lightweight, general, scalable C++ library for finite element methods

# The main license is under BSD-3-Clause, but some files are under other licenses:
# AmgXWrapper (linalg/amgxsolver.{hpp,cpp}) -- MIT license
# Catch++ (tests/unit/catch.hpp) -- Boost 1.0 license
# Gecko (general/gecko.{cpp,hpp}) -- BSD 3-clause license
# Picojson (fem/picojson.h) -- Custom 2-clause license
# TinyXML2 (general/tinyxml2.{cpp,h}) -- zlib license
# Zstr (general/zstr.hpp) -- MIT license
License:        BSD-3-Clause AND MIT AND BSL-1.0 AND BSD-2-Clause AND Zlib
URL:            %{forgeurl}
Source0:        %{forgesource}

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch: %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  flexiblas-devel
BuildRequires:  metis-devel

Provides:       bundled(AmgXWrapper)
Provides:       bundled(catch2) = 2.13.9
Provides:       bundled(gecko)
Provides:       bundled(picojson)
Provides:       bundled(tinyxml2)
Provides:       bundled(zstr)

%description
MFEM is a modular parallel C++ library for finite element methods. Its goal is
to enable high-performance scalable finite element discretization research and
application development on a wide variety of platforms, ranging from laptops to
supercomputers.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package contains development files for %{name}.

%if %{with openmpi}
%package        openmpi
Summary:        OpenMPI version of %{name}
BuildRequires:  openmpi-devel
BuildRequires:  hypre-openmpi-devel
BuildRequires:  superlu_dist-openmpi-devel
BuildRequires:  STRUMPACK-openmpi-devel
Requires:       openmpi%{?_isa}

%description openmpi
This package contains the %{name} library compiled against OpenMPI.

%package        openmpi-devel
Summary:        Development files for OpenMPI version of %{name}
Requires:       %{name}-openmpi%{?_isa} = %{version}-%{release}
Requires:       openmpi-devel%{?_isa}
Requires:       hypre-openmpi-devel%{?_isa}
Requires:       superlu_dist-openmpi-devel%{?_isa}
Requires:       STRUMPACK-openmpi-devel%{?_isa}

%description openmpi-devel
This package contains the %{name} development library compiled
against OpenMPI.
%endif

%if %{with mpich}
%package        mpich
Summary:        MPICH version of %{name}
BuildRequires:  mpich-devel
BuildRequires:  hypre-mpich-devel
BuildRequires:  superlu_dist-mpich-devel
BuildRequires:  STRUMPACK-mpich-devel
Requires:       mpich%{?_isa}

%description mpich
This package contains the %{name} library compiled against MPICH.

%package        mpich-devel
Summary:        Development libraries for MPICH version of %{name}
Requires:       %{name}-mpich%{?_isa} = %{version}-%{release}
Requires:       mpich-devel%{?_isa}
Requires:       hypre-mpich-devel%{?_isa}
Requires:       superlu_dist-mpich-devel%{?_isa}
Requires:       STRUMPACK-mpich-devel%{?_isa}

%description mpich-devel
This package contains the %{name} development library compiled
against MPICH.
%endif

%prep
%forgeautosetup -p1

%build
OPTIONS=(
    -GNinja \
    -DCMAKE_SKIP_BUILD_RPATH=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
%if %{with check}
    -DMFEM_ENABLE_TESTING=ON \
%else
    -DMFEM_ENABLE_TESTING=OFF \
%endif
    -DMFEM_ENABLE_EXAMPLES=OFF \
    -DMFEM_ENABLE_MINIAPPS=OFF \
    -DMFEM_ENABLE_GOOGLE_BENCHMARKS=OFF \
    -DMFEM_USE_LAPACK=ON \
    -DCMAKE_VERBOSE_MAKEFILE=OFF \
)

%global _vpath_builddir %{_target_platform}
%cmake \
    ${OPTIONS[@]} \
    -DINSTALL_LIB_DIR=%{_libdir} \
    -DINSTALL_INCLUDE_DIR=%{_includedir}/mfem \
    -DINSTALL_CMAKE_DIR=%{_libdir}/cmake/mfem \
    -DMFEM_USE_MPI=OFF \
# https://github.com/mfem/mfem/issues/3677#issuecomment-1553387055
%cmake_build --target exec

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake \
    ${OPTIONS[@]} \
    -DHYPRE_INCLUDE_DIR=${MPI_INCLUDE}/hypre \
    -DHYPRE_LIBRARY=${MPI_LIB}/libHYPRE.so \
    -DINSTALL_LIB_DIR=${MPI_LIB} \
    -DINSTALL_INCLUDE_DIR=${MPI_INCLUDE}/mfem \
    -DINSTALL_CMAKE_DIR=${MPI_LIB}/cmake/mfem \
    -DMFEM_USE_MPI=ON \
    -DMFEM_USE_SUPERLU=ON \
    -DSuperLUDist_INCLUDE_DIRS=${MPI_INCLUDE}/superlu_dist \
    -DSuperLUDist_LIBRARIES=${MPI_LIB}/libsuperlu_dist.so \
    -DMFEM_USE_STRUMPACK=ON \
    -DSTRUMPACK_INCLUDE_DIRS=${MPI_HOME}/include \
    -DSTRUMPACK_LIBRARIES=${MPI_LIB}/libstrumpack.so \
    -DSTRUMPACK_REQUIRED_PACKAGES="MPI;MPI_Fortran;METIS;ScaLAPACK;LAPACK;BLAS" \
    -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_HOME}/include" \
%cmake_build --target exec
%{_openmpi_unload}
%endif

%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake \
    ${OPTIONS[@]} \
    -DHYPRE_INCLUDE_DIR=${MPI_INCLUDE}/hypre \
    -DHYPRE_LIBRARY=${MPI_LIB}/libHYPRE.so \
    -DINSTALL_LIB_DIR=${MPI_LIB} \
    -DINSTALL_INCLUDE_DIR=${MPI_INCLUDE}/mfem \
    -DINSTALL_CMAKE_DIR=${MPI_LIB}/cmake/mfem \
    -DMFEM_USE_MPI=ON \
    -DMFEM_USE_SUPERLU=ON \
    -DSuperLUDist_INCLUDE_DIRS=${MPI_INCLUDE}/superlu_dist \
    -DSuperLUDist_LIBRARIES=${MPI_LIB}/libsuperlu_dist.so \
    -DMFEM_USE_STRUMPACK=ON \
    -DSTRUMPACK_INCLUDE_DIRS=${MPI_HOME}/include \
    -DSTRUMPACK_LIBRARIES=${MPI_LIB}/libstrumpack.so \
    -DSTRUMPACK_REQUIRED_PACKAGES="MPI;MPI_Fortran;METIS;ScaLAPACK;LAPACK;BLAS" \
    -DCMAKE_CXX_FLAGS="%{optflags} -I${MPI_HOME}/include" \
%cmake_build --target exec
%{_mpich_unload}
%endif

%install
%global _vpath_builddir %{_target_platform}
%cmake_install

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake_install
%{_openmpi_unload}
%endif

%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake_install
%{_mpich_unload}
%endif

%if %{with check}

%check
%global _vpath_builddir %{_target_platform}
# SIGABRT - Abort (abnormal termination) signal
%ctest -E unit_tests

%if %{with openmpi}
%{_openmpi_load}

%global _vpath_builddir %{_target_platform}-openmpi
# SIGABRT - Abort (abnormal termination) signal
%ctest -E unit_tests

%{_openmpi_unload}
%endif

%if %{with mpich}
%{_mpich_load}

%global _vpath_builddir %{_target_platform}-mpich
# many tests failed on s390x, skip the tests
%ifnarch s390x
# SIGABRT - Abort (abnormal termination) signal
%ctest -E unit_tests
%endif

%{_mpich_unload}
%endif

%endif

%files
%license LICENSE
%doc README.md
%{_libdir}/libmfem.so.%{sover}

%files devel
%dir %{_includedir}/mfem
%{_includedir}/mfem/*.hpp
%{_includedir}/mfem/mfem/
%{_libdir}/cmake/mfem/
%{_libdir}/libmfem.so
%dir %{_datadir}/mfem
%{_datadir}/mfem/config.mk
%{_datadir}/mfem/test.mk

%if %{with openmpi}
%files openmpi
%license LICENSE
%doc README.md
%{_libdir}/openmpi/lib/libmfem.so.%{sover}

%files openmpi-devel
%dir %{_includedir}/openmpi-%{_arch}/mfem
%{_includedir}/openmpi-%{_arch}/mfem/*.hpp
%{_includedir}/openmpi-%{_arch}/mfem/mfem/
%{_libdir}/openmpi/lib/cmake/mfem/
%{_libdir}/openmpi/lib/libmfem.so
%endif

%if %{with mpich}
%files mpich
%license LICENSE
%doc README.md
%{_libdir}/mpich/lib/libmfem.so.%{sover}

%files mpich-devel
%dir %{_includedir}/mpich-%{_arch}
%{_includedir}/mpich-%{_arch}/mfem/*.hpp
%{_includedir}/mpich-%{_arch}/mfem/
%{_libdir}/mpich/lib/cmake/mfem/
%{_libdir}/mpich/lib/libmfem.so
%endif

%changelog
* Fri Jul 03 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9-2.4
- Fix STRUMPACK header path: use $MPI_HOME/include (where STRUMPACK installs),
  not $MPI_INCLUDE (the Fedora mpi compiler include dir)

* Thu Jul 02 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9-2.3
- Enable MFEM_USE_STRUMPACK (required by smith contact solver)

* Wed Jul 01 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9-2.2
- Enable MFEM_USE_SUPERLU (SuperLUSolver, required by smith)

* Wed Jul 01 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9-2.1
- Enable MFEM_USE_LAPACK (DenseMatrixEigensystem, required by smith)

## START: Generated by rpmautospec
* Fri Jan 16 2026 Fedora Release Engineering <releng@fedoraproject.org> - 4.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_44_Mass_Rebuild

* Sun Dec 14 2025 topazus <topazus@outlook.com> - 4.9-1
- 4.9

* Thu Jul 24 2025 Fedora Release Engineering <releng@fedoraproject.org> - 4.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Thu May 01 2025 topazus <topazus@outlook.com> - 4.8-1
- 4.8

* Fri Jan 17 2025 Fedora Release Engineering <releng@fedoraproject.org> - 4.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Sun Dec 29 2024 Antonio Trande <sagitter@fedoraproject.org> - 4.7-4
- Rebuild for MUMPS-5.7.3

* Thu Jul 18 2024 Fedora Release Engineering <releng@fedoraproject.org> - 4.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Sun May 19 2024 topazus <topazus@outlook.com> - 4.7-2
- fix sover

* Sun May 12 2024 topazus <topazus@outlook.com> - 4.7-1
- 4.7

* Thu Mar 28 2024 Zhengyu He <hezhy472013@gmail.com> - 4.6-6
- Add support for riscv64

* Thu Jan 25 2024 Fedora Release Engineering <releng@fedoraproject.org> - 4.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 4.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Tue Nov 21 2023 topazus <topazus@outlook.com> - 4.6-3
- enable packit only for rawhide

* Sun Oct 29 2023 Orion Poplawski <orion@nwra.com> - 4.6-2
- Rebuild for openmpi 5.0.0, drops C++ API

* Tue Oct 24 2023 topazus <topazus@outlook.com> - 4.6-1
- update to 4.6

* Thu Jul 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 4.5.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Tue Jun 27 2023 topazus <topazus@outlook.com> - 4.5.2-5
- remove i686 architecture

* Sun Jun 18 2023 topazus <topazus@outlook.com> - 4.5.2-4
- add packit ci

* Sun Jun 18 2023 topazus <topazus@outlook.com> - 4.5.2-3
- skip some tests of mfem-openmpi on Fedora 38 ppc64le

* Sun Jun 18 2023 topazus <topazus@outlook.com> - 4.5.2-2
- skip tests of mfem-openmpi on fedora 38 i686

* Sat Jun 17 2023 topazus <topazus@outlook.com> - 4.5.2-1
- initial import (rhbz#2214308)
## END: Generated by rpmautospec
