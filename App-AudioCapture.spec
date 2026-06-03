%global commit 47b51677117c1a993dd23514a5af401609ff6401
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260602

Name:           App-AudioCapture
Version:        0.2.0
Release:        1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Capture audio and stream it over the Lab Streaming Layer (LSL)

License:        MIT
URL:            https://github.com/labstreaminglayer/App-AudioCapture
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
# C++20 helpers (qt_add_executable, install path normalization, LSL_*).
# liblsl >= 1.17.7-2 installs LSLCMake.cmake at /usr/lib64/cmake/lsl/.
BuildRequires:  liblsl-devel >= 1.17.7
# Qt6
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtmultimedia-devel

Requires:       liblsl%{?_isa} >= 1.17.7
Requires:       hicolor-icon-theme

%description
AudioCapture streams microphone audio over the Lab Streaming Layer (LSL).
It is one of the standard reference applications maintained by the
labstreaminglayer project.

%prep
%autosetup -p1 -n %{name}-%{commit}

# Upstream CMakeLists has two paths: pre-installed liblsl, or FetchContent
# from GitHub.  Force the pre-installed path (mock/COPR has no network).
# The default LSL_INSTALL_ROOT="" triggers FetchContent; we pass the real
# path via -DLSL_INSTALL_ROOT below.
#
# Strip out the macOS / Windows-only deployment helpers (LSL_install_liblsl,
# LSL_deploy_qt, LSL_install_mingw_runtime, LSL_codesign).  Linux already
# has liblsl in /usr/lib64 via the liblsl package; copying it again would
# create a duplicate file outside /usr/lib64 and fail the install.
sed -i \
    -e '/^LSL_install_liblsl(/,/^)/ d' \
    -e '/^LSL_deploy_qt(/,/^)/ d' \
    -e '/^LSL_install_mingw_runtime(/,/^)/ d' \
    -e '/^LSL_codesign(/,/^)/ d' \
    CMakeLists.txt

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DLSL_INSTALL_ROOT=%{_prefix} \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DQt6_DIR=%{_libdir}/cmake/Qt6

%cmake_build

%install
%cmake_install

# CMakeLists installs the executable in %%{_bindir} (GNUInstallDirs path on Linux).
# Belt-and-braces: strip any RPATH if the SKIP_INSTALL_RPATH flag was ignored.
chrpath --delete %{buildroot}%{_bindir}/AudioCapture 2>/dev/null || :

# Create a Desktop Entry
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=AudioCapture
Comment=Stream microphone audio over LSL
Exec=AudioCapture
Icon=audio-input-microphone
Terminal=false
Type=Application
Categories=Science;AudioVideo;
EOF

%files
%license LICENSE
%doc README.md
%{_bindir}/AudioCapture
%{_datadir}/applications/%{name}.desktop

%changelog
* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.0-1.20260602git47b5167
- Initial RPM package for App-AudioCapture (master commit 47b5167).
- Force pre-installed liblsl path (disable FetchContent), strip
  Linux-no-op deployment helpers, drop RPATH.
