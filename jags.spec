# Major version drives the soname (libjags.so.%%{somajor}), the upstream
# download path (%%{somajor}.x), and the module dir (%%{_libdir}/JAGS/modules-N).
%global somajor 5

Name:           jags
Version:        5.0.0
Release:        1%{?dist}
Summary:        Just Another Gibbs Sampler for Bayesian MCMC simulation

# Whole tree is GPLv2 (COPYING = GPL v2, no "or later" in source headers).
License:        GPL-2.0-only
URL:            https://mcmc-jags.sourceforge.io/
Source0:        https://downloads.sourceforge.net/project/mcmc-jags/JAGS/%{somajor}.x/Source/JAGS-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  make
# BLAS/LAPACK via Fedora's flexiblas front-end.
BuildRequires:  flexiblas-devel

# JAGS bundles a trimmed, modified copy of SuiteSparse's AMD/sparse routines
# under src/lib/SSparse (upstream ships no system-SuiteSparse switch). Documented
# per Fedora bundling policy. TODO(Fedora): evaluate de-bundling vs system
# suitesparse before a formal review.
Provides:       bundled(suitesparse)

%description
JAGS (Just Another Gibbs Sampler) is a program for analysis of Bayesian
hierarchical models using Markov Chain Monte Carlo (MCMC) simulation. It uses a
dialect of the BUGS language and runs cross-platform. JAGS was written to be
extensible, providing a software platform for experimentation with ideas in
Bayesian modeling.

%package        devel
Summary:        Development files for JAGS
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Downstream consumers (rjags, runjags) build against BLAS/LAPACK transitively.
Requires:       flexiblas-devel

%description devel
Headers, the unversioned shared-library symlinks, and the pkg-config file needed
to build applications and interfaces (e.g. rjags) against the JAGS library.

%prep
%autosetup -n JAGS-%{version}

%build
# Point the ax_blas/ax_lapack macros at Fedora's flexiblas front-end rather than
# a hardcoded reference BLAS, so JAGS picks up the user's selected backend.
%configure \
    --disable-static \
    --with-blas="-lflexiblas" \
    --with-lapack="-lflexiblas"
%make_build

%install
%make_install
# Drop libtool archives — Fedora does not ship .la files.
find %{buildroot} -name '*.la' -delete

%files
%license COPYING
%doc README NEWS AUTHORS
%{_bindir}/jags
# jags is a wrapper script that execs the real terminal binary in libexec.
%{_libexecdir}/jags-terminal
%{_libdir}/libjags.so.%{somajor}*
%{_libdir}/libjrmath.so.0*
%{_libdir}/JAGS/
%{_mandir}/man1/jags.1*

%files devel
%{_includedir}/JAGS/
%{_libdir}/libjags.so
%{_libdir}/libjrmath.so
%{_libdir}/pkgconfig/jags.pc

%changelog
* Sun Aug 02 2026 Morgan Hough <morgan.hough@gmail.com> - 5.0.0-1
- Initial package of JAGS 5.0.0 (new upstream major release, 2026-08-01).
- Built against system flexiblas (BLAS/LAPACK); autotools build.
- SSparse/AMD subset bundled (Provides: bundled(suitesparse)).
