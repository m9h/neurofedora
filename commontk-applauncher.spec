# Required-by Slicer: launcher binary that sets up the Slicer process
# environment (paths, library dirs, Python paths) before exec'ing the
# real Slicer binary. Also produces a small library (libCTKAppLauncher.so)
# that other CommonTK consumers can link to programmatically launch
# applications with the same env-prep logic.
#
# Upstream (commontk/AppLauncher) is more commonly called "CTKAppLauncher"
# but in Fedora-package-namespace we prefer the commontk-* prefix.

%global commit       a37ad37c06e6fb4fc203434787f8bbffb52749bb
%global shortcommit  %(c=%{commit}; echo ${c:0:8})
%global snapdate     20251018
%global upstream_ver 0.1.34

Name:           commontk-applauncher
Version:        %{upstream_ver}
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        CommonTK launcher for Slicer-style applications

License:        Apache-2.0
URL:            https://github.com/commontk/AppLauncher
Source0:        %{url}/archive/%{commit}/CTKAppLauncher-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.5
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Test)

# Slicer (and other consumers) call find_package(CTKAppLauncher) which
# expects the executable + cmake helper modules at known paths. We install
# everything into Fedora-standard locations and let the cmake config
# translate.
Requires:       qt6-qtbase

%description
CTKAppLauncher is a small Qt-based binary used by 3D Slicer (and other
CommonTK applications) to set up the run-time environment of a larger
application: extending LD_LIBRARY_PATH, PATH, PYTHONPATH, and other
variables from a settings file before exec'ing the real binary. The
launcher is what users actually invoke as `Slicer`; it then chains into
`SlicerApp-real`.

This package ships both the standalone CTKAppLauncher binary and the
libCTKAppLauncher shared library so consumers can launch applications
programmatically without forking.

%package devel
Summary:        Development files for CTKAppLauncher
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers, cmake configuration files, and the shared-library symlink for
linking against libCTKAppLauncher.

%prep
%autosetup -n AppLauncher-%{commit} -p1

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCTKAppLauncher_QT_VERSION:STRING=6 \
    -DBUILD_TESTING:BOOL=OFF \
    -DCTKAppLauncher_INSTALL_LauncherLibrary:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/CTKAppLauncher
%{_libdir}/libCTKAppLauncher.so.*

%files devel
%{_includedir}/ctkAppLauncher*.h
%{_libdir}/libCTKAppLauncher.so
%{_datadir}/CTKAppLauncher
# upstream installs cmake config files into share/ or lib/cmake depending
# on the layout; pick one with a wildcard if both end up present.
%{_libdir}/cmake/CTKAppLauncher

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.34-0.1.20251018gita37ad37c
- Initial COPR package. Pinned to the commit 3D Slicer 5.10 expects.
- Build the launcher lib (CTKAppLauncher_INSTALL_LauncherLibrary=ON) so
  Slicer can link libCTKAppLauncher without bundling its own copy.
- Qt6 (CTKAppLauncher_QT_VERSION=6).
