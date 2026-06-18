%global commit 7ff1f477a0538a45061d56a7dcde894fca2f3f65
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           rr-libstruct
Version:        2.9.2
Release:        0.1.git%{shortcommit}%{?dist}
Summary:        Structural analysis library for SBML stoichiometric matrices

# Upstream ships no LICENSE file; headers carry the BSD-3-Clause notice used
# across the sys-bio/roadrunner project.
License:        BSD-3-Clause
URL:            https://github.com/sys-bio/rr-libstruct
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
# Fedora-clean shared-lib build (upstream is static-only / superbuild-oriented).
Source1:        rr-libstruct-CMakeLists.txt
# Minimal CLAPACK prototype shim (Fedora dropped clapack; symbols come from
# system liblapack). Installed as clapack.h for the upstream #include.
Source2:        rr-libstruct-clapack-shim.h

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  f2c
BuildRequires:  libsbml-devel
BuildRequires:  lapack-devel
BuildRequires:  blas-devel

%description
rr-libstruct (libStructural) computes structural properties of biochemical
reaction networks from their SBML stoichiometric matrices — conservation laws,
the link/gamma matrices, fully/partially-reduced stoichiometry, and related
linear-algebra analyses. It is a core dependency of libRoadRunner.

%package devel
Summary:        Development files for rr-libstruct
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libsbml-devel

%description devel
Headers for building against rr-libstruct.

%prep
%autosetup -n %{name}-%{shortcommit}
# Drop in the Fedora-clean shared-library build and the clapack prototype shim.
cp -p %{SOURCE1} CMakeLists.txt
cp -p %{SOURCE2} clapack.h

%build
%cmake -GNinja -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%files
%{_libdir}/librr-libstruct.so.2
%{_libdir}/librr-libstruct.so.2.*

%files devel
%{_includedir}/rr-libstruct/
%{_libdir}/librr-libstruct.so

%changelog
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 2.9.2-0.1.git7ff1f47
- Initial package: rr-libstruct (sys-bio) as a Fedora-clean shared library.
- Replace upstream static-only/superbuild CMake with a shared build linking
  system libSBML + Fortran LAPACK/BLAS; supply a minimal clapack.h prototype
  shim (f2c.h from the system f2c package). Foundation dep for libRoadRunner.
