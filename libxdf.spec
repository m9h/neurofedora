Name:           libxdf
Version:        0.99
Release:        1%{?dist}
Summary:        C++ library for loading XDF (Extensible Data Format) files
# FIX 1: Use specific SPDX identifier (Check your LICENSE file to confirm 2 or 3 clause)
License:        BSD-3-Clause
URL:            https://github.com/xdf-modules/libxdf
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  pugixml-devel

%description
Libxdf is a cross-platform C++ library for loading multimodal, multi-rate 
signals stored in XDF files.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pugixml-devel

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1

# FIX 2: GCC 15 includes patch
sed -i '/#include <set>/a #include <cstdint>' xdf.h
sed -i '/#include <cmath>/a #include <cstdint>' xdf.cpp

# FIX 3: Force SONAME versioning for Fedora compliance
# We append a CMake command to set the SOVERSION to 0 and VERSION to 0.99
# This makes the build produce libxdf.so.0 and libxdf.so.0.99
echo 'set_target_properties(xdf-shared PROPERTIES VERSION %{version} SOVERSION 0)' >> CMakeLists.txt

%build
%cmake -DBUILD_SHARED_LIBS=ON \
       -DCMAKE_BUILD_TYPE=Release 

%cmake_build

%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_includedir}

# FIX 4: Install all library version files (libxdf.so, libxdf.so.0, etc.)
# cp -a preserves the symlinks created by CMake
cp -a redhat-linux-build/libxdf.so* %{buildroot}%{_libdir}/

install -m 0644 xdf.h %{buildroot}%{_includedir}/xdf.h

%files
%license LICENSE.txt
%doc README.md
# The wildcard below catches both the soname symlink (libxdf.so.0) 
# AND the actual binary (libxdf.so.0.99)
%{_libdir}/libxdf.so.0*

%files devel
%{_includedir}/xdf.h
# The devel package owns ONLY the unversioned symlink
%{_libdir}/libxdf.so

%changelog
* Wed Jan 07 2026 Your Name <your.email@example.com> - 0.99-1
- Initial package for Fedora
- Patched for GCC 15
- Enforced SONAME versioning
