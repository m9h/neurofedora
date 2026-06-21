%global apiversion 1.15
%global soversion  1.15

# Large C++ template library; debuginfo is enormous and not useful for a COPR.
%global debug_package %{nil}
# PCL's feature/surface template instantiations are extremely memory-heavy; cut
# the debug level and disable fat-LTO objects to keep per-compile RAM down
# (mirrors what Fedora's pcl package did to avoid OOM).
%global optflags %(echo %{optflags} | sed -e 's/-g /-g1 /' -e 's/-ffat-lto-objects/-fno-fat-lto-objects/')

Name:           pcl
Version:        1.15.1
Release:        1%{?dist}
Summary:        Point Cloud Library — 2D/3D image and point cloud processing

# BSD-3-Clause throughout; bundled headers carry their own (see Provides below).
License:        BSD-3-Clause
URL:            https://pointclouds.org/
# Upstream tags are "pcl-X.Y.Z" and the archive extracts to "pcl-pcl-X.Y.Z".
Source0:        https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-%{version}.tar.gz#/pcl-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  gcc
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  boost-devel
BuildRequires:  eigen3-devel
BuildRequires:  flann-devel
BuildRequires:  qhull-devel
BuildRequires:  libusbx-devel
BuildRequires:  openni-devel
BuildRequires:  vtk-devel
BuildRequires:  gl2ps-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  libXext-devel
BuildRequires:  libX11-devel
BuildRequires:  libpng-devel
BuildRequires:  libomp-devel

%description
The Point Cloud Library (PCL) is a standalone, large-scale, open-source C++
library for 2D/3D image and point cloud processing. It contains state-of-the-art
algorithms for filtering, feature estimation, surface reconstruction, model
fitting, registration, segmentation and visualization, used widely in robotics,
3D perception, LiDAR processing and computer vision.

%package devel
Summary:        Development files for the Point Cloud Library
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       eigen3-devel
Requires:       flann-devel
Requires:       boost-devel
Requires:       vtk-devel

%description devel
Headers, CMake package configuration and pkg-config files for building
applications against the Point Cloud Library.

%package tools
Summary:        Command-line tools built on the Point Cloud Library
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description tools
A large collection of pcl_* command-line utilities for converting, filtering,
registering, segmenting and visualizing point cloud data.

%prep
%autosetup -n %{name}-%{name}-%{version}

# Eigen 5 trap: PCL requests Eigen3 3.3, which Fedora's eigen3 5.0.1
# (SameMajorVersion) rejects. Drop the version (PCL's own VERSION_LESS 3.3 guard
# still passes), and PCL 1.15.1 compiles cleanly against Eigen 5.
sed -i 's/find_package(Eigen3 3.3 REQUIRED NO_MODULE)/find_package(Eigen3 REQUIRED NO_MODULE)/' CMakeLists.txt

%build
# PCL uses LIB_INSTALL_DIR (not CMAKE_INSTALL_LIBDIR). No CUDA/GPU (proprietary);
# docs off. It bakes its own install RPATH -> skip it (libs land in a system dir).
cmake -S . -B cbuild -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DLIB_INSTALL_DIR=%{_lib} \
    -DCMAKE_SKIP_RPATH=ON \
    -DWITH_CUDA=OFF \
    -DBUILD_GPU=OFF \
    -DWITH_DOCS=OFF \
    -DBUILD_examples=OFF \
    -DCMAKE_CXX_STANDARD_LIBRARIES=-lX11
# pcl_visualization underlinks X11; Fedora's -Wl,--as-needed then drops it and
# downstream executables fail to resolve X* symbols. Appending -lX11 to every
# C++ link line (above) resolves it (--as-needed drops it where unused).

# Cap parallelism by available RAM (>=4GB/job) — PCL's template-heavy compiles
# OOM a builder at full -j.
cmake --build cbuild %{limit_build -m 4000}

%install
DESTDIR=%{buildroot} cmake --install cbuild

%ldconfig_scriptlets

%files
%license LICENSE.txt
%doc README.md
%{_libdir}/libpcl_*.so.%{soversion}
%{_libdir}/libpcl_*.so.%{version}

%files devel
%{_includedir}/pcl-%{apiversion}/
%{_libdir}/libpcl_*.so
%{_datadir}/pcl-%{apiversion}/
%{_libdir}/pkgconfig/pcl_*.pc

%files tools
%{_bindir}/pcl_*

%changelog
* Sat Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 1.15.1-1
- Revive PCL (retired from Fedora at 1.12.0) at upstream 1.15.1. Builds against
  current Fedora: system Eigen 5.0.1 (drop the find_package 3.3 version pin),
  GCC 15, VTK, Qt5, Boost 1.90, FLANN, qhull. No CUDA/GPU; docs off. Provides the
  20 PCL libraries + headers/CMake config (-devel) + the pcl_* tools.
