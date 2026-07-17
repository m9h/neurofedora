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
Release:        0.21.%{snapdate}git%{shortcommit}%{?dist}
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

# Make the per-module wrap loop self-trimming: only compile a Qt module's
# wrappers (and define PYTHONQT_WITH_<MOD>) if the generator actually emitted
# its _init.cpp. Qt6 restructured some modules (e.g. QtOpenGL) to yield no
# wrappable classes; without this, enabling such a module fails configure on a
# missing source and would leave PythonQt_QtAll::init() referencing an
# undefined PythonQt_init_Qt<MOD>.
Patch2:         pythonqt-wrap-only-generated-modules.patch

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
# Pulled in transitively once the per-module wrappers below are enabled:
# the Qt6 "gui" wraplib depends on Widgets/OpenGL/PrintSupport, and the
# svg wrapper depends on SvgWidgets (see qt_wrapped_lib_depends_* in
# upstream CMakeLists). Qt6Widgets/OpenGLWidgets/Multimedia are already
# listed above; add the remaining -Widgets companions explicitly.
BuildRequires:  cmake(Qt6SvgWidgets)
BuildRequires:  cmake(Qt6PrintSupport)

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

# NOTE: qt.QTimer is still MISSING under Qt6 — PythonQt's generator drops the
# QTimer class because it cannot parse QTimer's Qt6 template singleShot
# declarations (an upstream-acknowledged gap: the masterinclude carries a
# Qt5-only Q_CLANG_QDOC workaround commented "does not work in Qt6 … needs other
# fixes"). Typesystem modify-function removals and masterinclude Q_QDOC blocks
# have NO effect (the generator parses each class's header directly). The real
# fix is a post-generation hand-written QTimer wrapper + registerClass, tracked
# separately. -0.16..-0.18 attempted typesystem fixes that did nothing; reverted.

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

# Fix a second generator bug exposed once the full QtCore wrapper is compiled:
# Qt 6.8+ made QElapsedTimer's relational operators hidden friends
# (friend bool operator<(QElapsedTimer, QElapsedTimer)). The generator
# mis-wrapped operator< as a two-arg member returning QElapsedTimer:
#   QElapsedTimer __lt__(QElapsedTimer*, const QElapsedTimer& lhs, const QElapsedTimer& rhs)
#   { return ( theWrappedObject->operator<(lhs, rhs)); }
# which fails to compile ('QElapsedTimer has no member operator<'). Every other
# wrapped class emits the correct one-arg form; rewrite this one to match.
# (Only QElapsedTimer is affected — verified across the whole generated tree.)
sed -i \
    -e 's|QElapsedTimer  PythonQtWrapper_QElapsedTimer::__lt__(QElapsedTimer\* theWrappedObject, const QElapsedTimer\&  lhs, const QElapsedTimer\&  rhs)|bool  PythonQtWrapper_QElapsedTimer::__lt__(QElapsedTimer* theWrappedObject, const QElapsedTimer\&  rhs)|' \
    -e 's|return ( theWrappedObject->operator<(lhs, rhs));|return ( (*theWrappedObject)< rhs);|' \
    generated_cpp_qt6/generated_cpp/com_trolltech_qt_core/com_trolltech_qt_core0.cpp
sed -i \
    's|QElapsedTimer  __lt__(QElapsedTimer\* theWrappedObject, const QElapsedTimer\&  lhs, const QElapsedTimer\&  rhs);|bool  __lt__(QElapsedTimer* theWrappedObject, const QElapsedTimer\&  rhs);|' \
    generated_cpp_qt6/generated_cpp/com_trolltech_qt_core/com_trolltech_qt_core0.h

# THE QTimer FIX. The generator drops QTimer at PARSE time — its Qt6 templated
# singleShot(chrono, Functor) declarations break the parser, so no wrapper and no
# registration are emitted and qt.QTimer is absent (breaking every Slicer
# SegmentEditorEffect that does `self.timer = qt.QTimer()`). Typesystem and
# masterinclude workarounds all proved no-ops (the parser reads each class header
# directly). Fix = inject a hand-written wrapper post-generation and register it
# by staticMetaObject, exactly as the generator does for QThread. QTimer is a
# QObject, so Qt's meta-object system exposes start/stop/setInterval/interval/
# singleShot/isActive/timeout via introspection at runtime — the wrapper only has
# to supply the constructor (QTimer's ctor is not Q_INVOKABLE, so meta-object
# registration alone can't construct it). Validated on the CTest farm (the py_
# SegmentEditor tests that failed on qt.QTimer pass with this in place).
CORE=generated_cpp_qt6/generated_cpp/com_trolltech_qt_core
cat >> "${CORE}/com_trolltech_qt_core0.h" <<'QTIMEREOF'

#include <QTimer>
// Decorator wrapper for QTimer (PythonQt convention: instance methods take the
// wrapped object as first arg; new_/delete_ are ctor/dtor). registerClass with
// &QTimer::staticMetaObject additionally exposes the timeout() signal, the
// active/interval/singleShot/timerType properties, and the start()/stop() slots
// via Qt introspection — but QTimer's setInterval()/setSingleShot()/start(int)
// etc. are NOT slots, so they must be wrapped explicitly here or Slicer's
// SegmentEditor code (setInterval/setSingleShot) can't call them.
class PythonQtWrapper_QTimer : public QObject
{ Q_OBJECT
public Q_SLOTS:
QTimer* new_QTimer(QObject* parent = nullptr) { return new QTimer(parent); }
void delete_QTimer(QTimer* obj) { delete obj; }
int  interval(QTimer* o) const { return o->interval(); }
bool isActive(QTimer* o) const { return o->isActive(); }
bool isSingleShot(QTimer* o) const { return o->isSingleShot(); }
int  remainingTime(QTimer* o) const { return o->remainingTime(); }
void setInterval(QTimer* o, int msec) { o->setInterval(msec); }
void setSingleShot(QTimer* o, bool s) { o->setSingleShot(s); }
void setTimerType(QTimer* o, Qt::TimerType t) { o->setTimerType(t); }
void start(QTimer* o, int msec) { o->start(msec); }
void start(QTimer* o) { o->start(); }
void stop(QTimer* o) { o->stop(); }
Qt::TimerType timerType(QTimer* o) const { return o->timerType(); }
};

// Same generator gap as QTimer: QProcess is dropped at parse time, so qt.QProcess
// is absent — and Slicer launches its CLI modules through QProcess, which breaks the
// CLI test cluster + DCMTKPrivateDict. Hand-wrap it identically. The meta-object
// supplies the signals (finished/errorOccurred/readyRead*), the kill()/terminate()
// slots and the enums; these decorators supply the ctor and the non-slot methods.
#include <QProcess>
#include <QStringList>
class PythonQtWrapper_QProcess : public QObject
{ Q_OBJECT
public:
Q_ENUMS(ProcessState ExitStatus ProcessError)
enum ProcessState { NotRunning = QProcess::NotRunning, Starting = QProcess::Starting, Running = QProcess::Running };
enum ExitStatus  { NormalExit = QProcess::NormalExit, CrashExit = QProcess::CrashExit };
enum ProcessError{ FailedToStart = QProcess::FailedToStart, Crashed = QProcess::Crashed, Timedout = QProcess::Timedout,
                   ReadError = QProcess::ReadError, WriteError = QProcess::WriteError, UnknownError = QProcess::UnknownError };
public Q_SLOTS:
QProcess* new_QProcess(QObject* parent = nullptr) { return new QProcess(parent); }
void delete_QProcess(QProcess* o) { delete o; }
void start(QProcess* o, const QString& program, const QStringList& args) { o->start(program, args); }
void start(QProcess* o) { o->start(); }
void startCommand(QProcess* o, const QString& cmd) { o->startCommand(cmd); }
bool waitForStarted(QProcess* o, int msecs = 30000) { return o->waitForStarted(msecs); }
bool waitForFinished(QProcess* o, int msecs = 30000) { return o->waitForFinished(msecs); }
QByteArray readAllStandardOutput(QProcess* o) { return o->readAllStandardOutput(); }
QByteArray readAllStandardError(QProcess* o) { return o->readAllStandardError(); }
int  exitCode(QProcess* o) const { return o->exitCode(); }
int  exitStatus(QProcess* o) const { return (int)o->exitStatus(); }
int  state(QProcess* o) const { return (int)o->state(); }
int  error(QProcess* o) const { return (int)o->error(); }
void setProgram(QProcess* o, const QString& p) { o->setProgram(p); }
QString program(QProcess* o) const { return o->program(); }
void setArguments(QProcess* o, const QStringList& a) { o->setArguments(a); }
QStringList arguments(QProcess* o) const { return o->arguments(); }
void setWorkingDirectory(QProcess* o, const QString& d) { o->setWorkingDirectory(d); }
QString workingDirectory(QProcess* o) const { return o->workingDirectory(); }
qint64 processId(QProcess* o) const { return o->processId(); }
void closeWriteChannel(QProcess* o) { o->closeWriteChannel(); }
qint64 write(QProcess* o, const QByteArray& b) { return o->write(b); }
};
QTIMEREOF
sed -i '/registerClass(&QThread::staticMetaObject/a PythonQt::priv()->registerClass(&QTimer::staticMetaObject, "QtCore", PythonQtCreateObject<PythonQtWrapper_QTimer>, NULL, module, 0);\nPythonQt::priv()->registerClass(&QProcess::staticMetaObject, "QtCore", PythonQtCreateObject<PythonQtWrapper_QProcess>, NULL, module, 0);' \
    "${CORE}/com_trolltech_qt_core_init.cpp"

# Further generator bugs exposed by compiling the full QtGui wrapper, all from
# Qt6 API changes the v4.0.1 generator predates. Each target string is unique
# across the whole generated tree (verified). Fixing the bodies only; the
# declared signatures stay valid.
#  (a) QPolygonF::translate() returns void in Qt6 (translated() is the
#      value-returning one). The wrapper declares a QPolygonF return, so do the
#      in-place translate and return the object.
#  (b) QQuaternion operator+/operator== became hidden friends; the generator
#      emitted bogus two-operand member calls. Use the free operators.
sed -i \
    -e 's|return ( theWrappedObject->translate(offset));|theWrappedObject->translate(offset); return (*theWrappedObject);|' \
    -e 's|return ( theWrappedObject->operator+(q1, q2));|return ( q1 + q2 );|' \
    -e 's|return ( theWrappedObject->operator==(q1, q2));|return ( q1 == q2 );|' \
    generated_cpp_qt6/generated_cpp/com_trolltech_qt_gui/com_trolltech_qt_gui7.cpp

#  (c) QMediaFormat::mimeType() returns QMimeType, which the generated
#      multimedia wrapper only forward-declares. Pull in the full definition.
#      It must go in the header: AUTOMOC generates moc_*.cpp from the header
#      and instantiates QMimeType there too, so a .cpp-only include is not
#      enough. The .cpp includes this header, so one edit covers both.
sed -i '1a #include <QMimeType>' \
    generated_cpp_qt6/generated_cpp/com_trolltech_qt_multimedia/com_trolltech_qt_multimedia0.h

# Step 3: Build the runtime library against the freshly-generated wrappers.
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPythonQt_QT_VERSION:STRING=6 \
    -DPythonQt_GENERATED_PATH:PATH="${SRCDIR}/generated_cpp_qt6/generated_cpp" \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    `# Compile the per-module Qt wrappers into libPythonQt (not just the` \
    `# minimal *_builtin subset). Each enabled module defines` \
    `# PYTHONQT_WITH_<MOD>, which makes PythonQt_QtAll::init() actually` \
    `# register that module's classes. CTK's ctkAbstractPythonManager` \
    `# already calls PythonQt_QtAll::init() unconditionally — without these` \
    `# flags that call is a no-op, so "import qt; qt.QWidget" fails in` \
    `# Slicer's scripted modules (DICOM, Segment Editor, etc.).` \
    `# NOTE: do NOT use PythonQt_Wrap_QtAll=ON — it force-enables qml/quick/` \
    `# webkit, whose wrappers we trim in %prep, leaving PythonQt_init_QtQml` \
    `# undefined at link time. Enable only the modules we actually generate.` \
    `# Widgets maps to the "gui" wraplib in Qt6 (qtlib_to_wraplib_Widgets).` \
    -DPythonQt_Wrap_Qtcore:BOOL=ON \
    -DPythonQt_Wrap_Qtgui:BOOL=ON \
    -DPythonQt_Wrap_Qtnetwork:BOOL=ON \
    -DPythonQt_Wrap_Qtsql:BOOL=ON \
    -DPythonQt_Wrap_Qtsvg:BOOL=ON \
    -DPythonQt_Wrap_Qtopengl:BOOL=ON \
    -DPythonQt_Wrap_Qtxml:BOOL=ON \
    -DPythonQt_Wrap_Qtuitools:BOOL=ON \
    -DPythonQt_Wrap_Qtmultimedia:BOOL=ON \
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
* Sun Jul 12 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.21.20260329git7ef4c5ee
- Wrap qt.QProcess (same generator gap as QTimer, same post-generation technique).
  A probe of 23 common Qt classes in Slicer showed QProcess was the ONLY remaining
  missing one -- and Slicer launches CLI modules through it, so its absence breaks
  the CLI test cluster (py_CLIEventTest, TwoCLIsInARow/Parallel, qSlicerCLIModuleTest1)
  and DCMTKPrivateDictTest with "module 'qt' has no attribute 'QProcess'".

* Wed Jul 08 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.20.20260329git7ef4c5ee
- FINALLY FIX qt.QTimer (the real fix, after 0.16-0.19 dead ends). The generator
  drops QTimer at parse time (Qt6 template singleShot), so no wrapper/registration
  is emitted. Inject a hand-written PythonQtWrapper_QTimer + registerClass(
  &QTimer::staticMetaObject, ..., PythonQtCreateObject<PythonQtWrapper_QTimer>)
  into the generated QtCore post-generation, modeled on the generator's own
  QThread registration. QTimer being a QObject, its meta-object exposes start/
  stop/interval/timeout at runtime; the wrapper only supplies the constructor
  (QTimer's ctor isn't Q_INVOKABLE). Developed + validated on the intel-skullcandy
  CTest farm (the py_ SegmentEditor self-tests that AttributeError'd on qt.QTimer
  pass with this lib installed). Restores GrowCut/GrowFromSeeds/FillBetweenSlices.

* Fri Jun 26 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.19.20260329git7ef4c5ee
- Revert the ineffective QTimer typesystem edit from 0.16-0.18. Investigation
  (local patched generator + LD_PRELOAD runtime probe) proved qt.QTimer is
  dropped at the generator's HEADER-PARSE stage on QTimer's Qt6 template
  singleShot — an upstream-acknowledged limitation (masterinclude: the Qt5
  Q_CLANG_QDOC workaround "does not work in Qt6 … needs other fixes"). Typesystem
  modify-function removals and a Qt6 Q_QDOC masterinclude block both produced
  byte-identical output, so 0.16-0.18 were no-ops. Functionally identical to
  0.15; the real fix (post-generation hand-written QTimer wrapper +
  registerClass) is tracked separately. qt.QTimer remains absent for now.

* Fri Jun 26 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.18.20260329git7ef4c5ee
- Fix missing qt.QTimer on top of the -0.15 QtAll wrap fix. -0.15 enabled the
  per-module wrap libs so QtAll::init() registers their classes, but QTimer was
  never *generated*: Qt6's std::chrono overloads (esp. the chrono-returning
  intervalAsDuration/remainingTimeAsDuration) make PythonQt's generator drop the
  whole QTimer wrapper, the same chrono limit behind its QChronoTimer rejection.
  Remove just QTimer's chrono members in typesystem_core.xml so its int-based API
  wraps and qt.QTimer exists. Restores SegmentEditorEffects (GrowCut/
  GrowFromSeeds/FillBetweenSlices). Caught by the new headless slicer.bats.
  Use sed not perl in %prep (perl absent from mock chroot — what failed 0.16/0.17).

* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.15.20260329git7ef4c5ee
- Compile the full per-module Qt wrappers into libPythonQt, not just the
  minimal com_trolltech_qt_{core,gui}_builtin subset. Enable
  PythonQt_Wrap_Qt{core,gui,network,sql,svg,opengl,xml,uitools,multimedia}.
  Each flag defines PYTHONQT_WITH_<MOD>, which is what makes the (already
  exported but previously empty) PythonQt_QtAll::init() register those
  modules' classes. Fixes 3D Slicer bug #9b: CTK's ctkAbstractPythonManager
  calls PythonQt_QtAll::init() unconditionally, so before this change
  "import qt" worked but qt.QWidget/QDialog/QTimer were missing, breaking
  every GUI scripted module (DICOM, Segment Editor effects, ...).
  Widgets folds into the "gui" wraplib under Qt6.
- Deliberately NOT using PythonQt_Wrap_QtAll=ON: it force-enables
  qml/quick/webkit, whose generated wrappers we trim in %prep, which would
  leave PythonQt_init_QtQml&co undefined at link time.
- Add BuildRequires cmake(Qt6SvgWidgets), cmake(Qt6PrintSupport) — the
  gui/svg wraplibs depend on them once wrapping is enabled.
- Add Patch2 (pythonqt-wrap-only-generated-modules): the upstream wrap loop
  appends each enabled module's _init.cpp unconditionally. Qt6 yields no
  QtOpenGL wrappers, so enabling opengl failed configure on a missing source.
  Guard the whole per-module block on the generated _init.cpp existing, so the
  build self-trims to whatever the generator actually produced and
  PythonQt_QtAll::init() stays consistent with the compiled modules.
- Post-process four more generator bugs surfaced by compiling the full
  QtCore/QtGui/QtMultimedia wrappers against Qt 6.11 (the generator predates
  these Qt6 API changes): QElapsedTimer::operator< (hidden friend, mis-wrapped
  as a 2-arg member), QQuaternion operator+/operator== (hidden friends),
  QPolygonF::translate (returns void in Qt6), and a missing <QMimeType>
  include in the multimedia wrapper. All are narrow sed fixes on unique
  generated strings.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-0.14.20260329git7ef4c5ee
- Also set legacy uppercase variables in PythonQtConfig.cmake.
  CTK's ctkMacroWrapPythonQt.cmake uses PYTHONQT_FOUND (uppercase)
  and PYTHONQT_INCLUDE_DIR (uppercase, singular) — the older Find-
  module convention. -0.13 only set the modern PythonQt_FOUND and
  PYTHONQT_INCLUDE_DIRS plural, so Slicer's build via CTK aborted
  with "PythonQt package is required to build qMRMLWidgetsPythonQt".

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
