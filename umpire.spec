# BLT is LLNL's build-time-only CMake macro framework (not Fedora's Tcl/Tk
# "blt"); bundled at build time and disclosed below. camp and fmt are taken
# from the system (camp_DIR / fmt_DIR) rather than the vendored submodules.
%global blt_version 0.7.2

Name:           umpire
Version:        2025.12.0
Release:        1%{?dist}
Summary:        Application-focused API for memory management on heterogeneous architectures

License:        MIT
URL:            https://github.com/LLNL/Umpire
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        https://github.com/LLNL/blt/archive/refs/tags/v%{blt_version}.tar.gz#/blt-%{blt_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  camp-devel
BuildRequires:  fmt-devel

Provides:       bundled(blt) = %{blt_version}

%description
Umpire is a resource management library that allows the discovery, provision,
and management of memory on machines with multiple memory devices like NUMA
and GPUs. It is part of the LLNL RADIUSS performance-portability stack.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       camp-devel%{?_isa}
# umpire-config.cmake does find_dependency(fmt)
Requires:       fmt-devel%{?_isa}

%description devel
This package contains the headers and CMake configuration files needed to
build applications against %{name}.

%prep
%autosetup -n Umpire-%{version}
# Provide BLT at build time (see comment near %%blt_version above)
tar -xf %{SOURCE1}

# Upstream ships libumpire.so unversioned; add a versioned soname so the
# runtime lib (.so.MAJOR) and devel symlink (.so) split cleanly.
sed -i '/\$<INSTALL_INTERFACE:\${CMAKE_INSTALL_INCLUDEDIR}>)/a set_target_properties(umpire PROPERTIES VERSION ${PROJECT_VERSION} SOVERSION ${PROJECT_VERSION_MAJOR})' src/umpire/CMakeLists.txt

%build
%cmake \
    -DBLT_SOURCE_DIR=%{_builddir}/Umpire-%{version}/blt-%{blt_version} \
    -Dcamp_DIR=%{_libdir}/cmake/camp \
    -Dfmt_DIR=%{_libdir}/cmake/fmt \
    -DCMAKE_SKIP_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DENABLE_TESTS=OFF \
    -DENABLE_EXAMPLES=OFF \
    -DENABLE_BENCHMARKS=OFF \
    -DENABLE_DOCS=OFF \
    -DENABLE_OPENMP=OFF \
    -DENABLE_MPI=OFF \
    -DUMPIRE_ENABLE_FORTRAN=OFF \
    -DUMPIRE_ENABLE_TOOLS=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libumpire.so.*

%files devel
%{_includedir}/umpire/
%{_libdir}/libumpire.so
%{_libdir}/cmake/umpire/

%changelog
* Sun Jun 28 2026 Morgan Hough <morgan.hough@gmail.com> - 2025.12.0-1
- Initial package (RADIUSS dependency stack for LLNL/smith)
