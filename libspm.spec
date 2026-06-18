%bcond openmp 1

Name:           libspm
Version:        0.1.0
Release:        2%{?dist}
Summary:        Standalone C library from SPM numerical routines

License:        GPL-2.0-only
URL:            https://github.com/m9h/libspm
# Vendored snapshot (git archive of the m9h/libspm dev repo) — the standalone C
# library extracted from SPM (Statistical Parametric Mapping, SPM25 / 25.01).
# Upstream repo not yet published, so ship the tarball in-tree instead of a
# (currently 404) Source URL.
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  cmake >= 3.16
BuildRequires:  gcc
BuildRequires:  make
%if %{with openmp}
BuildRequires:  libomp-devel
%endif

%description
libspm packages the numerical C core of SPM (Statistical Parametric Mapping)
as a native shared library. Includes diffeomorphic registration (Geodesic
Shooting / DARTEL), Full Multigrid and Conjugate Gradient PDE solvers,
B-spline interpolation (degrees 0-7), joint histograms for mutual-information
registration, Gaussian Mixture Models for tissue segmentation, matrix
exponential, and regularisation operators.

All linear algebra, interpolation, and PDE solvers are self-contained with
no external numerical library dependencies.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers, pkg-config, and CMake config files for developing against %{name}.

%package        static
Summary:        Static library for %{name}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description    static
Static archive (.a) for linking %{name} into standalone executables.

%prep
%autosetup

%build
%cmake \
    -DSPM_USE_OPENMP:BOOL=%{?with_openmp:ON}%{!?with_openmp:OFF} \
    -DSPM_BUILD_SHARED:BOOL=ON \
    -DSPM_BUILD_STATIC:BOOL=ON \
    -DSPM_BUILD_EXAMPLES:BOOL=OFF \
    -DSPM_BUILD_TESTS:BOOL=ON
%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license LICENSE
%doc README.md
%{_libdir}/libspm.so.0{,.*}

%files devel
%{_includedir}/spm/
%{_libdir}/libspm.so
%{_libdir}/pkgconfig/libspm.pc
%{_libdir}/cmake/spm/

%files static
%{_libdir}/libspm.a

%changelog
* Wed Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-2
- Vendor the source tarball in-tree (git archive of the m9h/libspm dev repo).
  The previous Source0 pointed at github.com/m9h/libspm which 404s (repo not yet
  published), so the GitLab-SCM build failed at the source stage. Ships the
  standalone C library extracted from SPM25 (DARTEL/Geodesic Shooting, PDE
  solvers, B-splines, GMM, joint histograms).

* Thu Mar 26 2026 m9h - 0.1.0-1
- Initial package
