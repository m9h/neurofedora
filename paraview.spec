# Disable LTO — causes linker issues with large C++ builds
%global _lto_cflags %{nil}

# Suppress debug packages — they are enormous for ParaView
%define debug_package %{nil}

# Limit parallelism to prevent OOM on COPR workers
%global _smp_mflags -j4

%global pv_maj 6
%global pv_min 0
%global pv_patch 1
%global pv_majmin %{pv_maj}.%{pv_min}

Name:           paraview
Version:        %{pv_maj}.%{pv_min}.%{pv_patch}
Release:        1%{?dist}
Summary:        Parallel visualization application using VTK

License:        BSD-3-Clause
URL:            https://www.paraview.org/
Source0:        https://www.paraview.org/files/v%{pv_majmin}/ParaView-v%{version}.tar.gz
# MIME type definition for ParaView data files
Source1:        paraview.xml

# Fix location of resources (look in share/paraview as well as share/paraview-VERSION)
Patch0:         paraview-resources.patch
# Fix build with Qt 6.10.1 — cast unscoped enums to int in QtTesting
# https://gitlab.kitware.com/paraview/qttesting/-/commit/c11a762d
Patch1:         paraview-qt6101-qttesting.diff
# Fix build with Qt 6.10.1 — cast unscoped enums to int in ParaView Qt code
# https://gitlab.kitware.com/paraview/paraview/-/commit/cd7e633d
Patch2:         paraview-qt6101-main.patch

ExcludeArch:    %{ix86}

# ---- Build Tools ----
BuildRequires:  cmake >= 3.12
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  patchelf
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# ---- External VTK 9.5.2 from mhough/neurofedora COPR ----
BuildRequires:  vtk-devel >= 9.5.2

# ---- VTK transitive cmake deps ----
# VTK-vtk-module-find-packages.cmake runs find_package() for all unbundled
# modules; these -devel packages must be present or configure fails.
# (Once vtk-devel Requires are hardened, this block can be removed.)
BuildRequires:  boost-devel
BuildRequires:  cgnslib-devel
BuildRequires:  double-conversion-devel
BuildRequires:  expat-devel
BuildRequires:  fmt-devel >= 8.1.0
BuildRequires:  freetype-devel
BuildRequires:  gdal-devel
BuildRequires:  hdf5-devel
BuildRequires:  json-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  libarchive-devel
BuildRequires:  libGL-devel
BuildRequires:  libharu-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libogg-devel
BuildRequires:  libpng-devel
BuildRequires:  libpq-devel
BuildRequires:  libtheora-devel
BuildRequires:  libtiff-devel
BuildRequires:  libX11-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXext-devel
BuildRequires:  libxml2-devel
BuildRequires:  libXt-devel
BuildRequires:  lz4-devel
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  openslide-devel
BuildRequires:  PEGTL-devel
BuildRequires:  proj-devel
BuildRequires:  pugixml-devel
BuildRequires:  sqlite-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel

# ---- Qt6 ----
BuildRequires:  cmake(Qt6)
BuildRequires:  cmake(Qt6Core5Compat)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6UiPlugin)

# ---- Python ----
BuildRequires:  python3-devel

# ---- Other direct ParaView dependencies ----
BuildRequires:  cli11-devel
BuildRequires:  eigen3-devel
BuildRequires:  fast_float-devel
BuildRequires:  openssl-devel
BuildRequires:  protobuf-devel
BuildRequires:  readline-devel
BuildRequires:  tk-devel

# ---- Runtime dependencies ----
Requires:       %{name}-data = %{version}-%{release}
Requires:       hdf5%{?_hdf5_version: = %{_hdf5_version}}
Requires:       python3-numpy
Requires:       qt6-qtsvg%{?_isa}

# ParaView bundles these components even when using external VTK
Provides:       bundled(catalyst) = 2.0
Provides:       bundled(diy2)
Provides:       bundled(exprtk) = 2.71
Provides:       bundled(h5part) = 1.6.6
Provides:       bundled(icet)
Provides:       bundled(ioss)
Provides:       bundled(kwsys-base64)
Provides:       bundled(kwsys-commandlinearguments)
Provides:       bundled(kwsys-directory)
Provides:       bundled(kwsys-dynamicloader)
Provides:       bundled(kwsys-encoding)
Provides:       bundled(kwsys-fstream)
Provides:       bundled(kwsys-fundamentaltype)
Provides:       bundled(kwsys-glob)
Provides:       bundled(kwsys-md5)
Provides:       bundled(kwsys-process)
Provides:       bundled(kwsys-regularexpression)
Provides:       bundled(kwsys-status)
Provides:       bundled(kwsys-system)
Provides:       bundled(kwsys-systeminformation)
Provides:       bundled(kwsys-systemtools)
Provides:       bundled(libharu)
Provides:       bundled(qttesting)
Provides:       bundled(verdict) = 1.4.0
Provides:       bundled(xdmf2)

# Do not auto-provide anything from paraview's private library directory
%global __provides_exclude_from ^%{_libdir}/paraview/.*$
# Do not auto-require paraview's private libraries
%global __requires_exclude ^lib(catalyst|LegacyGhostCellsGenerator|IceT|pq|QtTesting|StereoCursorViews|vtk).*$

%description
ParaView is an open-source, multi-platform data analysis and visualization
application. ParaView users can quickly build visualizations to analyze their
data using qualitative and quantitative techniques. The data exploration can
be done interactively in 3D or programmatically using ParaView's batch
processing capabilities.

This package is built against external VTK 9.5.2 from the mhough/neurofedora
COPR, with Python 3 and Qt6 support enabled. MPI, Catalyst, raytracing,
and VisitBridge are disabled for simplicity.

%package data
Summary:        Data files for ParaView
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description data
Architecture-independent data files for ParaView including icons, desktop
integration, and shared resources.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vtk-devel%{?_isa}

%description devel
Headers, cmake config, and static libraries for developing applications
that use ParaView.

%package -n python3-%{name}
Summary:        Python 3 bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-numpy

%description -n python3-%{name}
Python 3 bindings for ParaView, providing programmatic access to the
ParaView visualization pipeline.

%prep
%autosetup -p1 -n ParaView-v%{version}

# Install python properly
sed -i -s '/VTK_INSTALL_PYTHON_USING_CMAKE/s/TRUE/FALSE/' CMakeLists.txt

%build
# GCC 15 / Fedora 43 compatibility
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
export CFLAGS="%{optflags} -std=gnu17 -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"

%cmake -GNinja -Wno-dev \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_INSTALL_DOCDIR:PATH=share/doc/%{name} \
    -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib}/paraview \
    -DOpenGL_GL_PREFERENCE=GLVND \
    \
    -DPARAVIEW_USE_EXTERNAL_VTK:BOOL=ON \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    \
    -DPARAVIEW_BUILD_SHARED_LIBS:BOOL=ON \
    -DPARAVIEW_VERSIONED_INSTALL:BOOL=OFF \
    -DPARAVIEW_INSTALL_DEVELOPMENT_FILES:BOOL=ON \
    \
    -DPARAVIEW_USE_PYTHON:BOOL=ON \
    -DVTK_PYTHON_VERSION=3 \
    -DPARAVIEW_ENABLE_GDAL:BOOL=ON \
    \
    -DPARAVIEW_USE_MPI:BOOL=OFF \
    -DPARAVIEW_ENABLE_CATALYST:BOOL=OFF \
    -DPARAVIEW_ENABLE_RAYTRACING:BOOL=OFF \
    -DPARAVIEW_ENABLE_VISITBRIDGE:BOOL=OFF \
    -DPARAVIEW_ENABLE_XDMF3:BOOL=OFF \
    -DPARAVIEW_ENABLE_FIDES:BOOL=OFF \
    -DPARAVIEW_ENABLE_ADIOS2:BOOL=OFF \
    -DPARAVIEW_ENABLE_FFMPEG:BOOL=OFF \
    -DPARAVIEW_ENABLE_OPENVDB:BOOL=OFF \
    -DPARAVIEW_ENABLE_LAS:BOOL=OFF \
    -DPARAVIEW_ENABLE_PDAL:BOOL=OFF \
    -DPARAVIEW_ENABLE_MOTIONFX:BOOL=OFF \
    \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON

%cmake_build

%install
%cmake_install

# Install MIME type definition
install -d %{buildroot}%{_datadir}/mime/packages
install -m644 %{SOURCE1} %{buildroot}%{_datadir}/mime/packages/paraview.xml

# Validate desktop and appdata files
desktop-file-validate %{buildroot}%{_datadir}/applications/org.paraview.ParaView.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/org.paraview.ParaView.appdata.xml

# Remove VTK wrapper binaries that conflict with vtk-devel
rm -f %{buildroot}%{_bindir}/vtk{ParseJava,ProbeOpenGLVersion,Wrap{Hierarchy,Java,Python,SerDes}}* 2>/dev/null || true

# Fix permissions on source-like files
find %{buildroot} \( -name \*.txt -o -name \*.xml -o -name '*.[ch]' -o -name '*.[ch][px][px]' \) -print0 | xargs -0 chmod -x 2>/dev/null || true

# Create doc symlink for ParaView internal lookups
if [ -d %{buildroot}%{_datadir}/paraview ]; then
    ln -sf ../doc/paraview %{buildroot}%{_datadir}/paraview/doc
fi

%files
%{_bindir}/paraview
%{_bindir}/paraview.conf
%{_bindir}/pvbatch
%{_bindir}/pvdataserver
%{_bindir}/pvpython
%{_bindir}/pvrenderserver
%{_bindir}/pvserver
%{_bindir}/smTestDriver
%{_libdir}/paraview/
%exclude %{_libdir}/paraview/*.a

%files data
%license Copyright.txt
%{_datadir}/metainfo/org.paraview.ParaView.appdata.xml
%{_datadir}/applications/org.paraview.ParaView.desktop
%{_datadir}/icons/hicolor/*/apps/paraview.png
%{_datadir}/licenses/ParaView/
%{_datadir}/mime/packages/paraview.xml
%{_datadir}/paraview/

%files devel
%{_bindir}/paraview-config
%{_bindir}/vtkWrapClientServer
%{_bindir}/vtkProcessXML
%{_includedir}/paraview/
%{_libdir}/cmake/paraview/
%{_libdir}/paraview/*.a

%files -n python3-%{name}
# Python modules are installed inside the paraview lib directory.
# The main paraview package owns the paraview libdir tree.

%changelog
* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.1-1
- Initial COPR package of ParaView 6.0.1 for Fedora 43
- Built against external VTK 9.5.2 (PARAVIEW_USE_EXTERNAL_VTK=ON)
- Python 3 and Qt6 GUI enabled; GDAL support enabled
- MPI, Catalyst, raytracing, VisitBridge, XDMF3, ADIOS2 disabled
- Qt 6.10.1 compatibility patches from Fedora rawhide
- GCC 15 / Fedora 43 compatibility flags
