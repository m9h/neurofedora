# PythonQt — Python bindings for Qt6, required by 3D Slicer's
# PythonQt-based scripted module / extension system.
#
# Upstream: commontk/PythonQt — Slicer + CTK both use this fork, on the
# `patched-9` branch (latest stable Qt6-capable). Maintained by Kitware
# and contributors.

%global commit       7f7105ba
%global longcommit   7f7105ba9ec59d719ded80090e049fa85ad76e79
%global snapdate     20240329

Name:           python-pythonqt
Version:        0
Release:        0.1.%{snapdate}git%{commit}%{?dist}
Summary:        Python bindings for Qt — dynamic Python/Qt object interop

License:        LGPL-2.1-only
URL:            https://github.com/commontk/PythonQt
Source0:        %{url}/archive/%{commit}/PythonQt-%{commit}.tar.gz

BuildRequires:  cmake >= 3.5
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  python3-numpy

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
BuildRequires:  cmake(Qt6Quick)
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

%package devel
Summary:        Development files for PythonQt
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(Qt6Core)

%description devel
Headers, cmake configuration files, and link-time symlinks for embedding
PythonQt into Qt6 applications.

%prep
%autosetup -p1 -n PythonQt-%{longcommit}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPythonQt_Qt_VERSION:STRING=6 \
    -DPythonQt_QT_VERSION:STRING=6 \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DPythonQt_INSTALL_HEADERS:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE_LGPL
%doc README.md
%{_libdir}/libPythonQt*.so.*

%files devel
%{_includedir}/PythonQt/
%{_libdir}/libPythonQt*.so
%{_libdir}/cmake/PythonQt/

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20240329git7f7105ba
- Initial COPR package. commontk/PythonQt patched-9 branch (Qt6-capable).
- Required-by 3D Slicer, CTK, MITK.
