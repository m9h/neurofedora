Name:           ciftilib
Version:        1.6.0
Release:        2%{?dist}
Summary:        C++ library for reading and writing CIFTI-1 and CIFTI-2 files

# Whole library is BSD-3-Clause (Washington University School of Medicine)
License:        BSD-3-Clause
URL:            https://github.com/Washington-University/CiftiLib
# Upstream tags releases as vX.Y.Z; the GitHub archive unpacks to CiftiLib-X.Y.Z
Source0:        %{url}/archive/v%{version}/CiftiLib-%{version}.tar.gz

# Upstream still declares cmake_minimum_required(VERSION 2.6) and sets
# CMP0045 to OLD to silence a UseDoxygen warning. Fedora's CMake >= 4 has
# removed compatibility with CMake < 3.5 and removed that OLD policy, so
# configure fails outright. Bump the minimum to 3.10, drop the dead policy
# block, make UseDoxygen optional, and sync the internal version (was 1.5)
# to the 1.6.0 release tag so the soname/pkgconfig match what FSL pins.
Patch0:         ciftilib-cmake4-compat.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  make
# XML backend: upstream prefers Qt4, then Qt5Core, else libxml++. On Fedora
# Qt4 is gone, so it resolves to Qt5::Core (QXmlStreamReader lives in QtCore).
BuildRequires:  cmake(Qt5Core)
# Boost is FIND_PACKAGE(Boost REQUIRED) in both the Qt and non-Qt paths.
BuildRequires:  boost-devel
# zlib is optional but enables compressed-volume (.nii.gz) reading, which FSL
# needs. The classic zlib.h / FindZLIB target comes from the zlib-ng *compat*
# devel package on Fedora; zlib-ng-devel ships only the native zlib-ng.h.
BuildRequires:  zlib-ng-compat-devel

%description
CiftiLib is a C++ library for reading and writing files in the CIFTI-2 and
CIFTI-1 connectivity formats used in human brain imaging (notably the Human
Connectome Project). It is a required build and link dependency of several
FSL tools, including MELODIC and FLAMEO.

%package devel
Summary:        Development files for CiftiLib
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Public headers expose Boost; consumers building against them need Boost headers.
Requires:       boost-devel
Requires:       cmake(Qt5Core)

%description devel
Headers and pkg-config metadata for developing applications that use
CiftiLib to read and write CIFTI-1/CIFTI-2 files.

%prep
%autosetup -p1 -n CiftiLib-%{version}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DIGNORE_QT=OFF \
    -DBUILD_SHARED_LIBS=ON
%cmake_build

%install
%cmake_install

%check
# Confirm the shared library and a public header actually landed.
test -e %{buildroot}%{_libdir}/libCifti.so.0
test -e %{buildroot}%{_includedir}/CiftiLib/CiftiFile.h
test -e %{buildroot}%{_libdir}/pkgconfig/CiftiLib.pc
# Guard against the zlib backend being silently dropped (FindZLIB needs the
# classic zlib.h from zlib-ng-compat-devel): the library MUST link libz.
ldd %{buildroot}%{_libdir}/libCifti.so.%{version} | grep -q libz.so

%files
%license LICENSE
%doc README USAGE
# SOVERSION is 0 (upstream did not design ABI stability); real file carries
# the full version. Both are owned by the runtime package.
%{_libdir}/libCifti.so.0
%{_libdir}/libCifti.so.%{version}

%files devel
%{_includedir}/CiftiLib/
%{_libdir}/libCifti.so
%{_libdir}/pkgconfig/CiftiLib.pc

%changelog
* Mon Jun 08 2026 Morgan Hough <morgan.hough@gmail.com> - 1.6.0-2
- Fix zlib backend: BuildRequire zlib-ng-compat-devel (provides classic
  zlib.h) so .nii.gz volume reading is actually enabled; previously FindZLIB
  silently failed and the feature was compiled out
- Assert libz linkage in %%check to prevent silent regression

* Sun Jun 07 2026 Morgan Hough <morgan.hough@gmail.com> - 1.6.0-1
- Initial package (required build/link dependency for FSL melodic and flameo)
- Patch CMakeLists for CMake >= 4 (raise minimum to 3.10, drop removed
  CMP0045 OLD policy, drop UseDoxygen include, sync version to 1.6.0)
- Build against system Qt5Core XML backend with Boost and zlib-ng
