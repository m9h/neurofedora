%global _lto_cflags %{nil}
# ANTs instantiates ITK templates across 2D/3D/4D; each g++ process peaks at ~3 GB.
# Limit parallelism so the build stays within COPR worker memory (typically 16 GB).
%global _smp_mflags -j4
# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the debuginfo
# package stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

%global commit ceb21bad7fae52b4422a0350af9488596e278076
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate 20260316

Name:           ANTs3
Version:        3.0.0^%{snapdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Advanced Normalization Tools for medical imaging (ITK 6 branch)

License:        Apache-2.0
URL:            https://github.com/ANTsX/ANTs
Source0:        https://github.com/ANTsX/ANTs/archive/%{commit}/ANTs-%{shortcommit}.tar.gz

# ANTs3 ships the same binaries as ANTs (2.6.5/ITK5); only one can be installed
Conflicts:      ANTs
Conflicts:      ants

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.22
BuildRequires:  make
BuildRequires:  zlib-devel
BuildRequires:  InsightToolkit6-devel >= 6.0.0
# Transitive deps re-found by ITK's cmake config when downstream does include(${ITK_USE_FILE})
BuildRequires:  hdf5-devel
BuildRequires:  fftw-devel
BuildRequires:  expat-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  gdcm-devel
BuildRequires:  dcmtk-devel
BuildRequires:  openjpeg2-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif
# VTK transitive deps (VTK-vtk-module-find-packages.cmake runs find_package for these)
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  json-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  proj-devel
BuildRequires:  libxml2-devel
BuildRequires:  double-conversion-devel

%description
Advanced Normalization Tools (ANTs) extracts information from complex datasets
that include imaging. ANTs computes high-dimensional mappings to capture the
statistics of brain structure and function.

This package is built from the ANTs master branch (post-ITK6 merge) and links
against InsightToolkit 6. It cannot be installed alongside the ANTs 2.6.5
package which links against ITK 5.

%prep
%autosetup -n ANTs-%{commit}
# antsUtilities lacks SOVERSION in upstream cmake; add it so the installed
# libantsUtilities.so.1 has a valid versioned SONAME (Fedora packaging requirement).
sed -i '/^target_link_libraries(antsUtilities/a set_target_properties(antsUtilities PROPERTIES SOVERSION 1)' \
    Examples/CMakeLists.txt

%build
# C++17 required by ITK 6; permissive mode for older ANTs code on GCC 14+/15
export CXXFLAGS="%{optflags} -std=c++17 -fpermissive -Wno-error=incompatible-pointer-types"
export CFLAGS="%{optflags} -std=gnu17 -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"

# Build ANTs directly against system InsightToolkit6 — no superbuild network downloads.
# ANTs_SUPERBUILD=OFF: skip the ExternalProject wrapper and configure ANTs directly.
# ITK_DIR points to the versioned cmake config installed by InsightToolkit6-devel.
%cmake \
    -DANTS_SUPERBUILD=OFF \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-6.0 \
    -DUSE_SYSTEM_ITK:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED:BOOL=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install
# Remove static archives: ANTs' internal l_* libraries are not a public API
find %{buildroot}%{_libdir} -name '*.a' -delete
# Remove unversioned .so symlinks (devel-file-in-non-devel-package rpmlint warning).
# These are internal implementation libraries, not a public development API.
find %{buildroot}%{_libdir} -maxdepth 1 -name '*.so' -type l -delete

%ldconfig_scriptlets

%files
%license COPYING.txt
%doc README.md
%{_bindir}/*
%{_libdir}/libantsUtilities.so.*
%{_libdir}/libl_*.so.*

%changelog
* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 3.0.0^20260316gitceb21bad-1
- Initial ANTs3 package from master branch snapshot (post-ITK6 merge, PR 1933)
- Build against InsightToolkit6-devel (ITK 6.0 beta) instead of ITK 5
- ANTs_SUPERBUILD=OFF with system ITK (Fedora policy: no network downloads in build)
- Conflicts with ANTs 2.6.5 (same binary names)
