%define debug_package %{nil}

Name:           dtk-qt6
Version:        1.7.1
Release:        1%{?dist}
Summary:        Inria dtk scientific platform — Qt6 fork

License:        BSD-3-Clause
URL:            https://gitlab.com/morgan.hough/dtk-qt6
# Source0 is a `git archive` of the qt6-port branch at
# gitlab.com/morgan.hough/dtk-qt6. Upstream dtk (gitlab.inria.fr/dtk/dtk)
# is dormant (last commit 2021-03-25) and Qt5-only. This fork ports the
# medInria-enabled subset to Qt6 and trims unused components (dtkMeta,
# dtkAbstractDataComposite, dtkDistributed, dtkComposer, all wrappers).
# Generated locally with:
#   git -C work/dtk-qt6 archive --format=tar.gz --prefix=dtk-qt6-1.7.1/ \
#     qt6-port -o SOURCES/dtk-qt6-1.7.1.tar.gz
Source0:        dtk-qt6-%{version}.tar.gz

# Conflicts with the original dtk package: same library names, same
# header tree (/usr/include/dtkCore/..., libdtkCore.so.1.7.1). A user can
# have one or the other, not both.
Conflicts:      dtk
Conflicts:      dtk-devel

BuildRequires:  cmake >= 3.16
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6) >= 6.5
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Concurrent)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6Test)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Xml)
BuildRequires:  zlib-devel

Requires:       qt6-qtbase

%description
dtk is a plugin/factory-based scientific software platform from Inria,
originally written against Qt5. Upstream dtk has been dormant since
2021 and the public repository has no Qt6 branch.

This package is a Qt6 port maintained as a downstream fork against the
1.7.1 upstream tag. It rebuilds the subset of dtk that medInria 5.x
actually depends on: dtkCore, dtkCoreSupport, dtkGuiSupport,
dtkMathSupport, dtkVrSupport, dtkLog, dtkMath, dtkWidgets. The
following upstream components are excluded because they are either
unused by all known downstream consumers or carry deep Qt5-private-API
coupling that would require significant rewrite for marginal benefit:

  - dtkMeta (Qt5 private QMetaType API; rewritten in Qt6)
  - dtkAbstractDataComposite (QList/QVector overload duplication after
    Qt6 aliased the two types)
  - dtkComposer / dtkComposerSupport (visual node-graph editor; not
    used by medInria)
  - dtkDistributed (HPC cluster/MPI front-end; not used by medInria)
  - dtkScript / dtkContainerSupport / dtkPlotSupport (unused)
  - SIP/SWIG Python wrappers

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers, cmake configuration, and import libraries for building
applications against the Qt6 fork of dtk 1.7.1.

%prep
%autosetup -n dtk-qt6-%{version}

# The C++20 'concept' keyword clash (original dtk uses `concept` as a
# variable name throughout dtkCore). Renamed to `pluginConcept` at
# build time. Originally a downstream sed in dtk.spec; preserve it
# here since the upstream rename has not been merged.
find src/dtkCore -name "*.h" -o -name "*.cpp" -o -name "*.tpp" | \
    xargs sed -i 's/\bconcept\b/pluginConcept/g'

# Inject SOVERSION for Support libraries that upstream omits
for lib in dtkCoreSupport dtkGuiSupport dtkMathSupport dtkVrSupport; do
    cmake_file="src/${lib}/CMakeLists.txt"
    if [ -f "$cmake_file" ]; then
        echo "set_target_properties(${lib} PROPERTIES VERSION %{version} SOVERSION 1)" >> "$cmake_file"
    fi
done

# dtkCpuid x86 inline asm fails on aarch64. Guard with arch check.
sed -i 's/#elif defined(DTK_BUILD_64)/#elif defined(DTK_BUILD_64) \&\& (defined(__x86_64__) || defined(__i386__))/' \
    src/dtkCoreSupport/dtkCpuid.cpp

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -Wno-error=deprecated-declarations -Wno-deprecated-declarations"

%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DDTK_BUILD_TESTS:BOOL=OFF \
    -DDTK_BUILD_APPS:BOOL=OFF \
    -DDTK_BUILD_DOC:BOOL=OFF \
    -DDTK_BUILD_COMPOSER:BOOL=OFF \
    -DDTK_BUILD_DISTRIBUTED:BOOL=OFF \
    -DDTK_BUILD_SCRIPT:BOOL=OFF \
    -DDTK_BUILD_WRAPPERS:BOOL=OFF \
    -DDTK_BUILD_WIDGETS:BOOL=ON \
    -DDTK_BUILD_SUPPORT_CORE:BOOL=ON \
    -DDTK_BUILD_SUPPORT_CONTAINER:BOOL=OFF \
    -DDTK_BUILD_SUPPORT_COMPOSER:BOOL=OFF \
    -DDTK_BUILD_SUPPORT_DISTRIBUTED:BOOL=OFF \
    -DDTK_BUILD_SUPPORT_GUI:BOOL=ON \
    -DDTK_BUILD_SUPPORT_MATH:BOOL=ON \
    -DDTK_BUILD_SUPPORT_PLOT:BOOL=OFF \
    -DDTK_BUILD_SUPPORT_VR:BOOL=ON

%cmake_build

%install
%cmake_install

# SIP/SWIG wrapper directory — never populated since WRAPPERS=OFF.
rm -rf %{buildroot}/usr/wrp

# cmake config shims for module-specific find_package calls that
# downstream consumers (medInria) may make: find_package(dtkFonts),
# find_package(dtkThemes), find_package(dtkSettings).
for module in Fonts Themes Settings; do
    dest=%{buildroot}%{_libdir}/cmake/dtk/dtk${module}Config.cmake
    echo "include(\${CMAKE_CURRENT_LIST_DIR}/dtkConfig.cmake)" > "$dest"
done

%ldconfig_scriptlets

%files
%license LICENSE.md
%{_libdir}/libdtk*.so.*

%files devel
%{_includedir}/dtk*
%{_libdir}/libdtk*.so
%{_libdir}/cmake/dtk/

%changelog
* Tue May 19 2026 Morgan Hough <morgan.hough@gmail.com> - 1.7.1-1
- Initial dtk-qt6 fork — Qt6 port of upstream dtk 1.7.1, trimmed to
  the subset medInria 5.x consumes. Source at
  https://gitlab.com/morgan.hough/dtk-qt6 (qt6-port branch).
- Trims: dtkMeta, dtkAbstractDataComposite, dtkComposer, dtkDistributed,
  dtkScript, SIP/SWIG wrappers
- Mechanical Qt5->Qt6 ports across cmake (Qt5:: -> Qt6::,
  qt5_add_resources -> qt6_add_resources, cmake_minimum 3.2 -> 3.16)
  and source (QRegExp -> QRegularExpression, QFontMetrics::width ->
  horizontalAdvance, QLayout::margin -> contentsMargins,
  QApplication::globalStrut removed, QDesktopWidget -> QScreen,
  Qt::Modifier + -> bitwise |, qSort -> std::sort, qLess -> std::less,
  qVariantFromValue -> QVariant::fromValue, QRegExpValidator ->
  QRegularExpressionValidator, QHash::insertMulti -> QMultiHash,
  QAtomicInt::load/store -> loadRelaxed/storeRelaxed,
  QString::SkipEmptyParts -> Qt::SkipEmptyParts, QLinkedList -> QList,
  endl -> Qt::endl, return 0 -> Qt::Orientations{},
  setFilterRegExp -> setFilterRegularExpression)
- Latent bug fixed: dtkDistributedArray::range() called this->get()
  (no such method) - replaced with this->range() recursive call
