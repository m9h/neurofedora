# Lean self-compiles a 180MB libleanshared + ~2400 .olean modules; debuginfo on the
# generated C is enormous and useless, and the bootstrap is sensitive to flag
# injection — keep the upstream release config and skip debuginfo extraction.
%global debug_package %{nil}

Name:           lean4
Version:        4.32.0
Release:        1%{?dist}
Summary:        Theorem prover and functional programming language (toolchain)

License:        Apache-2.0
URL:            https://lean-lang.org/
# Release archive includes stage0/ (a checked-in C-source snapshot of the
# compiler) so the bootstrap needs no pre-existing Lean or elan.
Source0:        https://github.com/leanprover/lean4/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  clang
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gmp-devel
BuildRequires:  libuv-devel
BuildRequires:  openssl-devel
# find_program() picks these up so Lean does NOT download them at build time:
BuildRequires:  cadical
BuildRequires:  leangz

# Runtime: cadical is the SAT solver for decide/bv_decide; leantar (from leangz)
# is used by Lake to (un)pack library caches. We build with INSTALL_*=OFF so Lean
# ships no copies of its own — they come from these packages.
Requires:       cadical
Requires:       leangz
Requires:       clang

%description
Lean is an interactive theorem prover and a dependently-typed functional
programming language developed at the Lean FRO. This package provides the
Lean 4 toolchain: the `lean` compiler/checker, the `lake` build tool, the
`leanc` C-backend driver, and the bundled Init/Std/Lean libraries.

Note: this is the system toolchain. Projects that pin a specific toolchain via
`lean-toolchain` (the elan-managed workflow used by Mathlib) will not use it;
it is intended for building Lean code against the distribution toolchain.

%prep
%autosetup -n %{name}-%{version}

%build
# Root CMakeLists orchestrates stage0 (built from the checked-in C snapshot) then
# stage1; it forwards flags to both and does find_program(LEANTAR)/find_program(
# CADICAL) so the system tools are used (no network). USE_MIMALLOC=OFF drops the
# bundled-mimalloc FetchContent; INSTALL_{CADICAL,LEANTAR}=OFF avoids shipping
# copies that would file-conflict with the cadical and leangz packages.
# Raw cmake (not %%cmake): Lean's staged bootstrap is sensitive to injected flags,
# and stage0 deliberately discards extra CXX flags — match the validated invocation.
export CC=clang CXX=clang++
cmake \
    -S . -B build/release \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DSTAGE0_CMAKE_C_COMPILER=clang \
    -DSTAGE0_CMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DUSE_MIMALLOC=OFF \
    -DUSE_GMP=ON \
    -DUSE_GITHASH=OFF \
    -DLLVM=OFF \
    -DINSTALL_CADICAL=OFF \
    -DINSTALL_LEANTAR=OFF

# Lean's stdlib self-compile spikes multiple GB per process; cap parallelism by
# available RAM (>=3GB/job) so it never OOMs on a constrained builder.
cmake --build build/release %{limit_build -m 3000}

%install
# stage1 is an ExternalProject; install from its sub-build directory.
DESTDIR=%{buildroot} cmake --install build/release/stage1

# Lean installs its license files at the prefix root (/usr/LICENSE, /usr/LICENSES);
# drop them — the Apache-2.0 LICENSE is shipped properly via %%license below.
rm -f %{buildroot}%{_prefix}/LICENSE
rm -rf %{buildroot}%{_prefix}/LICENSES

%files
%license LICENSE
%{_bindir}/lean
%{_bindir}/leanc
%{_bindir}/leanchecker
%{_bindir}/leanir
%{_bindir}/leanmake
%{_bindir}/lake
%{_includedir}/lean/
%{_prefix}/lib/lean/
%{_prefix}/src/lean/
%{_datadir}/lean/

%changelog
* Sat Jun 20 2026 Morgan Hough <morgan.hough@gmail.com> - 4.31.0-1
- Initial package: Lean 4 theorem prover toolchain (lean, lake, leanc, leanchecker,
  leanir + bundled Init/Std/Lean libraries). Built from source via the stage0
  C-snapshot bootstrap (no elan). System gmp/libuv/cadical; leantar from leangz;
  USE_MIMALLOC=OFF and INSTALL_{CADICAL,LEANTAR}=OFF. Mathlib is out of scope
  (built per-project via Lake). $ORIGIN-relative RUNPATH (private /usr/lib/lean).
