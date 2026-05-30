# Required-by Slicer: extension manager / app update REST client.
# Upstream has no tagged releases — pin to the commit Slicer pins so the
# ABI matches what Slicer expects, plus a snapshot-date for clarity.
#
# (Slicer's External_qRestAPI.cmake explicitly says
#  "Enabling Slicer_USE_SYSTEM_qRestAPI is not supported !" — meaning it
#  doesn't expose a system-path build option for itself. We override that
#  in our Slicer spec by injecting -DSlicer_USE_SYSTEM_qRestAPI=ON; the
#  underlying CMake module just does find_package(qRestAPI) so the
#  system-package path works regardless of upstream's warning text.)

%global commit       88c02c5d90169dfe065fa068969e59ada314d3cb
%global shortcommit  %(c=%{commit}; echo ${c:0:8})
%global snapdate     20251018

Name:           qRestAPI
Version:        0
Release:        0.5.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Qt-based REST API client library

License:        Apache-2.0
URL:            https://github.com/commontk/qRestAPI
Source0:        %{url}/archive/%{commit}/qRestAPI-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.5
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6Test)

Requires:       qt6-qtbase
Requires:       qt6-qtdeclarative

%description
qRestAPI is a small Qt-based library for invoking REST APIs. It is used by
3D Slicer's extension manager and application-update facility, and by
several CommonTK consumers (CTK).

%package devel
Summary:        Development files for qRestAPI
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(Qt6Core)
Requires:       cmake(Qt6Network)

%description devel
Headers, the qRestAPIConfig.cmake config file, and the shared library
symlink needed to link against qRestAPI from other Qt6 applications.

%prep
%autosetup -n qRestAPI-%{commit} -p1

# qRestAPI has no SONAME versioning (links with -soname,libqRestAPI.so plain),
# so it functionally behaves like an unversioned shared library. The %files
# section ships only libqRestAPI.so (no .so.N variant). Consumers should
# treat the API as pinned via build-time finding (find_package).

%build
%cmake -G Ninja \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DqRestAPI_QT_VERSION:STRING=6 \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
# Upstream's CMakeLists has zero install() rules — the library and headers
# are just produced in the build tree. Hand-install everything.
install -d %{buildroot}%{_libdir}
install -d %{buildroot}%{_includedir}/qRestAPI
install -d %{buildroot}%{_libdir}/cmake/qRestAPI

# Shared lib (no SONAME — upstream links with -soname,libqRestAPI.so plain).
install -m 0755 %{__cmake_builddir}/libqRestAPI.so %{buildroot}%{_libdir}/libqRestAPI.so

# Headers from the source tree plus the generated export header
for h in qRestAPI.h qRestAPI_p.h qRestResult.h qGirderAPI.h qMidasAPI.h; do
    [ -f "$h" ] && install -m 0644 "$h" %{buildroot}%{_includedir}/qRestAPI/
done
install -m 0644 %{__cmake_builddir}/qRestAPI_Export.h %{buildroot}%{_includedir}/qRestAPI/

# Generated cmake config (file name is GenerateqRestAPIConfig.cmake-produced
# qRestAPIConfig.cmake — globs are forgiving here).
for f in %{__cmake_builddir}/qRestAPIConfig*.cmake %{__cmake_builddir}/UseqRestAPI.cmake %{__cmake_builddir}/qRestAPIExports*.cmake; do
    [ -f "$f" ] && install -m 0644 "$f" %{buildroot}%{_libdir}/cmake/qRestAPI/
done

# Upstream's CMakeLists only generates BUILD-tree configs (paths point at
# /builddir/build/BUILD/qRestAPI-0-build/qRestAPI-<commit>/redhat-linux-build/).
# Rewrite those paths to install-tree locations so 3D Slicer's
# find_package(qRestAPI) gets working values. Same applies to
# qRestAPIExports.cmake which carries hardcoded paths in
# INTERFACE_INCLUDE_DIRECTORIES and IMPORTED_LOCATION_NOCONFIG.
BUILDDIR_RE="/builddir/build/BUILD/qRestAPI-0-build/qRestAPI-[a-f0-9]*/redhat-linux-build"
SRCDIR_RE="/builddir/build/BUILD/qRestAPI-0-build/qRestAPI-[a-f0-9]*"
for f in qRestAPIConfig.cmake qRestAPIExports.cmake; do
    sed -i \
        -e "s|${BUILDDIR_RE}/libqRestAPI\.so|%{_libdir}/libqRestAPI.so|g" \
        -e "s|${BUILDDIR_RE}/qRestAPIExports\.cmake|%{_libdir}/cmake/qRestAPI/qRestAPIExports.cmake|g" \
        -e "s|${BUILDDIR_RE}/UseqRestAPI\.cmake|%{_libdir}/cmake/qRestAPI/UseqRestAPI.cmake|g" \
        -e "s|${BUILDDIR_RE};${SRCDIR_RE}|%{_includedir}/qRestAPI|g" \
        -e "s|${BUILDDIR_RE}|%{_libdir}|g" \
        -e "s|${SRCDIR_RE}|%{_includedir}/qRestAPI|g" \
        %{buildroot}%{_libdir}/cmake/qRestAPI/$f
done

%files
%license LICENSE
%doc README.md
%{_libdir}/libqRestAPI.so

%files devel
%{_includedir}/qRestAPI/
%dir %{_libdir}/cmake/qRestAPI
%{_libdir}/cmake/qRestAPI/*.cmake

%changelog

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.5.20251018git88c02c5d
- Also sed-rewrite hardcoded paths in qRestAPIExports.cmake (not just
  Config). The Exports file carries the build-tree paths in
  INTERFACE_INCLUDE_DIRECTORIES and IMPORTED_LOCATION_NOCONFIG,
  surfaced by 3dslicer-17 generate-step with 'Imported target
  qRestAPI includes non-existent path /builddir/.../redhat-linux-build'.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.4.20251018git88c02c5d
- Actually fix the path rewrite. -0.3's sed used %%{__cmake_builddir}
  (the relative subdir name) but the cmake config has the absolute
  /builddir/build/BUILD/... prefix. Match that via a glob with a
  regex-style commit placeholder.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.3.20251018git88c02c5d
- Rewrite hardcoded /builddir/.../redhat-linux-build/ paths in the
  shipped qRestAPIConfig.cmake to install-tree locations (broken — the
  sed pattern didn't match the absolute build path).

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.2.20251018git88c02c5d
- Hand-install lib + headers + cmake config: upstream's CMakeLists
  has zero install() rules. Library has no SONAME versioning
  (built with -soname,libqRestAPI.so plain), so %files ships only
  libqRestAPI.so without .so.N variants.
- License file is LICENSE (not LICENSE_Apache_20.txt).
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20251018git88c02c5d
- Initial COPR package. Pinned to the commit 3D Slicer 5.10 expects.
- Built against Qt6 (qRestAPI_QT_VERSION=6).
- BUILD_TESTING off — upstream tests hit live REST endpoints.
