%global commit 2d5dfa1891ac726524495d4ca8a3461be86c12f5
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define debug_package %{nil}

Name:           greedy
Version:        1.3.0~alpha
Release:        5%{?dist}
Summary:        Fast diffeomorphic image registration tool

License:        GPL-3.0-or-later
URL:            https://github.com/pyushkevich/greedy
Source0:        https://github.com/pyushkevich/greedy/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4
BuildRequires:  vtk-devel >= 9.1
# VTK transitive BuildRequires (VTK cmake config requires these at find_package time)
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
# ITK/VTK transitive BuildRequires
BuildRequires:  hdf5-devel
BuildRequires:  python3-devel
BuildRequires:  qt6-qtdeclarative-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif

%description
Greedy is a fast diffeomorphic image registration tool that implements
greedy diffeomorphic registration, an alternative to ANTs SyN. It provides
comparable accuracy with significantly faster computation times and includes
tools for template averaging and multi-chunk registration.

%prep
%setup -q -n greedy-%{commit}

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
%cmake \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_SHARED_LIBS:BOOL=OFF \
    -DGREEDY_BUILD_AS_SUBPROJECT:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install

# Remove cmake export files generated in build dir (triggers check-files error)
rm -f redhat-linux-build/GreedyTargets*.cmake

# Remove development files — no -devel subpackage
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}/usr/lib/cmake
rm -f %{buildroot}%{_libdir}/*.a
rm -f %{buildroot}/usr/lib/*.a
rm -f %{buildroot}%{_libdir}/*.so
rm -f %{buildroot}/usr/lib/*.so

%files
%license COPYING.txt
%doc README.md
%{_bindir}/greedy
%{_bindir}/greedy_template_average
%{_bindir}/multi_chunk_greedy
%{_bindir}/greedy_propagation

%changelog
* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.3.0~alpha-4
- Remove cmake export target files from build dir (unpackaged files error)
- Add VTK transitive BuildRequires (python3-devel, qt6-qtdeclarative-devel)

* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.3.0~alpha-1
- Initial package of greedy 1.3.0-alpha (git snapshot %{shortcommit})
- Built against system InsightToolkit5 and VTK with static internal libraries
