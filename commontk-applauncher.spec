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
Release:        0.5.%{snapdate}git%{shortcommit}%{?dist}
Summary:        CommonTK launcher for Slicer-style applications

License:        Apache-2.0
URL:            https://github.com/commontk/AppLauncher
Source0:        %{url}/archive/%{commit}/CTKAppLauncher-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.5
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
# %prep does git init + tag so ctkVersionSource.cmake (which runs
# git describe) is happy
BuildRequires:  git-core
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

# Upstream's CMake/ctkVersionSource.cmake runs `git describe` to derive
# the version string at configure time and aborts hard if the source
# isn't a git tree. Tarball extracts aren't git — fake the minimum by
# initialising a throw-away repo and tagging it with our version.
git init -q
git config user.email rpmbuild@invalid
git config user.name 'RPM Build'
git add -A
git commit -q -m 'snapshot' --no-gpg-sign
git tag -a "v%{upstream_ver}" -m 'snapshot tag for ctkVersionSource'

%build
# Upstream installs to non-standard paths by default: /usr/CMake/, /usr/./,
# and /usr/lib/ (not arch lib64). Set the *_INSTALL_*_DIR vars explicitly
# to land everything in Fedora-policy locations.
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCTKAppLauncher_QT_VERSION:STRING=6 \
    -DBUILD_TESTING:BOOL=OFF \
    -DCTKAppLauncher_INSTALL_LauncherLibrary:BOOL=ON \
    -DCTK_INSTALL_BIN_DIR:STRING=bin \
    -DCTK_INSTALL_LIB_DIR:STRING=%{_lib} \
    -DCTK_INSTALL_INCLUDE_DIR:STRING=include/CTKAppLauncher \
    -DCTK_INSTALL_CMAKE_DIR:STRING=%{_lib}/cmake/CTKAppLauncher \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

# Upstream places assorted top-level *Config.cmake at /usr/./ (both
# CTKAppLauncherConfig.cmake and CTKAppLauncherLibConfig.cmake). Sweep
# anything at the bare /usr/ root into the canonical cmake dir.
mkdir -p %{buildroot}%{_libdir}/cmake/CTKAppLauncher
for f in %{buildroot}%{_prefix}/*Config*.cmake; do
    [ -f "$f" ] && mv "$f" %{buildroot}%{_libdir}/cmake/CTKAppLauncher/
done
# .ini.in template — move out of bin to share
mkdir -p %{buildroot}%{_datadir}/CTKAppLauncher
if [ -f %{buildroot}%{_bindir}/CTKAppLauncherSettings.ini.in ]; then
    mv %{buildroot}%{_bindir}/CTKAppLauncherSettings.ini.in \
       %{buildroot}%{_datadir}/CTKAppLauncher/
fi

%files
%license LICENSE_Apache_20
%doc README.md
%{_bindir}/CTKAppLauncher
%{_datadir}/CTKAppLauncher/

%files devel
%{_includedir}/CTKAppLauncher/
# upstream builds a STATIC archive (libCTKAppLauncherLib.a), not .so.
%{_libdir}/libCTKAppLauncherLib.a
%dir %{_libdir}/cmake/CTKAppLauncher
%{_libdir}/cmake/CTKAppLauncher/*.cmake

%changelog

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.34-0.5.20251018gita37ad37c
- Glob ALL /usr/*Config*.cmake into lib64/cmake/CTKAppLauncher/
  (upstream drops both CTKAppLauncherConfig.cmake AND -LibConfig.cmake
  at the bare /usr root).

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.34-0.4.20251018gita37ad37c
- Set CTK_INSTALL_*_DIR vars to Fedora-policy paths (was /usr/CMake/).
- Move CTKAppLauncherSettings.ini.in into %%{_datadir}/CTKAppLauncher/.
- License file is LICENSE_Apache_20 (not LICENSE).
- Library is the STATIC libCTKAppLauncherLib.a — keep in -devel.


* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.34-0.2.20251018gita37ad37c
- Initialise a throwaway git repo in %%prep so ctkVersionSource.cmake
  can git-describe a version (upstream aborts hard otherwise).
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.34-0.1.20251018gita37ad37c
- Initial COPR package. Pinned to the commit 3D Slicer 5.10 expects.
- Build the launcher lib (CTKAppLauncher_INSTALL_LauncherLibrary=ON) so
  Slicer can link libCTKAppLauncher without bundling its own copy.
- Qt6 (CTKAppLauncher_QT_VERSION=6).
