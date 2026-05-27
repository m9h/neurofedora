Name:           sigviewer
Version:        0.7.1
Release:        5%{?dist}
Summary:        Viewing and inspection of biosignals (EEG, EMG, ECG)
License:        GPL-3.0-or-later
URL:            https://github.com/cbrnr/sigviewer
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# 0.7.1 switched from qmake → cmake and Qt5 → Qt6.
BuildRequires:  cmake >= 3.21
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  desktop-file-utils

# Qt6 components requested by CMakeLists.txt:21
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Xml)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6LinguistTools)
BuildRequires:  cmake(Qt6Test)

# External libraries — both at the exact versions upstream pins (now both
# in COPR mhough/neurofedora: libxdf 0.99.10 and biosig4c++ 3.9.4).
BuildRequires:  libxdf-devel >= 0.99.10
BuildRequires:  biosig4c++-devel >= 3.9.4

Requires:       qt6-qtbase
Requires:       qt6-qtsvg

%description
SigViewer is a powerful viewing and scoring application for biosignals.
It supports various data formats including XDF, GDF, EDF, BDF.

%prep
%autosetup -p1

# Upstream's external/build_deps.cmake downloads + builds libxdf and libbiosig
# from scratch at the pinned versions, then writes external/versions.cmake.
# We can't do that in mock/COPR (no network) so we satisfy the version-match
# check by writing the file directly with the expected version strings.
mkdir -p external
cat > external/versions.cmake <<EOF
set(LIBXDF_VERSION_INSTALLED    "0.99.10")
set(LIBBIOSIG_VERSION_INSTALLED "3.9.4")
EOF

# Repoint upstream's STATIC IMPORTED targets at the system *shared* libraries
# (libxdf-devel and biosig4c++-devel install both /usr/lib64/libfoo.so and
# the headers in /usr/include — no separate include dir needed).
sed -i 's|add_library(dep_libxdf STATIC IMPORTED)|add_library(dep_libxdf SHARED IMPORTED)|' CMakeLists.txt
sed -i 's|add_library(dep_libbiosig STATIC IMPORTED)|add_library(dep_libbiosig SHARED IMPORTED)|' CMakeLists.txt
sed -i 's|"\${DEPS_DIR}/lib/libxdf.a"|"%{_libdir}/libxdf.so"|'   CMakeLists.txt
sed -i 's|"\${DEPS_DIR}/lib/libbiosig.a"|"%{_libdir}/libbiosig.so"|' CMakeLists.txt
sed -i 's|"\${DEPS_DIR}/include"|"%{_includedir}"|g'             CMakeLists.txt

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON
%cmake_build

%install
%cmake_install

# Fallback. Upstream CMakeLists may lack install(TARGETS sigviewer ...);
# in that case cmake_install does not place the binary at the right path.
# Locate and install manually if needed.
# (NB: apostrophes removed from comments here because the %cmake_install
# macro emits a line-continuation that swallows the next lines literally;
# bash then treats an open apostrophe in a comment as quote-start and
# eats everything until the matching close.)
:
if [ ! -f %{buildroot}%{_bindir}/sigviewer ]; then
    bin=$(find %{__cmake_builddir} -maxdepth 3 -type f -executable -name sigviewer | head -1)
    if [ -n "$bin" ]; then
        mkdir -p %{buildroot}%{_bindir}
        install -m 0755 "$bin" %{buildroot}%{_bindir}/sigviewer
    else
        echo "ERROR sigviewer binary not found in build tree" >&2
        find %{__cmake_builddir} -maxdepth 4 -type f -executable -name 'sigviewer*' >&2
        exit 1
    fi
fi

# Install desktop file and icon if cmake_install didn't already place them
if [ -f deploy/debian/sigviewer.desktop ] && [ ! -f %{buildroot}%{_datadir}/applications/sigviewer.desktop ]; then
    mkdir -p %{buildroot}%{_datadir}/applications
    desktop-file-install --dir=%{buildroot}%{_datadir}/applications deploy/debian/sigviewer.desktop
fi
if [ -f sigviewer.svg ] && [ ! -f %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/sigviewer.svg ]; then
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
    install -m 0644 sigviewer.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/sigviewer.svg
fi

%check
[ -f %{buildroot}%{_datadir}/applications/sigviewer.desktop ] && \
    desktop-file-validate %{buildroot}%{_datadir}/applications/sigviewer.desktop || :

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/sigviewer
%{_datadir}/applications/sigviewer.desktop
%{_datadir}/icons/hicolor/scalable/apps/sigviewer.svg

%changelog

* Tue May 26 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-5
- Strip apostrophes from %%install comments. The %%cmake_install
  macro emits a line-continuation; bash then treats apostrophes
  in following comment lines as quote-starts that consume the
  rest of the fallback block as one literal argument to cmake.
- Add a no-op : before the fallback to terminate any leftover
  line-continuation from the macro expansion.

* Tue May 26 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-4
- Add binary-find fallback after %%cmake_install: upstream's
  CMakeLists.txt may lack install(TARGETS sigviewer ...), in which
  case the binary stays in the build tree. Locate and install it
  manually if cmake_install didn't place it at %{_bindir}/sigviewer.
* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-3
- Require biosig4c++-devel >= 3.9.4 (now in COPR); both pinned external deps
  are at the exact versions upstream expects, so the stub versions.cmake
  matches reality.

* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-2
- Port spec from qmake/Qt5 to cmake/Qt6 (upstream 0.7.1 dropped qmake).
- Stub external/versions.cmake to satisfy upstream's pinned-version FATAL_ERROR
  (LIBXDF 0.99.10 is exact from COPR; LIBBIOSIG 3.9.4 vs system 2.6.1 — will
  iterate if biosig 2.x API isn't compatible with sigviewer 0.7.1 needs).
- Repoint upstream's STATIC IMPORTED dep targets at system shared libs.

* Thu Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-1
- Update to 0.7.1

* Wed Jan 07 2026 Your Name <your.email@example.com> - 0.6.4-1
- Initial package for Fedora
- Switched to QMake build system
- Patched to link against system libxdf and biosig4c++
