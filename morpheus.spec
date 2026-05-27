%define debug_package %{nil}

# Filter auto-Requires for morpheus's bundled shared libs. The 2.3.9 cmake
# emits them as libXMLUtils.so / libMorpheusMLconv.so / libmuParser.so /
# libgnuplot_interface.so / libtiny-process-library.so under
# %%{_libdir}/morpheus/ (private dir, ldconfig doesn't index). The morpheus
# binary's RPATH points there. rpmbuild's auto-dep generator doesn't know
# about RPATH so it'd generate unsatisfiable Requires for these unversioned
# SONAMEs — exclude them explicitly.
%global __requires_exclude ^lib(XMLUtils|MorpheusMLconv|muParser|gnuplot_interface|tiny-process-library|qtsingleapp)\.so

Name:           morpheus
Version:        2.3.9
Release:        8%{?dist}
Summary:        Modeling environment for multicellular systems biology

License:        BSD-3-Clause
URL:            https://morpheus.gitlab.io
Source0:        morpheus-%{version}.tar.gz
# Bundled header-only libraries (Fedora 43 xtensor 0.27.0 has incompatible
# header layout — restructured include/ hierarchy breaks Morpheus includes)
Source1:        xtl-0.7.5.tar.gz
Source2:        xsimd-10.0.0.tar.gz
Source3:        xtensor-0.24.6.tar.gz

# Replace bundled xmlParser (Aladdin Free Public License — Fedora-rejected)
# with a thin pugixml wrapper. Was developed against 2.3.7 in the local
# morpheus fork (see memory/morpheus_xmlparser_replacement.md); applies
# cleanly through at least 2.3.9. The .spec's -2.3.7-1 changelog claimed
# this work shipped, but the wrapper files (xmlutils/xml_compat.{h,cpp})
# were only ever in the local working tree — never committed, never
# tarballed back as a patch — so the 2.3.9 bump regressed back to the
# AFPL xmlParser code and shipped libxmlParser.so as a runtime dep that
# nothing on F44 can satisfy (broken-dep skip on the harness install run).
Patch0:         morpheus-2.3.7-xml_compat-pugixml.patch

BuildRequires:  cmake >= 3.5
BuildRequires:  gcc-c++
BuildRequires:  patchelf
BuildRequires:  make
BuildRequires:  boost-devel
BuildRequires:  pugixml-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  libtiff-devel
BuildRequires:  libxslt
BuildRequires:  libxml2
BuildRequires:  doxygen

# GUI subpackage dependencies
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtwebengine-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libsbml-devel

Requires:       gnuplot

Provides:       bundled(muParser)
Provides:       bundled(gnuplot_i)
Provides:       bundled(tiny-process-library)
Provides:       bundled(xtensor) = 0.24.6
Provides:       bundled(xtl) = 0.7.5
Provides:       bundled(xsimd) = 10.0.0

%description
Morpheus is a modeling and simulation environment for the study of
multi-scale and multicellular systems. It includes simulators for ODEs,
PDEs, and cellular Potts models (CPM). Models are defined in XML
(MorpheusML) without programming.

This package provides the command-line simulator.

%package        gui
Summary:        Graphical user interface for Morpheus
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       gnuplot
Requires:       qt5-qtbase
Requires:       qt5-qtsvg

%description    gui
Graphical modeling and simulation environment for Morpheus. Provides a
GUI for creating, editing, running, and visualizing multicellular
models.

%prep
# Split %%setup and %%patch instead of %%autosetup. The combined form
# `%%autosetup -n X -p1` silently dropped the -n flag on build 10510718,
# causing %%prep to cd to the default `morpheus-2.3.9` (Source0 basename)
# instead of `morpheus-v2.3.9` (the tarball's actual top-level dir). The
# split form below is unambiguous and works with any rpmbuild version.
# (NB: macro names in comments need %% escaping or rpmbuild expands them
# anyway — found out the hard way on the SRPM build for -3.)
%setup -q -n morpheus-v%{version}
%patch -P 0 -p1

# Morpheus bundles muParser, gnuplot_i, tiny-process-lib, qtsingleapp.
# Fedora 43 xtensor 0.27.0 restructured its include layout (xtensor/containers/
# instead of xtensor/) making it incompatible with Morpheus.  Bundle the
# versions Morpheus was developed against (all header-only, MIT/BSD).

# Extract bundled xtensor-stack headers alongside the source tree
tar xzf %{SOURCE1} -C 3rdparty/
tar xzf %{SOURCE2} -C 3rdparty/
tar xzf %{SOURCE3} -C 3rdparty/

# Disable system xtensor detection — force bundled path
sed -i 's/FIND_PACKAGE(xtensor QUIET)/# FIND_PACKAGE(xtensor QUIET)/' 3rdparty/CMakeLists.txt
sed -i 's/IF(\${xtensor_DIR} STREQUAL "xtensor_DIR-NOTFOUND" )/IF(TRUE)/' 3rdparty/CMakeLists.txt

# Replace xtl download with local header copy
cat > 3rdparty/xtl/CMakeLists.txt << 'XTLEOF'
SET(XTL_INCLUDE_DIR ${CMAKE_BINARY_DIR}/3rdparty/include)
add_library(xtl INTERFACE)
target_include_directories(xtl INTERFACE ${XTL_INCLUDE_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/3rdparty/xtl-0.7.5/include/xtl
     DESTINATION ${XTL_INCLUDE_DIR})
message(STATUS "Using bundled xtl from ${XTL_INCLUDE_DIR}/xtl")
XTLEOF

# Replace xsimd download with local header copy
cat > 3rdparty/xsimd/CMakeLists.txt << 'XSIMDEOF'
SET(XSIMD_INCLUDE_DIR ${CMAKE_BINARY_DIR}/3rdparty/include)
add_library(xsimd INTERFACE)
target_include_directories(xsimd INTERFACE ${XSIMD_INCLUDE_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/3rdparty/xsimd-10.0.0/include/xsimd
     DESTINATION ${XSIMD_INCLUDE_DIR})
message(STATUS "Using bundled xsimd from ${XSIMD_INCLUDE_DIR}/xsimd")
XSIMDEOF

# Replace xtensor download with local header copy
cat > 3rdparty/xtensor/CMakeLists.txt << 'XTENSOREOF'
SET(XTENSOR_INCLUDE_DIR ${CMAKE_BINARY_DIR}/3rdparty/include)
add_library(xtensor INTERFACE)
target_include_directories(xtensor INTERFACE ${XTENSOR_INCLUDE_DIR})
target_compile_definitions(xtensor INTERFACE XTENSOR_USE_XSIMD=1 XTENSOR_OPENMP_TRESHOLD=1000)
target_link_libraries(xtensor INTERFACE xsimd xtl)
file(COPY ${CMAKE_SOURCE_DIR}/3rdparty/xtensor-0.24.6/include/xtensor
     DESTINATION ${XTENSOR_INCLUDE_DIR})
message(STATUS "Using bundled xtensor from ${XTENSOR_INCLUDE_DIR}/xtensor")
XTENSOREOF

# Disable xtensor download option
sed -i 's/OPTION(DOWNLOAD_XTENSOR "Download latest xtensor source" ON)/OPTION(DOWNLOAD_XTENSOR "Download latest xtensor source" OFF)/' CMakeLists.txt

# Fix static Boost linkage: upstream sets Boost_USE_STATIC_LIBS ON when BUILD_TESTING=OFF
# Fedora does not ship static Boost libs by default — force dynamic linking
sed -i 's/Boost_USE_STATIC_LIBS ON/Boost_USE_STATIC_LIBS OFF/' CMakeLists.txt morpheus/CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -std=c++17"

%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DMORPHEUS_GUI=ON \
    -DBUILD_TESTING=OFF \
    -DDOWNLOAD_XTENSOR=OFF \
    -DMORPHEUS_STATIC_BUILD=OFF \
    -DMORPHEUS_OPENMP=ON

%cmake_build

%install
%cmake_install

# Ship the 5 bundled shared libs morpheus and morpheus-gui link against.
# Upstream cmake builds them as SHARED but doesn't install() them; the
# 2.3.7 -> 2.3.9 jump introduced a regression where these went from static
# (baked in) to shared (NEEDED entries on the binaries). Install to a
# private %%{_libdir}/morpheus/ dir + patchelf the binaries to RPATH
# there. Private dir keeps ldconfig from indexing them globally (would
# collide with Fedora's muParser, for instance).
install -d %{buildroot}%{_libdir}/morpheus
for lib in \
    redhat-linux-build/xmlutils/libXMLUtils.so \
    redhat-linux-build/morpheusML/libMorpheusMLconv.so \
    redhat-linux-build/3rdparty/muParser/libmuParser.so \
    redhat-linux-build/3rdparty/gnuplot_i/libgnuplot_interface.so \
    redhat-linux-build/3rdparty/tiny-process/libtiny-process-library.so \
    redhat-linux-build/3rdparty/qtsingleapp/libqtsingleapp.so; do
    if [ -f "$lib" ]; then
        install -m 0755 "$lib" %{buildroot}%{_libdir}/morpheus/
    fi
done

# Strip build-tree RPATH from the bundled libs and re-set everyone to
# the install-time private dir. cmake embeds rpaths pointing at the
# build tree (e.g. ".../redhat-linux-build/xmlutils") in BOTH the libs
# AND the binaries; Fedora's check-rpaths rejects any build-tree path.
#
# The bundled libs reference EACH OTHER at runtime (libMorpheusMLconv.so
# dlopens libXMLUtils.so etc.), so just stripping their RPATH leaves them
# unable to find siblings — even though the morpheus BINARY's RPATH
# points at /usr/lib64/morpheus, the loader uses each LIB's own RPATH
# (not the binary's) when resolving that lib's deps. Set $ORIGIN so
# each lib looks in its own directory.
#
# Bug surfaced 2026-05-26 by the test harness's qa-2 ldd scan:
# 'morpheus missing: libXMLUtils.so (1 affected binary)' — the affected
# binary was libMorpheusMLconv.so, not /usr/bin/morpheus directly.
for solib in %{buildroot}%{_libdir}/morpheus/*.so; do
    [ -f "$solib" ] && patchelf --set-rpath '$ORIGIN' "$solib"
done
for bin in %{buildroot}%{_bindir}/morpheus %{buildroot}%{_bindir}/morpheus-gui; do
    [ -x "$bin" ] && patchelf --set-rpath %{_libdir}/morpheus "$bin"
done

# Install desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/morpheus.desktop || true

%files
%license LICENSE.md
%{_bindir}/morpheus
%dir %{_libdir}/morpheus
%{_libdir}/morpheus/lib*.so

%files gui
%{_bindir}/morpheus-gui
%{_datadir}/applications/morpheus.desktop
%{_datadir}/icons/hicolor/scalable/apps/morpheus.svg
%dir %{_datadir}/morpheus
%{_datadir}/morpheus/

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-8
- Set RUNPATH=$ORIGIN on every bundled .so in %%{_libdir}/morpheus/
  (was: --remove-rpath, which left siblings unable to find each other).
  The bundled libs reference each other at runtime — libMorpheusMLconv.so
  dlopens libXMLUtils.so — and each lib's OWN RUNPATH (not the parent
  binary's) drives that resolution. Surfaced 2026-05-26 by the
  neurofedora-tests qa-2 ldd scan as Bug 5 in
  [[copr-packaging-bugs-2026-05-23]]:
    morpheus missing: libXMLUtils.so (1 affected binary)
  with the actual affected binary being libMorpheusMLconv.so, not
  /usr/bin/morpheus.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-7
- Strip build-tree RPATH from the bundled libs in %%{_libdir}/morpheus/
  before shipping. cmake embeds RPATHs into BOTH the binaries (which
  we explicitly set to the install dir) AND the libs (which we hadn't
  touched). Fedora's check-rpaths rejected libMorpheusMLconv.so's
  embedded ".../redhat-linux-build/xmlutils" path. Strip with
  patchelf --remove-rpath on each .so.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-6
- Fix %%cmake macro expansion inside %%install comment from -5: a comment
  said "(the %cmake build embeds ...)" without %% escape, rpmbuild
  expanded it into a multi-line cmake invocation that made %%install
  fail at line 104 with `syntax error near unexpected token ')'`.
  Escape now. Also swap [[ ]] for [ ] in install since the spec script
  runs under sh; bash-only syntax was incidentally working before but
  isn't worth depending on.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-5
- Install the 5 bundled shared libs (libXMLUtils, libMorpheusMLconv,
  libmuParser, libgnuplot_interface, libtiny-process-library) to a
  private %%{_libdir}/morpheus/ dir + patchelf the morpheus / morpheus-gui
  binaries to RPATH there. Upstream cmake builds them as SHARED but
  doesn't install() them; the 2.3.7 -> 2.3.9 jump made the binaries
  NEEDED these libs at runtime, so the -4 RPM shipped with unsatisfiable
  Requires that blocked dnf install. Private dir avoids collision with
  Fedora's own muParser. Auto-Requires for the private SONAMEs filtered
  via %%__requires_exclude.
- Add patchelf to BuildRequires.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-4
- Replace `%%autosetup -n morpheus-v%%{version} -p1` with split
  `%%setup -q -n morpheus-v%%{version}` + `%%patch -P 0 -p1`. The
  combined form silently dropped the `-n` flag on build 10510718,
  making %prep cd to `morpheus-2.3.9` (Source0 default) instead of
  `morpheus-v2.3.9`. The split form is unambiguous.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-3
- Add explicit `-p1` to %autosetup. Builds 10509082 / 10509139 / 10509158
  all failed at the patch step despite the patch applying cleanly with
  `patch -p1 --fuzz=0` locally. Root cause: %autosetup's invocation of
  patch did NOT pass `-p1`, and patch's auto-detect couldn't pick the
  right strip level for git-style `a/`/`b/` prefixed paths. Reproduced
  locally with the exact mock command line; with -p1, clean apply.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-2
- Add Patch0: morpheus-2.3.7-xml_compat-pugixml.patch to actually deliver
  the AFPL→MIT xmlParser→pugixml replacement that the 2.3.7-1 changelog
  claimed shipped. The wrapper code lived only in the local working tree
  until now; -2.3.9-1 silently regressed to bundled AFPL xmlParser,
  shipping libxmlParser.so as a runtime dep with no F44 provider.

* Wed Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.9-1
- Update to 2.3.9

* Sat Mar 14 2026 Morgan Hough <mhough@fedoraproject.org> - 2.3.7-2
- Bundle xtensor/xtl/xsimd 0.24.6/0.7.5/10.0.0 (Fedora 43 xtensor 0.27.0 incompatible headers)
- Add doxygen BuildRequires (GUI appdoc)

* Sat Mar 14 2026 Morgan Hough <mhough@fedoraproject.org> - 2.3.7-1
- Initial Fedora/COPR package
- Replaced bundled xmlParser (AFPL) with pugixml (MIT) via xml_compat wrapper
- Provides: bundled(muParser), bundled(gnuplot_i), bundled(tiny-process-library)
