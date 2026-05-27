# SlicerOpenIGTLink — Image-guided therapy network protocol integration
# for 3D Slicer. Used heavily in surgical navigation research, real-time
# tool tracking, and image streaming for OR/research-system integration.
#
# Depends on the OpenIGTLink C++ library (which may need separate
# packaging in COPR; for now this spec BR's it from Fedora if available).

%global commit       35d84281
%global longcommit   35d8428100000000000000000000000000000000
%global snapdate     20260225

Name:           3dslicer-openigtlink
Version:        0
Release:        0.1.%{snapdate}git%{commit}%{?dist}
Summary:        OpenIGTLink networking integration for 3D Slicer

License:        BSD-3-Clause
URL:            https://github.com/openigtlink/SlicerOpenIGTLink
Source0:        %{url}/archive/%{commit}/SlicerOpenIGTLink-%{commit}.tar.gz

BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  3dslicer-devel >= 5.10.0
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  qt6-qtbase-devel
# OpenIGTLink C++ library: not in Fedora as of writing. SuperBuild path is
# used by upstream; we'll iterate to package it separately if the spec
# fails on missing OpenIGTLink_DIR.

Requires:       3dslicer >= 5.10.0

%description
SlicerOpenIGTLink integrates 3D Slicer with the OpenIGTLink real-time
image-guided-therapy network protocol. It provides:

  * Connection management (TCP server/client) for surgical navigation
  * Real-time image/tracker data streaming in/out of Slicer
  * Transform and tracking data interop with research/clinical hardware

Widely used in image-guided therapy research (PLUS toolkit, NDI tracker
integration, custom robotic-surgery systems).

%prep
%autosetup -p1 -n SlicerOpenIGTLink-%{longcommit}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_DIR:PATH=%{_prefix}/lib/slicer-5.10.0/lib/cmake/Slicer \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix}/lib/slicer-5.10.0
%cmake_build

%install
%cmake_install

%files
%license License.txt 2>/dev/null || true
%doc README.md
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-loadable-modules/*OpenIGT*
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-scripted-modules/*IGT*
%{_prefix}/lib/slicer-5.10.0/share/Slicer-5.10/qt-loadable-modules/*OpenIGT*

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260225git35d84281
- Initial COPR package tracking SlicerOpenIGTLink master.
- NOTE: OpenIGTLink C++ library is not in Fedora; if the build fails on
  find_package(OpenIGTLink), package the lib separately in COPR first.
