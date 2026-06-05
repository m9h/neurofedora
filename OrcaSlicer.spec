# OrcaSlicer bundles ~25 dependencies (wxWidgets, Boost, OpenCASCADE, CGAL,
# OpenVDB, TBB, OpenCV, ...) which it builds from source as STATIC libraries and
# links into the final executable. They are not shipped as separate files, so the
# resulting RPM depends only on Fedora system shared libraries at runtime.
#
# NOTE: the %%build phase downloads the bundled-dependency source tarballs from the internet
# (see deps/*/*.cmake). Build this with network access enabled:
#     mock --enable-network ...           (local clean chroot)
#     copr  -> enable "internet access during build" in the project settings
#
# Debuginfo is disabled: the statically-linked binary is large and the vendored
# static libs are not built with Fedora's debug flags, so a debuginfo subpackage
# adds little value here.
%global debug_package %{nil}

# Upstream snapshot this spec was cut from.
%global commit          58a8722a6993de3aff4851137b51102a70dfb7cf
%global shortcommit     58a8722a
%global snapdate        20260604

Name:           OrcaSlicer
Version:        2.4.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Open source slicer for FDM 3D printers

# OrcaSlicer itself is AGPLv3+. It also embeds an Andrew Ellis pressure-advance
# calibration pattern under GPLv3+, and the vendored libraries carry their own
# permissive/copyleft licenses (Boost, MIT, BSD, LGPL, MPL, etc.).
License:        AGPL-3.0-or-later AND GPL-3.0-or-later AND BSL-1.0 AND MIT AND BSD-3-Clause AND LGPL-2.1-or-later AND MPL-2.0
URL:            https://github.com/OrcaSlicer/OrcaSlicer
Source0:        %{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

# --- Build toolchain ---
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  make
BuildRequires:  git
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  m4
BuildRequires:  gettext
BuildRequires:  texinfo
BuildRequires:  file
BuildRequires:  wget
BuildRequires:  perl-FindBin
BuildRequires:  perl-interpreter
BuildRequires:  extra-cmake-modules
BuildRequires:  patchelf
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# --- System library headers required to build (from scripts/linux.d/fedora) ---
BuildRequires:  dbus-devel
BuildRequires:  eglexternalplatform-devel
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-good-gtk
BuildRequires:  gstreamermm-devel
BuildRequires:  gtk3-devel
BuildRequires:  libcurl-devel
BuildRequires:  libmspack-devel
BuildRequires:  libquadmath-devel
BuildRequires:  libsecret-devel
BuildRequires:  libspnav-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  openssl-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  webkit2gtk4.1-devel

# Icon cache / desktop integration help
Requires:       hicolor-icon-theme
# Media playback (calibration help videos, etc.) loads GStreamer plugins at runtime
Recommends:     gstreamer1-plugins-good
Recommends:     gstreamer1-plugins-bad-free

# Vendored (statically linked) dependencies.
Provides:       bundled(wxWidgets) = 3.3.2
Provides:       bundled(boost)
Provides:       bundled(cereal)
Provides:       bundled(cgal)
Provides:       bundled(c-blosc)
Provides:       bundled(draco)
Provides:       bundled(eigen3)
Provides:       bundled(expat)
Provides:       bundled(freetype)
Provides:       bundled(glew)
Provides:       bundled(glfw)
Provides:       bundled(gmp)
Provides:       bundled(libjpeg-turbo)
Provides:       bundled(libnoise)
Provides:       bundled(libpng)
Provides:       bundled(mpfr)
Provides:       bundled(nanosvg)
Provides:       bundled(nlopt)
Provides:       bundled(occt)
Provides:       bundled(opencsg)
Provides:       bundled(opencv)
Provides:       bundled(openexr)
Provides:       bundled(openssl)
Provides:       bundled(openvdb)
Provides:       bundled(qhull)
Provides:       bundled(tbb)
Provides:       bundled(zlib)

%description
OrcaSlicer is an open source slicer for FDM (fused deposition modeling) 3D
printers. It is a fork of Bambu Studio, which itself is based on PrusaSlicer
and Slic3r. OrcaSlicer turns 3D models (STL, 3MF, STEP, OBJ, AMF) into G-code
for a wide range of printers, with features such as advanced calibration tools,
precise wall/seam control, sandwich (inner-outer-inner) wall ordering and
extensive printer/filament profiles.

%prep
%autosetup -n %{name}-%{version}

%build
# 1) Build the vendored dependencies as static libraries into
#    deps/build/OrcaSlicer_dep/usr/local. The superbuild is serialised (-j1) so
#    only one heavy dependency (OpenCV/OCCT/Boost) compiles at a time, bounding
#    peak RAM; each individual dependency still builds multi-threaded internally.
#    This step requires network access to download the dependency sources.
cmake -S deps -B deps/build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DDEP_WX_GTK3=ON
cmake --build deps/build -j1

# 2) Build OrcaSlicer against the vendored deps, installed FHS-style under /usr.
#    CMAKE_SKIP_INSTALL_RPATH avoids upstream baking the build-tree dep path into
#    the installed binary's RPATH (harmless since deps are static, but it would
#    trip rpmbuild's rpath QA check).
#    The main build is capped at -j8 (not %%{?_smp_mflags}): the heavy libslic3r
#    template instantiation (Config.hpp) uses ~2 GB/job, so -j16 on a 32 GB box
#    OOM-kills the build (observed: killed at [77/647] with no compiler error).
cmake -S . -B %{_vpath_builddir} -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DSLIC3R_FHS=ON \
    -DSLIC3R_GTK=3 \
    -DSLIC3R_PCH=OFF \
    -DSLIC3R_DESKTOP_INTEGRATION=OFF \
    -DBBL_RELEASE_TO_PUBLIC=1 \
    -DORCA_TOOLS=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_PREFIX_PATH="%{_builddir}/%{name}-%{version}/deps/build/OrcaSlicer_dep/usr/local"
cmake --build %{_vpath_builddir} --target OrcaSlicer -j8

# 3) Compile translations into ./resources/i18n so the install step ships them.
#    Best-effort: a localization hiccup must not fail the package build.
./scripts/run_gettext.sh || :

%install
DESTDIR=%{buildroot} cmake --install %{_vpath_builddir}

# Upstream's install drops LICENSE.txt at the prefix root (/usr/LICENSE.txt);
# ship it via %%license instead.
rm -f %{buildroot}%{_prefix}/LICENSE.txt

# The vendored stb_dxt dependency leaks its dev header and cmake config into the
# FHS prefix during cmake --install. OrcaSlicer links stb_dxt statically, so these
# are stray build artifacts with no runtime/devel consumer; drop them.
rm -f %{buildroot}%{_includedir}/stb_dxt/stb_dxt.h
rm -f %{buildroot}%{_prefix}/lib/cmake/stb_dxt/stb_dxtTargets.cmake
rmdir --ignore-fail-on-non-empty \
    %{buildroot}%{_includedir}/stb_dxt \
    %{buildroot}%{_prefix}/lib/cmake/stb_dxt 2>/dev/null || :

# Belt-and-suspenders: strip any residual build-tree RPATH from the binary.
patchelf --remove-rpath %{buildroot}%{_bindir}/orca-slicer || :

# Strip the statically-linked executable. debug_package is disabled (vendored
# static deps aren't built with Fedora's debug flags), so rpmbuild does not strip
# it automatically; doing it here clears the unstripped-binary warning and cuts
# the binary's size substantially.
strip %{buildroot}%{_bindir}/orca-slicer

# Drop upstream zero-length resource cruft: empty swiper .less/.scss/.min.css
# stubs, an i18n placeholder.txt, empty HMS cache PNGs and a stray
# profiles/FlyingBear/error_hull_show. rpmlint flags each as a zero-length error
# and none are referenced at runtime. Prune any dirs left empty afterwards.
find %{buildroot}%{_datadir}/OrcaSlicer -type f -empty -delete
find %{buildroot}%{_datadir}/OrcaSlicer -type d -empty -delete

# AppStream metainfo (the FHS install rule does not place it).
install -Dpm0644 scripts/flatpak/com.orcaslicer.OrcaSlicer.metainfo.xml \
    %{buildroot}%{_metainfodir}/com.orcaslicer.OrcaSlicer.metainfo.xml

# Validate desktop entry and appstream metadata (non-fatal on warnings).
desktop-file-validate %{buildroot}%{_datadir}/applications/com.orcaslicer.OrcaSlicer.desktop || :
appstream-util validate-relax --nonet \
    %{buildroot}%{_metainfodir}/com.orcaslicer.OrcaSlicer.metainfo.xml || :

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/orca-slicer
%{_datadir}/OrcaSlicer/
%{_datadir}/applications/com.orcaslicer.OrcaSlicer.desktop
%{_datadir}/icons/hicolor/*/apps/OrcaSlicer.png
%{_metainfodir}/com.orcaslicer.OrcaSlicer.metainfo.xml

%changelog
* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 2.4.0-0.1.20260604git58a8722a
- Initial package, built from upstream OrcaSlicer snapshot 58a8722a.
