# SlicerElastix — Image registration GUI for 3D Slicer that wraps the
# Elastix registration library. Mostly scripted Python module; pulls in
# elastix binary as a runtime Requires (we already package elastix).

%global commit       507db199
%global longcommit   507db19900000000000000000000000000000000
%global snapdate     20260218

Name:           3dslicer-elastix
Version:        0
Release:        0.1.%{snapdate}git%{commit}%{?dist}
Summary:        Elastix registration integration for 3D Slicer

License:        BSD-3-Clause
URL:            https://github.com/lassoan/SlicerElastix
Source0:        %{url}/archive/%{commit}/SlicerElastix-%{commit}.tar.gz

BuildArch:      noarch
BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  3dslicer-devel >= 5.10.0

Requires:       3dslicer >= 5.10.0
Requires:       elastix >= 5.3

%description
SlicerElastix wraps the Elastix image-registration library inside 3D
Slicer's GUI. Provides:

  * Preset parameter files for common registration tasks (rigid, affine,
    BSpline, multi-resolution)
  * Forward/inverse transform application
  * Bidirectional batch processing

Elastix itself runs as an external CLI (the elastix binary, which we
package separately in this COPR).

%prep
%autosetup -p1 -n SlicerElastix-%{longcommit}

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
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-scripted-modules/Elastix*
%{_prefix}/lib/slicer-5.10.0/share/Slicer-5.10/qt-scripted-modules/Elastix*

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260218git507db199
- Initial COPR package tracking SlicerElastix master.
- Pure-Python scripted module; runtime-Requires elastix from this COPR.
