%define debug_package %{nil}

Name:           dtk
Version:        1.7.1
Release:        2%{?dist}
Summary:        Scientific software platform (Inria)

License:        BSD-3-Clause
URL:            https://dtk.inria.fr/
Source0:        https://gitlab.inria.fr/dtk/dtk/-/archive/%{version}/dtk-%{version}.tar.gz

BuildRequires:  cmake >= 3.2
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  qt5-qtscript-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtxmlpatterns-devel
BuildRequires:  zlib-devel

Requires:       qt5-qtbase

%description
The dtk framework is a platform for scientific software development
created at Inria. It provides a plugin-based architecture with core,
logging, mathematical, and widget modules for building extensible
applications.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development libraries, headers, and cmake config files for dtk.

%prep
%autosetup -n dtk-%{version}

# ---------------------------------------------------------
# 1. Remove dtkComposer (requires dtkDistributed + dtkWidgets, heavy)
# ---------------------------------------------------------
sed -i '/add_subdirectory(dtkComposer)/d' src/CMakeLists.txt

# ---------------------------------------------------------
# 2. FIX: C++20 'concept' is a keyword — rename in dtkCore
# ---------------------------------------------------------
# dtkCore uses "concept" as a variable/method name for plugin metadata.
# C++20 (used by some dependent builds) makes this a keyword.
find src/dtkCore -name "*.h" -o -name "*.cpp" -o -name "*.tpp" | \
    xargs sed -i 's/\bconcept\b/pluginConcept/g'

# ---------------------------------------------------------
# 3. Inject SOVERSION for Support libraries (upstream lacks it)
# ---------------------------------------------------------
for lib in dtkCoreSupport dtkGuiSupport dtkMathSupport dtkVrSupport; do
  cmake_file="src/${lib}/CMakeLists.txt"
  if [ -f "$cmake_file" ]; then
    echo "set_target_properties(${lib} PROPERTIES VERSION %{version} SOVERSION 1)" >> "$cmake_file"
  fi
done

# ---------------------------------------------------------
# 4. FIX: Bug in dtkDistributedArray::range()
# ---------------------------------------------------------
# range() calls this->get() which doesn't exist — should be this->range() (recursive)
sed -i 's/this->get(index + owner_capacity/this->range(index + owner_capacity/' \
  src/dtkDistributed/dtkDistributedArray.tpp

# ---------------------------------------------------------
# 4. FIX: Enforce C++17
# ---------------------------------------------------------
sed -i 's/CMAKE_CXX_STANDARD 11/CMAKE_CXX_STANDARD 17/g' CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -Wno-error=deprecated-declarations"

%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DDTK_BUILD_TESTS:BOOL=OFF \
    -DDTK_BUILD_EXAMPLES:BOOL=OFF \
    -DDTK_BUILD_DOCUMENTATION:BOOL=OFF \
    -DDTK_BUILD_DISTRIBUTED:BOOL=ON \
    -DDTK_BUILD_COMPOSER:BOOL=OFF \
    -DDTK_BUILD_SCRIPT:BOOL=OFF \
    -DDTK_BUILD_WRAPPERS:BOOL=OFF \
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

# Remove SIP wrapper stubs (Python wrappers not built)
rm -rf %{buildroot}/usr/wrp

# Create cmake config shims for modules that downstream (medInria) may request
# via find_package(dtk<Module>). These redirect to the main dtkConfig.cmake.
for module in Fonts Themes Settings; do
  dest=%{buildroot}%{_libdir}/cmake/dtk/dtk${module}Config.cmake
  echo "include(\${CMAKE_CURRENT_LIST_DIR}/dtkConfig.cmake)" > $dest
done

%ldconfig_scriptlets

%files
%license LICENSE.md
%{_bindir}/dtkPluginsMetaInfoFetcher
%{_bindir}/dtkDeploy
%{_bindir}/dtkConceptGenerator
%{_bindir}/dtkDistributedDashboard
%{_bindir}/dtkDistributedServer
%{_bindir}/dtkDistributedSlave
%{_bindir}/dtkDistributedSlides
%{_libdir}/libdtk*.so.*

%files devel
%{_includedir}/dtk*
%{_libdir}/libdtk*.so
%{_libdir}/cmake/dtk/

%changelog
* Tue Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 1.7.1-2
- Enable support modules needed by medInria: Core, GUI, Math, VR, Distributed
- Enable dtkDistributed module (required by medInria layer)
- Use Ninja generator, add cstdint include for GCC 15
- Use CMAKE_SKIP_INSTALL_RPATH instead of disabling brp-check-rpaths
- Add ldconfig scriptlets for shared libraries
- Remove unpackaged_files_terminate_build hack, list all files explicitly
- Remove /usr/wrp/ stale entry from devel files

* Tue Jan 06 2026 Morgan Hough <morgan.hough@gmail.com> - 1.7.1-1
- Initial package for dtk 1.7.1
