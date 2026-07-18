# Disable LTO - causes linker issues with ITK on Fedora 43+
%global _lto_cflags %{nil}

%global commit 3bd8e038024b5a0684bf8284d4af0ac69cc0eb3c
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate 20260301

# On x86_64, _libdir is lib64; cmake config files use this for relative paths
%global sem_install_lib_dir %{_lib}

Name:           SlicerExecutionModel
Version:        2.0.0
Release:        0.10.%{snapdate}git%{shortcommit}%{?dist}
Summary:        CMake macros and tools for building 3D Slicer CLI modules

# Main code: 3D-Slicer-1.0 (BSD-style)
# Bundled tclap: MIT
License:        3D-Slicer-1.0 AND MIT
URL:            https://github.com/Slicer/SlicerExecutionModel
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

# Install-tree config templates (upstream has these as TODO)
Source1:        GenerateCLPInstallConfig.cmake.in
Source2:        SlicerExecutionModelInstallConfig.cmake.in

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  InsightToolkit5-devel
BuildRequires:  expat-devel
# find_package(ITK) loads ITKVtkGlue -> vtk-config, and VTK 9.6's cmake
# config now does find_package(CLI11) for all consumers at configure time.
BuildRequires:  cli11-devel

# Bundled tclap (header-only library, Slicer-modified version)
Provides:       bundled(tclap)

%description
SlicerExecutionModel is a CMake-based project that provides macros and
associated tools allowing to easily build 3D Slicer CLI (Command Line
Interface) modules. These are self-describing executables that automatically
generate XML descriptions of their command-line arguments, which 3D Slicer
uses to construct graphical user interfaces.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake
Requires:       InsightToolkit5-devel
Requires:       expat-devel

%description    devel
Development headers, CMake config files, and the GenerateCLP tool for
building applications that use %{name}.

%prep
%autosetup -n %{name}-%{commit}

# Install our install-tree config templates
cp -p %{SOURCE1} GenerateCLP/
cp -p %{SOURCE2} .

# --- Fix 1: Uncomment MDP install-tree config generation (upstream TODO) ---
sed -i '/^#configure_file(/,/^#  )/{s/^#//}' \
    ModuleDescriptionParser/GenerateModuleDescriptionParserConfig.cmake
# Remove the TODO comment line
sed -i '/^# TODO Configure ModuleDescriptionParser/d' \
    ModuleDescriptionParser/GenerateModuleDescriptionParserConfig.cmake

# --- Fix 2: Uncomment TCLAP install-tree config generation (upstream TODO) ---
sed -i 's|^#configure_file(\${TCLAP_SOURCE_DIR}/TCLAPInstallConfig|configure_file(\${TCLAP_SOURCE_DIR}/TCLAPInstallConfig|' \
    tclap/GenerateTCLAPConfig.cmake
sed -i 's|^#               \${TCLAP_BINARY_DIR}/install/TCLAPConfig|               \${TCLAP_BINARY_DIR}/install/TCLAPConfig|' \
    tclap/GenerateTCLAPConfig.cmake

# --- Fix 2b: Fix case mismatch in INSTALL_NO_DEVELOPMENT propagation ---
# Top-level sets tclap_INSTALL_NO_DEVELOPMENT but tclap checks TCLAP_INSTALL_NO_DEVELOPMENT
sed -i 's|set(tclap_INSTALL_NO_DEVELOPMENT|set(TCLAP_INSTALL_NO_DEVELOPMENT|' \
    CMakeLists.txt

# --- Fix 3: Add GenerateCLP install-tree config generation ---
# The CMakeLists.txt expects _install-suffixed files; add configure_file calls
cat >> GenerateCLP/GenerateGenerateCLPConfig.cmake << 'ENDOFPATCH'

# Settings specific for installation trees
set(SEM_INSTALL_LIB_DIR "%{sem_install_lib_dir}")
configure_file(${GenerateCLP_SOURCE_DIR}/GenerateCLPInstallConfig.cmake.in
  ${GenerateCLP_BINARY_DIR}/GenerateCLPConfig.cmake_install @ONLY)
configure_file(${GenerateCLP_SOURCE_DIR}/UseGenerateCLP.cmake.in
  ${GenerateCLP_BINARY_DIR}/UseGenerateCLP.cmake_install @ONLY)
ENDOFPATCH

# --- Fix 4: Add top-level SEM install-tree config generation ---
cat >> GenerateSlicerExecutionModelConfig.cmake << 'ENDOFPATCH'

# Settings specific for installation trees
set(SEM_INSTALL_LIB_DIR "%{sem_install_lib_dir}")
configure_file(
  ${SlicerExecutionModel_SOURCE_DIR}/SlicerExecutionModelInstallConfig.cmake.in
  ${SlicerExecutionModel_BINARY_DIR}/install/SlicerExecutionModelConfig.cmake
  @ONLY
  )
ENDOFPATCH

# --- Fix 5: Fix hardcoded lib/ cmake config install paths to use _libdir ---
# ModuleDescriptionParser cmake configs
sed -i 's|DESTINATION lib/\${lib_name}|DESTINATION %{sem_install_lib_dir}/\${lib_name}|' \
    ModuleDescriptionParser/CMakeLists.txt

# TCLAP cmake configs
sed -i 's|DESTINATION lib/tclap|DESTINATION %{sem_install_lib_dir}/tclap|' \
    tclap/CMakeLists.txt

# GenerateCLP cmake configs
sed -i 's|DESTINATION lib/GenerateCLP|DESTINATION %{sem_install_lib_dir}/GenerateCLP|' \
    GenerateCLP/CMakeLists.txt

# --- Fix 6: Add install rules for top-level SEM config ---
# Append to top-level CMakeLists.txt
cat >> CMakeLists.txt << 'ENDOFPATCH'

# Install top-level SEM config files
if(NOT SlicerExecutionModel_INSTALL_NO_DEVELOPMENT)
  set(_sem_cmake_install_dir %{sem_install_lib_dir}/SlicerExecutionModel)
  install(FILES
    ${SlicerExecutionModel_BINARY_DIR}/install/SlicerExecutionModelConfig.cmake
    DESTINATION ${_sem_cmake_install_dir}
    COMPONENT Development
    )
  install(FILES
    ${SlicerExecutionModel_BINARY_DIR}/UseSlicerExecutionModel.cmake
    DESTINATION ${_sem_cmake_install_dir}
    COMPONENT Development
    )
  # Install CMake support scripts needed by SEMMacroBuildCLI
  install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/CMake/
    DESTINATION ${_sem_cmake_install_dir}/CMake
    COMPONENT Development
    FILES_MATCHING
      PATTERN "*.cmake"
      PATTERN "*.cxx"
      PATTERN "*.in"
      PATTERN "*.manifest"
    )
endif()
ENDOFPATCH

# --- Fix 7: Update MDP InstallConfig to use correct relative lib dir ---
# The template assumes lib/ModuleDescriptionParser; fix for lib64 if needed
sed -i 's|"\${ModuleDescriptionParser_CONFIG_DIR}/../../include|"\${ModuleDescriptionParser_CONFIG_DIR}/../../include|' \
    ModuleDescriptionParser/ModuleDescriptionParserInstallConfig.cmake.in

# --- Fix 8: Update TCLAP InstallConfig relative paths ---
# (already correct - uses ../../include/)

%build
# GCC 15 / Fedora 43+ fixes
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17"

%cmake \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DSlicerExecutionModel_INSTALL_BIN_DIR=%{_bindir} \
    -DSlicerExecutionModel_INSTALL_LIB_DIR=%{_libdir}/%{name} \
    -DSlicerExecutionModel_INSTALL_NO_DEVELOPMENT=OFF \
    -DSlicerExecutionModel_USE_JSONCPP=OFF \
    -DSlicerExecutionModel_USE_UTF8=OFF \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4

%cmake_build

%install
%cmake_install

# Upstream's GenerateCLP/CMakeLists.txt doesn't install GenerateCLP.cmake,
# but UseGenerateCLP.cmake's last line does
#   include(${GenerateCLP_CMAKE_DIR}/GenerateCLP.cmake)
# so downstream cmake calls (e.g. 3D Slicer's SEMMacroBuildCLI) abort with
# "include could not find requested file: /usr/lib64/GenerateCLP/GenerateCLP.cmake".
install -p -m 0644 GenerateCLP/GenerateCLP.cmake \
    %{buildroot}%{_libdir}/GenerateCLP/

# Drop GenerateCLPLauncher: it's a CTKAppLauncher wrapper that, with no
# *LauncherSettings.ini shipped, resolves the real binary via the baked-in
# default <launcherDir>/../GenerateCLP = /usr/GenerateCLP (nonexistent),
# breaking downstream CLP generation (3D Slicer Modules/CLI). The launcher
# only existed to inject LD_LIBRARY_PATH for the private
# libModuleDescriptionParser.so; with that .so now installed into the standard
# %{_libdir}, GenerateCLP runs standalone and the launcher is dead weight.
rm -f %{buildroot}%{_bindir}/GenerateCLPLauncher

# Move libModuleDescriptionParser.so out of the private %{_libdir}/%{name}
# into the standard library path. Downstream consumers (3D Slicer's
# SlicerBaseCLI) link it as a bare "-lModuleDescriptionParser" with no -L,
# because UseModuleDescriptionParser.cmake.in's link_directories() line is
# commented out upstream and ModuleDescriptionParser_LIBRARY_DIRS points at the
# config dir, not the .so dir. Installing into %{_libdir} makes both the link
# (default -L) and runtime (ldconfig) resolution work without rpath hacks.
mv %{buildroot}%{_libdir}/%{name}/libModuleDescriptionParser.so \
    %{buildroot}%{_libdir}/libModuleDescriptionParser.so

%ldconfig_scriptlets

%files
%license License.txt tclap/COPYING
%doc README.md NOTICE
%{_libdir}/libModuleDescriptionParser.so

%files devel
%{_bindir}/GenerateCLP
%{_includedir}/ModuleDescriptionParser/
%{_includedir}/tclap/
%dir %{_libdir}/%{name}
%{_libdir}/GenerateCLP/
%{_libdir}/ModuleDescriptionParser/
%{_libdir}/tclap/
%{_libdir}/%{name}/CMake/
%{_libdir}/%{name}/SlicerExecutionModelConfig.cmake
%{_libdir}/%{name}/UseSlicerExecutionModel.cmake

%changelog
* Sun Jul 13 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.10
- MAJOR FIX: guard the DEFAULT_CLI_* output/install dir variables in the shipped
  SlicerExecutionModelConfig.cmake with if(NOT DEFINED ...). They were set
  unconditionally, and find_package(SlicerExecutionModel) is called MANY times by a
  consumer (3D Slicer: Base/CLI, Base/Logic, Base/QTCLI, Base/QTCore + every CLI
  module). Each call clobbered the consumer's values, so Slicer's central
  lib/Slicer-X.Y/cli-modules/ path was overwritten with our relative bin/lib64
  defaults; all 39 CLI modules built into their own per-module dirs and Slicer
  loaded ZERO of them. The shipped 3dslicer therefore had NO working CLI modules
  (Threshold/Resample/Cast/N4/...) and CropVolume could not load its dependency.
  Caught by the CTest farm; fix verified on a live build tree (AddScalarVolumes now
  links into lib/Slicer-5.12/cli-modules/).

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.9.20260301git3bd8e038
- Install libModuleDescriptionParser.so into the standard %%{_libdir} instead
  of the private %%{_libdir}/SlicerExecutionModel. 3D Slicer's SlicerBaseCLI
  links it as a bare "-lModuleDescriptionParser" with no -L (upstream's
  UseModuleDescriptionParser.cmake.in comments out link_directories() and
  ModuleDescriptionParser_LIBRARY_DIRS points at the config dir, not the .so
  dir), so the -0.8 build failed with "cannot find -lModuleDescriptionParser".
  Standard libdir makes both link-time (-L) and runtime (ldconfig) resolution
  work; restore CMAKE_SKIP_INSTALL_RPATH=ON (the GenerateCLP rpath hack is no
  longer needed) and add %%ldconfig_scriptlets.

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.8.20260301git3bd8e038
- Add cli11-devel BR. VTK 9.6's cmake config now does find_package(CLI11)
  for every consumer; SEM reaches it via find_package(ITK) -> ITKVtkGlue
  -> vtk-config. -0.6 predated the VTK 9.6 bump so didn't hit it. (The
  -0.7 launcher fix below never published — folded in here.)

* Sat May 30 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.7.20260301git3bd8e038
- Drop the broken GenerateCLPLauncher and run GenerateCLP directly.
  The launcher (a CTKAppLauncher wrapper) shipped without a settings
  .ini, so it resolved the real binary via the baked-in default
  <launcherDir>/../GenerateCLP = /usr/GenerateCLP and failed
  ("Error converting executable file /usr/bin/../GenerateCLP to real
  path"), breaking 3D Slicer's Modules/CLI CLP-header generation at
  build time. The install config's find_program preferred the launcher
  over GenerateCLP. Now: reorder NAMES to prefer GenerateCLP, give
  GenerateCLP an rpath to %%{_libdir}/SlicerExecutionModel so it loads
  the private libModuleDescriptionParser.so standalone, and stop
  shipping the launcher. Surfaced by 3dslicer-21.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.6.20260301git3bd8e038
- Install GenerateCLP/GenerateCLP.cmake explicitly. Upstream's
  GenerateCLP/CMakeLists.txt has no install() rule for it, but
  UseGenerateCLP.cmake's last line includes it via
  ${GenerateCLP_CMAKE_DIR}/GenerateCLP.cmake. Downstream cmake calls
  to SEMMacroBuildCLI (e.g. 3D Slicer's Modules/CLI/*) abort without it.

* Fri May 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.5.20260301git3bd8e038
- Rebump (skip -0.3, -0.4 that built but silently regressed and
  shipped without SlicerExecutionModelConfig.cmake — discovered when
  3D Slicer's find_package(SlicerExecutionModel) in Libs/MRML/CLI
  failed against the COPR-shipped -0.4 binary). No spec changes from
  -0.2 which was last known good.

* Wed Mar 04 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.2.20260301git3bd8e038
- Fix install-tree CMake config generation for all components
- Add GenerateCLP and top-level SEM install configs (upstream TODO)
- Uncomment MDP and TCLAP install-tree config generation
- Fix hardcoded lib/ paths for cmake configs on lib64 systems
- Install SEM CMake support scripts (SEMMacroBuildCLI, etc.)

* Wed Mar 04 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-0.1.20260301git3bd8e038
- Initial package (git snapshot)
- Uses system ITK 5.4.x from COPR
- Bundled tclap (Slicer-modified version)
