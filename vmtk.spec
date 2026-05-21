# Disable LTO - causes linker issues with VTK on Fedora 43+
%global _lto_cflags %{nil}

# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

%global commit 311f4792bc0145a12204a17e478e0bcedafb372d
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate 20250820

# vtkAddon cmake macros for Python wrapping (downloaded by CMake/CMakeLists.txt
# at configure time; we bundle them for offline mock/COPR builds)
%global vtkaddon_commit cf1126568415179fb5b1c16121087bd2494e2e0e

Name:           vmtk
Version:        1.5.0
Release:        0.2.%{snapdate}git%{shortcommit}%{?dist}
Summary:        The Vascular Modeling Toolkit

# vmtk core: BSD-3-Clause
# Bundled TetGen 1.4.3: MIT-like (pre-AGPLv3 license)
# Bundled OpenNL: BSD-3-Clause
License:        BSD-3-Clause
URL:            http://www.vmtk.org/
Source0:        https://github.com/vmtk/vmtk/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

# vtkAddon cmake wrapping macros (4 files needed for Python wrapping)
# These are normally downloaded at configure time; bundle for offline builds
Source10:       https://raw.githubusercontent.com/Slicer/vtkAddon/%{vtkaddon_commit}/CMake/vtkMacroKitPythonWrap.cmake
Source11:       https://raw.githubusercontent.com/Slicer/vtkAddon/%{vtkaddon_commit}/CMake/vtkWrapHierarchy.cmake
Source12:       https://raw.githubusercontent.com/Slicer/vtkAddon/%{vtkaddon_commit}/CMake/vtkWrapPython.cmake
Source13:       https://raw.githubusercontent.com/Slicer/vtkAddon/%{vtkaddon_commit}/CMake/vtkWrapperInit.data.in

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake >= 3.12
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  chrpath
BuildRequires:  python3-devel
BuildRequires:  python3-numpy

# ITK 5.x
BuildRequires:  InsightToolkit5-devel
BuildRequires:  hdf5-devel

# VTK 9.5.2 (COPR)
BuildRequires:  vtk-devel
# VTK cmake config transitive deps (COPR vtk-devel doesn't Require these)
BuildRequires:  json-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  fmt-devel
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  PEGTL-devel
BuildRequires:  libglvnd-devel
BuildRequires:  libtheora-devel
BuildRequires:  libogg-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  fontconfig-devel
BuildRequires:  expat-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  sqlite-devel
BuildRequires:  libxml2-devel
BuildRequires:  netcdf-devel
BuildRequires:  proj-devel
BuildRequires:  tbb-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  libharu-devel
BuildRequires:  gl2ps-devel
BuildRequires:  double-conversion-devel
BuildRequires:  eigen3-devel
BuildRequires:  cli11-devel
BuildRequires:  boost-devel
BuildRequires:  gdal-devel
BuildRequires:  postgresql-server-devel

# X11 / GL
BuildRequires:  libX11-devel
BuildRequires:  libXt-devel
BuildRequires:  libGL-devel

# Bundled libs (source not separated from vmtk)
Provides:       bundled(tetgen) = 1.4.3
Provides:       bundled(OpenNL)

%description
vmtk is a collection of libraries and tools for 3D reconstruction,
geometric analysis, mesh generation and surface data analysis for
image-based modeling of blood vessels. It provides centerline computation,
surface mesh generation, and hemodynamic simulation capabilities.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vtk-devel
Requires:       InsightToolkit5-devel

%description    devel
This package contains the header files, libraries and CMake config
files for developing applications with %{name}.

%package -n     python3-%{name}
Summary:        Python 3 bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-vtk
Requires:       python3-numpy

%description -n python3-%{name}
Python 3 bindings, scripts, and PypeS framework for the Vascular
Modeling Toolkit. Includes ~150 scripts for centerline computation,
surface mesh generation, and hemodynamic analysis.

%prep
%autosetup -n %{name}-%{commit}

# Pre-populate vtkAddon cmake macros so CMake/CMakeLists.txt does not
# attempt network downloads (which fail in mock/COPR).
mkdir -p CMake/vtkAddon
cp %{SOURCE10} CMake/vtkAddon/
cp %{SOURCE11} CMake/vtkAddon/
cp %{SOURCE12} CMake/vtkAddon/
cp %{SOURCE13} CMake/vtkAddon/

# Replace CMake/CMakeLists.txt: upstream downloads vtkAddon cmake files at
# configure time via file(DOWNLOAD ...). Point to our pre-populated copies.
cat > CMake/CMakeLists.txt << 'CMAKEOF'
# vtkAddon cmake macros for Python wrapping (pre-populated from Source10-13)
set(vtkAddon_CMAKE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vtkAddon" CACHE PATH
    "Path to vtkAddon cmake macros" FORCE)
list(INSERT CMAKE_MODULE_PATH 0 ${vtkAddon_CMAKE_DIR})
CMAKEOF

# Add SOVERSION to all vtkvmtk libraries (Fedora packaging requirement).
# The vmtk_build_library() function in CMake/vmtkFunctions.cmake creates
# all library targets; inject VERSION/SOVERSION after the LINKER_LANGUAGE line.
sed -i '/set_target_properties.*LINKER_LANGUAGE CXX/a \
  set_target_properties(${lib_name} PROPERTIES VERSION %{version} SOVERSION 1)' \
    CMake/vmtkFunctions.cmake

# Fix cmake minimum version for CMake 4+ compatibility
sed -i 's|cmake_minimum_required(VERSION 3.12...3.29.1)|cmake_minimum_required(VERSION 3.12...4.0)|' CMakeLists.txt

# Fix cmake config install paths: upstream uses TYPE LIB (dumps into libdir)
# and installs VMTK-Targets to the build dir. Fix both to use standard cmake dir.
sed -i 's|install(EXPORT VMTK-Targets DESTINATION ${VMTK_BINARY_DIR})|install(EXPORT VMTK-Targets DESTINATION %{_lib}/cmake/vmtk)|' CMakeLists.txt
sed -i 's|TYPE LIB|DESTINATION %{_lib}/cmake/vmtk|' CMakeLists.txt

# Fix tetgen install: upstream puts libtet.a in BIN_DIR (bug)
sed -i 's|install(TARGETS tet DESTINATION ${VTK_VMTK_INSTALL_BIN_DIR}|install(TARGETS tet DESTINATION ${VTK_VMTK_INSTALL_LIB_DIR}|' \
    vtkVmtk/Utilities/tetgen1.4.3/CMakeLists.txt

%build
# GCC 15 / Fedora 43+ compatibility
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint -fpermissive"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17 -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"

%cmake \
    -DVMTK_USE_SUPERBUILD:BOOL=OFF \
    -DUSE_SYSTEM_VTK:BOOL=ON \
    -DUSE_SYSTEM_ITK:BOOL=ON \
    -DVTK_VMTK_WRAP_PYTHON:BOOL=ON \
    -DVMTK_USE_VTK9:BOOL=ON \
    -DVMTK_USE_ITK5:BOOL=ON \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DVMTK_WITH_LIBRARY_VERSION:BOOL=ON \
    -DVMTK_CONTRIB_SCRIPTS:BOOL=ON \
    -DVMTK_SCRIPTS_ENABLED:BOOL=ON \
    -DVMTK_USE_RENDERING:BOOL=ON \
    -DVMTK_BUILD_TETGEN:BOOL=ON \
    -DVMTK_TEST_DATA_SOURCE:STRING=in-place \
    -DVMTK_BUILD_TESTING:BOOL=OFF \
    -DBUILD_VMTK_DOCUMENTATION:BOOL=OFF \
    -DVMTK_PYTHON_VERSION:STRING=python%{python3_version} \
    -DVMTK_MINIMAL_INSTALL:BOOL=OFF \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    -DVTK_VMTK_INSTALL_LIB_DIR:PATH=%{_lib} \
    -DVTK_VMTK_INSTALL_BIN_DIR:PATH=bin \
    -DVTK_VMTK_INSTALL_INCLUDE_DIR:PATH=include/vmtk \
    -DVTK_VMTK_MODULE_INSTALL_LIB_DIR:PATH=%{python3_sitearch}/vmtk \
    -DVMTK_SCRIPTS_INSTALL_BIN_DIR:PATH=bin \
    -DVMTK_SCRIPTS_INSTALL_LIB_DIR:PATH=%{python3_sitelib}/vmtk \
    -DPYPES_INSTALL_BIN_DIR:PATH=bin \
    -DPYPES_MODULE_INSTALL_LIB_DIR:PATH=%{python3_sitelib}/vmtk

%cmake_build

%install
%cmake_install

# Fix Python shebangs: upstream uses "#!/usr/bin/env python" which Fedora rejects
find %{buildroot}%{_bindir} -type f -exec \
    sed -i '1s|^#!/usr/bin/env python$|#!/usr/bin/python3|' {} +
find %{buildroot}%{python3_sitelib} -name '*.py' -exec \
    sed -i '1s|^#!/usr/bin/env python$|#!/usr/bin/python3|' {} +

# Remove stray __init__ script from bindir (cmake installs it alongside bin scripts)
rm -f %{buildroot}%{_bindir}/__init__

# Strip RPATHs for Fedora compliance
find %{buildroot}%{_libdir} -name '*.so*' -exec chrpath --delete {} \; 2>/dev/null || :
find %{buildroot}%{_bindir} -type f -exec chrpath --delete {} \; 2>/dev/null || :
find %{buildroot}%{python3_sitearch} -name '*.so' -exec chrpath --delete {} \; 2>/dev/null || :

%ldconfig_scriptlets

%files
%license LICENSE
%{_libdir}/libvtkvmtk*.so.1
%{_libdir}/libvtkvmtk*.so.%{version}

%files devel
%{_includedir}/vmtk/
%{_libdir}/libvtkvmtk*.so
%{_libdir}/cmake/vmtk/
# Bundled static archives (OpenNL, tetgen)
%{_libdir}/libnl.a
%{_libdir}/libtet.a

%files -n python3-%{name}
# Python wrapper C extensions (arch-specific .so modules)
%{python3_sitearch}/vmtk/
# Pure Python scripts and PypeS framework
%{python3_sitelib}/vmtk/
# CLI entry points (vmtk*, pype* scripts)
%{_bindir}/*

%changelog
* Mon Apr 21 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.0-0.2.20250820git311f4792
- Fix VMTK_PYTHON_VERSION detection (upstream uses wrong cmake variable names)
- Fix cmake config install paths to standard libdir/cmake/vmtk/
- Fix tetgen static archive install to libdir (was bindir)
- Fix Python shebangs: #!/usr/bin/env python → #!/usr/bin/python3
- Add VMTK_TEST_DATA_SOURCE=in-place to avoid Git build requirement
- Remove stray __init__ from bindir

* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.0-0.1.20250820git311f4792
- Initial package (git snapshot for VTK 9.5 / ITK 5.4 support)
- Superbuild disabled; builds against system VTK 9.5.2 and ITK 5.4.5
- vtkAddon cmake macros bundled for offline Python wrapping
- Bundled: tetgen 1.4.3, OpenNL
