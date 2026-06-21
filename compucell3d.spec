# CompuCell3D bundles a heavily modified muParser and a very old Eigen 3.1.1;
# system muParser has different API; bundled Eigen is only used by PDESolvers.
# ViennaCL is header-only for OpenCL (disabled here).
%define debug_package %{nil}

# Upstream hardcodes USE_LIBRARY_VERSIONS=OFF and sets empty SOVERSION.
# We override this to inject proper SOVERSION for Fedora shared lib policy.
# When USE_LIBRARY_VERSIONS=ON, upstream sets SOVERSION=MAJOR.MINOR (4.9).
%global cc3d_soversion 4.9

# 4.9.0 is a release candidate: upstream ships it on the release/4.9.0 branch
# and as binary RC installers on SourceForge, but has NOT cut a 4.9.0 git tag
# yet (newest tag is 4.8.0-fix-3). We therefore build a pre-release snapshot
# from the branch tip commit. Bump %%commit0 (and the changelog/date) when the
# branch advances; switch Source0 back to the tag and Release to 1 once 4.9.0
# is tagged.
%global commit0 780374e5e17145de12452aeabd224710134fa53f
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           compucell3d
Version:        4.9.0
Release:        0.3.rc.20260617git%{shortcommit0}%{?dist}
Summary:        Multi-scale virtual tissue simulation environment

License:        MIT
URL:            https://github.com/CompuCell3D/CompuCell3D
Source0:        %{url}/archive/%{commit0}/CompuCell3D-%{commit0}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.14
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  patchelf
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
# Runtime imports of the cc3d engine (per upstream conda meta.yaml run: deps).
# Without these the engine fails to import before a simulation can start.
Requires:       python3-lxml
Requires:       python3-scipy
Requires:       python3-pandas
Requires:       python3-jinja2
Requires:       python3-psutil
Requires:       python3-deprecated
# webcolors is an optional cosmetic dep (named-colour parsing in logging);
# missing it only prints a warning, so pull it weakly.
Recommends:     python3-webcolors
# Optional sub-cellular network solvers (imported lazily; the engine warns, not
# fatal, when absent). Pulled weakly so the demos work out of the box:
#   - python3-roadrunner : SBML continuous kinetics (cc3d.core.RoadRunner)
#   - python3-cc3dext     : bundled MaBoSS Boolean networks (cc3d.core.MaBoSSCC3D)
#   - python3-simservice  : service-mode (CC3D-as-a-service) simulations
Recommends:     python3-roadrunner
Recommends:     python3-cc3dext
Recommends:     python3-simservice

%description -n python3-%{name}
Python 3 SWIG bindings and the cc3d Python package for scripting
CompuCell3D cellular Potts model simulations.  Includes the cc3d Python
module, SWIG wrapper modules (CompuCell, CC3DXML, PlayerPython, etc.),
and plugin/steppable shared libraries.

Example simulations are installed under %{_datadir}/compucell3d/Demos/.
To run one headlessly (engine only) pass its .cc3d project to the bundled
runner, for example the Angiogenesis demo under the Demos subdirectory
BookChapterDemos_ComputationalMethodsInCellBiology/Angiogenesis/:

  cc3d_runScript.sh -i <demo-dir>/Angiogenesis.cc3d

To run the same example interactively with rendering, install the
cc3d-player5 package (see that package).

%package devel
Summary:        Development headers for CompuCell3D
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
C++ development headers and CMake config files for building plugins and
steppables against the CompuCell3D simulation engine.

%prep
%autosetup -n CompuCell3D-%{commit0}

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

# --- $ORIGIN RPATHs for the private cc3d/cpp library tree ---
# The SWIG extension modules (_CompuCell.so, etc.) and the CC3D plugin/steppable
# libraries are installed under %%{python3_sitelib}/cc3d/cpp/, which is NOT on the
# loader path. The SWIG modules have DT_NEEDED entries for the plugin/steppable
# libs (e.g. libCC3DBiasVectorSteppable.so.%%{cc3d_soversion}), so without an
# RPATH the engine fails to import. Core libs in %%{_libdir} resolve via the
# default path. Fedora permits RPATH that points into a package's own private
# libdir, so use $ORIGIN-relative entries (no standard-dir RPATH -> rpmlint clean).
_cpp=%{buildroot}%{python3_sitelib}/cc3d/cpp
if [ -d "${_cpp}" ]; then
    # Top-level SWIG modules need both sibling plugin/steppable dirs.
    find "${_cpp}" -maxdepth 1 -name '*.so' \
        -exec patchelf --set-rpath '$ORIGIN/CompuCell3DPlugins:$ORIGIN/CompuCell3DSteppables' {} \;
    # Plugin and steppable libs reference each other across the two dirs.
    find "${_cpp}/CompuCell3DPlugins" -name '*.so*' -type f \
        -exec patchelf --set-rpath '$ORIGIN:$ORIGIN/../CompuCell3DSteppables' {} \;
    find "${_cpp}/CompuCell3DSteppables" -name '*.so*' -type f \
        -exec patchelf --set-rpath '$ORIGIN:$ORIGIN/../CompuCell3DPlugins' {} \;
fi

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

# Upstream's run scripts invoke bare "python" (does not exist on Fedora) and
# hardcode a python-version-specific PYTHONPATH. Point them at python3 and the
# real interpreter sitelib so the engine runs in a clean Fedora environment.
sed -i -e 's|^export PYTHON_EXEC=python$|export PYTHON_EXEC=python3|' \
       -e 's|^export PYTHONPATH=.*$|export PYTHONPATH=%{python3_sitelib}|' \
    %{buildroot}%{_bindir}/cc3d_runScript.sh \
    %{buildroot}%{_bindir}/cc3d_paramScan.sh

# Remove License/ReleaseNotes installed to prefix root (we use RPM tags)
rm -f %{buildroot}%{_prefix}/License.txt \
      %{buildroot}%{_prefix}/ReleaseNotes.rst \
      %{buildroot}/License.txt \
      %{buildroot}/ReleaseNotes.rst

# --- Install the bundled example simulations (Demos) ---
# Upstream does not install these; they are the canonical way to exercise the
# engine and the Player (e.g. the Angiogenesis example). Ship them at a stable,
# documented path so the run command is predictable:
#   cc3d-player5 -i %%{_datadir}/compucell3d/Demos/.../Angiogenesis/Angiogenesis.cc3d
install -d %{buildroot}%{_datadir}/compucell3d
cp -a CompuCell3D/core/Demos %{buildroot}%{_datadir}/compucell3d/Demos
# These are example data, not executables: drop any shebangs/exec bits so
# rpmlint does not flag non-interpreter scripts under %%{_datadir}.
find %{buildroot}%{_datadir}/compucell3d/Demos -type f -name '*.py' -exec chmod 0644 {} +
# Drop VCS/hidden cruft shipped in the demo tree (rpmlint: version-control-internal-file).
find %{buildroot}%{_datadir}/compucell3d/Demos -name '.gitignore' -delete

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
# Bundled example simulations (Angiogenesis, cellsort, etc.) for testing the
# engine and the Player.
%{_datadir}/compucell3d/

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
* Sat Jun 20 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.3.rc.20260617git780374e
- Weakly pull the sub-cellular network solvers now that they are packaged:
  Recommends python3-roadrunner (SBML), python3-cc3dext (bundled MaBoSS),
  python3-simservice (service mode) — enables the SBML/MaBoSS demos.

* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.2.rc.20260617git780374e
- Rebuild to deliver the runtime fixes (python3 run-script, $ORIGIN RPATHs,
  lxml/scipy/pandas/jinja2/psutil/deprecated Requires, webcolors Recommends,
  installed Demos); 0.1 was never bumped across rebuilds so dnf would not
  upgrade past the first incomplete build. No source change (same commit).

* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.1.rc.20260615git780374e
- Update to 4.9.0 release candidate (release/4.9.0 branch, commit 780374e;
  no upstream 4.9.0 tag cut yet, so packaged as a pre-release snapshot)
- Bump injected SOVERSION 4.8 -> 4.9 to track upstream MAJOR.MINOR scheme
- Install bundled example simulations to %%{_datadir}/compucell3d/Demos/
  (incl. the Angiogenesis example) and document the headless run command
- Make the package actually runnable (build-success was masking runtime breaks):
  * Fix cc3d_runScript.sh / cc3d_paramScan.sh to call python3 (not bare
    "python", absent on Fedora) and use the real interpreter sitelib
  * Add $ORIGIN RPATHs to the private cc3d/cpp SWIG/plugin/steppable libs so
    the engine can load libCC3D*Steppable/Plugin libs at import time
  * Add the engine's runtime python deps (lxml, scipy, pandas, jinja2,
    psutil, deprecated) that were missing from Requires
- Validated end-to-end by running the Angiogenesis demo headlessly

* Thu Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 4.8.0-1
- Update to 4.8.0

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
