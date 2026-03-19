%global _lto_cflags %{nil}
# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

# VTK compilation is parallelism-friendly but link steps are memory-heavy.
# Limit to avoid OOM on COPR workers (16 GB RAM, many large shared libs).
%global _smp_mflags -j8

Name:           vtk
Version:        9.5.2
Release:        10%{?dist}
Summary:        Visualization Toolkit - a high level 3D visualization library

License:        BSD-3-Clause
URL:            https://vtk.org/
Source0:        https://www.vtk.org/files/release/9.5/VTK-%{version}.tar.gz
# Patch required libharu version check (system libharu >= 2.3.0 is sufficient)
Patch0:         vtk-libharu.patch
# Tk 9.0 compatibility fix
Patch1:         vtk-tk9.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6UiPlugin)
BuildRequires:  boost-devel
BuildRequires:  cli11-devel
BuildRequires:  double-conversion-devel
BuildRequires:  expat-devel
# fast_float and eigen3 are bundled: system versions use SameMajorVersion cmake
# compatibility and Fedora ships fast_float 8.x / eigen3 5.x (on F44+) while
# VTK bundles older major versions, causing find_package() failures.
BuildRequires:  fmt-devel >= 8.1.0
BuildRequires:  freeglut-devel
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
BuildRequires:  libxkbcommon-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  lz4-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  openslide-devel
BuildRequires:  PEGTL-devel
BuildRequires:  proj-devel
BuildRequires:  pugixml-devel
BuildRequires:  sqlite-devel
BuildRequires:  tcl-devel
BuildRequires:  tk-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  libxml2-devel
BuildRequires:  chrpath

# Bundled libraries (not yet separately packaged or carrying local modifications)
Provides:       bundled(eigen3)
Provides:       bundled(fast_float)
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

%description
VTK is an open-source software system for image processing, 3D
graphics, volume rendering and visualization. VTK includes many
advanced algorithms (e.g., surface reconstruction, implicit modeling,
decimation) and rendering techniques (e.g., hardware-accelerated
volume rendering, LOD control).

This COPR package provides VTK 9.5 for applications requiring
a newer VTK than the Fedora system package (9.2.6).

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-qt%{?_isa} = %{version}-%{release}
Requires:       python3-%{name}%{?_isa} = %{version}-%{release}
Requires:       cmake
# Qt6 cmake configs referenced by VTK module targets
Requires:       cmake(Qt6Core)
Requires:       cmake(Qt6Widgets)
Requires:       cmake(Qt6OpenGL)
Requires:       cmake(Qt6OpenGLWidgets)
Requires:       qt6-qtdeclarative-devel
# Transitive dependencies: VTK-vtk-module-find-packages.cmake runs
# find_package() for every unbundled module when a downstream consumer
# calls find_package(VTK).  All -devel packages below must be installed
# or the downstream configure will fail.
Requires:       boost-devel
Requires:       cgnslib-devel
Requires:       double-conversion-devel%{?_isa}
Requires:       expat-devel%{?_isa}
Requires:       fmt-devel%{?_isa}
Requires:       freetype-devel%{?_isa}
Requires:       gdal-devel
Requires:       glew-devel%{?_isa}
Requires:       hdf5-devel%{?_isa}
Requires:       json-devel
Requires:       jsoncpp-devel%{?_isa}
Requires:       libarchive-devel%{?_isa}
Requires:       libGL-devel%{?_isa}
Requires:       libharu-devel%{?_isa}
Requires:       libjpeg-devel%{?_isa}
Requires:       libogg-devel%{?_isa}
Requires:       libpng-devel%{?_isa}
# libpq-devel conflicts with postgresql-private-devel on F43; use Recommends
# to avoid unresolvable dep chains. VTK SQL module is optional for most consumers.
Recommends:     libpq-devel%{?_isa}
Requires:       libtheora-devel%{?_isa}
Requires:       libtiff-devel%{?_isa}
Requires:       libX11-devel%{?_isa}
Requires:       libXcursor-devel%{?_isa}
Requires:       libXext-devel%{?_isa}
Requires:       libxml2-devel%{?_isa}
Requires:       libXt-devel%{?_isa}
Requires:       lz4-devel%{?_isa}
Recommends:     mariadb-connector-c-devel%{?_isa}
Requires:       netcdf-cxx-devel%{?_isa}
Requires:       nlohmann-json-devel
Requires:       openslide-devel%{?_isa}
Requires:       PEGTL-devel
Requires:       proj-devel%{?_isa}
Requires:       pugixml-devel%{?_isa}
Requires:       sqlite-devel%{?_isa}
Requires:       utf8cpp-devel
Requires:       xz-devel%{?_isa}
Requires:       zlib-devel%{?_isa}
Requires:       python3-devel

%description devel
This provides the VTK header files and cmake config required to compile
C++ programs that use VTK 9.5.

%package -n python3-%{name}
Summary:        Python 3 bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}
Python 3 bindings for VTK 9.5.

%package qt
Summary:        Qt6 widgets and rendering for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description qt
Qt6 rendering and widget libraries for VTK 9.5.

%prep
%autosetup -p1 -n VTK-%{version}

# Remove bundled third-party sources replaced by system packages.
# fast_float and eigen3 are intentionally NOT removed — system versions have
# incompatible major versions vs what VTK expects (SameMajorVersion compat).
for x in vtkcli11 vtkdoubleconversion vtkexpat \
          vtkfmt vtkfreetype vtkhdf5 vtkjpeg vtkjsoncpp vtklibharu \
          vtklibproj vtklibxml2 vtklz4 vtklzma vtknetcdf vtknlohmannjson \
          vtkogg vtkpegtl vtkpng vtkpugixml vtksqlite vtktheora vtktiff \
          vtkutf8 vtkzlib
do
  rm -rf ThirdParty/*/${x}
done

%build
export CFLAGS="%{optflags} -D_UNICODE -DHAVE_UINTPTR_T"
export CXXFLAGS="%{optflags} -D_UNICODE -DHAVE_UINTPTR_T"

%cmake -GNinja \
    -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
    -DVTK_VERSIONED_INSTALL:BOOL=OFF \
    -DVTK_CUSTOM_LIBRARY_SUFFIX="" \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DVTK_BUILD_TESTING:BOOL=OFF \
    -DVTK_BUILD_DOCUMENTATION:BOOL=OFF \
    -DVTK_BUILD_EXAMPLES:BOOL=OFF \
    -DVTK_WRAP_PYTHON:BOOL=ON \
    -DVTK_WRAP_JAVA:BOOL=OFF \
    -DVTK_USE_TK:BOOL=ON \
    -DVTK_GROUP_ENABLE_Qt:STRING=YES \
    -DVTK_GROUP_ENABLE_Rendering:STRING=YES \
    -DVTK_GROUP_ENABLE_Imaging:STRING=YES \
    -DVTK_GROUP_ENABLE_Views:STRING=YES \
    -DVTK_GROUP_ENABLE_StandAlone:STRING=YES \
    -DVTK_PYTHON_OPTIONAL_LINK:BOOL=OFF \
    -DVTK_ENABLE_OSPRAY:BOOL=OFF \
    -DVTK_MODULE_ENABLE_VTK_RenderingExternal:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingAnari:STRING=NO \
    -DVTK_MODULE_ENABLE_VTK_fides:STRING=NO \
    -DVTK_MODULE_ENABLE_VTK_IOADIOS2:STRING=NO \
    -DVTK_MODULE_ENABLE_VTK_IOOpenVDB:STRING=NO \
    -DVTK_MODULE_ENABLE_VTK_FiltersOpenTURNS:STRING=NO \
    -DVTK_MODULE_ENABLE_VTK_GeovisGDAL:STRING=NO \
    -DVTK_MODULE_ENABLE_VTK_IOOCCT:STRING=NO \
    -DVTK_MODULE_ENABLE_VTK_RenderingMatplotlib:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingVolumeAMR:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingParallel:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOXdmf2:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOVPIC:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOAvmesh:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOH5part:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOH5Rage:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOOMF:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOParallelExodus:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOParallelLSDyna:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOPIO:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_IOTRUCHAS:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_FiltersParallelDIY2:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_FiltersParallelVerdict:STRING=YES \
    -DVTK_MODULE_ENABLE_VTK_FiltersParallelStatistics:STRING=YES \
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

%install
%cmake_install

# Remove the FindHDF5 cmake patch — this fix is already in cmake itself
rm -f %{buildroot}%{_libdir}/cmake/vtk/patches/99/FindHDF5.cmake

# Strip RPATHs from installed binaries
find %{buildroot}%{_bindir} -type f -exec chrpath --delete {} \; 2>/dev/null || true

# Separate Qt libraries into their own file lists for subpackage
ls %{buildroot}%{_libdir}/libvtkGUISupportQt*.so.* \
   %{buildroot}%{_libdir}/libvtkRenderingQt*.so.* \
   %{buildroot}%{_libdir}/libvtkViewsQt*.so.* \
   2>/dev/null | sed "s|%{buildroot}||" > /tmp/vtk-qt-libs.txt || true

%ldconfig_scriptlets

%files
%{_datadir}/licenses/VTK/
%doc README.md
%{_libdir}/libvtk*.so.*
# Qt libs are in the -qt subpackage
%exclude %{_libdir}/libvtkGUISupportQt*.so.*
%exclude %{_libdir}/libvtkRenderingQt*.so.*
%exclude %{_libdir}/libvtkViewsQt*.so.*

%files devel
%{_includedir}/vtk/
%{_libdir}/cmake/vtk/
%{_libdir}/libvtk*.so
%{_bindir}/vtk*

%files -n python3-%{name}
%{python3_sitearch}/vtkmodules/
%{python3_sitearch}/vtk.py
%{python3_sitearch}/__pycache__/vtk.cpython-*.pyc
%{_libdir}/vtk/

%files qt
%{_libdir}/libvtkGUISupportQt*.so.*
%{_libdir}/libvtkRenderingQt*.so.*
%{_libdir}/libvtkViewsQt*.so.*

%changelog
* Thu Mar 19 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-10
- vtk-devel: add Requires qt6-qtdeclarative-devel (VTK cmake config
  runs find_package(Qt6Qml) which requires Qt6Declarative headers)

* Thu Mar 19 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-9
- Add missing vtk-devel Requires: zlib-devel, python3-devel
  (VTK cmake config calls find_package(ZLIB) and find_package(Python3))

* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-8
- Downgrade libpq-devel and mariadb-connector-c-devel from Requires to
  Recommends: libpq-devel conflicts with postgresql-private-devel on F43,
  causing unresolvable dep chains for all vtk-devel consumers

* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-7
- Enable 15 additional VTK modules required by ParaView with external VTK:
  RenderingMatplotlib, RenderingVolumeAMR, RenderingParallel, IOXdmf2, IOVPIC,
  IOAvmesh, IOH5part, IOH5Rage, IOOMF, IOParallelExodus, IOParallelLSDyna,
  IOPIO, IOTRUCHAS, FiltersParallelDIY2, FiltersParallelVerdict,
  FiltersParallelStatistics

* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-6
- vtk-devel: add ~35 transitive Requires for cmake find_package consumers
  VTK-vtk-module-find-packages.cmake runs find_package() for all unbundled
  module dependencies; downstream packages need these -devel packages installed
- vtk-devel: add Requires on vtk-qt subpackage (Qt .so symlinks need it)

* Fri Feb 27 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-5
- Explicitly enable VTK_MODULE_ENABLE_VTK_RenderingExternal=YES: module is not
  in the Rendering group so VTK_GROUP_ENABLE_Rendering=YES did not enable it;
  required by ITK-SNAP 4.x standalone.cmake FIND_PACKAGE(VTK COMPONENTS ...)

* Thu Feb 26 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-4
- Add debug_package suppression via define scope to fix EPEL 9 SRPM rebuild
  failure caused by auto-injected debuginfo stanza

* Thu Feb 26 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-3
- Fix unpackaged files: add licenses/VTK/ to base, add vtk.py
  and libdir/vtk/hierarchy/ to python3-vtk subpackage

* Thu Feb 26 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-2
- Bundle fast_float and eigen3 instead of using system versions; Fedora ships
  fast_float 8.x and eigen3 5.x (F44+) but VTK expects older major versions,
  causing SameMajorVersion cmake compat failures identical to ITK/Eigen3 issue

* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 9.5.2-1
- Initial COPR package of VTK 9.5.2 for Fedora 43/44
- Simplified spec: no MPI, no Java, no testing/examples/doc packages
- Targets neuroimaging apps requiring VTK >= 9.3 (ITK-SNAP, medInria)
- Based on Fedora rawhide vtk.spec with GDAL, OpenCASCADE, Anari disabled
- Fetched patches from Fedora: vtk-libharu.patch, vtk-tk9.patch
