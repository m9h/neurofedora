# BLT is LLNL's build-time-only CMake macro framework (not Fedora's Tcl/Tk
# "blt"); bundled at build time and disclosed below. camp is taken from the
# system (camp_DIR) rather than the vendored submodule. Desul atomics (another
# vendored submodule) are disabled for this CPU build.
%global blt_version 0.7.2

Name:           RAJA
Version:        2025.12.2
Release:        1%{?dist}
Summary:        Performance portability layer for HPC loop-based computation

License:        BSD-3-Clause
URL:            https://github.com/LLNL/RAJA
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  camp-devel

Provides:       bundled(blt) = %{blt_version}

%description
RAJA is a library of C++ software abstractions that enables architecture and
programming-model portability for HPC applications. It is part of the LLNL
RADIUSS performance-portability stack.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       camp-devel%{?_isa}

%description devel
This package contains the headers and CMake configuration files needed to
build applications against %{name}.

%prep
%autosetup -n RAJA-%{version}
# Provide BLT at build time (see comment near %%blt_version above)
tar -xf %{SOURCE1}

# Honor Fedora's libdir instead of the hardcoded "lib" (spread across the top
# CMakeLists and several cmake/ helper files).
sed -i 's|lib/cmake/raja|%{_lib}/cmake/raja|g' \
    CMakeLists.txt cmake/SetupPackages.cmake cmake/SetupRajaConfig.cmake
sed -i 's|/lib/pkgconfig|/%{_lib}/pkgconfig|g' cmake/SetupRajaConfig.cmake
sed -i -E 's|(ARCHIVE\|LIBRARY\|RUNTIME) DESTINATION lib|\1 DESTINATION %{_lib}|' CMakeLists.txt

# Upstream ships libRAJA.so unversioned; add a versioned soname.
sed -i '/^install(TARGETS RAJA/i set_target_properties(RAJA PROPERTIES VERSION ${PROJECT_VERSION} SOVERSION ${PROJECT_VERSION_MAJOR})' CMakeLists.txt

%build
%cmake \
    -DBLT_SOURCE_DIR=%{_builddir}/RAJA-%{version}/blt-%{blt_version} \
    -Dcamp_DIR=%{_libdir}/cmake/camp \
    -DCMAKE_SKIP_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DRAJA_ENABLE_DESUL_ATOMICS=OFF \
    -DRAJA_ENABLE_TESTS=OFF \
    -DRAJA_ENABLE_EXAMPLES=OFF \
    -DRAJA_ENABLE_EXERCISES=OFF \
    -DRAJA_ENABLE_BENCHMARKS=OFF \
    -DRAJA_ENABLE_DOCUMENTATION=OFF \
    -DENABLE_TESTS=OFF \
    -DENABLE_EXAMPLES=OFF \
    -DENABLE_OPENMP=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libRAJA.so.*

%files devel
%{_includedir}/RAJA/
%{_libdir}/libRAJA.so
%{_libdir}/cmake/raja/
%{_libdir}/pkgconfig/RAJA.pc

%changelog
* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.2-1
- Initial package (RADIUSS dependency stack for LLNL/smith)
