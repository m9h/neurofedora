# Disable LTO - causes linker issues with ITK on Fedora 43+
%global _lto_cflags %{nil}

%global commit 3bd8e038024b5a0684bf8284d4af0ac69cc0eb3c
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate 20260301

# On x86_64, _libdir is lib64; cmake config files use this for relative paths
%global sem_install_lib_dir %{_lib}

Name:           SlicerExecutionModel
Version:        2.0.0
Release:        0.2.%{snapdate}git%{shortcommit}%{?dist}
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
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DSlicerExecutionModel_INSTALL_BIN_DIR=%{_bindir} \
    -DSlicerExecutionModel_INSTALL_LIB_DIR=%{_libdir}/%{name} \
    -DSlicerExecutionModel_INSTALL_NO_DEVELOPMENT=OFF \
    -DSlicerExecutionModel_USE_JSONCPP=OFF \
    -DSlicerExecutionModel_USE_UTF8=OFF \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4

%cmake_build

%install
%cmake_install

%files
%license License.txt tclap/COPYING
%doc README.md NOTICE
%{_libdir}/%{name}/libModuleDescriptionParser.so

%files devel
%{_bindir}/GenerateCLP
%{_bindir}/GenerateCLPLauncher
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
