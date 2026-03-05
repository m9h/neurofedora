Name:           afni
Version:        26.0.08
Release:        1%{?dist}
Summary:        Analysis of Functional NeuroImages

License:        GPLv2+
URL:            https://afni.nimh.nih.gov/
Source0:        https://github.com/afni/afni/archive/refs/tags/AFNI_%{version}.tar.gz

BuildRequires:  gcc >= 14
BuildRequires:  gcc-c++
BuildRequires:  libXp-devel
BuildRequires:  libXpm-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  expat-devel
BuildRequires:  gsl-devel
BuildRequires:  glib2-devel
BuildRequires:  openmotif-devel
BuildRequires:  libomp-devel
BuildRequires:  netpbm-progs
BuildRequires:  mesa-libGLw-devel
BuildRequires:  tcsh
BuildRequires:  R-devel
BuildRequires:  make
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  patchelf
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  git-core
BuildRequires:  gts-devel
BuildRequires:  nifticlib-devel
BuildRequires:  gifticlib-devel
BuildRequires:  freeglut-devel
# BuildRequires:  compat-f2c-devel # Verify if needed or available

Requires:       tcsh
Requires:       python3
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-matplotlib
Requires:       netpbm
Requires:       %{name}-data = %{version}-%{release}

%description
AFNI is a set of C programs for processing, analyzing, and displaying functional
MRI (FMRI) data. This package contains the main binaries and python scripts.

%package data
Summary:        Brain atlases and reference data for AFNI
BuildArch:      noarch

%description data
This package contains the reference templates (MNI, Talairach) and heavy
data files for AFNI.

%prep
%setup -q -n afni-AFNI_%{version}

# Create missing CMake Find modules for system libraries
# Check for system NIFTI/GIFTI via standard paths since pkg-config might be missing/broken for these

# FindNIFTI.cmake
cat > cmake/FindNIFTI.cmake << 'EOF'
find_path(NIFTI_INCLUDE_DIR NAMES nifti1.h PATH_SUFFIXES nifti)
find_library(NIFTI_LIBRARY NAMES niftiio)
find_library(ZNZ_LIBRARY NAMES znz)
find_library(NIFTICDF_LIBRARY NAMES nifticdf)

include(FindPackageHandleStandardArgs)
# Check for both niftiio and nifticdf
find_package_handle_standard_args(NIFTI DEFAULT_MSG NIFTI_LIBRARY NIFTI_INCLUDE_DIR NIFTICDF_LIBRARY)

if(NIFTI_FOUND)
  set(NIFTI_LIBRARIES ${NIFTI_LIBRARY} ${ZNZ_LIBRARY} ${NIFTICDF_LIBRARY})
  set(NIFTI_INCLUDE_DIRS ${NIFTI_INCLUDE_DIR})
  
  if(NOT TARGET NIFTI::nifti2)
    add_library(NIFTI::nifti2 UNKNOWN IMPORTED)
    set_target_properties(NIFTI::nifti2 PROPERTIES
      IMPORTED_LOCATION "${NIFTI_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${NIFTI_INCLUDE_DIR}"
      INTERFACE_LINK_LIBRARIES "${ZNZ_LIBRARY}"
    )
  endif()
  
  if(NOT TARGET NIFTI::nifticdf)
    add_library(NIFTI::nifticdf UNKNOWN IMPORTED)
    set_target_properties(NIFTI::nifticdf PROPERTIES
      IMPORTED_LOCATION "${NIFTICDF_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${NIFTI_INCLUDE_DIR}"
    )
  endif()
  
  if(NOT TARGET NIFTI::niftiio)
    add_library(NIFTI::niftiio UNKNOWN IMPORTED)
    set_target_properties(NIFTI::niftiio PROPERTIES
      IMPORTED_LOCATION "${NIFTI_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${NIFTI_INCLUDE_DIR}"
      INTERFACE_LINK_LIBRARIES "${ZNZ_LIBRARY}"
    )
  endif()
endif()
EOF

# FindGIFTI.cmake
cat > cmake/FindGIFTI.cmake << 'EOF'
find_path(GIFTI_INCLUDE_DIR NAMES gifti_io.h PATH_SUFFIXES gifti)
find_library(GIFTI_LIBRARY NAMES giftiio)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(GIFTI DEFAULT_MSG GIFTI_LIBRARY GIFTI_INCLUDE_DIR)

if(GIFTI_FOUND)
  set(GIFTI_LIBRARIES ${GIFTI_LIBRARY})
  set(GIFTI_INCLUDE_DIRS ${GIFTI_INCLUDE_DIR})
  if(NOT TARGET GIFTI::gifti)
    add_library(GIFTI::gifti UNKNOWN IMPORTED)
    set_target_properties(GIFTI::gifti PROPERTIES
      IMPORTED_LOCATION "${GIFTI_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${GIFTI_INCLUDE_DIR}"
    )
  endif()
endif()
EOF

%build
%cmake -DUSE_SYSTEM_GTS=ON -DUSE_SYSTEM_NIFTI=ON -DUSE_SYSTEM_GIFTI=ON -DUSE_SYSTEM_GLUT=ON -DUSE_OMP=ON
%cmake_build

# Build Python Utils
cd src/python_scripts
%pyproject_wheel
cd ../..

%install
%cmake_install

# Install Python Utils (afnipy)
cd src/python_scripts
%pyproject_install
%pyproject_save_files afnipy
cd ../..

# Install Scripts
cp src/python_scripts/scripts/*.py %{buildroot}%{_bindir}/
cp src/R_scripts/*.R %{buildroot}%{_bindir}/

# Fix Shebangs
# Python
find %{buildroot}%{_bindir} -name "*.py" -exec sed -i '1s|^#!.*python.*$|#!/usr/bin/python3|' {} +
# R
find %{buildroot}%{_bindir} -name "*.R" -exec sed -i '1s|^#!.*R.*$|#!/usr/bin/Rscript|' {} +

# Fix RPATHs
for bin in %{buildroot}%{_bindir}/*; do
  if file "$bin" | grep -q "ELF.*executable"; then
    patchelf --remove-rpath "$bin" || echo "patchelf failed on $bin"
  fi
done

%check
%ctest

# Setup Environment Script
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cat <<EOF > %{buildroot}%{_sysconfdir}/profile.d/afni.sh
export AFNI_PLUGINPATH="%{_libdir}/afni"
export AFNI_GLOBAL_SESSION="%{_datadir}/afni"
export AFNI_ATLAS_PATH="%{_datadir}/afni"
EOF

%files -f %{pyproject_files}
%license doc/README.copyright
%{_bindir}/*
%{_libdir}/*.so
%{_libdir}/afni/
%{_includedir}/afni/
%config(noreplace) %{_sysconfdir}/profile.d/afni.sh

%files data
%{_datadir}/afni/

%changelog
* Sun Feb 15 2026 Morgan Hough <morgan.hough@gmail.com> - 26.0.08-1
- Update to AFNI 26.0.08

* Mon Feb 02 2026 Morgan Hough <morgan.hough@gmail.com> - 25.3.04-1
- Initial fresh spec for AFNI 25.3.04
