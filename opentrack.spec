Name:           opentrack
Version:        2026.1.0
Release:        3%{?dist}
Summary:        Head tracking software for game and flight simulators

# Per OPENTRACK-LICENSING.txt the project is a collage of per-module licenses.
# The dominant licenses for the modules built on Linux (core, gui, most
# trackers/protocols/filters) are ISC and GPL-3.0-or-later (e.g. proto-ft,
# tracker-aruco wrapper). Bundled third-party code in 3rdparty-notices/
# (Aruco fork, FaceTrackNoIR, libQxt, NPClient, FreePIE, FreeTrack, etc.) is
# either ISC, BSD-2-Clause or GPL-3.0-or-later. We pick the most-restrictive
# union that covers what gets actually compiled into the binary RPM.
License:        ISC AND GPL-3.0-or-later AND BSD-2-Clause AND BSD-3-Clause

# Bundled libraries shipped in the binary RPM. qxt-mini is vendored
# under qxt-mini/ in the upstream source tree; its license (BSD-3-Clause)
# is already covered by the License: expression above.
Provides:       bundled(qxt-mini)

URL:            https://github.com/opentrack/opentrack
# GitHub auto-generated tarball for the "opentrack-2026.1.0" tag unpacks to
# opentrack-opentrack-2026.1.0/.
Source0:        %{url}/archive/opentrack-%{version}/opentrack-%{version}.tar.gz

# Local desktop entry + AppStream metainfo (upstream ships none).
Source10:       opentrack.desktop
Source11:       opentrack.metainfo.xml

BuildRequires:  cmake >= 3.21
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  pkgconfig
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# Qt6 — Core, Gui, Widgets, Network, LinguistTools are mandatory in
# cmake/opentrack-qt.cmake; SerialPort is optional but enables the Arduino
# tracker (tracker-hatire); Qt6 GuiPrivate ships with qt6-qtbase-private-devel.
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6LinguistTools)
BuildRequires:  cmake(Qt6SerialPort)
BuildRequires:  qt6-qtbase-private-devel

# OpenCV for tracker-pt (PointTracker) and several optional video trackers.
BuildRequires:  opencv-devel

# Linux-only modules
BuildRequires:  pkgconfig(libevdev)
BuildRequires:  pkgconfig(libproc2)
BuildRequires:  pkgconfig(x11)

# PS3 eye driver subprocess (video-ps3eye)
BuildRequires:  libusb1-devel

Requires:       hicolor-icon-theme

%description
opentrack tracks head motion in space and broadcasts position and rotation to
flight and racing simulators. It supports a wide variety of input devices
(webcams, IR-LED point trackers, Arduino hardware, gamepads, IMUs) and output
protocols (freetrack, TrackIR/NPClient, UDP, joystick, X-Plane plugin, etc).

Tracking modules and protocols are loaded as plugins from
%{_libexecdir}/opentrack/. Several modules included in upstream require
proprietary SDKs (Tobii, RealSense, Kinect SDK, Oculus libOVR, Razer Hydra,
TrackHat) or the opentrack Aruco fork; those are omitted from this build.

%prep
%autosetup -n opentrack-opentrack-%{version} -p1

# Replace upstream's git-describe-driven version string with the release tag.
# Without this, opentrack-version.cmake leaves OPENTRACK_VERSION empty when
# building from a tarball outside a git checkout (mock/COPR).
cat > cmake/opentrack-version.cmake <<'EOF'
include_guard(GLOBAL)
set(OPENTRACK_COMMIT "opentrack-%{version}")
file(WRITE ${CMAKE_BINARY_DIR}/opentrack-version.hxx "#define OPENTRACK_VERSION \"${OPENTRACK_COMMIT}\"")
set(version-string "\
#ifdef __cplusplus
extern \"C\"
#else
extern
#endif

const char* const opentrack_version;
const char* const opentrack_version = \"${OPENTRACK_COMMIT}\";
")
set(file "${CMAKE_CURRENT_BINARY_DIR}/version.cpp")
set(crapola-ver)
if(EXISTS "${file}")
    file(READ "${file}" crapola-ver)
endif()
if(NOT (crapola-ver STREQUAL version-string))
    file(WRITE "${file}" "${version-string}")
endif()
add_library(opentrack-version STATIC "${file}")
if(NOT MSVC)
    target_compile_options(opentrack-version PRIVATE -fno-lto)
endif()
EOF

# Upstream's top-level CMakeLists hard-codes "-O3 -march=native" for GCC.
# Replace with Fedora optflags so the binary RPM is portable (no AVX/FMA
# requirements baked in) and so %{optflags}/_FORTIFY_SOURCE survive.
sed -i \
    -e 's/-O3 -march=native//' \
    -e 's|set(CMAKE_${i}_FLAGS_RELEASE.*CACHE STRING.*FORCE)|#&|' \
    -e 's|set(CMAKE_${i}_FLAGS .*-ggdb -Wall -Wextra -Wpedantic.*CACHE STRING.*FORCE)|#&|' \
    CMakeLists.txt

# linux.cmake forces a global "-ffast-math -O3 -flto" CXX_FLAGS_RELEASE and
# hard-codes ~/dev/opentrack-depends/opencv/build for OpenCV_DIR. It is only
# included by sdk-paths-*.cmake user files we don't ship — but neutralise it
# anyway in case anything else picks it up.
: > cmake/linux.cmake

# Drop the Windows-only loader DLLs (freetrackclient*.dll, NPClient*.dll,
# TrackIR.exe) that opentrack-install.cmake installs into libexec on every
# platform. We don't want those in the Linux RPM. Trim from the
# "this must be done last" comment which immediately precedes the Windows
# install blocks; the cleanup_visual_studio_debug() function is unused
# outside Windows so dropping it is safe.
sed -i '/^# this must be done last/,$ d' cmake/opentrack-install.cmake

%build
# -fpermissive: opentrack uses C++20 and some bundled vendor headers still
# trip the stricter GCC 14/15 parser.
# -Wno-error=template-id-cdtor and -Wno-error=narrowing: silence breaking
# changes in GCC 15 that opentrack hasn't caught up to yet.
export CXXFLAGS="%{optflags} -Wno-error -fpermissive"
export CFLAGS="%{optflags} -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"

# __otr_compile_flags_set short-circuits the -O3 -march=native block in the
# top-level CMakeLists.txt (defence in depth in case the sed above misses).
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_SKIP_INSTALL_RPATH=OFF \
    -DCMAKE_INSTALL_RPATH="%{_libexecdir}/opentrack" \
    -D__otr_compile_flags_set:BOOL=TRUE \
    -DSDK_WINE:BOOL=OFF \
    -DSDK_XPLANE:BOOL=OFF

%cmake_build

%install
%cmake_install

# Defensive: remove any Windows artefacts that slipped through (the install
# patch above should already prevent this).
rm -f %{buildroot}%{_libexecdir}/opentrack/freetrackclient*.dll \
      %{buildroot}%{_libexecdir}/opentrack/NPClient*.dll \
      %{buildroot}%{_libexecdir}/opentrack/TrackIR.exe \
      %{buildroot}%{_libexecdir}/opentrack/qt.conf || :

# Icon (hicolor 256x256 — upstream's icon is a 256-px PNG)
install -Dpm 0644 gui/images/opentrack.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/opentrack.png

# Desktop entry
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE10}

# AppStream metainfo
install -Dpm 0644 %{SOURCE11} \
    %{buildroot}%{_metainfodir}/opentrack.metainfo.xml
appstream-util validate-relax --nonet \
    %{buildroot}%{_metainfodir}/opentrack.metainfo.xml || :

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/opentrack.desktop

%files
%license OPENTRACK-LICENSING.txt
%license WARRANTY.txt
%doc README.md AUTHORS.md
%doc %{_docdir}/opentrack/3rdparty-notices/
%doc %{_docdir}/opentrack/settings/
%{_bindir}/opentrack
%dir %{_libexecdir}/opentrack/
%{_libexecdir}/opentrack/*.so
%dir %{_libexecdir}/opentrack/presets/
%{_libexecdir}/opentrack/presets/*
%{_datadir}/opentrack/i18n/
%{_datadir}/applications/opentrack.desktop
%{_datadir}/icons/hicolor/256x256/apps/opentrack.png
%{_metainfodir}/opentrack.metainfo.xml
# README files re-installed under share/doc/opentrack/ by upstream's
# opentrack-install.cmake — claimed via %doc/%license above (the README.md
# and OPENTRACK-LICENSING.txt under share/doc/opentrack/ are duplicates of
# the ones in the source root). Suppress the duplicate-listing warning by
# explicitly excluding them here.
%exclude %{_docdir}/opentrack/README.md
%exclude %{_docdir}/opentrack/CONTRIBUTING.md
%exclude %{_docdir}/opentrack/WARRANTY.txt
%exclude %{_docdir}/opentrack/OPENTRACK-LICENSING.txt
%exclude %{_docdir}/opentrack/AUTHORS.md

%changelog
* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.1.0-3
- Add pkgconfig(libproc2) BuildRequires. Build 10561394 failed at
  cmake configure: compat/CMakeLists.txt:21 demands libproc2 or
  libprocps for process enumeration on Linux.

* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.1.0-2
- Add Provides: bundled(qxt-mini). qxt-mini is vendored under qxt-mini/
  in the upstream source tree and shipped in the binary RPM; Fedora
  packaging policy requires an explicit bundled() Provides for every
  bundled library. License (BSD-3-Clause) is already covered by the
  existing License: expression.

* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.1.0-1
- Initial package for opentrack 2026.1.0
