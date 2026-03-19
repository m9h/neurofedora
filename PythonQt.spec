%global _lto_cflags %{nil}

%global commit ec7e1416e17fae645f3b99a8df4533719e17cbf6
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global commitdate 20260105
%global branch patched-v3.6.1-2025-12-22-469f01f6a

Name:           PythonQt
Version:        3.6.1
Release:        0.1.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Dynamic Python binding for the Qt framework

License:        LGPL-2.1-only
URL:            https://github.com/commontk/PythonQt
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.20
BuildRequires:  make
BuildRequires:  python3-devel

# Qt 5 core
BuildRequires:  qt5-qtbase-devel >= 5.15.0
BuildRequires:  qt5-qtbase-private-devel >= 5.15.0

# Qt 5 modules used by PythonQt wrappers
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qtmultimedia-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qttools-static
BuildRequires:  qt5-qtxmlpatterns-devel

# OpenGL
BuildRequires:  libglvnd-devel

%description
PythonQt is a dynamic Python binding for the Qt framework. It offers an easy
way to embed the Python scripting language into your C++ Qt applications. It
makes heavy use of the Qt meta object system and thus requires no binding code
generation at compile-time. It provides access to all Qt classes via their
meta-object definitions at runtime.

This is the commontk fork of PythonQt, which is used by CTK and 3D Slicer.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       qt5-qtbase-devel%{?_isa}
Requires:       python3-devel%{?_isa}

%description    devel
Development headers and libraries for building applications that use PythonQt.

%prep
%autosetup -n %{name}-%{commit}

%build
# --- GCC 15 / Fedora 43 Fixes ---
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17"

%cmake \
    -DPythonQt_QT_VERSION=5 \
    -DPythonQt_GENERATED_PATH:PATH=%{_builddir}/%{name}-%{commit}/generated_cpp_515 \
    -DPythonQt_Wrap_QtAll=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DPythonQt_INSTALL_LIBRARY_DIR=%{_lib} \
    -DPythonQt_INSTALL_ARCHIVE_DIR=%{_lib} \
    -DPythonQt_INSTALL_INCLUDE_DIR=include/%{name}

%cmake_build

%install
%cmake_install

%files
%license COPYING
%doc README.md
%{_libdir}/libPythonQt.so

%files devel
%{_includedir}/%{name}/

%changelog
* Wed Mar 04 2026 Morgan Hough <morgan.hough@gmail.com> - 3.6.1-0.1.20260105gitec7e1416
- Initial package (commontk fork, branch patched-v3.6.1-2025-12-22-469f01f6a)
- Built with Qt5 and pre-generated wrappers for Qt 5.15
- Enable all Qt wrapper modules (PythonQt_Wrap_QtAll)
