# IGSIO — Image-Guided Surgery IO: VTK/ITK-based libraries for tracked
# ultrasound sequence IO and volume reconstruction. Shared by SlicerIGSIO /
# SlicerIGT, Plus toolkit, etc. We package it as a standalone system library
# (USE_3DSlicer=OFF) so SlicerIGSIO can build against it, mirroring the
# openigtlink/openigtlinkio packaging.
# Chain: igsio -> 3dslicer-igsio (SlicerIGSIO) -> 3dslicer-igt (SlicerIGT).

%global commit      5a2d9dcfc01962d9d12a9573e7f773a6de46e1cb
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260615

Name:           igsio
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Image-Guided Surgery IO libraries (sequence IO, volume reconstruction)

License:        BSD-3-Clause
URL:            https://github.com/IGSIO/IGSIO
Source0:        %{url}/archive/%{commit}/IGSIO-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.15
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  InsightToolkit5-devel
BuildRequires:  InsightToolkit5-vtk-devel
BuildRequires:  vtkAddon-devel
BuildRequires:  zlib-devel

%description
IGSIO (Image-Guided Surgery IO) provides VTK/ITK-based libraries for handling
tracked image sequences: reading/writing sequence metafiles and NRRD sequences,
and reconstructing volumes from tracked 2D ultrasound sweeps. It is the
code-sharing layer used by SlicerIGSIO, SlicerIGT, and the Plus toolkit.

Built standalone (not against a 3D Slicer build) so Slicer extensions can link
it as a system library; the MKV/VP9 video codecs are disabled.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vtk-devel
Requires:       InsightToolkit5-devel

%description    devel
Headers and CMake package configuration for building against %{name}.

%prep
%autosetup -n IGSIO-%{commit}

# IGSIO hardcodes find_package(VTK NO_MODULE REQUIRED PATHS ${VTK_DIR}
# NO_DEFAULT_PATH); the NO_DEFAULT_PATH + PATHS form doesn't locate Fedora's
# modern vtk-config.cmake even with VTK_DIR set. Relax to a standard search.
sed -i -E 's|find_package\(VTK NO_MODULE REQUIRED PATHS \$\{VTK_DIR\} NO_DEFAULT_PATH\)|find_package(VTK NO_MODULE REQUIRED)|' CMakeLists.txt

%build
%cmake -G Ninja \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DIGSIO_USE_3DSlicer:BOOL=OFF \
    -DIGSIO_BUILD_SEQUENCEIO:BOOL=ON \
    -DIGSIO_BUILD_VOLUMERECONSTRUCTION:BOOL=ON \
    -DIGSIO_SEQUENCEIO_ENABLE_MKV:BOOL=OFF \
    -DIGSIO_USE_SYSTEM_ZLIB:BOOL=ON \
    -DIGSIO_INSTALL_LIB_DIR:STRING=%{_lib} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE
# IGSIO libs are unversioned (no SOVERSION upstream), so .so-only in the main pkg.
%{_libdir}/lib*.so

%files devel
%{_includedir}/IGSIO-1.0/
# NOTE: IGSIO upstream only generates IGSIOConfig.cmake for the build tree (no
# install-tree config), so none is shipped yet. SlicerIGSIO will need an
# install-tree IGSIOConfig fixup (same pattern as the 3dslicer foundation)
# before it can find_package(IGSIO). Tracked separately.

%changelog
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260615git5a2d9dcf
- Initial package. IGSIO git snapshot built standalone against system VTK + ITK
  (USE_3DSlicer off, MKV/VP9 off, volume reconstruction on) for the SlicerIGSIO
  and SlicerIGT build chain.
