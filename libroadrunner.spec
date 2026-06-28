%global debug_package %{nil}
# LLVM JIT version. RoadRunner 2.9.2's codegen uses typed-pointer IR, so it must
# stay on an LLVM that still defaults to typed pointers (<= 14; 15+ forces opaque
# pointers and would break ModelDataIRBuilder). Rawhide (f45+) retired llvm13, so
# target the next-oldest available compat there: llvm14 (the code's >=13 guards
# also cover 14). F44 keeps the proven llvm13.
%if 0%{?fedora} >= 45
%global llvmver 14
%else
%global llvmver 13
%endif

Name:           libroadrunner
Version:        2.9.2
Release:        2%{?dist}
Summary:        High-performance SBML simulation library (LLVM-JIT), no-NLEQ build

# RoadRunner is Apache-2.0. Bundled header-only deps: parallel-hashmap (Apache-2.0),
# thread-pool (MIT). NLEQ (non-free) is removed in this build (see the transform).
License:        Apache-2.0 AND MIT
URL:            https://github.com/sys-bio/roadrunner
Source0:        libroadrunner-%{version}.tar.gz
# Fedora-clean transform: drop superbuild deps prefix + NLEQ (non-free) + clapack,
# use system libSBML/SUNDIALS/POCO/LLVM-13/rr-libstruct, global-namespace libSBML.
Source1:        libroadrunner-fedora-transform.sh

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  swig
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
# LLVM JIT: llvm13 on F44 (proven), llvm14 on rawhide (llvm13 was retired there).
# See the %%global llvmver block above for the typed-pointer rationale.
BuildRequires:  llvm%{llvmver}-devel
BuildRequires:  libsbml-devel
BuildRequires:  sundials-devel
BuildRequires:  poco-devel
BuildRequires:  expat-devel
BuildRequires:  zlib-ng-compat-static
BuildRequires:  ncurses-devel
BuildRequires:  f2c
BuildRequires:  lapack-devel
BuildRequires:  blas-devel
BuildRequires:  rr-libstruct-devel
BuildRequires:  chrpath

Provides:       bundled(parallel-hashmap)
Provides:       bundled(thread-pool)

%description
libRoadRunner is a high-performance SBML simulation library that JIT-compiles
models through LLVM. This Fedora build links system libraries (libSBML,
SUNDIALS, POCO, LLVM %{llvmver}, rr-libstruct) instead of the upstream
superbuild, and omits the non-free NLEQ steady-state solvers (the free Newton
and Newton-linesearch solvers remain). Time-course integration uses CVODE.

%package -n python3-roadrunner
Summary:        Python bindings for libRoadRunner
Requires:       libsbml
Requires:       python3-numpy
%description -n python3-roadrunner
Python bindings for libRoadRunner — load and simulate SBML models from Python.
Used by CompuCell3D's network solvers for sub-cellular reaction kinetics.

%package devel
Summary:        Development files for libRoadRunner
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description devel
Headers and C API for building against libRoadRunner.

%prep
%autosetup -n libroadrunner-%{version}
# Apply the Fedora-clean / no-NLEQ / system-libs / global-libSBML transform.
bash %{SOURCE1} .

%build
export LLVM_DIR=%{_libdir}/llvm%{llvmver}
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DRR_DEPENDENCIES_INSTALL_PREFIX=/usr \
    -DLLVM_INSTALL_PREFIX=%{_libdir}/llvm%{llvmver} \
    -DBUILD_PYTHON=ON \
    -DBUILD_LLVM=ON \
    -DBUILD_RR_CAPI=ON \
    -DBUILD_TESTS=OFF
%cmake_build

%install
# RoadRunner's build tree lays the artifacts out under <build>/lib; install them
# into the Fedora locations directly (its own install rules assume the prefix tree).
b=%{__cmake_builddir}
install -d %{buildroot}%{_libdir} %{buildroot}%{python3_sitearch}
cp -a "$b"/lib/libroadrunner.so* %{buildroot}%{_libdir}/
cp -a "$b"/lib/libroadrunner_c_api.so* %{buildroot}%{_libdir}/ 2>/dev/null || :
cp -a "$b"/lib/site-packages/roadrunner %{buildroot}%{python3_sitearch}/
# headers
install -d %{buildroot}%{_includedir}/rr
cp -a source/*.h %{buildroot}%{_includedir}/rr/ 2>/dev/null || :
# strip build-tree RPATHs; the python ext finds libroadrunner.so via %{_libdir}
find %{buildroot} -name '*.so' -o -name '*.so.*' | xargs -r chrpath --delete 2>/dev/null || :

%files
%license LICENSE.txt
# Upstream sets no SOVERSION, so the libraries are unversioned.
%{_libdir}/libroadrunner.so
%{_libdir}/libroadrunner_c_api.so

%files -n python3-roadrunner
%{python3_sitearch}/roadrunner/

%files devel
%{_includedir}/rr/

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 2.9.2-2
- Build on rawhide (f45+) against llvm14 (llvm13 compat retired there);
  F44 stays on llvm13. RoadRunner's >=13 codegen guards cover 14, and 14
  still defaults to typed pointers (15+ opaque pointers would break the
  IR builder). No longer F44-only.

* Thu Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.9.2-1
- Initial package: libRoadRunner 2.9.2, Fedora-clean no-NLEQ build.
- Links system libSBML/SUNDIALS-7/POCO/LLVM-13/rr-libstruct (no superbuild);
  removes the non-free NLEQ solvers (Newton/Newton-linesearch retained);
  adapts to Fedora's global-namespace libSBML. Validated: SBML CVODE time-course.
