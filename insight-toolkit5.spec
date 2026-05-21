# Disable LTO (Link Time Optimization) to prevent OOM/Compiler crashes
%global _lto_cflags %{nil}

# Limit parallel jobs to prevent OOM (Adjust -j4 to half your CPU cores)
%global _smp_mflags -j2

Name:           insight-toolkit5
Version:        5.4.2
Release:        1%{?dist}
Summary:        Insight Toolkit (ITK) - Version 5
License:        Apache-2.0
URL:            https://itk.org/
Source0:        https://github.com/InsightSoftwareConsortium/ITK/releases/download/v%{version}/InsightToolkit-%{version}.tar.gz

# Conflict with the old system package if you want to replace it entirely, 
# but parallel install is safer.
# Conflicts:      InsightToolkit < 5.0

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  doxygen
BuildRequires:  graphviz

# ITK Dependencies (Force System Versions)
BuildRequires:  dcmtk-devel
BuildRequires:  gdcm-devel
BuildRequires:  hdf5-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  zlib-devel
BuildRequires:  expat-devel
BuildRequires:  fftw-devel
BuildRequires:  eigen3-devel
BuildRequires:  libminc-devel
BuildRequires:  openjpeg2-devel
BuildRequires:  double-conversion-devel

%description
ITK is an open-source, cross-platform system that provides developers with an 
extensive suite of software tools for image analysis. 
This package provides ITK %{version} (v5).

%package devel
Summary:        Development files for ITK 5
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       dcmtk-devel
Requires:       gdcm-devel
Requires:       hdf5-devel

%description devel
Development files and headers for building applications that use ITK 5.

%prep
%autosetup -n InsightToolkit-%{version}

# FIX: Add missing <cstdint> for uint8_t (Fixes GCC 13+ compilation error)
sed -i 's/#include "itkSingletonMacro.h"/#include <cstdint>\n#include "itkSingletonMacro.h"/' Modules/Core/Common/include/itkFloatingPointExceptions.h

%build
# 1. Limit parallelism to prevent OOM kills on NUC
%global _smp_mflags -j2

# 2. Relax Compiler Flags for Legacy C Code
# -std=gnu89 allows old-style function declarations (Fixes MINC ParseArgv error)
# -Wno-error prevents Fedora's strict policy from stopping the build on warnings
export CFLAGS="%{optflags} -std=gnu89 -Wno-error=incompatible-pointer-types -Wno-error=int-conversion"
export CXXFLAGS="%{optflags} -Wno-error=format-security -Wno-format-security"

%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DITK_LEGACY_REMOVE:BOOL=ON \
    -DITK_BUILD_DEFAULT_MODULES:BOOL=ON \
    -DModule_ITKReview:BOOL=ON \
    -DITK_USE_REVIEW:BOOL=ON \
    -DITK_USE_SYSTEM_LIBRARIES:BOOL=ON \
    -DITK_USE_SYSTEM_MINC:BOOL=ON \
    -DITK_USE_SYSTEM_OPENJPEG:BOOL=ON \
    -DITK_USE_SYSTEM_DOUBLECONVERSION:BOOL=ON \
    -DITK_USE_SYSTEM_DCMTK:BOOL=ON \
    -DITK_USE_SYSTEM_GDCM:BOOL=ON \
    -DITK_USE_SYSTEM_HDF5:BOOL=ON \
    -DITK_USE_SYSTEM_JPEG:BOOL=ON \
    -DITK_USE_SYSTEM_PNG:BOOL=ON \
    -DITK_USE_SYSTEM_TIFF:BOOL=ON \
    -DITK_USE_SYSTEM_ZLIB:BOOL=ON \
    -DITK_USE_SYSTEM_EIGEN:BOOL=ON \
    -DITK_USE_SYSTEM_EXPAT:BOOL=ON \
    -DITK_USE_FFTW:BOOL=ON \
    -DITK_USE_SYSTEM_FFTW:BOOL=ON \
    -DITK_USE_64BIT_IDS:BOOL=ON \
    -DITK_INSTALL_PACKAGE_DIR:PATH=%{_libdir}/cmake/ITK-5.4 \
    -DITK_INSTALL_LIBRARY_DIR:PATH=%{_libdir} \
    -DITK_INSTALL_INCLUDE_DIR:PATH=include/ITK-5.4 \
    -DITK_INSTALL_DOC_DIR:PATH=share/doc/%{name} 

%cmake_build

%install
%cmake_install

# CLEANUP: Remove the LICENSE file installed by CMake.
# We will use the %license macro to install it cleanly from the source,
# avoiding the "File listed twice" warning.
rm -f %{buildroot}%{_datadir}/doc/%{name}/LICENSE

%files
%license LICENSE
%doc README.md
%{_libdir}/libITK*.so.*
%{_libdir}/libitk*.so.*
%{_bindir}/itkTestDriver

# Include the doc directory (containing NOTICE, Copyright.txt, etc.)
# but NOT the LICENSE we just deleted.
%{_datadir}/doc/%{name}/

%files devel
%{_includedir}/ITK-5.4/
%{_libdir}/cmake/ITK-5.4/
%{_libdir}/libITK*.so
%{_libdir}/libitk*.so

%changelog
* Wed Jan 07 2026 Morgan Hough <morgan.hough@gmail.com> - 5.4.2-1
- Initial packaging of ITK 5.4.2 for MITK compatibility
- Enabled Module_ITKReview
