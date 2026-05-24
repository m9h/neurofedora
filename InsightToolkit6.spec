%global _lto_cflags %{nil}

# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

%global itk_ver 6.0b02

Name:           InsightToolkit6
Version:        6.0.0~b02
Release:        2%{?dist}
Summary:        Insight Segmentation and Registration Toolkit (ITK) v6

License:        Apache-2.0
URL:            https://itk.org/
Source0:        ITK-%{itk_ver}.tar.gz
# Remote modules (pre-populated for offline mock/COPR builds)
# GenericLabelInterpolator: required by ANTs
%global glinterp_commit ebf2436469ccf82c08fab54b7446f699ad0eae01
Source1:        https://github.com/InsightSoftwareConsortium/ITKGenericLabelInterpolator/archive/%{glinterp_commit}/ITKGenericLabelInterpolator-%{glinterp_commit}.tar.gz
# AdaptiveDenoising: required by ANTs DenoiseImage and antsJointFusion
%global adenoise_commit 24825c8d246e941334f47968553f0ae388851f0c
Source2:        https://github.com/InsightSoftwareConsortium/ITKAdaptiveDenoising/archive/%{adenoise_commit}/ITKAdaptiveDenoising-%{adenoise_commit}.tar.gz
# MorphologicalContourInterpolation: required by some segmentation workflows
%global morphinterp_commit 821bf9b3ef8eaaab10391ed060dc9ca5e4d37b39
Source3:        https://github.com/InsightSoftwareConsortium/ITKMorphologicalContourInterpolation/archive/%{morphinterp_commit}/ITKMorphologicalContourInterpolation-%{morphinterp_commit}.tar.gz
# GrowCut: required by ITK-SNAP
%global growcut_commit cbf93ab65117abfbf5798745117e34f22ff04728
Source4:        https://github.com/InsightSoftwareConsortium/ITKGrowCut/archive/%{growcut_commit}/ITKGrowCut-%{growcut_commit}.tar.gz
# SimpleITKFilters: required by SimpleITK
%global sitk_commit bb896868fc6480835495d0da4356d5db009592a6
Source5:        https://github.com/InsightSoftwareConsortium/ITKSimpleITKFilters/archive/%{sitk_commit}/ITKSimpleITKFilters-%{sitk_commit}.tar.gz
# LabelErodeDilate: required by many pipelines
%global lerode_commit 22d8846dbe4368312aa3aa95ecfe3542ab894e15
Source6:        https://github.com/InsightSoftwareConsortium/ITKLabelErodeDilate/archive/%{lerode_commit}/ITKLabelErodeDilate-%{lerode_commit}.tar.gz

# --- Dependencies ---
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  fftw-devel
BuildRequires:  libtiff-devel
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  expat-devel
BuildRequires:  hdf5-devel
BuildRequires:  gdcm-devel
BuildRequires:  libminc-devel
BuildRequires:  vtk-devel
BuildRequires:  double-conversion-devel
BuildRequires:  json-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  dcmtk-devel
BuildRequires:  freetype-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  libxml2-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  lz4-devel
BuildRequires:  openjpeg-devel
BuildRequires:  proj-devel
BuildRequires:  sqlite-devel
BuildRequires:  PEGTL-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  fmt-devel

%description
ITK is an open-source, cross-platform system that provides developers with
an extensive suite of software tools for image analysis.

# Version 6.0 is a major upgrade with significant API changes.
# It is installed into versioned paths to avoid conflict with ITK 5.

%package devel
Summary:        Development files for ITK v6
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vtk-devel
Requires:       fftw-devel
Requires:       hdf5-devel

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use ITK v6.

%package examples
Summary:        ITK v6 examples
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description examples
Example source code, CMakeLists.txt, and test data for building
applications with ITK 6. Use as starting points for new projects.

%prep
%autosetup -n ITK-%{itk_ver}

# Fix missing include for GCC 14+ (cstdint)
sed -i 's/#include "itkMacro.h"/#include "itkMacro.h"\n#include <cstdint>/' \
    Modules/Core/Common/include/itkFloatingPointExceptions.h 2>/dev/null || true

# Prepare Remote Modules
mkdir -p Modules/Remote/GenericLabelInterpolator
mkdir -p Modules/Remote/AdaptiveDenoising
mkdir -p Modules/Remote/MorphologicalContourInterpolation
mkdir -p Modules/Remote/GrowCut
mkdir -p Modules/Remote/SimpleITKFilters
mkdir -p Modules/Remote/LabelErodeDilate

tar -xzf %{SOURCE1} --strip-components=1 \
    -C Modules/Remote/GenericLabelInterpolator
tar -xzf %{SOURCE2} --strip-components=1 \
    -C Modules/Remote/AdaptiveDenoising
tar -xzf %{SOURCE3} --strip-components=1 \
    -C Modules/Remote/MorphologicalContourInterpolation
tar -xzf %{SOURCE4} --strip-components=1 \
    -C Modules/Remote/GrowCut
tar -xzf %{SOURCE5} --strip-components=1 \
    -C Modules/Remote/SimpleITKFilters
tar -xzf %{SOURCE6} --strip-components=1 \
    -C Modules/Remote/LabelErodeDilate

# Remove remote module fetch triggers to prevent git calls during build
rm Modules/Remote/GenericLabelInterpolator.remote.cmake
rm Modules/Remote/AdaptiveDenoising.remote.cmake
rm Modules/Remote/MorphologicalContourInterpolation.remote.cmake
rm Modules/Remote/GrowCut.remote.cmake
rm Modules/Remote/SimpleITKFilters.remote.cmake
rm Modules/Remote/LabelErodeDilate.remote.cmake

%build
# GCC 15 compatibility flags
export CXXFLAGS="%{optflags} -fpermissive -Wno-error=incompatible-pointer-types -Wno-error=int-conversion -D_GNU_SOURCE -I%{_builddir}/ITK-%{itk_ver}/Modules/Core/Common/include"

%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DITK_BUILD_DEFAULT_MODULES:BOOL=ON \
    -DITK_USE_SYSTEM_LIBRARIES:BOOL=OFF \
    -DITK_USE_SYSTEM_EIGEN:BOOL=OFF \
    -DITK_USE_SYSTEM_EXPAT:BOOL=ON \
    -DITK_USE_SYSTEM_FFTW:BOOL=ON \
    -DITK_USE_SYSTEM_ZLIB:BOOL=ON \
    -DITK_USE_SYSTEM_OPENJPEG:BOOL=ON \
    -DITK_USE_SYSTEM_DOUBLECONVERSION:BOOL=OFF \
    -DITK_USE_SYSTEM_GDCM:BOOL=OFF \
    -DITK_USE_SYSTEM_MINC:BOOL=OFF \
    -DModule_ITKGoogleTest:BOOL=OFF \
    -DModule_GenericLabelInterpolator:BOOL=ON \
    -DModule_AdaptiveDenoising:BOOL=ON \
    -DModule_MorphologicalContourInterpolation:BOOL=ON \
    -DModule_GrowCut:BOOL=ON \
    -DModule_SimpleITKFilters:BOOL=ON \
    -DModule_LabelErodeDilate:BOOL=ON \
    -DModule_ITKVtkGlue:BOOL=ON \
    -DModule_ITKIOPhilipsREC:BOOL=ON \
    -DModule_ITKDeprecated:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DITK_INSTALL_INCLUDE_DIR:PATH=include/ITK-6.0 \
    -DITK_INSTALL_LIBRARY_DIR:PATH=%{_lib}/ITK-6.0 \
    -DITK_INSTALL_PACKAGE_DIR:PATH=%{_lib}/cmake/ITK-6.0

%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/ITK-6.0/libITK*.so.1
%{_libdir}/ITK-6.0/libitk*.so.1
%{_bindir}/h5*
%{_bindir}/itkTestDriver
%{_libdir}/ITK-6.0/libhdf5.settings
%{_libdir}/ITK-6.0/pkgconfig/*.pc
%{_datadir}/ITK-6.0/
%{_datadir}/doc/ITK-6.0/

%files devel
%{_includedir}/ITK-6.0/
%{_libdir}/cmake/ITK-6.0/
%{_libdir}/ITK-6.0/libITK*.so
%{_libdir}/ITK-6.0/libitk*.so
%{_libdir}/ITK-6.0/cmake/itkLIBMINC*.cmake
%{_libdir}/ITK-6.0/cmake/UseitkLIBMINC.cmake
%{_includedir}/itkopenjpeg-2.5/

%changelog
* Wed May 06 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-2
- Bundle GDCM and MINC to fix ITK 6.0 beta target errors
- Clean up spec file and use versioned install paths

* Wed Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-1
- Update to ITK 6.0 beta 2
- Fix Source0 and build paths

* Tue Feb 24 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b01-1
- Initial package for ITK 6.0 beta 1
