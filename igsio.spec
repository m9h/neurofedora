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
Release:        0.2.%{snapdate}git%{shortcommit}%{?dist}
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

# Install-tree IGSIOConfig.cmake. Upstream IGSIO only configures the build-tree
# variant (configure_file -> build dir) and exports targets via an in-tree
# IGSIO_LIBRARY_TARGETS_FILE; nothing relocatable is installed. Synthesize a
# relocatable config so find_package(IGSIO) works against the installed library
# (needed by SlicerIGSIO -> SlicerIGT). Headers are flat in include/IGSIO-1.0;
# each installed .so already records its full VTK/ITK/vtkAddon closure in
# DT_NEEDED, so the imported targets need only IMPORTED_LOCATION + include dirs.
mkdir -p %{buildroot}%{_libdir}/cmake/IGSIO
cat > %{buildroot}%{_libdir}/cmake/IGSIO/IGSIOConfig.cmake <<'IGSIOCFG'
# Relocatable install-tree IGSIOConfig.cmake (Fedora igsio package).
get_filename_component(_igsio_libdir "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
get_filename_component(_igsio_prefix "${_igsio_libdir}/.." ABSOLUTE)
set(_igsio_incdir "${_igsio_prefix}/include/IGSIO-1.0")

# Per-component include dirs (headers install flat in IGSIO-1.0). Provide both the
# _INCLUDE_DIRS and _INCLUDES spellings consumers (SlicerIGSIO) reference.
foreach(_v VTKIGSIOCOMMON VTKSEQUENCEIO VTKVOLUMERECONSTRUCTION VTKIGSIOCALIBRATION)
  set(${_v}_INCLUDE_DIRS "${_igsio_incdir}")
  set(${_v}_INCLUDES     "${_igsio_incdir}")
endforeach()
set(IGSIO_INCLUDE_DIRS "${_igsio_incdir}")

# Build options baked into this package (VP9/MKV off; sequence IO + volume recon on).
set(IGSIO_BUILD_SEQUENCEIO ON)
set(IGSIO_SEQUENCEIO_ENABLE_MKV OFF)
set(IGSIO_BUILD_VOLUMERECONSTRUCTION ON)
set(IGSIO_USE_VP9 OFF)

# Imported targets for the three installed libraries (upstream would supply these
# via IGSIO_LIBRARY_TARGETS_FILE). DT_NEEDED carries the rest of the closure.
foreach(_t vtkIGSIOCommon vtkSequenceIO vtkVolumeReconstruction)
  if(NOT TARGET ${_t})
    add_library(${_t} SHARED IMPORTED)
    set_target_properties(${_t} PROPERTIES
      IMPORTED_LOCATION "${_igsio_libdir}/lib${_t}.so"
      INTERFACE_INCLUDE_DIRECTORIES "${_igsio_incdir}")
  endif()
endforeach()

set(IGSIO_LIBRARIES vtkIGSIOCommon vtkSequenceIO vtkVolumeReconstruction)
set(IGSIO_FOUND TRUE)
IGSIOCFG

%files
%license LICENSE
# IGSIO libs are unversioned (no SOVERSION upstream), so .so-only in the main pkg.
%{_libdir}/lib*.so

%files devel
%{_includedir}/IGSIO-1.0/
%{_libdir}/cmake/IGSIO/

%changelog
* Mon Jun 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.2.20260615git5a2d9dcf
- Ship a relocatable install-tree IGSIOConfig.cmake in igsio-devel (upstream only
  generates a build-tree config). Defines imported targets vtkIGSIOCommon /
  vtkSequenceIO / vtkVolumeReconstruction (DT_NEEDED carries the VTK/ITK/vtkAddon
  closure) and the per-component include vars, with VP9/MKV off to match the
  library build. Unblocks find_package(IGSIO) for the SlicerIGSIO -> SlicerIGT
  build chain. Validated with a find_package(IGSIO) configure test.

* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260615git5a2d9dcf
- Initial package. IGSIO git snapshot built standalone against system VTK + ITK
  (USE_3DSlicer off, MKV/VP9 off, volume reconstruction on) for the SlicerIGSIO
  and SlicerIGT build chain.
