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
Version:        26.0.08
Release:        12%{?dist}
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

# -- Move shared libraries from private dir to system libdir --
# Core shared libs with SONAMEs go to %%{_libdir} for ldconfig
mkdir -p %{buildroot}%{_libdir}
for lib in mri 3DEdge eispack coxplot track_tools; do
  if ls %{buildroot}%{_prefix}/%{_lib}/afni/lib${lib}.so* 2>/dev/null; then
    mv %{buildroot}%{_prefix}/%{_lib}/afni/lib${lib}.so* %{buildroot}%{_libdir}/
  fi
done

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
"library-without-ldconfig-posttrans" = [".*afni/model_.*", ".*afni/plug_.*"]
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
# Core shared libs in system libdir
%{_libdir}/libmri.so.*
%{_libdir}/lib3DEdge.so.*
%{_libdir}/libeispack.so.*
# mpeg_encode may be built as object library (not shared)
#%%{_libdir}/libmpeg_encode.so.*
%{_libdir}/libcoxplot.so.*
%{_libdir}/libtrack_tools.so.*
# Private dir for model/plugin DSOs
%dir %{_libdir}/afni
# Model DSOs (if built as shared libs)
%{_libdir}/afni/libmodel_*.so
# profile.d
%config(noreplace) %{_sysconfdir}/profile.d/afni.sh
%config(noreplace) %{_sysconfdir}/profile.d/afni.csh
# rpmlint filter
%{_datadir}/rpmlint/afni.toml

# --- afni-core ---
%files core
%dir %{_libexecdir}/afni
# Core binaries (catch-all for corebinaries component targets)
# These are ELF executables in /usr/libexec/afni/ from COREBINARIES component
%{_libexecdir}/afni/1dApar2mat
%{_libexecdir}/afni/1dAstrip
%{_libexecdir}/afni/1dBandpass
%{_libexecdir}/afni/1dBport
%{_libexecdir}/afni/1dCorrelate
%{_libexecdir}/afni/1dFlagMotion
%{_libexecdir}/afni/1dMarry
%{_libexecdir}/afni/1dNLfit
%{_libexecdir}/afni/1dSEM
%{_libexecdir}/afni/1dTsort
%{_libexecdir}/afni/1dUpsample
%{_libexecdir}/afni/1dcat
%{_libexecdir}/afni/1ddot
%{_libexecdir}/afni/1deval
%{_libexecdir}/afni/1dfft
%{_libexecdir}/afni/1dgenARMA11
%{_libexecdir}/afni/1dmatcalc
%{_libexecdir}/afni/1dnorm
%{_libexecdir}/afni/1dsound
%{_libexecdir}/afni/1dsum
%{_libexecdir}/afni/1dsvd
%{_libexecdir}/afni/1dtranspose
%{_libexecdir}/afni/24swap
%{_libexecdir}/afni/2dImReg
%{_libexecdir}/afni/2dcat
%{_libexecdir}/afni/2perm
%{_libexecdir}/afni/2swap
%{_libexecdir}/afni/3dABoverlap
%{_libexecdir}/afni/3dAFNIto3D
%{_libexecdir}/afni/3dAFNItoANALYZE
%{_libexecdir}/afni/3dAFNItoNIFTI
%{_libexecdir}/afni/3dAFNItoNIML
%{_libexecdir}/afni/3dAFNItoRaw
%{_libexecdir}/afni/3dANALYZEtoAFNI
%{_libexecdir}/afni/3dANOVA
%{_libexecdir}/afni/3dANOVA2
%{_libexecdir}/afni/3dANOVA3
%{_libexecdir}/afni/3dAcost
%{_libexecdir}/afni/3dAnatNudge
%{_libexecdir}/afni/3dAnhist
%{_libexecdir}/afni/3dAttribute
%{_libexecdir}/afni/3dAutoTcorrelate
%{_libexecdir}/afni/3dAutobox
%{_libexecdir}/afni/3dAutomask
%{_libexecdir}/afni/3dBandpass
%{_libexecdir}/afni/3dBlurInMask
%{_libexecdir}/afni/3dBlurToFWHM
%{_libexecdir}/afni/3dBrainSync
%{_libexecdir}/afni/3dBrickStat
%{_libexecdir}/afni/3dCM
%{_libexecdir}/afni/3dClipLevel
%{_libexecdir}/afni/3dClustCount
%{_libexecdir}/afni/3dClustSim
%{_libexecdir}/afni/3dConformist
%{_libexecdir}/afni/3dConvolve
%{_libexecdir}/afni/3dCountSpikes
%{_libexecdir}/afni/3dDFT
%{_libexecdir}/afni/3dDTeig
%{_libexecdir}/afni/3dDTtoDWI
%{_libexecdir}/afni/3dDWItoDT
%{_libexecdir}/afni/3dDegreeCentrality
%{_libexecdir}/afni/3dDespike
%{_libexecdir}/afni/3dDetrend
%{_libexecdir}/afni/3dECM
%{_libexecdir}/afni/3dEmpty
%{_libexecdir}/afni/3dEntropy
%{_libexecdir}/afni/3dDepthMap
%{_libexecdir}/afni/3dErrtsCormat
%{_libexecdir}/afni/3dExtractGroupInCorr
%{_libexecdir}/afni/3dExtrema
%{_libexecdir}/afni/3dFDR
%{_libexecdir}/afni/3dFFT
%{_libexecdir}/afni/3dFWHM
%{_libexecdir}/afni/3dFWHMx
%{_libexecdir}/afni/3dFourier
%{_libexecdir}/afni/3dFriedman
%{_libexecdir}/afni/3dGetrow
%{_libexecdir}/afni/3dGrayplot
%{_libexecdir}/afni/3dGroupInCorr
%{_libexecdir}/afni/3dIntracranial
%{_libexecdir}/afni/3dInvFMRI
%{_libexecdir}/afni/3dKruskalWallis
%{_libexecdir}/afni/3dLFCD
%{_libexecdir}/afni/3dLRflip
%{_libexecdir}/afni/3dLSS
%{_libexecdir}/afni/3dLocalACF
%{_libexecdir}/afni/3dLocalBistat
%{_libexecdir}/afni/3dLocalHistog
%{_libexecdir}/afni/3dLocalPV
%{_libexecdir}/afni/3dLocalSVD
%{_libexecdir}/afni/3dLocalstat
%{_libexecdir}/afni/3dMSE
%{_libexecdir}/afni/3dMannWhitney
%{_libexecdir}/afni/3dMaskToASCII
%{_libexecdir}/afni/3dMean
%{_libexecdir}/afni/3dMedianFilter
%{_libexecdir}/afni/3dMultiThresh
%{_libexecdir}/afni/3dNormalityTest
%{_libexecdir}/afni/3dNotes
%{_libexecdir}/afni/3dNwarpAdjust
%{_libexecdir}/afni/3dNwarpApply
%{_libexecdir}/afni/3dNwarpCalc
%{_libexecdir}/afni/3dNwarpCat
%{_libexecdir}/afni/3dNwarpFuncs
%{_libexecdir}/afni/3dNwarpXYZ
%{_libexecdir}/afni/3dOverlap
%{_libexecdir}/afni/3dPVmap
%{_libexecdir}/afni/3dPeriodogram
%{_libexecdir}/afni/3dPolyfit
%{_libexecdir}/afni/3dPval
%{_libexecdir}/afni/3dQwarp
%{_libexecdir}/afni/3dREMLfit
%{_libexecdir}/afni/3dROIstats
%{_libexecdir}/afni/3dRank
%{_libexecdir}/afni/3dRankizer
%{_libexecdir}/afni/3dRegAna
%{_libexecdir}/afni/3dRetinoPhase
%{_libexecdir}/afni/3dRowFillin
%{_libexecdir}/afni/3dSetupGroupInCorr
%{_libexecdir}/afni/3dSharpen
%{_libexecdir}/afni/3dSpatNorm
%{_libexecdir}/afni/3dStatClust
%{_libexecdir}/afni/3dSynthesize
%{_libexecdir}/afni/3dTRfix
%{_libexecdir}/afni/3dTSgen
%{_libexecdir}/afni/3dTagalign
%{_libexecdir}/afni/3dTcat
%{_libexecdir}/afni/3dTcorr1D
%{_libexecdir}/afni/3dTcorrMap
%{_libexecdir}/afni/3dTcorrelate
%{_libexecdir}/afni/3dTfilter
%{_libexecdir}/afni/3dTfitter
%{_libexecdir}/afni/3dThreetoRGB
%{_libexecdir}/afni/3dTnorm
%{_libexecdir}/afni/3dToutcount
%{_libexecdir}/afni/3dToyProg
%{_libexecdir}/afni/3dTproject
%{_libexecdir}/afni/3dTqual
%{_libexecdir}/afni/3dTshift
%{_libexecdir}/afni/3dTsmooth
%{_libexecdir}/afni/3dTsort
%{_libexecdir}/afni/3dTsplit4D
%{_libexecdir}/afni/3dTstat
%{_libexecdir}/afni/3dTto1D
%{_libexecdir}/afni/3dTwotoComplex
%{_libexecdir}/afni/3dUndump
%{_libexecdir}/afni/3dUnifize
%{_libexecdir}/afni/3dUniformize
%{_libexecdir}/afni/3dUpsample
%{_libexecdir}/afni/3dWarp
%{_libexecdir}/afni/3dWarpDrive
%{_libexecdir}/afni/3dWavelets
%{_libexecdir}/afni/3dWilcoxon
%{_libexecdir}/afni/3dWinsor
%{_libexecdir}/afni/3dXClustSim
%{_libexecdir}/afni/3dXYZcat
%{_libexecdir}/afni/3dZcat
%{_libexecdir}/afni/3dZcutup
%{_libexecdir}/afni/3dZeropad
%{_libexecdir}/afni/3dZregrid
%{_libexecdir}/afni/3danisosmooth
%{_libexecdir}/afni/3daxialize
%{_libexecdir}/afni/3dbuc2fim
%{_libexecdir}/afni/3dbucket
%{_libexecdir}/afni/3dcalc
%{_libexecdir}/afni/3dclust
%{_libexecdir}/afni/3dcopy
%{_libexecdir}/afni/3ddelay
%{_libexecdir}/afni/3ddot
%{_libexecdir}/afni/3ddup
%{_libexecdir}/afni/3dedgedog
%{_libexecdir}/afni/3dedge3
%{_libexecdir}/afni/3dfim+
%{_libexecdir}/afni/3dfim
%{_libexecdir}/afni/3dfractionize
%{_libexecdir}/afni/3dhistog
%{_libexecdir}/afni/3dinfo
%{_libexecdir}/afni/3dmaskSVD
%{_libexecdir}/afni/3dmask_tool
%{_libexecdir}/afni/3dmaskave
%{_libexecdir}/afni/3dmaskdump
%{_libexecdir}/afni/3dmatcalc
%{_libexecdir}/afni/3dmatmult
%{_libexecdir}/afni/3dmaxima
%{_libexecdir}/afni/3dmerge
%{_libexecdir}/afni/3dnewid
%{_libexecdir}/afni/3dnoise
%{_libexecdir}/afni/3dnvals
%{_libexecdir}/afni/3dpc
%{_libexecdir}/afni/3dproject
%{_libexecdir}/afni/3drefit
%{_libexecdir}/afni/3drename
%{_libexecdir}/afni/3dresample
%{_libexecdir}/afni/3dretroicor
%{_libexecdir}/afni/3drotate
%{_libexecdir}/afni/3dsvm_linpredict
%{_libexecdir}/afni/3dtoXdataset
%{_libexecdir}/afni/3dttest++
%{_libexecdir}/afni/3dttest
%{_libexecdir}/afni/3dvolreg
%{_libexecdir}/afni/4swap
%{_libexecdir}/afni/AlphaSim
%{_libexecdir}/afni/DTIStudioFibertoSegments
%{_libexecdir}/afni/Dimon
%{_libexecdir}/afni/Dimon1
%{_libexecdir}/afni/FIRdesign
%{_libexecdir}/afni/GLTsymtest
%{_libexecdir}/afni/Ifile
%{_libexecdir}/afni/RSFgen
%{_libexecdir}/afni/Vecwarp
%{_libexecdir}/afni/abut
%{_libexecdir}/afni/adwarp
%{_libexecdir}/afni/afni_check_omp
%{_libexecdir}/afni/afni_history
%{_libexecdir}/afni/afni_vcheck
%{_libexecdir}/afni/apsearch
%{_libexecdir}/afni/bitvec
%{_libexecdir}/afni/byteorder
%{_libexecdir}/afni/cat_matvec
%{_libexecdir}/afni/ccalc
%{_libexecdir}/afni/cdf
%{_libexecdir}/afni/column_cat
%{_libexecdir}/afni/count
%{_libexecdir}/afni/dicom_hdr
%{_libexecdir}/afni/dicom_hinfo
%{_libexecdir}/afni/dicom_to_raw
%{_libexecdir}/afni/ent16
%{_libexecdir}/afni/epsim
%{_libexecdir}/afni/exx
%{_libexecdir}/afni/fdrval
%{_libexecdir}/afni/fftest
%{_libexecdir}/afni/file_tool
%{_libexecdir}/afni/fim2
%{_libexecdir}/afni/float_scan
%{_libexecdir}/afni/from3d
%{_libexecdir}/afni/ftosh
%{_libexecdir}/afni/ge_header
%{_libexecdir}/afni/get_afni_model_PRF
%{_libexecdir}/afni/get_afni_model_PRF_6
%{_libexecdir}/afni/get_afni_model_PRF_6_BAD
%{_libexecdir}/afni/gwarp
%{_libexecdir}/afni/help_format
%{_libexecdir}/afni/ibinom
%{_libexecdir}/afni/im2niml
%{_libexecdir}/afni/images_equal
%{_libexecdir}/afni/imand
%{_libexecdir}/afni/imaver
%{_libexecdir}/afni/imcalc
%{_libexecdir}/afni/imcutup
%{_libexecdir}/afni/imdump
%{_libexecdir}/afni/immask
%{_libexecdir}/afni/imrotate
%{_libexecdir}/afni/imstack
%{_libexecdir}/afni/imstat
%{_libexecdir}/afni/imupsam
%{_libexecdir}/afni/mayo_analyze
%{_libexecdir}/afni/mritopgm
%{_libexecdir}/afni/mycat
%{_libexecdir}/afni/myget
%{_libexecdir}/afni/nicat
%{_libexecdir}/afni/niccc
%{_libexecdir}/afni/nidset
%{_libexecdir}/afni/nimel
%{_libexecdir}/afni/niml_feedme
%{_libexecdir}/afni/nimltest
%{_libexecdir}/afni/nsize
%{_libexecdir}/afni/plugout_drive
%{_libexecdir}/afni/plugout_ijk
%{_libexecdir}/afni/plugout_tt
%{_libexecdir}/afni/plugout_tta
%{_libexecdir}/afni/quotize
%{_libexecdir}/afni/rmz
%{_libexecdir}/afni/rotcom
%{_libexecdir}/afni/rtfeedme
%{_libexecdir}/afni/serial_helper
%{_libexecdir}/afni/sfim
%{_libexecdir}/afni/siemens_vision
%{_libexecdir}/afni/sqwave
%{_libexecdir}/afni/stimband
%{_libexecdir}/afni/strblast
%{_libexecdir}/afni/test_powell
%{_libexecdir}/afni/testcox
%{_libexecdir}/afni/tfim
%{_libexecdir}/afni/tokens
%{_libexecdir}/afni/uncomment
%{_libexecdir}/afni/uniq_images
%{_libexecdir}/afni/unu
%{_libexecdir}/afni/waver
%{_libexecdir}/afni/whereami
%{_libexecdir}/afni/whirlgif
# /usr/bin symlinks
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

# --- afni-gui ---
%files gui
# GUI-component ELF binaries
%{_libexecdir}/afni/afni
%{_libexecdir}/afni/afni_open
%{_libexecdir}/afni/aiv
%{_libexecdir}/afni/imreg
# mrix is not a separate binary in cmake build
#%%{_libexecdir}/afni/mrix
%{_libexecdir}/afni/to3d
%{_libexecdir}/afni/FD2
%{_libexecdir}/afni/Xphace
%{_libexecdir}/afni/1dgrayplot
%{_libexecdir}/afni/1dplot
%{_libexecdir}/afni/3dAllineate
%{_libexecdir}/afni/3dDeconvolve
%{_libexecdir}/afni/3dDeconvolve_f
%{_libexecdir}/afni/3dExchange
%{_libexecdir}/afni/3dNLfim
%{_libexecdir}/afni/3dsvm
# GUI plugin DSOs (cmake installs with lib prefix)
%{_libdir}/afni/libplug_*.so
# /usr/bin symlinks
%{_bindir}/afni
%{_bindir}/to3d
%{_bindir}/3dAllineate
%{_bindir}/3dDeconvolve

# --- afni-suma ---
%files suma
# SUMA main programs
%{_libexecdir}/afni/SUMA
%{_libexecdir}/afni/suma
%{_libexecdir}/afni/DriveSuma
%{_libexecdir}/afni/HalloSuma
%{_libexecdir}/afni/InstaTract
# SUMA utilities
%{_libexecdir}/afni/AnalyzeTrace
%{_libexecdir}/afni/BrainSkin
%{_libexecdir}/afni/CompareSurfaces
%{_libexecdir}/afni/ConvertDset
%{_libexecdir}/afni/ConvertSurface
%{_libexecdir}/afni/ConvexHull
%{_libexecdir}/afni/CreateIcosahedron
%{_libexecdir}/afni/FSread_annot
%{_libexecdir}/afni/IsoSurface
%{_libexecdir}/afni/MakeColorMap
%{_libexecdir}/afni/MapIcosahedron
%{_libexecdir}/afni/NikoMap
%{_libexecdir}/afni/ParseName
%{_libexecdir}/afni/ProgramTemplate
%{_libexecdir}/afni/ROI2dataset
%{_libexecdir}/afni/ROIgrow
%{_libexecdir}/afni/RestSym
%{_libexecdir}/afni/SUMA_Read_SpecFile
%{_libexecdir}/afni/SUMA_glxdino
%{_libexecdir}/afni/SUMA_paperplane
%{_libexecdir}/afni/SUMA_pixmap2eps
%{_libexecdir}/afni/SampBias
%{_libexecdir}/afni/ScaleToMap
%{_libexecdir}/afni/SpharmDeco
%{_libexecdir}/afni/SpharmReco
%{_libexecdir}/afni/Surf2VolCoord
%{_libexecdir}/afni/SurfClust
%{_libexecdir}/afni/SurfDist
%{_libexecdir}/afni/SurfDsetInfo
%{_libexecdir}/afni/SurfExtrema
%{_libexecdir}/afni/SurfFWHM
%{_libexecdir}/afni/SurfInfo
%{_libexecdir}/afni/SurfMeasures
%{_libexecdir}/afni/SurfMesh
%{_libexecdir}/afni/SurfPatch
%{_libexecdir}/afni/SurfQual
%{_libexecdir}/afni/SurfRetinoMap
%{_libexecdir}/afni/SurfSmooth
%{_libexecdir}/afni/SurfToSurf
%{_libexecdir}/afni/SurfaceMetrics
%{_libexecdir}/afni/inflate_compare
%{_libexecdir}/afni/inspec
%{_libexecdir}/afni/niprobe
%{_libexecdir}/afni/path_optimize
%{_libexecdir}/afni/prompt_popup
%{_libexecdir}/afni/prompt_user
%{_libexecdir}/afni/quickspec
%{_libexecdir}/afni/segtools
%{_libexecdir}/afni/suma_gts
%{_libexecdir}/afni/volume_render
# SUMA-component binaries with 3d prefix
%{_libexecdir}/afni/1dDW_Grad_o_Mat++
%{_libexecdir}/afni/1dDW_Grad_o_Mat
%{_libexecdir}/afni/3dAmpToRSFC
%{_libexecdir}/afni/3dBRAIN_VOYAGERtoAFNI
%{_libexecdir}/afni/3dCRUISEtoAFNI
%{_libexecdir}/afni/3dClusterize
%{_libexecdir}/afni/3dDTtoNoisyDWI
%{_libexecdir}/afni/3dDWUncert
%{_libexecdir}/afni/3dEigsToDT
%{_libexecdir}/afni/3dGenFeatureDist
%{_libexecdir}/afni/3dGenPriors
%{_libexecdir}/afni/3dHist
%{_libexecdir}/afni/3dLombScargle
%{_libexecdir}/afni/3dMatch
%{_libexecdir}/afni/3dNetCorr
%{_libexecdir}/afni/3dProbTrackID
%{_libexecdir}/afni/3dROIMaker
%{_libexecdir}/afni/3dRSFC
%{_libexecdir}/afni/3dReHo
%{_libexecdir}/afni/3dSeg
%{_libexecdir}/afni/3dSkullStrip
%{_libexecdir}/afni/3dSliceNDice
%{_libexecdir}/afni/3dSpaceTimeCorr
%{_libexecdir}/afni/3dSurf2Vol
%{_libexecdir}/afni/3dSurfMask
%{_libexecdir}/afni/3dTORTOISEtoHere
%{_libexecdir}/afni/3dTrackID
%{_libexecdir}/afni/3dVecRGB_to_HSL
%{_libexecdir}/afni/3dVol2Surf
%{_libexecdir}/afni/3dZipperZapper
%{_libexecdir}/afni/3ddot_beta
%{_libexecdir}/afni/3dinfill
%{_libexecdir}/afni/3dkmeans
%{_libexecdir}/afni/map_TrackID
# /usr/bin symlinks
%{_bindir}/suma
%{_bindir}/3dSkullStrip

# --- python3-afni ---
%files -n python3-%{name} -f %{pyproject_files}
# Python scripts installed by cmake to libexec
%{_libexecdir}/afni/1d_tool.py
%{_libexecdir}/afni/1dplot.py
%{_libexecdir}/afni/@DoPerRoi.py
%{_libexecdir}/afni/@djunct_calc_mont_dims.py
%{_libexecdir}/afni/@djunct_combine_str.py
%{_libexecdir}/afni/@djunct_is_label.py
%{_libexecdir}/afni/@djunct_make_script_and_rst.py
%{_libexecdir}/afni/@djunct_select_str.py
%{_libexecdir}/afni/BayesianGroupAna.py
%{_libexecdir}/afni/PeakFinder.py
%{_libexecdir}/afni/PhaseEstimator.py
%{_libexecdir}/afni/RVT_from_PeakFinder.py
%{_libexecdir}/afni/RetroTS.py
%{_libexecdir}/afni/Show_RVT_Peak.py
%{_libexecdir}/afni/abids_json_info.py
%{_libexecdir}/afni/abids_json_tool.py
%{_libexecdir}/afni/abids_lib.py
%{_libexecdir}/afni/abids_tool.py
%{_libexecdir}/afni/afni_base.py
%{_libexecdir}/afni/afni_proc.py
%{_libexecdir}/afni/afni_restproc.py
%{_libexecdir}/afni/afni_skeleton.py
%{_libexecdir}/afni/afni_system_check.py
%{_libexecdir}/afni/afni_util.py
%{_libexecdir}/afni/afni_xmat.py
%{_libexecdir}/afni/align_epi_anat.py
%{_libexecdir}/afni/apqc_make_html.py
%{_libexecdir}/afni/apqc_make_tcsh.py
%{_libexecdir}/afni/ask_me.py
%{_libexecdir}/afni/auto_warp.py
%{_libexecdir}/afni/db_mod.py
%{_libexecdir}/afni/eg_main_chrono.py
%{_libexecdir}/afni/epi_b0_correct.py
%{_libexecdir}/afni/fat_lat_csv.py
%{_libexecdir}/afni/fat_mat_sel.py
%{_libexecdir}/afni/fat_mvm_gridconv.py
%{_libexecdir}/afni/fat_mvm_prep.py
%{_libexecdir}/afni/fat_mvm_review.py
%{_libexecdir}/afni/fat_mvm_scripter.py
%{_libexecdir}/afni/fat_roi_row.py
%{_libexecdir}/afni/gen_epi_review.py
%{_libexecdir}/afni/gen_group_command.py
%{_libexecdir}/afni/gen_ss_review_scripts.py
%{_libexecdir}/afni/gen_ss_review_table.py
%{_libexecdir}/afni/gui_uber_align_test.py
%{_libexecdir}/afni/gui_uber_skel.py
%{_libexecdir}/afni/gui_uber_subj.py
%{_libexecdir}/afni/gui_uber_ttest.py
%{_libexecdir}/afni/gui_xmat.py
%{_libexecdir}/afni/lib_RR_plot.py
%{_libexecdir}/afni/lib_RetroTS
%{_libexecdir}/afni/lib_afni1D.py
%{_libexecdir}/afni/lib_apqc_html.py
%{_libexecdir}/afni/lib_apqc_html_css.py
%{_libexecdir}/afni/lib_apqc_html_helps.py
%{_libexecdir}/afni/lib_apqc_io.py
%{_libexecdir}/afni/lib_apqc_tcsh.py
%{_libexecdir}/afni/lib_b0_corr.py
%{_libexecdir}/afni/lib_decay_timing.py
%{_libexecdir}/afni/lib_dti_sundry.py
%{_libexecdir}/afni/lib_fat_Rfactor.py
%{_libexecdir}/afni/lib_fat_funcs.py
%{_libexecdir}/afni/lib_fat_plot_sel.py
%{_libexecdir}/afni/lib_gershgorin.py
%{_libexecdir}/afni/lib_matplot.py
%{_libexecdir}/afni/lib_msar.py
%{_libexecdir}/afni/lib_plot_1D.py
%{_libexecdir}/afni/lib_qt_gui.py
%{_libexecdir}/afni/lib_rand_timing.py
%{_libexecdir}/afni/lib_realtime.py
%{_libexecdir}/afni/lib_ss_review.py
%{_libexecdir}/afni/lib_subjects.py
%{_libexecdir}/afni/lib_surf_clustsim.py
%{_libexecdir}/afni/lib_system_check.py
%{_libexecdir}/afni/lib_textdata.py
%{_libexecdir}/afni/lib_timing.py
%{_libexecdir}/afni/lib_uber_align.py
%{_libexecdir}/afni/lib_uber_skel.py
%{_libexecdir}/afni/lib_uber_subject.py
%{_libexecdir}/afni/lib_uber_ttest.py
%{_libexecdir}/afni/lib_vars_object.py
%{_libexecdir}/afni/lib_wx.py
%{_libexecdir}/afni/lpc_align.py
%{_libexecdir}/afni/make_pq_script.py
%{_libexecdir}/afni/make_random_timing.py
%{_libexecdir}/afni/make_stim_times.py
%{_libexecdir}/afni/meica.py
%{_libexecdir}/afni/module_test_lib.py
%{_libexecdir}/afni/neuro_deconvolve.py
%{_libexecdir}/afni/niml_parsing.py
%{_libexecdir}/afni/option_list.py
%{_libexecdir}/afni/parse_fs_lt_log.py
%{_libexecdir}/afni/python_module_test.py
%{_libexecdir}/afni/quick.alpha.vals.py
%{_libexecdir}/afni/read_matlab_files.py
%{_libexecdir}/afni/realtime_receiver.py
%{_libexecdir}/afni/slow_surf_clustsim.py
%{_libexecdir}/afni/tedana_wrapper.py
%{_libexecdir}/afni/timing_tool.py
%{_libexecdir}/afni/uber_align_test.py
%{_libexecdir}/afni/uber_proc.py
%{_libexecdir}/afni/uber_skel.py
%{_libexecdir}/afni/uber_subject.py
%{_libexecdir}/afni/uber_ttest.py
%{_libexecdir}/afni/ui_xmat.py
%{_libexecdir}/afni/unWarpEPI.py
%{_libexecdir}/afni/xmat_tool.py
%{_libexecdir}/afni/zscale.py
# /usr/bin symlinks
%{_bindir}/afni_proc.py
%{_bindir}/afni_system_check.py

# --- afni-tcsh ---
%files tcsh
%{_libexecdir}/afni/3dMax
%{_libexecdir}/afni/3dPAR2AFNI.pl
%{_libexecdir}/afni/@1dDiffMag
%{_libexecdir}/afni/@2dwarper
%{_libexecdir}/afni/@2dwarper.Allin
%{_libexecdir}/afni/@4Daverage
%{_libexecdir}/afni/@ANATICOR
%{_libexecdir}/afni/@AddEdge
%{_libexecdir}/afni/@AfniEnv
%{_libexecdir}/afni/@AfniOrient2RAImap
%{_libexecdir}/afni/@AfniOrientSign
%{_libexecdir}/afni/@Align_Centers
%{_libexecdir}/afni/@Atlasize
%{_libexecdir}/afni/@Center_Distance
%{_libexecdir}/afni/@CheckForAfniDset
%{_libexecdir}/afni/@CommandGlobb
%{_libexecdir}/afni/@DO.examples
%{_libexecdir}/afni/@DTI_studio_reposition
%{_libexecdir}/afni/@DeblankFileNames
%{_libexecdir}/afni/@DiceMetric
%{_libexecdir}/afni/@DriveAfni
%{_libexecdir}/afni/@DriveSuma
%{_libexecdir}/afni/@ElectroGrid
%{_libexecdir}/afni/@ExamineGenFeatDists
%{_libexecdir}/afni/@FS_roi_label
%{_libexecdir}/afni/@FSlabel2dset
%{_libexecdir}/afni/@FindAfniDsetPath
%{_libexecdir}/afni/@FromRAI
%{_libexecdir}/afni/@FullPath
%{_libexecdir}/afni/@GetAfniBin
%{_libexecdir}/afni/@GetAfniDims
%{_libexecdir}/afni/@GetAfniID
%{_libexecdir}/afni/@GetAfniOrient
%{_libexecdir}/afni/@GetAfniPrefix
%{_libexecdir}/afni/@GetAfniRes
%{_libexecdir}/afni/@GetAfniView
%{_libexecdir}/afni/@GradFlipTest
%{_libexecdir}/afni/@Install_3dPFM_Demo
%{_libexecdir}/afni/@Install_AfniRetinoDemo
%{_libexecdir}/afni/@Install_ClustScat_Demo
%{_libexecdir}/afni/@Install_D99_macaque
%{_libexecdir}/afni/@Install_DBSproc
%{_libexecdir}/afni/@Install_FATCAT_DEMO
%{_libexecdir}/afni/@Install_FATCAT_DEMO2
%{_libexecdir}/afni/@Install_FATMVM_DEMO
%{_libexecdir}/afni/@Install_InstaCorr_Demo
%{_libexecdir}/afni/@Install_MACAQUE_DEMO
%{_libexecdir}/afni/@Install_MEICA_Demo
%{_libexecdir}/afni/@Install_NIH_Marmoset
%{_libexecdir}/afni/@Install_RSFMRI_Motion_Group_Demo
%{_libexecdir}/afni/@Install_TSrestMovieDemo
%{_libexecdir}/afni/@IsoMasks
%{_libexecdir}/afni/@MakeLabelTable
%{_libexecdir}/afni/@NoExt
%{_libexecdir}/afni/@NoPound
%{_libexecdir}/afni/@NoisySkullStrip
%{_libexecdir}/afni/@Purify_1D
%{_libexecdir}/afni/@Quiet_Talkers
%{_libexecdir}/afni/@ROI_Corr_Mat
%{_libexecdir}/afni/@R_funclist
%{_libexecdir}/afni/@RenamePanga
%{_libexecdir}/afni/@Reorder
%{_libexecdir}/afni/@RetinoProc
%{_libexecdir}/afni/@SSwarper
%{_libexecdir}/afni/@SUMA_AlignToExperiment
%{_libexecdir}/afni/@SUMA_FSvolToBRIK
%{_libexecdir}/afni/@SUMA_Make_Spec_Caret
%{_libexecdir}/afni/@SUMA_Make_Spec_FS
%{_libexecdir}/afni/@SUMA_Make_Spec_SF
%{_libexecdir}/afni/@SUMA_renumber_FS
%{_libexecdir}/afni/@ScaleVolume
%{_libexecdir}/afni/@ScriptCheck
%{_libexecdir}/afni/@Shift_Volume
%{_libexecdir}/afni/@ShowDynamicRange
%{_libexecdir}/afni/@SkullStrip_TouchUp
%{_libexecdir}/afni/@Spharm.examples
%{_libexecdir}/afni/@SurfSmooth.HEAT_07.examples
%{_libexecdir}/afni/@T1scale
%{_libexecdir}/afni/@TimeDiff
%{_libexecdir}/afni/@ToRAI
%{_libexecdir}/afni/@UpdateAfni
%{_libexecdir}/afni/@VolCenter
%{_libexecdir}/afni/@afni.run.me
%{_libexecdir}/afni/@afni_refacer_make_master
%{_libexecdir}/afni/@afni_refacer_make_master_addendum
%{_libexecdir}/afni/@afni_refacer_make_onebigA12
%{_libexecdir}/afni/@afni_refacer_run
%{_libexecdir}/afni/@align_partial_oblique
%{_libexecdir}/afni/@animal_warper
%{_libexecdir}/afni/@auto_align
%{_libexecdir}/afni/@auto_tlrc
%{_libexecdir}/afni/@build_afni_Xlib
%{_libexecdir}/afni/@chauffeur_afni
%{_libexecdir}/afni/@clean_help_dir
%{_libexecdir}/afni/@clip_volume
%{_libexecdir}/afni/@compute_OC_weights
%{_libexecdir}/afni/@compute_gcor
%{_libexecdir}/afni/@demo_prompt
%{_libexecdir}/afni/@diff.files
%{_libexecdir}/afni/@diff.tree
%{_libexecdir}/afni/@djunct_4d_imager
%{_libexecdir}/afni/@djunct_4d_slices_to_3d_vol
%{_libexecdir}/afni/@djunct_anonymize
%{_libexecdir}/afni/@djunct_dwi_selector.tcsh
%{_libexecdir}/afni/@djunct_edgy_align_check
%{_libexecdir}/afni/@djunct_glue_imgs_vert
%{_libexecdir}/afni/@djunct_json_value.py
%{_libexecdir}/afni/@djunct_montage_coordinator
%{_libexecdir}/afni/@djunct_slice_space
%{_libexecdir}/afni/@djunct_vol_3slice_select
%{_libexecdir}/afni/@escape-
%{_libexecdir}/afni/@extract_meica_ortvec
%{_libexecdir}/afni/@fast_roi
%{_libexecdir}/afni/@fat_tract_colorize
%{_libexecdir}/afni/@fix_FSsphere
%{_libexecdir}/afni/@float_fix
%{_libexecdir}/afni/@get.afni.version
%{_libexecdir}/afni/@global_parse
%{_libexecdir}/afni/@grayplot
%{_libexecdir}/afni/@help.AFNI
%{_libexecdir}/afni/@isOblique
%{_libexecdir}/afni/@make_plug_diff
%{_libexecdir}/afni/@make_stim_file
%{_libexecdir}/afni/@measure_bb_thick
%{_libexecdir}/afni/@measure_erosion_thick
%{_libexecdir}/afni/@measure_in2out
%{_libexecdir}/afni/@move.to.series.dirs
%{_libexecdir}/afni/@np
%{_libexecdir}/afni/@parse_afni_name
%{_libexecdir}/afni/@parse_name
%{_libexecdir}/afni/@radial_correlate
%{_libexecdir}/afni/@simulate_motion
%{_libexecdir}/afni/@snapshot_volreg
%{_libexecdir}/afni/@snapshot_volreg3
%{_libexecdir}/afni/@statauxcode
%{_libexecdir}/afni/@suma_acknowledge
%{_libexecdir}/afni/@suma_reprefixize_spec
%{_libexecdir}/afni/@surf_to_vol_spackle
%{_libexecdir}/afni/@thickness_master
%{_libexecdir}/afni/@toMNI_Awarp
%{_libexecdir}/afni/@toMNI_Qwarpar
%{_libexecdir}/afni/@update.afni.binaries
%{_libexecdir}/afni/@xyz_to_ijk
%{_libexecdir}/afni/dsetstat2p
%{_libexecdir}/afni/fat_proc_align_anat_pair
%{_libexecdir}/afni/fat_proc_axialize_anat
%{_libexecdir}/afni/fat_proc_connec_vis
%{_libexecdir}/afni/fat_proc_convert_dcm_anat
%{_libexecdir}/afni/fat_proc_convert_dcm_dwis
%{_libexecdir}/afni/fat_proc_decmap
%{_libexecdir}/afni/fat_proc_dwi_to_dt
%{_libexecdir}/afni/fat_proc_filter_dwis
%{_libexecdir}/afni/fat_proc_grad_plot
%{_libexecdir}/afni/fat_proc_imit2w_from_t1w
%{_libexecdir}/afni/fat_proc_map_to_dti
%{_libexecdir}/afni/fat_proc_select_vols
%{_libexecdir}/afni/p2dsetstat
%{_libexecdir}/afni/suma_change_spec
# /usr/bin symlinks
%{_bindir}/@SSwarper
%{_bindir}/@chauffeur_afni
%{_bindir}/@auto_tlrc

# --- afni-rstats ---
%files rstats
%{_libexecdir}/afni/1dGC.R
%{_libexecdir}/afni/1dRplot
%{_libexecdir}/afni/1dRplot.R
%{_libexecdir}/afni/1dSEMr.R
%{_libexecdir}/afni/1dSVAR.R
%{_libexecdir}/afni/3dAOV.R
%{_libexecdir}/afni/3dGC.R
%{_libexecdir}/afni/3dICA.R
%{_libexecdir}/afni/3dICC
%{_libexecdir}/afni/3dICC.R
%{_libexecdir}/afni/3dICC_REML.R
%{_libexecdir}/afni/3dISC
%{_libexecdir}/afni/3dISC.R
%{_libexecdir}/afni/3dKS.R
%{_libexecdir}/afni/3dLME
%{_libexecdir}/afni/3dLME.R
%{_libexecdir}/afni/3dLMEr
%{_libexecdir}/afni/3dLMEr.R
%{_libexecdir}/afni/3dMEMA
%{_libexecdir}/afni/3dMEMA.R
%{_libexecdir}/afni/3dMEPFM
%{_libexecdir}/afni/3dMEPFM.R
%{_libexecdir}/afni/3dMVM
%{_libexecdir}/afni/3dMVM.R
%{_libexecdir}/afni/3dPFM
%{_libexecdir}/afni/3dPFM.R
%{_libexecdir}/afni/3dRprogDemo
%{_libexecdir}/afni/3dRprogDemo.R
%{_libexecdir}/afni/3dSignatures
%{_libexecdir}/afni/3dSignatures.R
%{_libexecdir}/afni/@afni_R_package_install
%{_libexecdir}/afni/AFNI_Batch_R
%{_libexecdir}/afni/AFNIio.R
%{_libexecdir}/afni/AFNIplot.R
%{_libexecdir}/afni/BayesianGroupAna.R
%{_libexecdir}/afni/ExamineXmat
%{_libexecdir}/afni/ExamineXmat.R
%{_libexecdir}/afni/Level2.R
%{_libexecdir}/afni/MBA
%{_libexecdir}/afni/MBA.R
%{_libexecdir}/afni/RBA
%{_libexecdir}/afni/RBA.R
%{_libexecdir}/afni/Signatures.R
%{_libexecdir}/afni/afni_run_R
%{_libexecdir}/afni/rPkgsInstall
%{_libexecdir}/afni/rPkgsInstall.R
%{_libexecdir}/afni/rio
%{_libexecdir}/afni/smooth.R

# --- afni-data ---
%files data
%dir %{_datadir}/afni
%{_datadir}/afni/*

# --- afni-doc ---
%files doc
%license doc/README/README.copyright
%{_docdir}/afni/

# --- afni-devel ---
%files devel
%{_includedir}/afni/
%{_libdir}/libmri.so
%{_libdir}/lib3DEdge.so
%{_libdir}/libeispack.so
# libmpeg_encode may not be a separate shared lib
#%%{_libdir}/libmpeg_encode.so
%{_libdir}/libcoxplot.so
%{_libdir}/libtrack_tools.so


%changelog
* Mon Mar 16 2026 Morgan Hough <morgan.hough@gmail.com> - 26.0.08-12
- Fix %%files: mrix not separate binary; plugins have lib prefix (libplug_*.so)
- Fix %%check: use ls instead of test -f with glob (multi-file expansion)
- Allow Python bytecompile errors (afnipy has Python 2 dead code)
- Add libstdc++-static BR (dcm2niix uses -static-libstdc++)
- Add -Wno-error=format-security (AFNI uses non-literal format strings)
- Bundle nifticlib and gifticlib: system versions too old
  (missing gifti_rotate_DAs_to_front, nifti_image_write_bricks_status)
- Fix bundled gifti: add giftiio include dirs, GIFTI::giftiio alias,
  redirect gifti's own FetchContent for nifti to local source
- Fix SONAME patch: ensure leading newline before appending to CMakeLists.txt

* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 26.0.08-1
- Complete rewrite: multi-subpackage architecture
- Split into afni-libs, afni-core, afni-gui, afni-suma, python3-afni,
  afni-tcsh, afni-rstats, afni-data, afni-doc, afni-devel
- Programs in /usr/libexec/afni/ with selective /usr/bin symlinks
- profile.d scripts for PATH and environment variables
- Unbundle system nifticlib and gifticlib (via gifticlib-cmake-devel)
- SONAME versioning for shared libraries
- Bundled: f2c, XmHTML, GLw (not available as system packages)
- GCC 15 / Fedora 43 compatibility flags

* Sun Feb 15 2026 Morgan Hough <morgan.hough@gmail.com> - 26.0.08-0
- Initial basic spec for AFNI 26.0.08
