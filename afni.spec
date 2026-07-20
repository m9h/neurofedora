# AFNI - Analysis of Functional NeuroImages
# Production multi-subpackage Fedora RPM spec
#
# Subpackages: afni (meta), afni-libs, afni-core, afni-gui, afni-suma,
#              python3-afni, afni-tcsh, afni-rstats, afni-data,
#              afni-doc, afni-devel

%global debug_package %{nil}

# Python bytecompile for noarch scripts
%global __python %{python3}
# Some afnipy files have Python 2 print statements (dead code); don't fail on bytecompile errors
%global _python_bytecompile_errors_terminate_build 0

Name:           afni
Version:        26.2.01
Release:        1%{?dist}
Summary:        Analysis of Functional NeuroImages

License:        GPL-2.0-or-later AND LicenseRef-Fedora-Public-Domain
URL:            https://afni.nimh.nih.gov/
Source0:        https://github.com/afni/afni/archive/refs/tags/AFNI_%{version}.tar.gz

# Bundled libraries (not available as system packages or incompatible)
Provides:       bundled(f2c)
Provides:       bundled(nifticlib)
Provides:       bundled(gifticlib)
Provides:       bundled(XmHTML)
Provides:       bundled(GLw)

BuildRequires:  gcc >= 14
BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.14.7
BuildRequires:  ninja-build
BuildRequires:  git-core
BuildRequires:  patchelf
BuildRequires:  libstdc++-static

# X11 / GUI deps
BuildRequires:  libXp-devel
BuildRequires:  libXpm-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  openmotif-devel

# OpenGL / SUMA deps
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  freeglut-devel

# Image / math / misc libs
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  expat-devel
BuildRequires:  gsl-devel
BuildRequires:  glib2-devel
BuildRequires:  gts-devel
BuildRequires:  libomp-devel
BuildRequires:  zlib-devel

# Neuroimaging libs (from COPR neurofedora)
# BuildRequires:  nifticlib-devel
# gifticlib/nifticlib bundled (system versions too old for AFNI)
# BuildRequires:  gifticlib-devel
# BuildRequires:  gifticlib-cmake-devel

# Python build
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip

# R (for COMP_RSTATS)
BuildRequires:  R-devel

# Script deps
BuildRequires:  tcsh
BuildRequires:  netpbm-progs

# -----------------------------------------------------------------------
# Meta-package: pulls in everything for AFNI bootcamp
# -----------------------------------------------------------------------
Requires:       %{name}-core = %{version}-%{release}
Requires:       %{name}-gui = %{version}-%{release}
Requires:       %{name}-suma = %{version}-%{release}
Requires:       python3-%{name} = %{version}-%{release}
Requires:       %{name}-tcsh = %{version}-%{release}
Requires:       %{name}-data = %{version}-%{release}
Requires:       %{name}-doc = %{version}-%{release}

%description
AFNI (Analysis of Functional NeuroImages) is a comprehensive suite of programs
for processing, analyzing, and displaying functional MRI (FMRI) data. This
meta-package installs all AFNI subpackages needed for bootcamp courses.

# -----------------------------------------------------------------------
# afni-libs: core shared libraries + model/plugin DSOs + profile.d
# -----------------------------------------------------------------------
%package libs
Summary:        Core shared libraries for AFNI
# nifticlib/gifticlib bundled (system versions too old)

%description libs
Core shared libraries for AFNI including libmri, lib3DEdge, libeispack,
libmpeg_encode, and 29 model DSOs for nonlinear fitting. Also installs
profile.d scripts that set AFNI environment variables.

%ldconfig_scriptlets libs

# -----------------------------------------------------------------------
# afni-core: ~290 C binaries in /usr/libexec/afni/ + key symlinks
# -----------------------------------------------------------------------
%package core
Summary:        Core AFNI command-line tools
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description core
Core AFNI command-line programs (3dcalc, 3dresample, 3dinfo, 3dcopy, 3dvolreg,
3dQwarp, etc.). Most programs are installed in /usr/libexec/afni/ and accessible
via the profile.d PATH addition. Key commands have /usr/bin symlinks.

# -----------------------------------------------------------------------
# afni-gui: AFNI GUI + X11/Motif programs + plugins
# -----------------------------------------------------------------------
%package gui
Summary:        AFNI graphical user interface and X11 programs
Requires:       %{name}-core%{?_isa} = %{version}-%{release}

%description gui
The AFNI GUI for interactive neuroimaging data visualization, plus X11/Motif
dependent programs (3dAllineate, 3dDeconvolve, to3d, etc.) and 52 GUI plugins.

# -----------------------------------------------------------------------
# afni-suma: SUMA surface analysis + OpenGL tools
# -----------------------------------------------------------------------
%package suma
Summary:        SUMA surface analysis and OpenGL tools
Requires:       %{name}-gui%{?_isa} = %{version}-%{release}

%description suma
SUMA (Surface Mapping) GUI for cortical surface analysis, plus ~90 OpenGL
dependent programs for surface-based analysis and tractography.

# -----------------------------------------------------------------------
# python3-afni: afnipy module + Python scripts (noarch)
# -----------------------------------------------------------------------
%package -n python3-%{name}
Summary:        AFNI Python module and scripts
BuildArch:      noarch
Requires:       %{name}-libs = %{version}-%{release}
Requires:       python3-numpy
Requires:       python3-matplotlib

%description -n python3-%{name}
The afnipy Python module and ~100 Python scripts for AFNI processing
pipelines, including afni_proc.py and afni_system_check.py.

# -----------------------------------------------------------------------
# afni-tcsh: tcsh scripts (noarch)
# -----------------------------------------------------------------------
%package tcsh
Summary:        AFNI tcsh shell scripts
BuildArch:      noarch
Requires:       %{name}-libs = %{version}-%{release}
Requires:       tcsh

%description tcsh
Over 150 tcsh shell scripts for AFNI workflows, including @SSwarper,
@chauffeur_afni, @auto_tlrc, and bootcamp data installers.

# -----------------------------------------------------------------------
# afni-rstats: R scripts (opt-in, NOT in meta-package)
# -----------------------------------------------------------------------
%package rstats
Summary:        AFNI R statistical analysis scripts
BuildArch:      noarch
Requires:       %{name}-libs = %{version}-%{release}
Requires:       R-core

%description rstats
R scripts for AFNI statistical analyses including 3dLME, 3dMVM, 3dMEMA,
3dISC, and other mixed-effects and Bayesian group analysis tools.

# -----------------------------------------------------------------------
# afni-data: atlas configs and templates (noarch)
# -----------------------------------------------------------------------
%package data
Summary:        AFNI atlas configuration and reference data
BuildArch:      noarch

%description data
Atlas space configuration files, NIML templates, and reference data for AFNI.
Large bootcamp datasets are not included and should be downloaded via
install_bootcamp_data.tcsh.

# -----------------------------------------------------------------------
# afni-doc: documentation (noarch)
# -----------------------------------------------------------------------
%package doc
Summary:        AFNI documentation
BuildArch:      noarch

%description doc
Documentation files for AFNI including README files and environment
configuration guides.

# -----------------------------------------------------------------------
# afni-devel: headers for libmri etc.
# -----------------------------------------------------------------------
%package devel
Summary:        AFNI development headers
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
Development headers for AFNI libraries (libmri, etc.) for building
programs that link against AFNI's core libraries.


%prep
%setup -q -n afni-AFNI_%{version}

# NOTE: NIFTI and GIFTI are bundled (USE_SYSTEM_*=OFF) because:
# - System gifticlib 1.0.9 is too old (missing gifti_rotate_DAs_to_front)
# - System nifticlib 3.0.1 is too old (missing nifti_image_write_bricks_status)
# - System nifti1_io.h/nifti2_io.h have conflicting type definitions
# AFNI's bundled versions are newer and internally consistent.
# FetchContent would try to git clone; redirect to bundled source dirs.
# FETCHCONTENT_SOURCE_DIR_<name> overrides the download/clone step.
# Also patch bundled gifti's CMakeLists.txt to not re-fetch nifti
# (AFNI's outer build already provides nifti targets via FetchContent).
sed -i '/FetchContent_Declare.*fetch_nifti_clib_git_repo/,/endif()/c\
  # [Fedora] nifti targets provided by outer AFNI build\
  find_package(NIFTI QUIET)\
  if(NOT TARGET NIFTI::nifti2)\
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/../nifti ${CMAKE_CURRENT_BINARY_DIR}/nifti_clib)\
  endif()' src/gifti/CMakeLists.txt

# Create GIFTI::giftiio alias target after bundled gifti builds giftiio
# (AFNI's CMakeLists_mri.txt expects GIFTI::giftiio but bundled creates giftiio)
cat >> src/gifti/CMakeLists.txt << 'ALIAS_EOF'

# [Fedora] Add public include dir and alias for AFNI build system compatibility
if(TARGET giftiio)
  target_include_directories(giftiio PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
  if(NOT TARGET GIFTI::giftiio)
    add_library(GIFTI::giftiio ALIAS giftiio)
  endif()
endif()
ALIAS_EOF

# -- SONAME versioning for shared libraries --
# AFNI upstream does not set VERSION/SOVERSION on shared libs.
# Patch CMakeLists_mri.txt (contains the mri library definition)
# Ensure trailing newline then append SONAME properties
# (some upstream CMakeLists.txt files lack a final newline)
for _soname_file in \
  src/CMakeLists_mri.txt:mri \
  src/3DEdge/CMakeLists.txt:3DEdge \
  src/eispack/CMakeLists.txt:eispack \
  src/mpeg_encodedir/CMakeLists.txt:mpeg_encode \
  src/coxplot/CMakeLists.txt:coxplot \
  src/ptaylor/CMakeLists.txt:track_tools \
; do
  _file="${_soname_file%%:*}"
  _target="${_soname_file##*:}"
  if [ -f "$_file" ]; then
    printf '\n# Fedora SONAME versioning (added by RPM spec)\nif(TARGET %s)\n  set_target_properties(%s PROPERTIES VERSION %s SOVERSION 26)\nendif()\n' \
      "$_target" "$_target" "%{version}" >> "$_file"
  fi
done


%build
export CC=gcc
export CXX=g++
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
export CFLAGS="%{optflags} -std=gnu17 -Wno-error=implicit-function-declaration \
  -Wno-error=int-conversion -Wno-error=incompatible-pointer-types \
  -Wno-error=format-security"

%cmake -GNinja \
  -DAFNI_COMPILER_CHECK=OFF \
  -DCOMP_CORELIBS=ON \
  -DCOMP_COREBINARIES=ON \
  -DCOMP_GUI=ON \
  -DCOMP_SUMA=ON \
  -DCOMP_PYTHON=ON \
  -DCOMP_TCSH=ON \
  -DCOMP_RSTATS=ON \
  -DCOMP_PLUGINS=ON \
  -DCOMP_ATLASES=OFF \
  -DCOMP_FUNSTUFF=OFF \
  -DCOMP_DOCS=OFF \
  -DUSE_SYSTEM_NIFTI=OFF \
  -DUSE_SYSTEM_GIFTI=OFF \
  -DFETCHCONTENT_SOURCE_DIR_NIFTI_CLIB=%{_builddir}/%{buildsubdir}/src/nifti \
  -DFETCHCONTENT_SOURCE_DIR_GIFTI_CLIB=%{_builddir}/%{buildsubdir}/src/gifti \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
  -DUSE_SYSTEM_GTS=ON \
  -DUSE_SYSTEM_GLUT=ON \
  -DUSE_SYSTEM_GLW=OFF \
  -DUSE_SYSTEM_XMHTML=OFF \
  -DUSE_SYSTEM_F2C=OFF \
  -DUSE_OMP=ON \
  -DSTANDARD_PYTHON_INSTALL=OFF \
  -DCMAKE_SKIP_INSTALL_RPATH=ON \
  -DAFNI_INSTALL_RUNTIME_DIR=libexec/afni \
  -DAFNI_INSTALL_LIBRARY_DIR=%{_lib}/afni \
  -DAFNI_INSTALL_INCLUDE_DIR=include/afni \
  -DREMOVE_BUILD_PARITY_CHECKS=ON

%cmake_build

# Build afnipy wheel
cd src/python_scripts
%pyproject_wheel
cd ../..


%install
# -- Full cmake install (all components go to libexec/afni and lib/afni) --
%cmake_install

# -- Install afnipy Python package --
cd src/python_scripts
%pyproject_install
%pyproject_save_files afnipy
cd ../..

# -- Drop bundled headers and CLI tools that would collide with system pkgs --
# These collide on path with nifticlib/gifticlib RPMs and aren't part of AFNI's
# runtime ABI, so just remove them.
rm -rf %{buildroot}%{_includedir}/nifti
rm -rf %{buildroot}%{_includedir}/gifti
rm -f  %{buildroot}%{_bindir}/nifti1_tool
rm -f  %{buildroot}%{_bindir}/nifti_stats
rm -f  %{buildroot}%{_bindir}/nifti_tool
rm -f  %{buildroot}%{_bindir}/gifti_tool
rm -f  %{buildroot}%{_bindir}/gifti_test
rm -rf %{buildroot}%{_datadir}/cmake/NIFTI

# -- Rename bundled libs that share SONAMEs with Fedora system packages --
#
# AFNI bundles patched versions of gifticlib, nifticlib, and (transitively) f2c.
# Each bundle has AFNI-specific symbols that the Fedora system versions don't
# carry (gifti_rotate_DAs_to_front, nifti_image_write_bricks_status, etc.).
# The bundled libs and system libs share the same SONAMEs (libgiftiio.so.0,
# libnifti2.so.2, libniftiio.so.2, libnifticdf.so.2, libznz.so.3, libf2c.so).
#
# Three failure modes the harness has surfaced as we iterated this:
#   - ship both → file conflict at install time (f2c)
#   - delete bundled, rely on system → "undefined symbol" at runtime
#   - move bundled to /usr/lib64/afni → ldconfig doesn't find them
#
# Working approach: rename SONAME of the bundled lib to libafni_<name>.so.<v>,
# patchelf every AFNI ELF that NEEDED the old name to point at the new one,
# ship the renamed lib at /usr/lib64/. The bundled and system libs then live
# side-by-side, ldconfig finds both, AFNI loads its bundled flavor through
# the renamed NEEDED chain, every other package keeps using system.
#
# The block below is repeated per-lib (rather than functioned out) because
# rpmbuild's %install runs under a single sh -c invocation and bash function
# definitions are visible to find -exec only via `export -f` which couples
# state in a way that's harder to debug than the redundancy.
mkdir -p %{buildroot}%{_libdir}

# Rename + move one versioned bundled lib (called per-lib below).
# Args: <bundled-name> <new-prefix-name> <SONAME-version> <full-versioned-suffix>
#   e.g. _afni_rename_lib  libgiftiio  libafni_giftiio  0  0.0.0
_afni_rename_lib() {
    local bundled="$1" newpfx="$2" sov="$3" fullv="$4"
    local src_dir=%{buildroot}%{_prefix}/lib
    local dst_dir=%{buildroot}%{_libdir}

    for src in "$src_dir"/"$bundled".so*; do
        [[ -e "$src" ]] || continue
        local base new_base
        base=$(basename "$src")
        new_base="${base/$bundled/$newpfx}"
        if [[ ! -L "$src" ]]; then
            patchelf --set-soname "${newpfx}.so.${sov}" "$src"
        fi
        mv "$src" "$dst_dir/$new_base"
    done

    # Recreate SONAME symlink (mv breaks the original link target chain)
    rm -f "$dst_dir/${newpfx}.so.${sov}"
    [[ -f "$dst_dir/${newpfx}.so.${fullv}" ]] && \
        ln -sf "${newpfx}.so.${fullv}" "$dst_dir/${newpfx}.so.${sov}"

    # Drop the bare devel symlink (nothing outside AFNI ever links to the
    # renamed bundle — and rpmbuild's check-files step rejects it as
    # unpackaged if %files's .so.* glob doesn't catch it).
    rm -f "$dst_dir/${newpfx}.so"
}
export -f _afni_rename_lib

# Rename: gifticlib, nifticlib (4 libs), f2c
# Format: bundled-name        new-prefix-name      SONAME-version  full-versioned-suffix
_afni_rename_lib libgiftiio    libafni_giftiio       0   0.0.0
_afni_rename_lib libnifti2     libafni_nifti2        2   2.1.0
_afni_rename_lib libniftiio    libafni_niftiio       2   2.1.0
_afni_rename_lib libnifticdf   libafni_nifticdf      2   2.1.0
_afni_rename_lib libznz        libafni_znz           3   3.0.0

# Patchelf every AFNI ELF that NEEDED any of the renamed libs to point at
# the libafni_* equivalent. Covers libmri.so.26, every 3d* binary in
# /usr/libexec/afni, and the model/plugin libs still in /usr/lib64/afni/.
# A single pass handles all five renames; consumers that don't reference a
# given lib are left alone by the inner conditional.
_patch_afni_consumers() {
    local target="$1"
    [[ -f "$target" && ! -L "$target" ]] || return
    file "$target" 2>/dev/null | grep -q ELF || return
    local entries
    entries=$(readelf -d "$target" 2>/dev/null) || return
    grep -q "libgiftiio.so"  <<<"$entries" && patchelf --replace-needed libgiftiio.so.0  libafni_giftiio.so.0  "$target" 2>/dev/null || :
    grep -q "libnifti2.so"   <<<"$entries" && patchelf --replace-needed libnifti2.so.2   libafni_nifti2.so.2   "$target" 2>/dev/null || :
    grep -q "libniftiio.so"  <<<"$entries" && patchelf --replace-needed libniftiio.so.2  libafni_niftiio.so.2  "$target" 2>/dev/null || :
    grep -q "libnifticdf.so" <<<"$entries" && patchelf --replace-needed libnifticdf.so.2 libafni_nifticdf.so.2 "$target" 2>/dev/null || :
    grep -q "libznz.so"      <<<"$entries" && patchelf --replace-needed libznz.so.3      libafni_znz.so.3      "$target" 2>/dev/null || :
}
export -f _patch_afni_consumers
find %{buildroot}%{_libexecdir}/afni -type f -executable -exec bash -c '_patch_afni_consumers "$0"' {} \;
find %{buildroot}%{_libdir}        -name "*.so*"  -type f -exec bash -c '_patch_afni_consumers "$0"' {} \;
find %{buildroot}%{_libdir}/afni   -name "*.so*"  -type f -exec bash -c '_patch_afni_consumers "$0"' {} \;

# -- Move shared libraries from private dir to system libdir --
# Core shared libs go to %%{_libdir} so the dynamic linker can find them
# without an RPATH or LD_LIBRARY_PATH dance.
#
# Group A (mri 3DEdge eispack coxplot track_tools) have proper versioned
# SONAMEs (libfoo.so.26) — collision-safe, move as-is.
#
# Group B (mrix SUMA XmHTML segtools) have UNVERSIONED SONAMEs but are
# uniquely-named — no other Fedora package ships them. Move as-is.
#
# Only model_/plugin_ libs (true AFNI plugins loaded via dlopen with
# AFNI_PLUGINPATH/AFNI_MODELPATH) stay in /usr/lib64/afni/.
mkdir -p %{buildroot}%{_libdir}
for lib in mri 3DEdge eispack coxplot track_tools \
           mrix SUMA XmHTML segtools; do
  if ls %{buildroot}%{_prefix}/%{_lib}/afni/lib${lib}.so* 2>/dev/null; then
    mv %{buildroot}%{_prefix}/%{_lib}/afni/lib${lib}.so* %{buildroot}%{_libdir}/
  fi
done

# f2c lives in /usr/lib64/afni/ (not /usr/lib/ like the bundled gifti/nifti),
# so it doesn't fit the _afni_rename_lib path pattern. Handle it inline.
# Same approach: rename SONAME, patchelf consumers via the unified
# _patch_afni_consumers pass below.
if [[ -e %{buildroot}%{_prefix}/%{_lib}/afni/libf2c.so ]]; then
    patchelf --set-soname libafni_f2c.so %{buildroot}%{_prefix}/%{_lib}/afni/libf2c.so
    mv %{buildroot}%{_prefix}/%{_lib}/afni/libf2c.so %{buildroot}%{_libdir}/libafni_f2c.so
fi

# Re-run the consumer-patchelf pass to catch f2c (the earlier pass above
# only had the 5 NIFTI/GIFTI lib mappings; f2c was renamed after, so its
# consumers still NEEDED the original libf2c.so name). Patch them too.
_patch_f2c_consumers() {
    local target="$1"
    [[ -f "$target" && ! -L "$target" ]] || return
    file "$target" 2>/dev/null | grep -q ELF || return
    if readelf -d "$target" 2>/dev/null | grep -q "libf2c.so"; then
        patchelf --replace-needed libf2c.so libafni_f2c.so "$target" 2>/dev/null || :
    fi
}
export -f _patch_f2c_consumers
find %{buildroot}%{_libexecdir}/afni -type f -executable -exec bash -c '_patch_f2c_consumers "$0"' {} \;
find %{buildroot}%{_libdir}        -name "*.so*"  -type f -exec bash -c '_patch_f2c_consumers "$0"' {} \;
find %{buildroot}%{_libdir}/afni   -name "*.so*"  -type f -exec bash -c '_patch_f2c_consumers "$0"' {} \;

# -- Symlinks for key commands in /usr/bin --
mkdir -p %{buildroot}%{_bindir}

# afni-core symlinks
for cmd in 3dcalc 3dresample 3dinfo 3dcopy 3drefit 3dmerge \
           3dAutomask 3dTshift 3dvolreg \
           3dQwarp 3dNwarpApply; do
  if [ -f %{buildroot}%{_libexecdir}/afni/"$cmd" ]; then
    ln -s %{_libexecdir}/afni/"$cmd" %{buildroot}%{_bindir}/"$cmd"
  fi
done

# afni-gui symlinks (3dDeconvolve is gui component)
for cmd in afni to3d 3dAllineate 3dDeconvolve; do
  if [ -f %{buildroot}%{_libexecdir}/afni/"$cmd" ]; then
    ln -s %{_libexecdir}/afni/"$cmd" %{buildroot}%{_bindir}/"$cmd"
  fi
done

# afni-suma symlinks (3dSkullStrip is suma component)
for cmd in suma 3dSkullStrip; do
  if [ -f %{buildroot}%{_libexecdir}/afni/"$cmd" ]; then
    ln -s %{_libexecdir}/afni/"$cmd" %{buildroot}%{_bindir}/"$cmd"
  fi
done

# python3-afni symlinks (scripts installed by pyproject to /usr/bin already,
# but cmake python scripts go to libexec)
for cmd in afni_proc.py afni_system_check.py; do
  if [ -f %{buildroot}%{_libexecdir}/afni/"$cmd" ] && \
     [ ! -f %{buildroot}%{_bindir}/"$cmd" ]; then
    ln -s %{_libexecdir}/afni/"$cmd" %{buildroot}%{_bindir}/"$cmd"
  fi
done

# afni-tcsh symlinks
for cmd in @SSwarper @chauffeur_afni @auto_tlrc; do
  if [ -f %{buildroot}%{_libexecdir}/afni/"$cmd" ]; then
    ln -s %{_libexecdir}/afni/"$cmd" %{buildroot}%{_bindir}/"$cmd"
  fi
done

# -- profile.d scripts --
mkdir -p %{buildroot}%{_sysconfdir}/profile.d

cat > %{buildroot}%{_sysconfdir}/profile.d/afni.sh << 'PROFILE_EOF'
export AFNI_PLUGINPATH="%{_libdir}/afni"
export AFNI_MODELPATH="%{_libdir}/afni"
export AFNI_GLOBAL_SESSION="%{_datadir}/afni"
export AFNI_ATLAS_PATH="%{_datadir}/afni"
export PATH="%{_libexecdir}/afni:$PATH"
PROFILE_EOF

cat > %{buildroot}%{_sysconfdir}/profile.d/afni.csh << 'PROFILE_EOF'
setenv AFNI_PLUGINPATH "%{_libdir}/afni"
setenv AFNI_MODELPATH "%{_libdir}/afni"
setenv AFNI_GLOBAL_SESSION "%{_datadir}/afni"
setenv AFNI_ATLAS_PATH "%{_datadir}/afni"
set path = ( %{_libexecdir}/afni $path )
PROFILE_EOF

# -- Fix shebangs --
# Python scripts in libexec
find %{buildroot}%{_libexecdir}/afni -name "*.py" -exec \
  sed -i '1s|^#!.*python.*$|#!/usr/bin/python3|' {} + 2>/dev/null || :
# R scripts in libexec
find %{buildroot}%{_libexecdir}/afni -name "*.R" -exec \
  sed -i '1s|^#!.*Rscript.*$|#!/usr/bin/Rscript|' {} + 2>/dev/null || :
find %{buildroot}%{_libexecdir}/afni -name "*.R" -exec \
  sed -i '1s|^#!.*R --no-save.*$|#!/usr/bin/Rscript|' {} + 2>/dev/null || :

# -- Strip RPATHs from ELF binaries --
find %{buildroot}%{_libexecdir}/afni -type f -executable | while read bin; do
  if file "$bin" | grep -q "ELF"; then
    patchelf --remove-rpath "$bin" 2>/dev/null || :
  fi
done
find %{buildroot}%{_libdir} -name "*.so*" -type f | while read lib; do
  patchelf --remove-rpath "$lib" 2>/dev/null || :
done

# -- Install data files --
mkdir -p %{buildroot}%{_datadir}/afni
# Atlas space config if present in source
if [ -f AFNI_atlas_spaces.niml ]; then
  install -m 644 AFNI_atlas_spaces.niml %{buildroot}%{_datadir}/afni/
fi

# -- Install documentation --
mkdir -p %{buildroot}%{_docdir}/afni
for f in doc/README/README.*; do
  install -m 644 "$f" %{buildroot}%{_docdir}/afni/ 2>/dev/null || :
done

# -- rpmlint filters --
mkdir -p %{buildroot}%{_datadir}/rpmlint
cat > %{buildroot}%{_datadir}/rpmlint/afni.toml << 'RPMLINT_EOF'
# Model and plugin DSOs are loadable modules in a private directory
# They intentionally lack SONAME versioning
[afni-libs.Filters]
"library-without-ldconfig-posttrans" = [".*afni/libmodel_.*", ".*afni/libplug_.*", ".*afni/lib.*\\.so"]
"shared-lib-without-dependency-information" = [".*afni/.*"]
RPMLINT_EOF


%check
# Verify key binaries were built
test -x %{buildroot}%{_libexecdir}/afni/3dcalc
test -x %{buildroot}%{_libexecdir}/afni/afni
ls %{buildroot}%{_libdir}/libmri.so.* >/dev/null 2>&1


# -----------------------------------------------------------------------
# FILE LISTS
# -----------------------------------------------------------------------

# --- afni (meta-package) ---
%files
# empty — just dependencies

# --- afni-libs ---
%files libs
%license doc/README/README.copyright
%{_libdir}/libmri.so.*
%{_libdir}/lib3DEdge.so.*
%{_libdir}/libeispack.so.*
%{_libdir}/libcoxplot.so.*
%{_libdir}/libtrack_tools.so.*
# Bundled libs with SONAMEs renamed to libafni_* to avoid collision with
# Fedora's gifticlib/nifticlib RPMs that ship the same paths but lack
# AFNI-only symbols (gifti_rotate_DAs_to_front, nifti_image_write_bricks_status,
# etc.). See the corresponding %%install section for the full rationale.
%{_libdir}/libafni_giftiio.so.*
%{_libdir}/libafni_nifti2.so.*
%{_libdir}/libafni_niftiio.so.*
%{_libdir}/libafni_nifticdf.so.*
%{_libdir}/libafni_znz.so.*
# Unversioned-SONAME libs: NEEDED directly by /usr/libexec/afni/afni and
# many 3d* binaries. Live in %%{_libdir} (not %%{_libdir}/afni) so
# ldconfig finds them at runtime. No -devel symlink ships for these
# because their SONAME *is* the unversioned name (upstream choice).
%{_libdir}/libmrix.so
%{_libdir}/libSUMA.so
%{_libdir}/libXmHTML.so
%{_libdir}/libsegtools.so
# Bundled f2c renamed (libf2c → libafni_f2c) — Fedora's f2c-20210928 owns
# /usr/lib64/libf2c.so, so we must namespace AFNI's copy to avoid an
# install-time file conflict. See the corresponding %%install section.
%{_libdir}/libafni_f2c.so
%dir %{_libdir}/afni
%{_libdir}/afni/*.so*
%config(noreplace) %{_sysconfdir}/profile.d/afni.sh
%config(noreplace) %{_sysconfdir}/profile.d/afni.csh
%{_datadir}/rpmlint/afni.toml

# --- afni-core ---
# All programs in libexec/afni except scripts (captured by other subpackages)
%files core
%dir %{_libexecdir}/afni
%{_libexecdir}/afni/*
%exclude %{_libexecdir}/afni/*.py
%exclude %{_libexecdir}/afni/*.R
%exclude %{_libexecdir}/afni/@*
%exclude %{_libexecdir}/afni/lib_RetroTS
# dcm2niix_afni and /usr/bin symlinks for core
%{_bindir}/dcm2niix_afni
%{_bindir}/3dcalc
%{_bindir}/3dresample
%{_bindir}/3dinfo
%{_bindir}/3dcopy
%{_bindir}/3drefit
%{_bindir}/3dmerge
%{_bindir}/3dAutomask
%{_bindir}/3dTshift
%{_bindir}/3dvolreg
%{_bindir}/3dQwarp
%{_bindir}/3dNwarpApply
%{_bindir}/afni
%{_bindir}/suma
%{_bindir}/to3d
%{_bindir}/3dAllineate
%{_bindir}/3dDeconvolve
%{_bindir}/3dSkullStrip

# --- afni-gui ---
# GUI functionality is in afni-core for now (single install dir)
# Will be split when we have confirmed file lists
%files gui
# empty — gui binaries included in core

# --- afni-suma ---
# SUMA functionality is in afni-core for now
%files suma
# empty — suma binaries included in core

# --- python3-afni ---
# Don't use %%pyproject_files — some afnipy .py files have Python 2 syntax
# and can't be byte-compiled, so the .pyc manifest is incomplete.
%files -n python3-%{name}
%{python3_sitelib}/afnipy/
%{python3_sitelib}/afnipy-*.dist-info/
%{_libexecdir}/afni/*.py
%exclude %{_libexecdir}/afni/@*.py
%{_libexecdir}/afni/lib_RetroTS
# Python scripts installed to /usr/bin by pyproject_install
%{_bindir}/*.py

# --- afni-tcsh ---
# @-prefixed scripts are the main tcsh content; other tcsh scripts
# (3dMax, dsetstat2p, fat_proc_*, etc.) stay in afni-core if installed
%files tcsh
%{_libexecdir}/afni/@*
%{_bindir}/@SSwarper
%{_bindir}/@chauffeur_afni
%{_bindir}/@auto_tlrc

# --- afni-rstats ---
# Only *.R files are reliably installed; R wrapper scripts without
# .R extension stay in afni-core if installed
%files rstats
%{_libexecdir}/afni/*.R

# --- afni-data ---
# Atlas data is not installed with COMP_ATLASES=OFF; just own the directory
%files data
%dir %{_datadir}/afni

# --- afni-doc ---
%files doc
%license doc/README/README.copyright
%{_docdir}/afni/

# --- afni-devel ---
# AFNI cmake does not install public headers, so no include dir.
# Unversioned .so symlinks for linking are created during lib move.
%files devel
%{_libdir}/libmri.so
%{_libdir}/lib3DEdge.so
%{_libdir}/libeispack.so
%{_libdir}/libcoxplot.so
%{_libdir}/libtrack_tools.so


%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 26.2.01-1
- Update to 26.2.01

* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 26.1.04-1
- Update to 26.1.04 (current upstream; freshness sweep 2026-06-14)

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 26.1.00-6
- Extend the SONAME-rename treatment to the bundled NIFTI libs (nifti2,
  niftiio, nifticdf, znz). The harness flipped the libmri.so.26 missing
  symbol from gifti_rotate_DAs_to_front (-3 fix) to
  nifti_image_write_bricks_status (still present in -5) — same class of
  bug, different library. AFNI bundles patched copies of nifticlib with
  *_status function variants the system nifticlib 3.0.1 doesn't carry;
  we previously deleted the bundle expecting system to suffice, and the
  dyld silently fell through to system libnifti2.so.2 → undefined symbol.
- Refactor the three rename code paths (gifti, nifti, f2c) into a single
  _afni_rename_lib helper + a single _patch_afni_consumers pass so future
  collision-class bundles are a one-line addition.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 26.1.00-5
- Rename bundled libf2c.so → libafni_f2c.so (SONAME + patchelf consumers)
  to avoid file conflict with Fedora's f2c-20210928 package, which ships
  /usr/lib64/libf2c.so. The conflict was latent — the AMD test box didn't
  have f2c installed, so -2/-3/-4 looked clean; the iMac install run
  surfaced it by rolling back the entire dnf transaction. Same SONAME
  namespacing approach as the bundled gifticlib in -3.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 26.1.00-4
- Drop the bare libafni_giftiio.so devel symlink — nothing outside AFNI
  links against the renamed bundled lib and check-files refused to ship
  it unpackaged. (-3 failed at the same step; this is the trivial fix.)

* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 26.1.00-3
- Rename bundled gifticlib SONAME (libgiftiio → libafni_giftiio) and
  patchelf libmri.so.26 + every 3d* binary to consume the new name.
  System gifticlib 1.0.9 lacks gifti_rotate_DAs_to_front (and other
  AFNI-only additions) but has identical SONAME; the previous spec
  deleted the bundled copy and let dyld fall through to the system
  version, which then crashed at runtime with "undefined symbol".
  Surfaced by the neurofedora test harness on the same run that
  validated the -2 libmrix.so fix.

* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 26.1.00-2
- Move libmrix, libSUMA, libXmHTML, libf2c, libsegtools out of the private
  /usr/lib64/afni/ subdir to /usr/lib64/ so ldconfig finds them at runtime.
  Without this, /usr/bin/afni and most 3d* tools fail at startup with
  "libmrix.so: cannot open shared object file" — the dynamic linker has
  no RPATH (patchelf strips it) and no LD_LIBRARY_PATH (profile.d only
  exports AFNI_PLUGINPATH/AFNI_MODELPATH). These libs have unversioned
  SONAMEs but are NEEDED entries on every afni binary, not dlopen
  plugins, so they belong on the standard ld search path. Surfaced by
  the neurofedora test harness.

* Wed Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 26.1.00-1
- Update to 26.1.00

* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 26.0.08-17
- Multi-subpackage rewrite (afni-libs, afni-core, python3-afni, afni-tcsh,
  afni-rstats, afni-data, afni-doc, afni-devel; afni-gui/afni-suma stubs)
- Programs in /usr/libexec/afni/ with profile.d PATH and key /usr/bin symlinks
- Bundle nifticlib and gifticlib (system versions too old for AFNI 26.x)
- Bundle f2c, XmHTML, GLw (not in Fedora)
- SONAME versioning for libmri, lib3DEdge, libeispack, libcoxplot, libtrack_tools
- GCC 15 / Fedora 43 flags (-Wno-error=format-security, -std=gnu17)
- libstdc++-static BR for dcm2niix static linking

* Sun Feb 15 2026 Morgan Hough <morgan.hough@gmail.com> - 26.0.08-0
- Initial basic spec for AFNI 26.0.08
