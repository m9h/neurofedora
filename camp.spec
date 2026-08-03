# BLT is LLNL's build-time-only CMake/CTest macro framework. It is NOT the
# Tcl/Tk "blt" package shipped by Fedora, and the name collision rules out a
# normal subpackage. BLT compiles to nothing; the few CMake files it
# contributes are installed into this package's own cmake dir, so it is only
# needed at build time and is bundled here (disclosed via Provides: bundled).
%global blt_version 0.7.2

Name:           camp
Version:        2025.12.0
Release:        1%{?dist}
Summary:        Compiler agnostic metaprogramming library for portability

License:        BSD-3-Clause
URL:            https://github.com/LLNL/camp
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build

Provides:       bundled(blt) = %{blt_version}

%description
CAMP (Compiler Agnostic Metaprogramming for Portability) is a C++ template
metaprogramming library that provides portability abstractions used by the
LLNL RADIUSS performance-portability stack (RAJA, Umpire, Axom).

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the headers and CMake configuration files needed to
build applications against %{name}.

%prep
%autosetup -n %{name}-%{version}
# Provide BLT at build time (see comment near %%blt_version above)
tar -xf %{SOURCE1}

# Honor Fedora's libdir (%{_lib}) instead of the hardcoded "lib", so the
# library and CMake config land in %{_libdir} (e.g. /usr/lib64) consistently.
sed -i 's|lib/cmake/camp|%{_lib}/cmake/camp|g' CMakeLists.txt cmake/load_blt.cmake
sed -i -E 's|(RUNTIME\|LIBRARY\|ARCHIVE) DESTINATION lib|\1 DESTINATION %{_lib}|' CMakeLists.txt

# Upstream ships libcamp.so with an unversioned SONAME; give it a versioned
# soname so the runtime lib (.so.MAJOR) and devel symlink (.so) split cleanly
# per Fedora shared-library guidelines.
sed -i 's|INTERFACE_LIB_VERSION ${PROJECT_VERSION}|VERSION ${PROJECT_VERSION} SOVERSION ${PROJECT_VERSION_MAJOR} INTERFACE_LIB_VERSION ${PROJECT_VERSION}|' CMakeLists.txt

%build
%cmake \
    -DBLT_SOURCE_DIR=%{_builddir}/%{name}-%{version}/blt-%{blt_version} \
    -DCMAKE_SKIP_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DENABLE_TESTS=OFF \
    -DENABLE_EXAMPLES=OFF \
    -DENABLE_DOCS=OFF \
    -DENABLE_OPENMP=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libcamp.so.*

%files devel
%{_includedir}/camp/
%{_libdir}/libcamp.so
%{_libdir}/cmake/camp/

%changelog
* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.0-1
- Initial package (RADIUSS dependency stack for LLNL/smith)
