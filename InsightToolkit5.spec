%global _lto_cflags %{nil}

# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

Name:           InsightToolkit5
Version:        5.4.5
Release:        15%{?dist}
Summary:        Insight Segmentation and Registration Toolkit (ITK) v5

License:        Apache-2.0
URL:            https://itk.org/
Source0:        https://github.com/InsightSoftwareConsortium/ITK/releases/download/v%{version}/InsightToolkit-%{version}.tar.gz
# ITK remote module required by ANTs (pinned commit from ITK 5.4.5's GenericLabelInterpolator.remote.cmake)
%global glinterp_commit ebf2436469ccf82c08fab54b7446f699ad0eae01
Source1:        https://github.com/InsightSoftwareConsortium/ITKGenericLabelInterpolator/archive/%{glinterp_commit}/ITKGenericLabelInterpolator-%{glinterp_commit}.tar.gz
# AdaptiveDenoising remote module: provides itkAdaptiveNonLocalMeansDenoisingImageFilter.h
# required by ANTs 2.6.5 DenoiseImage and antsJointFusion
%global adaptive_commit 24825c8d246e941334f47968553f0ae388851f0c
Source2:        https://github.com/ntustison/ITKAdaptiveDenoising/archive/%{adaptive_commit}/ITKAdaptiveDenoising-%{adaptive_commit}.tar.gz
# MorphologicalContourInterpolation remote module: required by ITK-SNAP 4.x
# (pinned commit from ITK 5.4.5's MorphologicalContourInterpolation.remote.cmake)
%global morphci_commit 821bf9b3ef8eaaab10391ed060dc9ca5e4d37b39
Source3:        https://github.com/KitwareMedical/ITKMorphologicalContourInterpolation/archive/%{morphci_commit}/ITKMorphologicalContourInterpolation-%{morphci_commit}.tar.gz
# GrowCut remote module: provides itkFastGrowCut.h required by MITK Segmentation
%global growcut_commit cbf93ab65117abfbf5798745117e34f22ff04728
Source4:        https://github.com/InsightSoftwareConsortium/ITKGrowCut/archive/%{growcut_commit}/ITKGrowCut-%{growcut_commit}.tar.gz
# SimpleITKFilters remote module: required by SimpleITK
%global sitkfilters_commit bb896868fc6480835495d0da4356d5db009592a6
Source5:        https://github.com/InsightSoftwareConsortium/ITKSimpleITKFilters/archive/%{sitkfilters_commit}/ITKSimpleITKFilters-%{sitkfilters_commit}.tar.gz
# LabelErodeDilate remote module: required by SimpleITK
%global labelerodedilate_commit 22d8846dbe4368312aa3aa95ecfe3542ab894e15
Source6:        https://github.com/InsightSoftwareConsortium/ITKLabelErodeDilate/archive/%{labelerodedilate_commit}/ITKLabelErodeDilate-%{labelerodedilate_commit}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch: %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16
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
# System VTK for ITKVtkGlue
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

# ITK 5.x is not fully compatible with ITK 4.x, so we package it separately.
# We use ITK's versioned install paths to allow side-by-side installation.
# Eigen3 is bundled (ITK_USE_SYSTEM_EIGEN=OFF) because Fedora 44+ ships
# eigen3-devel 5.0.1 which declares SameMajorVersion compatibility, breaking
# ITK's find_package(Eigen3 3.3) even though 5.0.1 > 3.3.
# DoubleConversion is bundled (ITK_USE_SYSTEM_DOUBLECONVERSION=OFF) — ITK
# carries minor patches; Fedora ITK4 also bundles it.
Provides:       bundled(double-conversion)
Provides:       bundled(eigen3)
Provides:       bundled(nifti)
Provides:       bundled(metaio)
Provides:       bundled(kwsys)

%description
The Insight Toolkit (ITK) is an open-source, cross-platform system that provides
developers with an extensive suite of software tools for image analysis.
This package provides version 5 of the toolkit.

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
Summary:        Provides an interface between ITK and VTK
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description vtk
Provides an interface between ITK and VTK.

%package vtk-devel
Summary:        Development files for the ITK-VTK bridge
Requires:       %{name}-vtk%{?_isa} = %{version}-%{release}
Requires:       vtk-devel%{?_isa}

%description vtk-devel
Libraries and header files for developing applications that use the
ITK-VTK bridge (ITKVtkGlue).

%package doc
Summary:        Documentation for %{name}
BuildArch:      noarch

%description doc
Documentation, copyright notices, and the ITK Software Guide references
for version 5 of the Insight Toolkit.

%package examples
Summary:        Example programs and data for %{name}
BuildArch:      noarch
Requires:       %{name}-devel = %{version}-%{release}

%description examples
Example source code, CMakeLists.txt, and test data for building
applications with ITK 5. Useful as starting points for new projects.

%prep
%autosetup -n InsightToolkit-%{version}

# Fix missing include for uint8_t in itkFloatingPointExceptions.h (required for GCC 14+)
sed -i 's/#include "itkMacro.h"/#include "itkMacro.h"\n#include <cstdint>/' Modules/Core/Common/include/itkFloatingPointExceptions.h

# Unpack the GenericLabelInterpolator remote module into the expected location.
# ITK's Module_GenericLabelInterpolator=ON normally fetches this at cmake time; we
# pre-populate the source directory so the build works offline (mock/COPR policy).
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
# Relax compiler checks for compatibility with GCC 14+ and force local include
# path to avoid system header conflicts
export CXXFLAGS="%{optflags} -fpermissive -Wno-error=incompatible-pointer-types -Wno-error=int-conversion -D_GNU_SOURCE -I%{_builddir}/InsightToolkit-%{version}/Modules/Core/Common/include"

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
    -DITK_INSTALL_PACKAGE_SUFFIX:STRING=-5.4 \
    -DITK_INSTALL_LIBRARY_DIR:PATH=%{_lib} \
    -DITK_INSTALL_INCLUDE_DIR:PATH=include/ITK-5.4 \
    -DITK_SKIP_PATH_LENGTH_CHECKS:BOOL=ON

%cmake_build

%install
%cmake_install
# Move bundled docs to doc subpackage location
mkdir -p %{buildroot}%{_docdir}/%{name}-doc
if [ -d %{buildroot}%{_datadir}/doc/ITK-5.4 ]; then
    mv %{buildroot}%{_datadir}/doc/ITK-5.4/* %{buildroot}%{_docdir}/%{name}-doc/ 2>/dev/null || true
    rm -rf %{buildroot}%{_datadir}/doc/ITK-5.4
fi

# Install examples for downstream developers
mkdir -p %{buildroot}%{_datadir}/%{name}/examples
cp -a Examples/* %{buildroot}%{_datadir}/%{name}/examples/ 2>/dev/null || true
# Remove zero-length stub headers (rpmlint zero-length error; ITK uses them as placeholders)
find %{buildroot}%{_includedir} -name stub.h -empty -delete
# Remove cmake configs for ITK's internal bundled MINC library (installed to lib64/cmake/
# when ITK_USE_SYSTEM_MINC=OFF on EPEL; directory does not exist on Fedora)
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
%{_includedir}/ITK-5.4/
%exclude %{_includedir}/ITK-5.4/itkImageToVTKImageFilter.h*
%exclude %{_includedir}/ITK-5.4/itkVTKImageToImageFilter.h*
%exclude %{_includedir}/ITK-5.4/QuickView.h
%exclude %{_includedir}/ITK-5.4/vtkCaptureScreen.h
%{_prefix}/lib/cmake/ITK*/
%exclude %{_prefix}/lib/cmake/ITK-5.4/Modules/ITKVtkGlue.cmake
%{_libdir}/libITK*.so
%{_libdir}/libitk*.so
%exclude %{_libdir}/libITKVtkGlue*.so
%{_bindir}/itkTestDriver

%files vtk
%{_libdir}/libITKVtkGlue*.so.1

%files vtk-devel
%{_libdir}/libITKVtkGlue*.so
%{_includedir}/ITK-5.4/itkImageToVTKImageFilter.h*
%{_includedir}/ITK-5.4/itkVTKImageToImageFilter.h*
%{_includedir}/ITK-5.4/QuickView.h
%{_includedir}/ITK-5.4/vtkCaptureScreen.h
%{_prefix}/lib/cmake/ITK-5.4/Modules/ITKVtkGlue.cmake

%files doc
%{_docdir}/%{name}-doc/

%files examples
%{_datadir}/%{name}/examples/

%changelog
* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 5.4.5-15
- Add doc and examples subpackages (matches Fedora ITK4 package structure)

* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 5.4.5-14
- Add SimpleITKFilters and LabelErodeDilate remote modules (Source5, Source6):
  required by SimpleITK 2.5.x

* Fri Mar 06 2026 Morgan Hough <morgan.hough@gmail.com> - 5.4.5-13
- Add GrowCut remote module (Source4): provides itkFastGrowCut.h
  required by MITK's Segmentation module

* Thu Mar 05 2026 Morgan Hough <morgan.hough@gmail.com> - 5.4.5-12
- Fedora-submission polish: unbundle DCMTK (ITK_USE_SYSTEM_DCMTK=ON),
  split vtk/vtk-devel subpackages for ITKVtkGlue bridge, add Provides:
  bundled() for double-conversion/eigen3/nifti/metaio/kwsys, add
  ExcludeArch: ix86, add ldconfig scriptlets, suppress debug_package
- Enable VtkGlue, PhilipsREC, Review, Deprecated modules
- Add VTK transitive cmake deps as BuildRequires (python3-devel, json-devel,
  Qt6, etc.) needed by VTK-vtk-module-find-packages.cmake

* Thu Mar 05 2026 Morgan Hough <morgan.hough@gmail.com> - 5.4.5-11
- Enable Module_ITKReview=ON: provides itkLabelGeometryImageFilter.h
  required by MITK's Multilabel module (ITKDeprecated alone was insufficient)

* Thu Mar 05 2026 Morgan Hough <morgan.hough@gmail.com> - 5.4.5-10
- Enable Module_ITKDeprecated=ON: dependency of ITKReview

* Fri Feb 27 2026 Morgan Hough <morgan@example.com> - 5.4.5-9
- Add MorphologicalContourInterpolation remote module (Source3): required by
  ITK-SNAP 4.x which requests it as a FIND_PACKAGE(ITK COMPONENTS ...) component

* Wed Feb 25 2026 Morgan Hough <morgan@example.com> - 5.4.5-8
- Guard bundled MINC cmake cleanup with directory existence check

* Wed Feb 25 2026 Morgan Hough <morgan@example.com> - 5.4.5-7
- Remove cmake configs for ITK's bundled MINC library in the install step

* Tue Feb 24 2026 Morgan Hough <morgan@example.com> - 5.4.5-6
- Add AdaptiveDenoising remote module (Source2)

* Tue Feb 24 2026 Morgan Hough <morgan@example.com> - 5.4.5-5
- Bundle GenericLabelInterpolator remote module (Source1)

* Tue Feb 24 2026 Morgan Hough <morgan@example.com> - 5.4.5-4
- Disable Module_ITKGoogleTest (OFF)

* Tue Feb 24 2026 Morgan Hough <morgan@example.com> - 5.4.5-3
- Add transitive system-lib Requires to -devel

* Tue Feb 24 2026 Morgan Hough <morgan@example.com> - 5.4.5-2
- Remove zero-length stub.h placeholders

* Mon Feb 23 2026 Morgan Hough <morgan@example.com> - 5.4.5-1
- Initial package of ITK 5.4.5

* Tue Feb 03 2026 Maintainer <maintainer@example.com> - 5.4.2-1
- Initial package for ITK 5.4.2
