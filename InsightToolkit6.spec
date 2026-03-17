%global _lto_cflags %{nil}

# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

%global itk_ver 6.0b01

Name:           InsightToolkit6
Version:        6.0.0~b01
Release:        2%{?dist}
Summary:        Insight Segmentation and Registration Toolkit (ITK) v6

License:        Apache-2.0
URL:            https://itk.org/
Source0:        https://github.com/InsightSoftwareConsortium/ITK/releases/download/v%{itk_ver}/InsightToolkit-%{itk_ver}.tar.gz
# Remote modules (pre-populated for offline mock/COPR builds)
# GenericLabelInterpolator: required by ANTs
%global glinterp_commit ebf2436469ccf82c08fab54b7446f699ad0eae01
Source1:        https://github.com/InsightSoftwareConsortium/ITKGenericLabelInterpolator/archive/%{glinterp_commit}/ITKGenericLabelInterpolator-%{glinterp_commit}.tar.gz
# AdaptiveDenoising: required by ANTs DenoiseImage and antsJointFusion
%global adaptive_commit 24825c8d246e941334f47968553f0ae388851f0c
Source2:        https://github.com/ntustison/ITKAdaptiveDenoising/archive/%{adaptive_commit}/ITKAdaptiveDenoising-%{adaptive_commit}.tar.gz
# MorphologicalContourInterpolation: required by ITK-SNAP
%global morphci_commit 821bf9b3ef8eaaab10391ed060dc9ca5e4d37b39
Source3:        https://github.com/KitwareMedical/ITKMorphologicalContourInterpolation/archive/%{morphci_commit}/ITKMorphologicalContourInterpolation-%{morphci_commit}.tar.gz
# GrowCut: provides itkFastGrowCut.h, required by MITK Segmentation
%global growcut_commit cbf93ab65117abfbf5798745117e34f22ff04728
Source4:        https://github.com/InsightSoftwareConsortium/ITKGrowCut/archive/%{growcut_commit}/ITKGrowCut-%{growcut_commit}.tar.gz
# SimpleITKFilters: required by SimpleITK
%global sitkfilters_commit bb896868fc6480835495d0da4356d5db009592a6
Source5:        https://github.com/InsightSoftwareConsortium/ITKSimpleITKFilters/archive/%{sitkfilters_commit}/ITKSimpleITKFilters-%{sitkfilters_commit}.tar.gz
# LabelErodeDilate: required by SimpleITK
%global labelerodedilate_commit 22d8846dbe4368312aa3aa95ecfe3542ab894e15
Source6:        https://github.com/InsightSoftwareConsortium/ITKLabelErodeDilate/archive/%{labelerodedilate_commit}/ITKLabelErodeDilate-%{labelerodedilate_commit}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch: %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.22
BuildRequires:  fftw-devel
BuildRequires:  expat-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  zlib-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif
BuildRequires:  hdf5-devel
BuildRequires:  gdcm-devel
BuildRequires:  dcmtk-devel
BuildRequires:  openjpeg2-devel
# VTK for ITKVtkGlue
BuildRequires:  vtk-devel
BuildRequires:  python3-devel
# Transitive deps of VTK's cmake config (find_package calls in
# VTK-vtk-module-find-packages.cmake); should be Requires of vtk-devel
BuildRequires:  json-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  fmt-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  proj-devel
BuildRequires:  pugixml-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  freetype-devel
BuildRequires:  libxml2-devel
BuildRequires:  double-conversion-devel
BuildRequires:  cmake(Qt6)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildConflicts: InsightToolkit-devel

# ITK 6 is not yet compatible with ITK 5 — versioned install paths allow
# co-installation but consumers must choose one.
# Eigen3 is bundled (ITK_USE_SYSTEM_EIGEN=OFF) because Fedora 44+ ships
# eigen3-devel 5.0.1 which declares SameMajorVersion compatibility, breaking
# ITK's find_package(Eigen3 3.3) even though 5.0.1 > 3.3.
# DoubleConversion is bundled — ITK carries minor patches.
Provides:       bundled(double-conversion)
Provides:       bundled(eigen3)
Provides:       bundled(nifti)
Provides:       bundled(metaio)
Provides:       bundled(kwsys)

%description
The Insight Toolkit (ITK) is an open-source, cross-platform system that provides
developers with an extensive suite of software tools for image analysis.
This package provides version 6 (beta) of the toolkit.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-vtk-devel%{?_isa} = %{version}-%{release}
# Transitive cmake find_package deps: downstream consumers of ITK's UseITK.cmake
# will have find_package() called for each system library ITK was built against.
Requires:       fftw-devel
Requires:       hdf5-devel
Requires:       expat-devel
Requires:       libjpeg-devel
Requires:       libpng-devel
Requires:       libtiff-devel
Requires:       zlib-devel
Requires:       gdcm-devel
Requires:       dcmtk-devel
Requires:       openjpeg2-devel
%if 0%{?fedora}
Requires:       libminc-devel
%endif

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package vtk
Summary:        Provides an interface between ITK 6 and VTK
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description vtk
Provides an interface between ITK 6 and VTK.

%package vtk-devel
Summary:        Development files for the ITK 6-VTK bridge
Requires:       %{name}-vtk%{?_isa} = %{version}-%{release}
Requires:       vtk-devel%{?_isa}

%description vtk-devel
Libraries and header files for developing applications that use the
ITK 6-VTK bridge (ITKVtkGlue).

%prep
%autosetup -n InsightToolkit-%{itk_ver}

# Fix missing include for GCC 14+ (cstdint)
sed -i 's/#include "itkMacro.h"/#include "itkMacro.h"\n#include <cstdint>/' \
    Modules/Core/Common/include/itkFloatingPointExceptions.h 2>/dev/null || true

# Unpack remote modules into expected locations for offline builds
mkdir -p Modules/Remote/GenericLabelInterpolator
tar -xzf %{SOURCE1} --strip-components=1 \
    -C Modules/Remote/GenericLabelInterpolator

mkdir -p Modules/Remote/AdaptiveDenoising
tar -xzf %{SOURCE2} --strip-components=1 \
    -C Modules/Remote/AdaptiveDenoising

mkdir -p Modules/Remote/MorphologicalContourInterpolation
tar -xzf %{SOURCE3} --strip-components=1 \
    -C Modules/Remote/MorphologicalContourInterpolation

mkdir -p Modules/Remote/GrowCut
tar -xzf %{SOURCE4} --strip-components=1 \
    -C Modules/Remote/GrowCut

mkdir -p Modules/Remote/SimpleITKFilters
tar -xzf %{SOURCE5} --strip-components=1 \
    -C Modules/Remote/SimpleITKFilters

mkdir -p Modules/Remote/LabelErodeDilate
tar -xzf %{SOURCE6} --strip-components=1 \
    -C Modules/Remote/LabelErodeDilate

%build
# GCC 15 compatibility flags
export CXXFLAGS="%{optflags} -fpermissive -Wno-error=incompatible-pointer-types -Wno-error=int-conversion -D_GNU_SOURCE -I%{_builddir}/InsightToolkit-%{itk_ver}/Modules/Core/Common/include"

%cmake \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DITK_BUILD_DEFAULT_MODULES:BOOL=ON \
    -DITK_USE_SYSTEM_LIBRARIES:BOOL=OFF \
    -DITK_USE_SYSTEM_EIGEN:BOOL=OFF \
    -DITK_USE_SYSTEM_EXPAT:BOOL=ON \
    -DITK_USE_SYSTEM_FFTW:BOOL=ON \
    -DITK_USE_SYSTEM_HDF5:BOOL=ON \
    -DITK_USE_SYSTEM_JPEG:BOOL=ON \
    -DITK_USE_SYSTEM_PNG:BOOL=ON \
    -DITK_USE_SYSTEM_TIFF:BOOL=ON \
    -DITK_USE_SYSTEM_ZLIB:BOOL=ON \
    -DITK_USE_SYSTEM_GDCM:BOOL=ON \
    -DITK_USE_SYSTEM_DCMTK:BOOL=ON \
    -DITK_USE_SYSTEM_OPENJPEG:BOOL=ON \
    -DITK_USE_SYSTEM_DOUBLECONVERSION:BOOL=OFF \
    -DModule_ITKGoogleTest:BOOL=OFF \
    -DModule_GenericLabelInterpolator:BOOL=ON \
    -DModule_AdaptiveDenoising:BOOL=ON \
    -DModule_MorphologicalContourInterpolation:BOOL=ON \
    -DModule_GrowCut:BOOL=ON \
    -DModule_SimpleITKFilters:BOOL=ON \
    -DModule_LabelErodeDilate:BOOL=ON \
    -DModule_ITKVtkGlue:BOOL=ON \
    -DModule_ITKIOPhilipsREC:BOOL=ON \
    -DModule_ITKReview:BOOL=ON \
    -DModule_ITKDeprecated:BOOL=ON \
    -DITK_FORBID_DOWNLOADS:BOOL=ON \
%if 0%{?fedora}
    -DITK_USE_SYSTEM_MINC:BOOL=ON \
%else
    -DITK_USE_SYSTEM_MINC:BOOL=OFF \
%endif
    -DITK_INSTALL_PACKAGE_SUFFIX:STRING=-6.0 \
    -DITK_INSTALL_LIBRARY_DIR:PATH=%{_lib} \
    -DITK_INSTALL_INCLUDE_DIR:PATH=include/ITK-6.0 \
    -DITK_SKIP_PATH_LENGTH_CHECKS:BOOL=ON

%cmake_build

%install
%cmake_install
# Drop bundled html docs
rm -rf %{buildroot}%{_datadir}/doc/ITK-6.0
# Remove zero-length stub headers (rpmlint zero-length error)
find %{buildroot}%{_includedir} -name stub.h -empty -delete
# Remove cmake configs for ITK's internal bundled MINC library
if [ -d %{buildroot}%{_libdir}/cmake ]; then
    find %{buildroot}%{_libdir}/cmake -maxdepth 1 \
        \( -name 'itkLIBMINC*.cmake' -o -name 'UseitkLIBMINC.cmake' \) -delete
fi

%ldconfig_scriptlets

%ldconfig_scriptlets vtk

%files
%license LICENSE
%doc NOTICE README.md
%{_libdir}/libITK*.so.1
%{_libdir}/libitk*.so.1
%exclude %{_libdir}/libITKVtkGlue*.so.1

%files devel
%{_includedir}/ITK-6.0/
%exclude %{_includedir}/ITK-6.0/itkImageToVTKImageFilter.h*
%exclude %{_includedir}/ITK-6.0/itkVTKImageToImageFilter.h*
%exclude %{_includedir}/ITK-6.0/QuickView.h
%exclude %{_includedir}/ITK-6.0/vtkCaptureScreen.h
%{_prefix}/lib/cmake/ITK*/
%exclude %{_prefix}/lib/cmake/ITK-6.0/Modules/ITKVtkGlue.cmake
%{_libdir}/libITK*.so
%{_libdir}/libitk*.so
%exclude %{_libdir}/libITKVtkGlue*.so
%{_bindir}/itkTestDriver

%files vtk
%{_libdir}/libITKVtkGlue*.so.1

%files vtk-devel
%{_libdir}/libITKVtkGlue*.so
%{_includedir}/ITK-6.0/itkImageToVTKImageFilter.h*
%{_includedir}/ITK-6.0/itkVTKImageToImageFilter.h*
%{_includedir}/ITK-6.0/QuickView.h
%{_includedir}/ITK-6.0/vtkCaptureScreen.h
%{_prefix}/lib/cmake/ITK-6.0/Modules/ITKVtkGlue.cmake

%changelog
* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b01-2
- Production quality rewrite: add VtkGlue bridge (vtk/vtk-devel subpackages),
  DCMTK support, all remote modules (GenericLabelInterpolator, AdaptiveDenoising,
  MorphologicalContourInterpolation, GrowCut, SimpleITKFilters, LabelErodeDilate),
  GCC 15 compat flags, bundled Eigen3/double-conversion, ExcludeArch i686,
  ldconfig scriptlets, bundled Provides, VTK transitive BuildRequires,
  debug_package suppression

* Tue Feb 24 2026 Morgan Hough <morgan@example.com> - 6.0.0~b01-1
- Initial package for ITK 6.0 beta 1
