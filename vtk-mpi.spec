%global _lto_cflags %{nil}
# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

# Linker is memory-heavy; cap parallelism to avoid OOM on COPR workers.
%global _smp_mflags -j8

# MPI flavors. Disable a flavor here only if upstream consumer (paraview)
# also drops its matching MPI subpackage.
%bcond_without mpich
%bcond_without openmpi

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
Name:           vtk-mpi
Version:        9.6.2
Release:        7%{?dist}
Summary:        Visualization Toolkit - MPI-parallel variants

License:        BSD-3-Clause
URL:            https://vtk.org/
Source0:        https://www.vtk.org/files/release/9.6/VTK-%{version}.tar.gz
Patch0:         vtk-libharu.patch
# Bundled h5hut module is missing a VTK::mpi dependency, so vtk_mpi.h is not on
# its include path once IOH5part is enabled in an MPI build (FTBFS at -6).
Patch1:         vtk-h5hut-mpi-dep.patch

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

# External Viskores (sibling COPR package viskores-1.1.0-2+). VTK's
# AcceleratorsVTKmFilters module finds it via the viskores::cont/
# cont_testing/filter/worklet imported targets viskores-devel exports.
BuildRequires:  viskores-devel
# Qt6 BR for vtk-mpi -6 (paraview-mpi needs VTK::GUISupportQt module).
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6UiPlugin)

# Bundled libraries (intentional — see SPECS/vtk.spec for rationale)
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
Provides:       bundled(xdmf2)
Provides:       bundled(xdmf3)

%description
This source package builds the MPI-parallel variants of VTK (vtk-mpich,
vtk-openmpi) for the neurofedora COPR. The serial VTK is shipped by the
sibling vtk package at the same version. ParaView's mpich/openmpi
subpackages BuildRequire vtk-{mpich,openmpi}-devel.

%if %{with mpich}
%package -n vtk-mpich
Summary:        VTK 9.6 - mpich parallel runtime
Requires:       mpich

%description -n vtk-mpich
Visualization Toolkit shared libraries built against mpich.
Install vtk-mpich-devel for headers and cmake configs.

%package -n vtk-mpich-devel
Summary:        VTK 9.6 - mpich development files
Requires:       vtk-mpich%{?_isa} = %{version}-%{release}
Requires:       mpich-devel
Requires:       cmake

%description -n vtk-mpich-devel
Headers and cmake configuration for building MPI-parallel applications
against vtk-mpich. Loaded by `module load mpi/mpich-%{_arch}` before
running cmake on a downstream project.
%endif

%if %{with openmpi}
%package -n vtk-openmpi
Summary:        VTK 9.6 - openmpi parallel runtime
Requires:       openmpi

%description -n vtk-openmpi
Visualization Toolkit shared libraries built against openmpi.
Install vtk-openmpi-devel for headers and cmake configs.

%package -n vtk-openmpi-devel
Summary:        VTK 9.6 - openmpi development files
Requires:       vtk-openmpi%{?_isa} = %{version}-%{release}
Requires:       openmpi-devel
Requires:       cmake

%description -n vtk-openmpi-devel
Headers and cmake configuration for building MPI-parallel applications
against vtk-openmpi. Loaded by `module load mpi/openmpi-%{_arch}` before
running cmake on a downstream project.
%endif

%prep
%autosetup -p1 -n VTK-%{version}

# Match SPECS/vtk.spec: unbundle the third-party trees that have system
# packages, keep vtkhdf5 + vtkfreetype bundled for rawhide compatibility.
for x in vtkcli11 vtkdoubleconversion vtkexpat \
          vtkfmt vtkjpeg vtkjsoncpp vtklibharu \
          vtklibproj vtklibxml2 vtklz4 vtklzma vtknetcdf vtknlohmannjson \
          vtkogg vtkpegtl vtkpng vtkpugixml vtksqlite vtktheora vtktiff \
          vtkutf8 vtkviskores vtkzlib
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
      -DVTK_GROUP_ENABLE_Qt:STRING=YES \
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
      `# Additional modules required by paraview-{mpich,openmpi}-6.1.1's` \
      `# plugin scan (CMakeLists.txt:568 in upstream paraview). Caught by` \
      `# build 10550668 after vtk-mpi -5 shipped too lean.` \
      -DVTK_MODULE_ENABLE_VTK_IOXdmf2:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOVPIC:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOH5part:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOH5Rage:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOOMF:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_IOTRUCHAS:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelDIY2:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelVerdict:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_FiltersParallelStatistics:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_GUISupportQt:STRING=YES \
      -DVTK_MODULE_ENABLE_VTK_RenderingVolumeAMR:STRING=YES \
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
      -DVTK_MODULE_USE_EXTERNAL_VTK_vtkviskores:BOOL=ON
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

  # Capture the runtime shared libraries for the %files manifest. Viskores
  # ships from the sibling viskores package now — VTK's external-Viskores
  # build doesn't install libviskores* under $MPI_HOME.
  ls %{buildroot}$MPI_HOME/lib/libvtk*.so.* \
    | sed "s|%{buildroot}||" > %{_vpath_builddir}/libs.list

  module purge
done

%ldconfig_scriptlets -n vtk-mpich
%ldconfig_scriptlets -n vtk-openmpi

%if %{with mpich}
%files -n vtk-mpich -f %{_vendor}-%{_target_os}-build-mpich/libs.list
%{_libdir}/mpich/share/licenses/VTK/

%files -n vtk-mpich-devel
%{_libdir}/mpich/include/vtk/
%{_libdir}/mpich/lib/cmake/vtk/
%{_libdir}/mpich/lib/libvtk*.so
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
%endif

%if %{with openmpi}
%files -n vtk-openmpi -f %{_vendor}-%{_target_os}-build-openmpi/libs.list
%{_libdir}/openmpi/share/licenses/VTK/

%files -n vtk-openmpi-devel
%{_libdir}/openmpi/include/vtk/
%{_libdir}/openmpi/lib/cmake/vtk/
%{_libdir}/openmpi/lib/libvtk*.so
%dir %{_libdir}/openmpi/lib/vtk
%{_libdir}/openmpi/lib/vtk/hierarchy/
%{_libdir}/openmpi/bin/vtkParseJava
%{_libdir}/openmpi/bin/vtkProbeOpenGLVersion
%{_libdir}/openmpi/bin/vtkWrapHierarchy
%{_libdir}/openmpi/bin/vtkWrapJava
%{_libdir}/openmpi/bin/vtkWrapJavaScript
%{_libdir}/openmpi/bin/vtkWrapPython
%{_libdir}/openmpi/bin/vtkWrapPythonInit
%{_libdir}/openmpi/bin/vtkWrapSerDes
%endif

%changelog
* Mon Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-7
- Fix FTBFS introduced at -6 (enabling IOH5part): the bundled VTK::h5hut
  module's vtk.module declares DEPENDS VTK::hdf5 only. In an MPI build the
  bundled hdf5 reports H5_HAVE_PARALLEL, so h5t_octree.h reaches its parallel
  branch and #include <vtk_mpi.h>, but without a VTK::mpi dependency that
  module's include dir is never propagated - "fatal error: vtk_mpi.h: No such
  file". Add VTK::mpi to the h5hut DEPENDS (vtk-h5hut-mpi-dep.patch). Unblocks
  paraview 6.1.1 (which requires IOH5part)

* Wed Jun  3 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-6
- Enable Qt group + 11 parallel I/O/filter modules required by paraview
  6.1.1's MPI variants (paraview-mpich, paraview-openmpi). vtk-mpi -5
  shipped only the bare ParallelMPI/FiltersParallelMPI set; paraview
  build 10550668 failed at CMakeLists.txt:568 with the full demand list
  (IOXdmf2, IOVPIC, IOH5part, IOH5Rage, IOOMF, IOTRUCHAS,
  FiltersParallelDIY2/Verdict/Statistics, GUISupportQt,
  RenderingVolumeAMR). Add Qt6 BRs to match.

* Mon Jun  1 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-5
- Unbundle Viskores (mirror vtk.spec -11). Consume sibling COPR package
  viskores-1.1.0-2 via VTK_MODULE_USE_EXTERNAL_VTK_vtkviskores=ON; drop
  the two Provides:bundled(viskores) lines; drop libviskores* + the
  pkgconfig file from both MPI %%files manifests; remove vtkviskores
  from the install-time libs.list glob; add vtkviskores to the %%prep
  unbundle loop; add BR: viskores-devel. Tracks
  [[vtk-viskores-split-backlog]].


* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.2-4
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
