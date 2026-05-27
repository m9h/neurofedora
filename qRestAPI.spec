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
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
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

%build
%cmake -G Ninja \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DqRestAPI_QT_VERSION:STRING=6 \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE_Apache_20.txt
%doc README.md
%{_libdir}/libqRestAPI.so.*

%files devel
%{_includedir}/qRestAPI*.h
%{_includedir}/qRestResult.h
%{_includedir}/qGirderAPI.h
%{_includedir}/qMidasAPI.h
%{_libdir}/libqRestAPI.so
%{_libdir}/cmake/qRestAPI

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20251018git88c02c5d
- Initial COPR package. Pinned to the commit 3D Slicer 5.10 expects.
- Built against Qt6 (qRestAPI_QT_VERSION=6).
- BUILD_TESTING off — upstream tests hit live REST endpoints.
