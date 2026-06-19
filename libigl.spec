Name:           libigl
Version:        2.3.0
Release:        1%{?dist}
Summary:        Simple C++ geometry processing library (header-only)

# The core (include/igl) is MPL-2.0; the optional copyleft modules
# (include/igl/copyleft, CGAL/tetgen/etc. wrappers) are GPL-3.0-or-later.
License:        MPL-2.0 AND GPL-3.0-or-later
URL:            https://libigl.github.io/
Source0:        https://github.com/libigl/libigl/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch

%description
libigl is a simple C++ geometry-processing library. The header-only core covers
discrete differential geometry, mesh I/O, parametrization, deformation, and a
broad set of linear-algebra / mesh utilities on top of Eigen. (The optional
modules that wrap CoMISo, Embree, CGAL, tetgen, etc. are not built here; only the
header-only library is shipped.)

%package        devel
Summary:        Development (header-only) files for %{name}
Requires:       eigen3-devel
Provides:       %{name}-static = %{version}-%{release}

%description    devel
Header-only C++ geometry-processing library. Pinned at v2.3.0, the version
ShapeWorks builds against. Depends on Eigen.

%prep
%autosetup

%build
# Header-only: nothing to compile (the upstream CMake build would download
# optional external modules at configure time, which we deliberately skip).

%install
mkdir -p %{buildroot}%{_includedir}
cp -a include/igl %{buildroot}%{_includedir}/

%files devel
%license LICENSE.MPL2 LICENSE.GPL
%doc README.md
%{_includedir}/igl/

%changelog
* Wed Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.0-1
- Initial package (header-only libigl v2.3.0, the version ShapeWorks pins).
  Ships only the header-only core; the network-downloading optional modules are
  skipped. Third prerequisite of the ShapeWorks dependency chain.
