# CompuCell3D bundles a heavily modified muParser and a very old Eigen 3.1.1;
# system muParser has different API; bundled Eigen is only used by PDESolvers.
# ViennaCL is header-only for OpenCL (disabled here).
%define debug_package %{nil}

# Upstream hardcodes USE_LIBRARY_VERSIONS=OFF and sets empty SOVERSION.
# We override this to inject proper SOVERSION for Fedora shared lib policy.
# When USE_LIBRARY_VERSIONS=ON, upstream sets SOVERSION=MAJOR.MINOR (4.7).
%global cc3d_soversion 4.7

Name:           compucell3d
Version:        4.7.0
Release:        5%{?dist}
Summary:        Multi-scale virtual tissue simulation environment

License:        MIT
URL:            https://github.com/CompuCell3D/CompuCell3D
Source0:        https://github.com/CompuCell3D/CompuCell3D/archive/refs/tags/%{version}/CompuCell3D-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.14
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  zlib-devel
BuildRequires:  swig
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
# VTK 9 for the SWIG bindings (FieldExtractor, SerializerDE, PlayerPython)
BuildRequires:  vtk-devel
# VTK transitive cmake deps (VTK cmake config requires these at find_package time)
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  hdf5-devel
BuildRequires:  boost-devel
BuildRequires:  double-conversion-devel
BuildRequires:  expat-devel
BuildRequires:  glew-devel
BuildRequires:  lz4-devel
BuildRequires:  libxml2-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libGL-devel
BuildRequires:  sqlite-devel
BuildRequires:  libarchive-devel
BuildRequires:  proj-devel
BuildRequires:  gdal-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  cgnslib-devel
BuildRequires:  libharu-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  libpq-devel
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  openslide-devel
BuildRequires:  qt5-qtwebkit-devel
BuildRequires:  qt6-qtdeclarative-devel

# Explicit runtime deps
Requires:       python3-numpy
Requires:       python3-vtk

Provides:       bundled(muParser)
Provides:       bundled(eigen) = 3.1.1

%global _description %{expand:
CompuCell3D (CC3D) is a flexible scriptable simulation environment for
multi-scale virtual-tissue modeling.  It uses the Cellular Potts Model
(CPM, also known as the Glazier-Graner-Hogeweg model) to simulate cell
growth, division, adhesion, chemotaxis, and many other biological
phenomena.  The core engine is written in C++ with Python 3 SWIG bindings
and a cc3d Python package for scripting simulations.}

%description %{_description}

%package -n python3-%{name}
Summary:        Python 3 bindings and runtime for CompuCell3D
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-numpy
Requires:       python3-vtk

%description -n python3-%{name}
Python 3 SWIG bindings and the cc3d Python package for scripting
CompuCell3D cellular Potts model simulations.  Includes the cc3d Python
module, SWIG wrapper modules (CompuCell, CC3DXML, PlayerPython, etc.),
and plugin/steppable shared libraries.

%package devel
Summary:        Development headers for CompuCell3D
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
C++ development headers and CMake config files for building plugins and
steppables against the CompuCell3D simulation engine.

%prep
%autosetup -n CompuCell3D-%{version}

# --- Fix C++ standard for GCC 15 / Fedora 43 ---
# Upstream sets C++11; GCC 15 requires C++17 for missing implicit includes.
sed -i 's/set(CMAKE_CXX_STANDARD 11)/set(CMAKE_CXX_STANDARD 17)/' \
    CompuCell3D/CMakeLists.txt

# Also fix C++11 in DeveloperZone (not built, but prevents cmake warnings)
sed -i 's/SET(CMAKE_CXX_STANDARD 11)/SET(CMAKE_CXX_STANDARD 17)/' \
    CompuCell3D/DeveloperZone/CMakeLists.txt 2>/dev/null || :

# --- Inject SOVERSION ---
# Upstream force-sets USE_LIBRARY_VERSIONS=OFF and assigns empty VERSION/SOVERSION.
# 1) Change the hardcoded OFF to ON so the macro applies properties
sed -i 's/^SET(USE_LIBRARY_VERSIONS OFF)/SET(USE_LIBRARY_VERSIONS ON)/' \
    CompuCell3D/CMakeLists.txt
# 2) Replace the empty version properties in the ELSE(USE_LIBRARY_VERSIONS) branch
#    with our version numbers so they take effect regardless
sed -i 's/SET(COMPUCELL3D_LIBRARY_PROPERTIES ${COMPUCELL3D_LIBRARY_PROPERTIES} VERSION "" SOVERSION "")/SET(COMPUCELL3D_LIBRARY_PROPERTIES ${COMPUCELL3D_LIBRARY_PROPERTIES} VERSION "%{version}" SOVERSION "%{cc3d_soversion}")/' \
    CompuCell3D/CMakeLists.txt

# --- Inject SOVERSION for libraries built with plain ADD_LIBRARY ---
# FieldExtractor, PyPlugin, SerializerDE bypass the CC3D macro
for _target in FieldExtractor PyPlugin SerializerDE; do
    _cmfiles=$(grep -rl "ADD_LIBRARY(${_target}" CompuCell3D/core/pyinterface/ 2>/dev/null || :)
    for _cmf in ${_cmfiles}; do
        printf '\nset_target_properties(%s PROPERTIES VERSION "%{version}" SOVERSION "%{cc3d_soversion}")\n' \
            "${_target}" >> "${_cmf}"
    done
done

# --- Fix hardcoded "lib" install destinations for x86_64 ---
# With BUILD_STANDALONE=OFF + ANACONDA_PYTHON_LAYOUT=OFF, the code path at
# lines 187-191 of CMakeLists.txt sets COMPUCELL3D_LIBRARY_DESTINATION = "lib".
# Replace all occurrences in that non-anaconda else block.
# Strategy: replace all SET(COMPUCELL3D_LIBRARY_DESTINATION lib) with lib64-aware version
# (there are 3 occurrences total: standalone, anaconda, non-anaconda)
sed -i 's|SET(COMPUCELL3D_LIBRARY_DESTINATION lib)|SET(COMPUCELL3D_LIBRARY_DESTINATION ${CMAKE_INSTALL_LIBDIR})|g' \
    CompuCell3D/CMakeLists.txt
sed -i 's|SET(COMPUCELL3D_ARCHIVE_DESTINATION lib)|SET(COMPUCELL3D_ARCHIVE_DESTINATION ${CMAKE_INSTALL_LIBDIR})|g' \
    CompuCell3D/CMakeLists.txt
# Also fix cmake config install path (hardcoded lib/cmake/)
sed -i 's|SET(COMPUCELL3D_INSTALL_CONFIG_DIR lib/cmake/CompuCell3D)|SET(COMPUCELL3D_INSTALL_CONFIG_DIR ${CMAKE_INSTALL_LIBDIR}/cmake/CompuCell3D)|' \
    CompuCell3D/CMakeLists.txt

# Also fix the static lib install in compucell3d_cmake_macros.cmake
# (ADD_STATIC_LIBRARY macro hardcodes LIBRARY DESTINATION lib / ARCHIVE DESTINATION lib)
sed -i 's|LIBRARY DESTINATION lib$|LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}|' \
    CompuCell3D/compucell3d_cmake_macros.cmake
sed -i 's|ARCHIVE DESTINATION lib$|ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}|' \
    CompuCell3D/compucell3d_cmake_macros.cmake

# --- Fix install of License/ReleaseNotes to CMAKE_INSTALL_PREFIX root ---
# Upstream installs to absolute ${CMAKE_INSTALL_PREFIX}; RPM uses DESTDIR
sed -i '/install(FILES/,/DESTINATION/{s|DESTINATION\n.*${CMAKE_INSTALL_PREFIX}|DESTINATION .|;}' \
    CompuCell3D/CMakeLists.txt 2>/dev/null || :
# Simpler approach: just delete the install of these files (we use %%license/%%doc)
sed -i '/^install(FILES/,/^)/d' CompuCell3D/CMakeLists.txt

# --- Remove stdc++fs link (not needed on GCC 15; libstdc++fs merged into libstdc++) ---
sed -i 's/ stdc++fs//' CompuCell3D/core/PublicUtilities/CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
export CFLAGS="%{optflags} -std=gnu17 -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"

# The CMakeLists.txt is in CompuCell3D/ subdirectory of the tarball
pushd CompuCell3D
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_STANDALONE:BOOL=OFF \
    -DANACONDA_PYTHON_LAYOUT:BOOL=OFF \
    -DBUILD_PYINTERFACE:BOOL=ON \
    -DBUILD_QT_WRAPPERS:BOOL=OFF \
    -DBUILD_CPP_ONLY_EXECUTABLE:BOOL=OFF \
    -DUSE_DOLFIN:BOOL=OFF \
    -DNO_OPENCL:BOOL=ON \
    -DUSE_LIBRARY_VERSIONS:BOOL=ON \
    -DCOMPUCELL3D_TEST:BOOL=OFF \
    -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED:BOOL=ON
%cmake_build
popd

%install
pushd CompuCell3D
%cmake_install
popd

# Strip any RPATHs that cmake may have left despite SKIP_INSTALL_RPATH
find %{buildroot} -type f \( -name '*.so' -o -name '*.so.*' \) \
    -exec chrpath --delete {} \; 2>/dev/null || :

# Remove any stale .la files
find %{buildroot} -name '*.la' -delete

# Ensure libraries are in the correct libdir (safety net for lib vs lib64)
if [ "%{_lib}" != "lib" ] && [ -d "%{buildroot}%{_prefix}/lib" ]; then
    find %{buildroot}%{_prefix}/lib -maxdepth 1 -name '*.so*' \
        -exec mv -v {} %{buildroot}%{_libdir}/ \; 2>/dev/null || :
fi

# Fix world-writable permissions on scripts (upstream installs as 777)
chmod 755 %{buildroot}%{_bindir}/cc3d_runScript.sh \
          %{buildroot}%{_bindir}/cc3d_paramScan.sh

# Remove License/ReleaseNotes installed to prefix root (we use RPM tags)
rm -f %{buildroot}%{_prefix}/License.txt \
      %{buildroot}%{_prefix}/ReleaseNotes.rst \
      %{buildroot}/License.txt \
      %{buildroot}/ReleaseNotes.rst

%check
# Basic smoke test: verify core shared library was built with versioned SONAME
test -f %{buildroot}%{_libdir}/libCC3DCompuCellLib.so.%{cc3d_soversion}

%ldconfig_scriptlets

%files
%license CompuCell3D/License.txt
%doc README.rst
%doc CompuCell3D/ReleaseNotes.rst
# Core shared libraries (CC3DLogger, CC3DField3D, CC3DBoundary, CC3DAutomaton,
# CC3DPotts3D, CC3DPublicUtilities, CC3DXMLUtils, CC3DmuParser,
# CC3DExpressionEvaluator, CC3DCompuCellLib, and all CC3D plugin/steppable libs
# except those installed under site-packages/cc3d/cpp/)
%{_libdir}/libCC3D*.so.%{cc3d_soversion}
%{_libdir}/libCC3D*.so.%{version}
# FieldExtractor, PyPlugin, SerializerDE (built via pyinterface, but installed to libdir)
%{_libdir}/libFieldExtractor.so.%{cc3d_soversion}
%{_libdir}/libFieldExtractor.so.%{version}
%{_libdir}/libPyPlugin.so.%{cc3d_soversion}
%{_libdir}/libPyPlugin.so.%{version}
%{_libdir}/libSerializerDE.so.%{cc3d_soversion}
%{_libdir}/libSerializerDE.so.%{version}
# Run scripts (non-standalone mode prefixes with cc3d_)
%{_bindir}/cc3d_runScript.sh
%{_bindir}/cc3d_paramScan.sh

%files -n python3-%{name}
# The cc3d Python package installed to site-packages.
# This includes pure Python files AND the SWIG .so wrapper modules
# (CompuCell, CC3DXML, CC3DAuxFields, PlayerPython, SerializerDEPy)
# as well as plugin/steppable .so files under cc3d/cpp/CompuCell3DPlugins/
# and cc3d/cpp/CompuCell3DSteppables/.
%{python3_sitelib}/cc3d/

%files devel
# Development headers
%{_includedir}/CompuCell3D/
%{_includedir}/pyinterface/
%{_includedir}/SerializerDE/
# CMake config files
%{_libdir}/cmake/CompuCell3D/
# Unversioned .so symlinks (devel only)
%{_libdir}/libCC3D*.so
%{_libdir}/libFieldExtractor.so
%{_libdir}/libPyPlugin.so
%{_libdir}/libSerializerDE.so

%changelog
* Sun Mar 15 2026 Morgan Hough <mhough@fedoraproject.org> - 4.7.0-5
- Add all VTK transitive cmake BuildRequires for clean COPR builds
- Add qt6-qtdeclarative-devel (VTK cmake config requires Qt6Quick)

* Sat Mar 14 2026 Morgan Hough <mhough@fedoraproject.org> - 4.7.0-2
- Fix world-writable permissions on cc3d_runScript.sh and cc3d_paramScan.sh
- Fix SOVERSION to match upstream scheme (4.7 instead of 0)
- Fix cmake config install path (lib/cmake/ to lib64/cmake/ on x86_64)

* Sat Mar 14 2026 Morgan Hough <mhough@fedoraproject.org> - 4.7.0-1
- Initial draft RPM spec for CompuCell3D 4.7.0
- Build against system VTK 9, Python 3, with SWIG bindings
- Disable standalone mode (BUILD_STANDALONE=OFF) for FHS-compliant install
- Disable Qt wrappers (upstream requires Qt4, not available on Fedora 43)
- Disable OpenCL, CUDA, Dolfin optional components
- Bundle modified muParser and Eigen 3.1.1 (system versions incompatible)
- Inject SOVERSION into upstream cmake macros for Fedora shared library policy
- Patch lib to lib64 install destinations for x86_64
- Strip RPATHs for Fedora compliance
- Remove stdc++fs link (merged into libstdc++ on GCC 15)
- GCC 15 compatibility: C++17 standard, cstdint include, fpermissive
