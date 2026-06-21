# FEBio links 12 module .so into a private libdir; debug_package nil keeps the
# first packaging simple (the build is Release with force-include GCC15 fixes).
%global debug_package %{nil}
%global febiolibdir %{_libdir}/febio

Name:           febio
Version:        4.12
Release:        1%{?dist}
Summary:        Finite element solver for biomechanics and biophysics

License:        MIT
URL:            https://febio.org/
Source0:        https://github.com/febiosoftware/FEBio/archive/refs/tags/v%{version}.tar.gz#/FEBio-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  gcc
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  libomp-devel
# Optional-feature libraries, all from Fedora (MKL is proprietary and omitted ->
# FEBio falls back to its built-in Skyline direct solver):
BuildRequires:  hypre-devel
BuildRequires:  levmar-devel
BuildRequires:  fftw-devel
BuildRequires:  zlib-ng-compat-devel
# MMG adaptive mesh refinement: the component headers/libs live in the per-engine
# subpackages (mmg-devel alone ships only the umbrella libmmg.h, which #includes
# them). FEBio uses the mmg3d engine; pull in the components it needs.
BuildRequires:  mmg-devel
BuildRequires:  mmg3d-devel
BuildRequires:  mmgs-devel

%description
FEBio (Finite Elements for Biomechanics) is a nonlinear finite element solver
developed at the University of Utah (SCI Institute / Musculoskeletal Research
Laboratories) for problems in computational biomechanics and biophysics: large-
deformation solid mechanics, biphasic/multiphasic (poroelastic) tissue, fluid
and FSI, reactive transport, and parameter optimization.

This package provides the `febio4` command-line solver with the HYPRE BoomerAMG
iterative solver, MMG adaptive mesh refinement, FFTW, zlib plot compression, and
levmar parameter optimization. It is built without Intel MKL (proprietary), so the
Pardiso/iterative MKL solvers are unavailable and FEBio uses its built-in Skyline
direct solver by default; the HYPRE iterative solver remains available.

%prep
%autosetup -n FEBio-%{version}

%build
# GCC 15 no longer transitively includes these; FEBio uses strcpy/uint*/etc.
# without the explicit headers -> force-include. MKL off (proprietary) -> Skyline.
# Static stdlibs off (Fedora policy). Optional libs (incl. MMG, via the mmg3d/mmgs
# component packages) wired to their Fedora system paths.
cmake -S . -B cbuild -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="%{optflags} -include cstring -include cstdint -include cstdlib" \
    -DUSE_MKL=OFF \
    -DUSE_STATIC_STDLIBS=OFF \
    -DUSE_ZLIB=ON  -DZLIB_LIBRARY_RELEASE=%{_libdir}/libz.so -DZLIB_INCLUDE_DIR=%{_includedir} \
    -DUSE_FFTW=ON  -DFFTW_LIB=%{_libdir}/libfftw3.so       -DFFTW_INC=%{_includedir} \
    -DUSE_HYPRE=ON -DHYPRE_LIB=%{_libdir}/libHYPRE.so      -DHYPRE_INC=%{_includedir}/hypre \
    -DUSE_LEVMAR=ON -DLEVMAR_LIB=%{_libdir}/liblevmar.so   -DLEVMAR_INC=%{_includedir} \
    -DUSE_MMG=ON   -DMMG_LIB=%{_libdir}/libmmg3d.so -DMMGS_LIB=%{_libdir}/libmmgs.so -DMMG_INC=%{_includedir}
cmake --build cbuild %{?_smp_mflags}

%install
# FEBio has no install rules. Co-locate febio4 + its module libs in a private dir
# with $ORIGIN RPATH, and expose febio4 on PATH via a symlink.
install -d %{buildroot}%{febiolibdir}
install -m 0755 cbuild/bin/febio4 %{buildroot}%{febiolibdir}/febio4
install -m 0755 cbuild/lib/*.so %{buildroot}%{febiolibdir}/

# Drop the build-dir RPATH leak; point everything at its own directory.
for f in %{buildroot}%{febiolibdir}/febio4 %{buildroot}%{febiolibdir}/*.so; do
    chrpath -r '$ORIGIN' "$f"
done

install -d %{buildroot}%{_bindir}
ln -s ../%{_lib}/febio/febio4 %{buildroot}%{_bindir}/febio4

%files
%license LICENSE
%doc README.md
%dir %{febiolibdir}
%{febiolibdir}/febio4
%{febiolibdir}/*.so
%{_bindir}/febio4

%changelog
* Sat Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 4.12-1
- Initial package: FEBio 4.12 finite element solver (febio4). Built with system
  HYPRE/levmar/FFTW/zlib and MMG adaptive mesh refinement (via the mmg3d-devel +
  mmgs-devel component packages); MKL omitted (proprietary -> Skyline solver).
  GCC15 force-include fixes; module libs in a private %%{_libdir}/febio with
  $ORIGIN RPATH. FEBio Studio (GUI) not included.
