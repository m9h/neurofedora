%global commit cf5fa4156734edb9c3515c7104c19783b17ed0c1
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260328

# Upstream ships no released version; the library carries no SONAME of its own.
# Inject VERSION/SOVERSION (see %prep) so the shared object is versioned per
# Fedora policy: libqttesting.so.0 (runtime) + libqttesting.so (devel symlink).
%global sover 0

Name:           qttesting
Version:        0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Qt GUI event record/replay testing library (Kitware/commontk)

# Copyright.txt is 3-clause BSD (Kitware Inc.)
License:        BSD-3-Clause
URL:            https://github.com/commontk/QtTesting
Source0:        %{url}/archive/%{commit}/QtTesting-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  chrpath
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)

%description
QtTesting is Kitware's Qt GUI testing framework, used to record and replay
user-interface events for automated regression testing of Qt applications.
It is a build dependency of CTK (CTK_USE_QTTESTING) and, through CTK, of the
3D Slicer GUI test suite. This package provides the Qt6 build.

%package devel
Summary:        Development files for qttesting
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(Qt6Widgets)

%description devel
Headers and CMake package configuration files for developing against
QtTesting (Qt6).

%prep
%autosetup -n QtTesting-%{commit}

# Upstream sets no SONAME on the library target; Fedora requires a versioned
# SONAME for shared libraries. Inject VERSION/SOVERSION right after the
# non-VTK-embedded build branch creates the target.
sed -i '/add_library(QtTesting ALIAS qttesting)/a\    set_target_properties(qttesting PROPERTIES VERSION %{version}.0.%{sover} SOVERSION %{sover})' CMakeLists.txt

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DQtTesting_QT_VERSION:STRING=6 \
    -DQT_TESTING_WITH_PYTHON:BOOL=OFF \
    -DQtTesting_INSTALL_LIB_DIR:STRING=%{_lib} \
    -DQtTesting_INSTALL_CMAKE_DIR:STRING=%{_lib}/cmake/qttesting \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

# Belt-and-suspenders RPATH strip
chrpath --delete %{buildroot}%{_libdir}/libqttesting.so.* 2>/dev/null || :

%files
%license Copyright.txt
%{_libdir}/libqttesting.so.%{sover}
%{_libdir}/libqttesting.so.%{version}.0.%{sover}

%files devel
%{_includedir}/QtTesting/
%{_libdir}/libqttesting.so
%{_libdir}/cmake/qttesting/

%changelog
* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260328gitcf5fa41
- Initial package: commontk/QtTesting master (cf5fa41), Qt6 build
- Dependency for CTK_USE_QTTESTING=ON -> 3D Slicer GUI test suite
- Inject SONAME (SOVERSION 0); install to %%{_libdir}; strip RPATH
