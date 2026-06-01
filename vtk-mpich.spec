%global _lto_cflags %{nil}
# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

# Linker is memory-heavy; cap parallelism to avoid OOM on COPR workers.
%global _smp_mflags -j8

# MPI flavors. Disable a flavor here only if upstream consumer (paraview)
# also drops its matching MPI subpackage.
%bcond_without mpich
%bcond_with openmpi

%global mpi_list %{nil}
%if %{with mpich}
%global mpi_list %mpi_list mpich
%endif
%if %{with openmpi}
%global mpi_list %mpi_list openmpi
%endif

# $mpi gets substituted in the per-flavor build loops below so each
# variant has its own out-of-tree build directory.
%global _vpath_builddir %{_vendor}-%{_target_os}-build-${mpi}

# Source name + version tracks the sibling vtk package exactly. This spec
# only produces the vtk-mpich / vtk-openmpi subpackages — the serial vtk
# is built by SPECS/vtk.spec (already shipping 9.6.2-5 in this COPR).
Name:           vtk-mpich
Version:        9.6.2
Release:        3%{?dist}
Summary:        VTK 9.6 - mpich parallel runtime

License:        BSD-3-Clause
URL:            https://vtk.org/
Source0:        https://www.vtk.org/files/release/9.6/VTK-%{version}.tar.gz
Patch0:         vtk-libharu.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  boost-devel
BuildRequires:  cli11-devel
BuildRequires:  gdal-devel
BuildRequires:  double-conversion-devel
BuildRequires:  expat-devel
BuildRequires:  fmt-devel >= 8.1.0
BuildRequires:  freetype-devel
BuildRequires:  hdf5-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  json-devel
BuildRequires:  libGL-devel
BuildRequires:  libharu-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libogg-devel
BuildRequires:  libpng-devel
BuildRequires:  libtheora-devel
BuildRequires:  libtiff-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  lz4-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  PEGTL-devel
BuildRequires:  proj-devel
BuildRequires:  pugixml-devel
BuildRequires:  sqlite-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  libxml2-devel
BuildRequires:  chrpath
BuildRequires:  environment-modules

%if %{with mpich}
BuildRequires:  mpich-devel
BuildRequires:  netcdf-mpich-devel
%endif
%if %{with openmpi}
BuildRequires:  openmpi-devel
BuildRequires:  netcdf-openmpi-devel
%endif

# Bundled libraries (intentional — see SPECS/vtk.spec for rationale)
Provides:       bundled(viskores)
Provides:       bundled(eigen3)
Provides:       bundled(fast_float)
Provides:       bundled(hdf5) = 1.14.6
Provides:       bundled(freetype)
Provides:       bundled(kwsys)
Provides:       bundled(diy2)
Provides:       bundled(exodusII) = 2.0.0
Provides:       bundled(exprtk)
Provides:       bundled(gl2ps) = 1.4.0
Provides:       bundled(h5part)
Provides:       bundled(ioss)
Provides:       bundled(kissfft)
Provides:       bundled(loguru)
Provides:       bundled(metaio)
Provides:       bundled(scn)
Provides:       bundled(token)
Provides:       bundled(verdict)
Provides:       bundled(viskores)
Provides:       bundled(xdmf2)
Provides:       bundled(xdmf3)

Requires:       mpich

%description
Visualization Toolkit shared libraries built against mpich.
Install vtk-mpich-devel for headers and cmake configs.

This spec is the mpich-only split of the former vtk-mpi superpackage
(which timed out in COPR when building both MPI flavors sequentially).
The serial VTK is shipped by the sibling vtk package.

%package devel
Summary:        VTK 9.6 - mpich development files
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       mpich-devel
Requires:       cmake

%description devel
Headers and cmake configuration for building MPI-parallel applications
against vtk-mpich. Loaded by `module load mpi/mpich-%{_arch}` before
running cmake on a downstream project.

%prep
%autosetup -p1 -n VTK-%{version}

# Match SPECS/vtk.spec: unbundle the third-party trees that have system
# packages, keep vtkhdf5 + vtkfreetype bundled for rawhide compatibility.
for x in vtkcli11 vtkdoubleconversion vtkexpat \
          vtkfmt vtkjpeg vtkjsoncpp vtklibharu \
          vtklibproj vtklibxml2 vtklz4 vtklzma vtknetcdf vtknlohmannjson \
          vtkogg vtkpegtl vtkpng vtkpugixml vtksqlite vtktheora vtktiff \
          vtkutf8 vtkzlib
do
  rm -rf ThirdParty/*/${x}
done

%build
export CFLAGS="%{optflags} -D_UNICODE -DHAVE_UINTPTR_T"
export CXXFLAGS="%{optflags} -D_UNICODE -DHAVE_UINTPTR_T"
export CC=mpicc
export CXX=mpic++

for mpi in %{mpi_list}
do
  module load mpi/$mpi-%{_arch}
  %cmake -GNinja \
      -DCMAKE_PREFIX_PATH:PATH=$MPI_HOME \
      -DCMAKE_INSTALL_PREFIX:PATH=$MPI_HOME \
      -DCMAKE_INSTALL_LIBDIR:PATH=lib \
      -DVTK_VERSIONED_INSTALL:BOOL=OFF \
      -DVTK_CUSTOM_LIBRARY_SUFFIX="" \
      -DBUILD_SHARED_LIBS:BOOL=ON \
      -DVTK_BUILD_TESTING:BOOL=OFF \
      -DVTK_BUILD_DOCUMENTATION:BOOL=OFF \
      -DVTK_BUILD_EXAMPLES:BOOL=OFF \
      -DVTK_WRAP_PYTHON:BOOL=OFF \
      -DVTK_WRAP_JAVA:BOOL=OFF \
      -DVTK_USE_TK:BOOL=OFF \
      -DVTK_GROUP_ENABLE_Qt:STRING=NO \
      -DVTK_GROUP_ENABLE_Rendering:STRING=YES \
      -DVTK_GROUP_ENABLE_Imaging:STRING=YES \
      -DVTK_GROUP_ENABLE_Views:STRING=YES \
      -DVTK_GROUP_ENABLE_StandAlone:STRING=YES \
      -DVTK_USE_MPI:BOOL=ON \
      -DVTK_MODULE_ENABLE_VTK_ParallelMPI:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_mpi:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelMPI:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelFlowPaths:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelGeometry:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOMPIImage:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOParallelNetCDF:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOParallelExodus:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOParallelLSDyna:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOPIO:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_RenderingParallel:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_RenderingParallelLIC:STRING=YES \
      `# Required by ParaView 6.1.1 MPI flavors. Skip the Web modules` \
      `# (WebCore / WebGLExporter / WebPython) — they all require` \
      `# VTK::Python which is intentionally off for MPI variants per` \
      `# Fedora packaging convention. paraview.spec compensates by` \
      `# setting PARAVIEW_ENABLE_WEB=OFF for the MPI flavors.` \
      -DVTK_MODULE_ENABLE_VTK_cli11:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOGDAL:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_AcceleratorsVTKmFilters:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOXdmf2:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelDIY2:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelVerdict:STRING=YES \
      -DVTK_MODULE_USE_EXTERNAL_VTK_hdf5:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_vtkhdf5:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_freetype:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_vtkfreetype:BOOL=OFF \
      -DHDF5_IS_PARALLEL:BOOL=FALSE \
      -DVTK_MODULE_USE_EXTERNAL_VTK_cli11:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_doubleconversion:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_eigen:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_expat:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_fast_float:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_fmt:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_freetype:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_hdf5:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_jpeg:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_jsoncpp:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_libharu:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_libproj:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_libxml2:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_lz4:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_lzma:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_netcdf:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_nlohmannjson:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_ogg:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_pegtl:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_png:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_pugixml:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_sqlite:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_theora:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_tiff:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_utf8:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_zlib:BOOL=ON \
      -DVTK_MODULE_USE_EXTERNAL_VTK_exprtk:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_gl2ps:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_ioss:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_scn:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_token:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_verdict:BOOL=OFF \
      -DVTK_MODULE_USE_EXTERNAL_VTK_vtkviskores:BOOL=OFF
  %cmake_build
  module purge
done

%install
for mpi in %{mpi_list}
do
  module load mpi/$mpi-%{_arch}
  %cmake_install

  # Strip build-time RPATHs from any installed binaries.
  find %{buildroot}$MPI_HOME/bin -type f -exec chrpath --delete {} \; 2>/dev/null || true

  # Capture the runtime shared libraries for the %files manifest.
  # Include bundled libviskores* (built when AcceleratorsVTKmFilters is enabled).
  ls %{buildroot}$MPI_HOME/lib/libvtk*.so.* \
     %{buildroot}$MPI_HOME/lib/libviskores*.so.* \
    | sed "s|%{buildroot}||" > %{_vpath_builddir}/libs.list

  module purge
done

%ldconfig_scriptlets

%files -f %{_vendor}-%{_target_os}-build-mpich/libs.list
%{_libdir}/mpich/share/licenses/VTK/

%files devel
%{_libdir}/mpich/include/vtk/
%{_libdir}/mpich/lib/cmake/vtk/
%{_libdir}/mpich/lib/libvtk*.so
%{_libdir}/mpich/lib/libviskores*.so
%{_libdir}/mpich/lib/pkgconfig/viskores.pc
%dir %{_libdir}/mpich/lib/vtk
%{_libdir}/mpich/lib/vtk/hierarchy/
%{_libdir}/mpich/bin/vtkParseJava
%{_libdir}/mpich/bin/vtkProbeOpenGLVersion
%{_libdir}/mpich/bin/vtkWrapHierarchy
%{_libdir}/mpich/bin/vtkWrapJava
%{_libdir}/mpich/bin/vtkWrapJavaScript
%{_libdir}/mpich/bin/vtkWrapPython
%{_libdir}/mpich/bin/vtkWrapPythonInit
%{_libdir}/mpich/bin/vtkWrapSerDes

%changelog
* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-3
- Bump Release past the old vtk-mpi-9.6.2-2 leftover binary subpackages.
  paraview-6.1.1-8 build 10529609 pulled vtk-mpich-devel-9.6.2-2.fc44
  (from the timed-out vtk-mpi-4 attempt) instead of the new
  9.6.2-1 because 9.6.2-2 > 9.6.2-1 in rpm version comparison.
  All the cli11 / IOGDAL / AcceleratorsVTKmFilters targets ARE in
  9.6.2-1 RPMs but dnf prefers the higher-Release older build.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-1
- Split from vtk-mpi.spec (mpich-only variant). Building both mpich
  + openmpi sequentially overran COPR's 5h timeout; vtk-mpi-9.6.2-4
  build 10528750 was killed at the 5h mark. Splitting halves the
  per-spec build to ~2.5h, comfortably within the limit. The serial
  VTK is shipped by SPECS/vtk.spec at the same version. The openmpi
  flavor lives in SPECS/vtk-openmpi.spec.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-4 (vtk-mpi)
- Drop the three Web module enables from -3. They all depend on
  VTK::Python which is intentionally off for MPI variants
  (VTK_WRAP_PYTHON=OFF). Build 10528746 failed in 60s with
  "VTK::WebCore requires the disabled module VTK::Python".
  paraview.spec must set PARAVIEW_ENABLE_WEB=OFF in MPI options
  to compensate. Keep cli11 / IOGDAL / AcceleratorsVTKmFilters.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-3
- Match vtk-9.6.2-10's module set so the MPI flavors of ParaView can
  pull WebCore / WebGLExporter / WebPython / cli11 / IOGDAL /
  AcceleratorsVTKmFilters from vtk-mpich-devel + vtk-openmpi-devel
  instead of falling back to the system Fedora vtk-mpi-9.6.2-2.
- BuildRequires gdal-devel + Provides bundled(viskores) + extend
  libs.list and -devel %files to ship the per-flavor libviskores
  set and viskores.pc.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-2
- Complete %%files manifest: include $MPI_HOME/lib/vtk/hierarchy/
  (268 module hierarchy files per flavor, used by downstream wrapping)
  and the 8 vtk wrapper binaries under $MPI_HOME/bin/ that the build
  installs unconditionally. Build 10522607 -1 compiled both flavors
  cleanly (~4h) but failed the unpackaged-files check.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-1
- Initial vtk-mpi spec, sibling to vtk-9.6.2-5. Builds vtk-mpich and
  vtk-openmpi variants only (no serial vtk, no Qt, no Python wrappers).
  Unblocks paraview-6.1.x which BuildRequires vtk-{mpich,openmpi}-devel.
