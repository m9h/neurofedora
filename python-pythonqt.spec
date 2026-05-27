# PythonQt — Python bindings for Qt6, required by 3D Slicer's PythonQt-
# based scripted module / extension system, and by CTK's PythonQt wrapper.
#
# Upstream: commontk/PythonQt — Slicer and CTK both use this fork.
# Branch:   patched-v4.0.1-2026-03-16-5cd9b581f (Qt6-capable; introduces
#           PythonQt_QT_VERSION cmake variable that accepts 5 or 6).
#
# Patched-9 (the previous "stable" branch) hardcodes Qt5; we require
# v4.0.1 specifically for Qt6 support.

%global commit       7ef4c5ee066b8ef1e7dc609b14071d504f59d4ba
%global shortcommit  7ef4c5ee
%global snapdate     20260329

Name:           python-pythonqt
Version:        4.0.1
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Python bindings for Qt — dynamic Python/Qt object interop

License:        LGPL-2.1-only
URL:            https://github.com/commontk/PythonQt
Source0:        %{url}/archive/%{commit}/PythonQt-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.5
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel

BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Sql)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6Xml)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6Multimedia)
BuildRequires:  cmake(Qt6MultimediaWidgets)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickWidgets)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6PrintSupport)
BuildRequires:  cmake(Qt6Core5Compat)
BuildRequires:  cmake(Qt6Test)
BuildRequires:  cmake(Qt6UiTools)

Requires:       qt6-qtbase

%description
PythonQt is a dynamic Python binding for the Qt framework. It enables
embedding Python into Qt applications (such as 3D Slicer's scripted
module interpreter) and exposing Qt classes to Python at runtime,
without the SIP / static-binding overhead.

Used by 3D Slicer, the Common Toolkit (CTK), MITK, and several other
Qt-based research applications.

This build targets Qt6.

%package devel
Summary:        Development files for PythonQt
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(Qt6Core)

%description devel
Headers and link-time symlinks for embedding PythonQt into Qt6
applications. Use CTK's FindPythonQt.cmake module with
PYTHONQT_INSTALL_DIR=/usr to consume from a CMake project.

%prep
%autosetup -p1 -n PythonQt-%{commit}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPythonQt_QT_VERSION:STRING=6 \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DPythonQt_INSTALL_LIBRARY_DIR:PATH=%{_lib} \
    -DPythonQt_INSTALL_ARCHIVE_DIR:PATH=%{_lib} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license COPYING
%doc README.md
%{_libdir}/libPythonQt*.so.*

%files devel
%{_includedir}/PythonQt/
%{_libdir}/libPythonQt*.so

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.1.20260329git7ef4c5ee
- Switch to commontk/PythonQt patched-v4.0.1 (Qt6-capable) from the
  Qt5-only patched-9 branch.
- Set PythonQt_QT_VERSION=6 for Qt6 build.
- Build needed by 3D Slicer 5.10+/main and CTK Qt6 builds.
