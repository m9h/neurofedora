Name:           compat-libtiff5
Version:        4.4.0
Release:        1%{?dist}
Summary:        Compatibility libtiff library (soname 5)

License:        libtiff
URL:            http://www.libtiff.org/
Source0:        https://download.osgeo.org/libtiff/tiff-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  libjpeg-devel
BuildRequires:  zlib-devel
BuildRequires:  xz-devel
BuildRequires:  libzstd-devel
BuildRequires:  libwebp-devel

# This package provides only the shared library for runtime compatibility.
# It does NOT conflict with system libtiff (which provides libtiff.so.6).

%description
Compatibility package providing libtiff.so.5 for applications built against
libtiff 4.x (soname 5), such as FreeSurfer RPMs built for Rocky Linux 9.
Fedora 43+ ships libtiff 4.6+ with soname 6.

%prep
%autosetup -n tiff-%{version}

%build
%cmake -GNinja \
    -DBUILD_SHARED_LIBS:BOOL=ON

%cmake_build

%install
# Only install the shared library, not headers/cmake/pkgconfig/tools
mkdir -p %{buildroot}%{_libdir}
cp -a %{__cmake_builddir}/libtiff/libtiff.so.5* %{buildroot}%{_libdir}/

%ldconfig_scriptlets

%files
%license COPYRIGHT
%{_libdir}/libtiff.so.5*

%changelog
* Tue Mar 24 2026 Morgan Hough <morgan.hough@gmail.com> - 4.4.0-1
- Initial compat-libtiff5 package for Fedora 43+
- Provides libtiff.so.5 (soname 5, version 5.8.0) needed by FreeSurfer 8.2.0
