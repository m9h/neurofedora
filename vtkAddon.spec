# Disable LTO - causes linker issues with VTK on Fedora 43+
%global _lto_cflags %{nil}

%global commit 2ed3e2226cf25958b4dbf8bf917b2f7793ecd6a2
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate 20251224

Name:           vtkAddon
Version:        0.1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        VTK extension classes for 3D Slicer

# 3D Slicer Contribution and Software License Agreement (BSD-style)
License:        3D-Slicer-1.0
URL:            https://github.com/Slicer/vtkAddon
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake >= 3.20
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  vtk-devel
# VTK cmake config transitive deps (COPR vtk-devel doesn't Require these)
BuildRequires:  python3-devel
BuildRequires:  json-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  hdf5-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  fmt-devel
BuildRequires:  libglvnd-devel
BuildRequires:  libtheora-devel
BuildRequires:  libogg-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel
BuildRequires:  expat-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  sqlite-devel
BuildRequires:  libxml2-devel
BuildRequires:  netcdf-devel
BuildRequires:  pugixml-devel
BuildRequires:  proj-devel
BuildRequires:  tbb-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  PEGTL-devel
BuildRequires:  libharu-devel
BuildRequires:  gl2ps-devel
BuildRequires:  double-conversion-devel
BuildRequires:  eigen3-devel
BuildRequires:  cli11-devel
BuildRequires:  boost-devel
BuildRequires:  gdal-devel
BuildRequires:  postgresql-server-devel

%description
vtkAddon provides general-purpose VTK extension classes that may be
integrated into VTK library in the future. These include spline generators,
oriented transforms, streaming volume codecs, and other utilities used by
3D Slicer and related applications.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vtk-devel

%description    devel
Development headers and CMake config files for building applications
that use %{name}.

%prep
%autosetup -n %{name}-%{commit}

# Fix cmake minimum version for CMake 4 compatibility
sed -i 's|cmake_minimum_required(VERSION 3.20.6)|cmake_minimum_required(VERSION 3.20.6...3.31)|' CMakeLists.txt


# Library and cmake config install paths are fixed via cmake flags below
# (upstream uses ${PROJECT_NAME} in variable names, making sed unreliable)

%build
# GCC 15 / Fedora 43+ fixes
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17"

%cmake \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DvtkAddon_INSTALL_NO_DEVELOPMENT=OFF \
    -DvtkAddon_INSTALL_LIB_DIR=%{_lib} \
    -DvtkAddon_INSTALL_CMAKE_DIR=%{_lib}/cmake/vtkAddon

%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libvtkAddon.so

%files devel
%{_includedir}/vtkAddon/
%{_libdir}/cmake/vtkAddon/

%changelog
* Wed Mar 04 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-0.1.20251224git2ed3e22
- Initial package (git snapshot for VTK 9.6 compatibility)
- VTK extension classes for 3D Slicer
