# PythonQt — Python bindings for Qt6, required by 3D Slicer's PythonQt-
# based scripted module / extension system, and by CTK's PythonQt wrapper.
#
# Upstream: commontk/PythonQt — Slicer and CTK both use this fork.
# Branch:   patched-v4.0.1-2026-03-16-5cd9b581f (Qt6-capable; introduces
#           PythonQt_QT_VERSION cmake variable that accepts 5 or 6).
#
# Patched-9 (the previous "stable" branch) hardcodes Qt5; we require
# v4.0.1 specifically for Qt6 support.
#
# Build flow: the upstream tarball ships only `generated_cpp_515` (Qt 5.15
# reference wrappers). For any Qt6 build we must run PythonQt's own
# binding generator at build time to emit Qt6-specific wrappers, then
# point the main cmake build at that directory via
# -DPythonQt_GENERATED_PATH. The %build section does this in three steps:
#   1. cmake-build the generator/ subdir as a Qt6 tool
#   2. run pythonqt_generator against Fedora's Qt6 headers
#   3. cmake-build the runtime library with PythonQt_GENERATED_PATH set

%global commit       7ef4c5ee066b8ef1e7dc609b14071d504f59d4ba
%global shortcommit  7ef4c5ee
%global snapdate     20260329

Name:           python-pythonqt
Version:        4.0.1
Release:        0.13.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Python bindings for Qt — dynamic Python/Qt object interop

License:        LGPL-2.1-only
URL:            https://github.com/commontk/PythonQt
Source0:        %{url}/archive/%{commit}/PythonQt-%{shortcommit}.tar.gz

# Cmake config shim — upstream PythonQt ships no PythonQtConfig.cmake,
# so downstream find_package(PythonQt) fails. This template gets minimal
# variable substitution at %install time and is dropped into
# /usr/lib64/cmake/PythonQt/.
Source1:        PythonQtConfig.cmake.in

# Generator's simplecpp preprocessor needs expanded built-in defines to
# parse Qt 6.11+ headers without aborting (and without crashing the
# downstream AST builder). Upstream tests only Qt 6.10, where the
# minimal define set still happens to work; Fedora 44 ships 6.11.1.
Patch0:         pythonqt-simplecpp-linux-defines.patch

# Cap TypeInfo::resolveType recursion at 64 frames. Without this, Qt 6.11
# cyclic type alias chains exhaust the stack and segfault.
Patch1:         pythonqt-resolvetype-depth-cap.patch

BuildRequires:  cmake >= 3.20.6
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  python3-devel

# Qt6 build deps. The generator only needs Core+Xml; the runtime library
# needs the full set so it can wrap each Qt module.
BuildRequires:  cmake(Qt6Core)
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Sql)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6Xml)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6Multimedia)
BuildRequires:  cmake(Qt6MultimediaWidgets)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickWidgets)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6PrintSupport)
BuildRequires:  cmake(Qt6Core5Compat)
BuildRequires:  cmake(Qt6Test)
BuildRequires:  cmake(Qt6UiTools)

Requires:       qt6-qtbase

%ldconfig_scriptlets

%description
PythonQt is a dynamic Python binding for the Qt framework. It enables
embedding Python into Qt applications (such as 3D Slicer's scripted
module interpreter) and exposing Qt classes to Python at runtime,
without the SIP / static-binding overhead.

Used by 3D Slicer, the Common Toolkit (CTK), MITK, and several other
Qt-based research applications.

This build targets Qt6.

%package devel
Summary:        Development files for PythonQt
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(Qt6Core)

%description devel
Headers and link-time symlinks for embedding PythonQt into Qt6
applications. Use CTK's FindPythonQt.cmake module with
PYTHONQT_INSTALL_DIR=/usr to consume from a CMake project.

%prep
%autosetup -p1 -n PythonQt-%{commit}

# Trim build_all.txt to modules we (a) actually need for Slicer/CTK and
# (b) don't crash PythonQt's AST parser on Qt 6.11. Skipping:
#   webkit, xmlpatterns — removed in Qt6
#   qml, quick        — template-heavy headers the parser segfaults on
sed -i \
    -e '/typesystem_qml\.xml/d' \
    -e '/typesystem_quick\.xml/d' \
    -e '/typesystem_webkit\.xml/d' \
    -e '/typesystem_xmlpatterns\.xml/d' \
    generator/build_all.txt

# Strip the matching includes from the master include header so the
# parser doesn't walk those modules either — typesystem trimming alone
# isn't enough because qtscript_masterinclude.h includes everything for
# Qt >= 5 unconditionally.
sed -i \
    -e '/<QtQml\/QtQml>/d' \
    -e '/<QtQuick\/QtQuick>/d' \
    -e '/<QtQuickWidgets\/QtQuickWidgets>/d' \
    -e '/<QtWebKit\/QtWebKit>/d' \
    -e '/<QtWebKitWidgets\/QtWebKitWidgets>/d' \
    -e '/<QtXmlPatterns\/QtXmlPatterns>/d' \
    generator/qtscript_masterinclude.h

# Inject VERSION/SOVERSION onto the PythonQt cmake target so the built
# shared lib gets a proper SONAME (libPythonQt.so.4 → libPythonQt.so.4.0.1).
# Upstream CMakeLists ships without versioning, which violates Fedora policy
# and leaves nothing for %%files to glob with libPythonQt*.so.*.
sed -i 's|^    AUTOMOC TRUE$|    AUTOMOC TRUE\n    VERSION %{version}\n    SOVERSION 4|' CMakeLists.txt

%build
export CXXFLAGS="%{optflags}"

# Resolve the actual source dir — Fedora's modern rpm layout wraps the
# extracted tree under <pkgname>-<version>-build/, so %{_builddir} alone
# doesn't get us to the cmake source root. pwd does.
SRCDIR="$(pwd)"

# Step 1: Build PythonQtGenerator. The generator is a Qt6 command-line
# tool that parses Qt6 headers and emits PythonQt's binding sources. It
# is a build-time-only artifact and is NOT installed.
%__mkdir_p generator-build
%{__cmake} \
    -G Ninja \
    -B generator-build \
    -S generator \
    -DCMAKE_BUILD_TYPE=Release \
    -DPythonQtGenerator_QT_VERSION:STRING=6 \
    -DQt6_DIR:PATH=%{_libdir}/cmake/Qt6
%{__cmake} --build generator-build %{?_smp_mflags}

# Step 2: Generate Qt6 binding sources into ./generated_cpp_qt6.
# Run from generator/ so the relative typesystem_*.xml load-statements
# in build_all.txt resolve correctly. The CMake target name is
# PythonQtGenerator (the qmake .pro file calls it pythonqt_generator,
# but the cmake project() name wins for the CMake build).
#
# Two paths matter:
#   QTDIR=%{_includedir}/qt6 — generator code falls back to using QTDIR
#     directly when QTDIR/include doesn't exist, giving the Qt6 header
#     root for QtCore/QObject/etc.
#   --include-paths=%{_includedir} — needed so simplecpp can find
#     glibc's bits/wordsize.h (included transitively from qconfig.h).
#     Without it, simplecpp errors out on __WORDSIZE and the typesystem
#     parser sees 0 classes. (Pattern documented by MeVisLab's Rocky CI:
#     git.rockylinux.org/staging/rpms/qt5-qtbase/-/blob/r8/SOURCES/qconfig-multilib.h)
%__mkdir_p generated_cpp_qt6
export QTDIR=%{_includedir}/qt6
cd generator
../generator-build/PythonQtGenerator \
    --include-paths=%{_includedir} \
    --output-directory="${SRCDIR}/generated_cpp_qt6" \
    qtscript_masterinclude.h \
    build_all.txt
cd "${SRCDIR}"

# Generator hardcodes a "/generated_cpp/" suffix on the output dir, so
# the actual wrappers land in generated_cpp_qt6/generated_cpp/. That's
# what PythonQt_GENERATED_PATH must point at.

# Fix one generator output bug: it emits `theWrappedObject->qHash(key, seed)`
# for QSizePolicy, but qHash for QSizePolicy is a friend free function
# (qsizepolicy.h:89), not a method. Rewrite to free-function form.
sed -i 's|return ( theWrappedObject->qHash(key, seed));|return ( ::qHash(*theWrappedObject, seed));|' \
    generated_cpp_qt6/generated_cpp/com_trolltech_qt_gui_builtin/com_trolltech_qt_gui_builtin0.cpp

# Step 3: Build the runtime library against the freshly-generated wrappers.
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPythonQt_QT_VERSION:STRING=6 \
    -DPythonQt_GENERATED_PATH:PATH="${SRCDIR}/generated_cpp_qt6/generated_cpp" \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DPythonQt_INSTALL_LIBRARY_DIR:PATH=%{_lib} \
    -DPythonQt_INSTALL_ARCHIVE_DIR:PATH=%{_lib} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

# Install the cmake config shim so find_package(PythonQt) works from
# CTK / Slicer / MITK consumers. Substitute @VERSION@ and @LIB@.
install -d %{buildroot}%{_libdir}/cmake/PythonQt
sed -e 's|@VERSION@|%{version}|g' \
    -e 's|@LIB@|%{_lib}|g' \
    %{SOURCE1} \
    > %{buildroot}%{_libdir}/cmake/PythonQt/PythonQtConfig.cmake

%files
%license COPYING
%doc README.md
%{_libdir}/libPythonQt*.so.*

%files devel
%{_includedir}/PythonQt/
%{_libdir}/libPythonQt*.so
%{_libdir}/cmake/PythonQt/

%changelog
* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.13.20260329git7ef4c5ee
- Ship a cmake config shim at /usr/lib64/cmake/PythonQt/PythonQtConfig.cmake.
  Upstream PythonQt installs no cmake config; downstream consumers like
  3D Slicer call find_package(PythonQt) in Config mode and abort with
  "Could not find a package configuration file provided by PythonQt".
  The shim exposes the imported target PythonQt::PythonQt plus the
  legacy PYTHONQT_INSTALL_DIR / PYTHONQT_INCLUDE_DIRS / PYTHONQT_LIBRARIES
  variables that CTK's FindPythonQt.cmake uses.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.12.20260329git7ef4c5ee
- Inject VERSION/SOVERSION onto the PythonQt cmake target so the
  shared library installs as libPythonQt.so.4.0.1 with SONAME
  libPythonQt.so.4 and a matching unversioned symlink. Upstream's
  CMakeLists ships without any versioning, which left %%files with
  nothing to glob.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.11.20260329git7ef4c5ee
- Post-process generated com_trolltech_qt_gui_builtin0.cpp to fix one
  call site where the generator wrapped qHash(QSizePolicy, size_t) as
  a method call. It's actually a friend free function (qsizepolicy.h:89),
  so the emitted `theWrappedObject->qHash(key, seed)` fails to compile.
  Rewrite to `::qHash(*theWrappedObject, seed)`.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.10.20260329git7ef4c5ee
- Add pythonqt-resolvetype-depth-cap.patch. GDB backtrace identified the
  segfault as stack overflow from infinite recursion in
  TypeInfo::resolveType — Qt 6.11 has cyclic type alias chains the
  resolver can't detect. Cap recursion at 64 frames via thread_local
  counter; degrade gracefully on overflow. Generator now emits 619
  wrappers (635 classes parsed) cleanly.
- Point PythonQt_GENERATED_PATH at generated_cpp_qt6/generated_cpp/.
  The generator hardcodes a /generated_cpp/ subdir on the output-dir
  argument (setupgenerator.cpp:280), so the actual wrappers land one
  level deeper than what --output-directory specifies.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.9.20260329git7ef4c5ee
- Also strip QML/Quick/WebKit/XmlPatterns from qtscript_masterinclude.h.
  Trimming build_all.txt alone wasn't enough; the master include header
  unconditionally pulls all those modules in for Qt >= 5, so the AST
  parser still walked QtQml headers and segfaulted, even though no
  wrappers were being generated for them.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.8.20260329git7ef4c5ee
- Trim QML/Quick/WebKit/XmlPatterns from generator/build_all.txt.
  WebKit and XmlPatterns don't exist in Qt6 at all. QML/Quick headers
  contain template-heavy code (QQmlElement<T>::ctor, QtPrivate::
  QMetaTypeForType<T>::getDefaultCtr) that crashes PythonQt's AST
  parser. Slicer/CTK use Qt Widgets, not Qt Quick, so this only
  removes modules we wouldn't have used anyway.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.7.20260329git7ef4c5ee
- Add pythonqt-simplecpp-linux-defines.patch to expand the simplecpp
  preprocessor's built-in defines (__cplusplus=201703L, __linux__,
  __GNUC__=15, __SIZE_MAX__, __SIZEOF_LONG__=8, __GLIBCXX__, etc.).
  Without these, Qt 6.11 headers fire seven #error directives and the
  generator's AST builder segfaults mid-parse. Upstream CI only tests
  Qt 6.10 where the minimal define set happens to work.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.6.20260329git7ef4c5ee
- Generator was producing 0 classes because simplecpp couldn't find
  glibc's bits/wordsize.h, gating out all Qt headers via #error
  in qconfig.h/qcompilerdetection.h. Add --include-paths=/usr/include
  (the glibc header root) and set QTDIR=/usr/include/qt6 so the
  generator's QLibraryInfo fallback lands on the right Qt header tree.
  Pattern lifted from MeVisLab/pythonqt's Rocky CI matrix.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.5.20260329git7ef4c5ee
- Pass --include-paths=/usr/include/qt6 to the generator. Fedora puts
  Qt6 headers under /usr/include/qt6/ while QTDIR/include conventionally
  resolves to /usr/lib64/qt6/include (which doesn't exist on Fedora),
  causing the generator to abort with "Could not find Qt version".
  Dropping the QTDIR export entirely since --include-paths supersedes it.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.4.20260329git7ef4c5ee
- Fix two %%build typos surfaced by mock: the generator binary is
  PythonQtGenerator (the cmake project() name), not pythonqt_generator
  (the qmake .pro target). Also use $(pwd) to address the source dir
  instead of %%{_builddir}/PythonQt-<commit>/ — Fedora's modern rpm
  layout wraps the tree under <pkg>-<version>-build/ and the macro
  alone doesn't reach into it.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.3.20260329git7ef4c5ee
- Run the upstream pythonqt_generator at build time to produce Qt6
  binding wrappers. The tarball ships only generated_cpp_515 (Qt 5.15
  reference), so Qt6 builds were aborting in cmake with
  "missing generated wrapper sources for Qt 6.x". The %%build now
  (1) builds the generator as a Qt6 cmake project,
  (2) runs it against Fedora's Qt6 headers,
  (3) builds the library with PythonQt_GENERATED_PATH pointing at the
      freshly-generated wrapper tree.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.2.20260329git7ef4c5ee
- Add BuildRequires: qt6-qtbase-private-devel — PythonQt wraps Qt6
  private classes (QObjectPrivate etc.) which live in a separately
  shipped private-headers package. Without it, cmake configure
  errors with "Could NOT find Qt6CorePrivate".

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.1.20260329git7ef4c5ee
- Switch to commontk/PythonQt patched-v4.0.1 (Qt6-capable) from the
  Qt5-only patched-9 branch.
- Set PythonQt_QT_VERSION=6 for Qt6 build.
- Build needed by 3D Slicer 5.10+/main and CTK Qt6 builds.
