%global commit ef34ca9
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           elastix
Version:        5.3.1
Release:        4%{?dist}
Summary:        A toolbox for rigid and nonrigid registration of images

License:        Apache-2.0
URL:            https://github.com/SuperElastix/elastix
Source0:        https://github.com/SuperElastix/elastix/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  eigen3-devel
BuildRequires:  hdf5-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif
BuildRequires:  gdcm-devel
BuildRequires:  openjpeg2-devel

Requires:       InsightToolkit5%{?_isa}

%description
elastix is a toolbox for rigid and nonrigid registration of images.

%prep
%setup -q -c
# Move the inner directory contents to the top level
mv elastix*/* . || true
# Clean up empty directory if it exists
# Clean up empty directory if it exists
find . -maxdepth 1 -type d -name "elastix*" -empty -delete

# Remove bundled FindEigen3 which conflicts with system version (5.0 vs 3.4)
rm -f CMake/FindEigen3.cmake

%build
%cmake \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_SHARED_LIBS:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DELASTIX_USE_EIGEN:BOOL=ON \
    -DELASTIX_USE_OPENMP:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
    -DITK_DIR:PATH=%{_libdir}/cmake/ITK-5.4

%cmake_build

%install
%cmake_install

# Remove development files that we are not packaging
# Be very explicit about deleting potential duplicate locations
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}/usr/lib/cmake
rm -f %{buildroot}%{_libdir}/*.a
rm -f %{buildroot}/usr/lib/*.a
%files
%license LICENSE
%doc README.md
%{_bindir}/elastix
%{_bindir}/transformix
%{_libdir}/libelx-ANNlib.so

%changelog
* Mon May 18 2026 Morgan Hough <morgan.hough@gmail.com> - 5.3.1-4
- Rebuild against InsightToolkit5 5.4.6 (GDCM CVE-2026-3650, F44 target)
- Bump BuildRequires: InsightToolkit5-devel >= 5.4.6

* Wed Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 5.3.1-1
- Update to 5.3.1

* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 5.3.0-2
- Make libminc-devel BuildRequires conditional on Fedora (not available on EPEL 9;
  elastix gets MINC support transitively through ITK which is also built without MINC on EPEL)
- Remove git-core BuildRequires (not needed in network-isolated mock/COPR builds)

* Mon Feb 09 2026 Morgan Hough <morgan.hough@gmail.com> - 5.3.0-1
- Initial package for elastix 5.3.0 built against InsightToolkit 5.4
