%global _lto_cflags %{nil}

# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

%global itk_ver 6.0b02

Name:           InsightToolkit6
Version:        6.0.0~b02
Release:        7%{?dist}
Summary:        Insight Segmentation and Registration Toolkit (ITK) v6

License:        Apache-2.0
URL:            https://itk.org/
Source0:        https://github.com/InsightSoftwareConsortium/ITK/archive/v%{itk_ver}/ITK-%{itk_ver}.tar.gz
# Remote modules (pre-populated for offline mock/COPR builds)
# GenericLabelInterpolator: required by ANTs
%global glinterp_commit cb171b099c476d160c79091b3869d2372b92ec6b
Source1:        https://github.com/InsightSoftwareConsortium/ITKGenericLabelInterpolator/archive/%{glinterp_commit}/ITKGenericLabelInterpolator-%{glinterp_commit}.tar.gz
# AdaptiveDenoising: required by ANTs DenoiseImage and antsJointFusion
%global adenoise_commit 99db4507f05ea933600c41ccf0d53b4202f4cab2
Source2:        https://github.com/ntustison/ITKAdaptiveDenoising/archive/%{adenoise_commit}/ITKAdaptiveDenoising-%{adenoise_commit}.tar.gz
# MorphologicalContourInterpolation: required by some segmentation workflows
%global morphinterp_commit afecbfd8cdf27db58643938483f58abce02057ad
Source3:        https://github.com/KitwareMedical/ITKMorphologicalContourInterpolation/archive/%{morphinterp_commit}/ITKMorphologicalContourInterpolation-%{morphinterp_commit}.tar.gz
# GrowCut: required by ITK-SNAP
%global growcut_commit a20ea641b1420f6c4b075e99217d5df2d2cc14eb
Source4:        https://github.com/InsightSoftwareConsortium/ITKGrowCut/archive/%{growcut_commit}/ITKGrowCut-%{growcut_commit}.tar.gz
# SimpleITKFilters: required by SimpleITK
%global sitk_commit 526d6c1140d76f2e5e198ff467371c2d74dc25eb
Source5:        https://github.com/InsightSoftwareConsortium/ITKSimpleITKFilters/archive/%{sitk_commit}/ITKSimpleITKFilters-%{sitk_commit}.tar.gz
# LabelErodeDilate: required by many pipelines
%global lerode_commit 5850a0f75214b72f0fe6e93f2d6101fc888c95c9
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

# Strip the invalid `typename std::is_nothrow_move_*<T>::value` from the bundled
# Eigen's Quaternion.h. `::value` is a non-type member, so the typename keyword
# is illegal; GCC 16 now enforces this. Mirror of the same fix in InsightToolkit5.spec
# so ITK6 consumers don't need per-package shadow-patches.
sed -i 's/typename std::is_nothrow_move_/std::is_nothrow_move_/g' \
    Modules/ThirdParty/Eigen3/src/itkeigen/Eigen/src/Geometry/Quaternion.h 2>/dev/null || true

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
    `# HDF5 explicit OFF: ITK6 cmake re-includes hdf5-targets.cmake via` \
    `# multiple module find_package calls. The system HDF5 export set` \
    `# only defines the shared targets; subsequent re-loads fail with` \
    `# "Some (but not all) targets in this export set were already defined".` \
    `# Bundling HDF5 sidesteps the conflict. (Same class of issue we hit` \
    `# in VTK 9.6.2; ITK has the same multi-include pattern internally.)` \
    -DITK_USE_SYSTEM_HDF5:BOOL=OFF \
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
%if 0%{?fedora} >= 45
    `# rawhide (f45+) hdf5 cmake added a strict re-include guard` \
    `# (hdf5-targets.cmake:42) that errors when VtkGlue ->` \
    `# find_package(VTK) -> VTK's find_package(HDF5) re-includes the` \
    `# system hdf5 export set ("Some (but not all) targets ... already` \
    `# defined"). With our HDF5 bundled, VtkGlue is the only path that` \
    `# pulls in the system HDF5, so disable it on rawhide until the` \
    `# Fedora hdf5 cmake guard is fixed. F44 keeps VtkGlue (no guard).` \
    -DModule_ITKVtkGlue:BOOL=OFF \
%else
    -DModule_ITKVtkGlue:BOOL=ON \
%endif
    -DModule_ITKIOPhilipsREC:BOOL=ON \
    -DModule_ITKDeprecated:BOOL=ON \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DITK_INSTALL_INCLUDE_DIR:PATH=include/ITK-6.0 \
    -DITK_INSTALL_LIBRARY_DIR:PATH=%{_lib}/ITK-6.0 \
    -DITK_INSTALL_PACKAGE_DIR:PATH=%{_lib}/cmake/ITK-6.0

%cmake_build

%install
%cmake_install

# Bundled HDF5 helper binaries (h5cc, h5c++, h5dump, h5ls, ...) must not escape
# into /usr/bin — the system hdf5-devel already owns those paths. We bundle
# HDF5 only to dodge ITK6's multi-include cmake conflict, not to expose its
# CLI tools.
rm -f %{buildroot}%{_bindir}/h5*

# Make itkTestDriver parallel-installable with InsightToolkit5-devel.
# ITKTargets-*.cmake exposes the binary as an imported cmake target whose
# IMPORTED_LOCATION points at /usr/bin/itkTestDriver — update both ends so
# ITK6 consumers continue to resolve the target correctly.
mv %{buildroot}%{_bindir}/itkTestDriver %{buildroot}%{_bindir}/itkTestDriver-6.0
sed -i 's|/bin/itkTestDriver"|/bin/itkTestDriver-6.0"|g' \
    %{buildroot}%{_libdir}/cmake/ITK-6.0/ITKTargets-*.cmake

%files
%license LICENSE
%doc README.md
%{_libdir}/ITK-6.0/libITK*.so.1
%{_libdir}/ITK-6.0/libitk*.so.1
%{_bindir}/itkTestDriver-6.0
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
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-6
- Give Source0 a real URL (github tag archive v6.0b02 -> ITK-6.0b02.tar.gz,
  extracts to ITK-6.0b02/) so the GitLab-SCM build can fetch the main ITK
  tarball instead of requiring it in lookaside.
- Align all six pre-populated remote modules to the exact commits ITK 6.0b02
  declares in Modules/Remote/*.remote.cmake (the tested-together set). Fixes the
  source-stage FTBFS: AdaptiveDenoising and MorphologicalContourInterpolation
  were pinned to InsightSoftwareConsortium URLs that 404 (the repos moved to
  ntustison/ and KitwareMedical/ and were archived); the other four (GenericLabel
  Interpolator, GrowCut, SimpleITKFilters, LabelErodeDilate) were stale b01-era
  commits. All six now match b02 and resolve.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-5
- Resolve parallel-install file conflicts with InsightToolkit5-devel and
  hdf5-devel (surfaced by neurofedora CDash dashboard).
  * Drop bundled HDF5 helper binaries (h5cc/h5c++/h5dump/...) from /usr/bin
    so they no longer collide with hdf5-devel. The bundled HDF5 is internal
    to ITK6; its CLI tools were never the intent.
  * Rename /usr/bin/itkTestDriver -> /usr/bin/itkTestDriver-6.0 and patch
    ITKTargets-*.cmake so the imported cmake target still resolves. ITK5
    keeps its unversioned /usr/bin/itkTestDriver; both ITKs now coexist.

* Tue May 26 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-4
- Bundle HDF5 (-DITK_USE_SYSTEM_HDF5:BOOL=OFF) to sidestep the
  cmake export-set conflict between hdf5-shared and hdf5_tools-shared
  when multiple module find_package calls re-include the system
  hdf5-targets.cmake. Same class of issue as VTK 9.6.2.
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-3
- Mirror of the InsightToolkit5-5.4.6-2 bundled-Eigen Quaternion.h fix:
  strip the invalid `typename std::is_nothrow_move_*<T>::value` keyword
  for GCC 16. Every ITK6 consumer inherits the fix automatically.

* Wed May 06 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-2
- Bundle GDCM and MINC to fix ITK 6.0 beta target errors
- Clean up spec file and use versioned install paths

* Thu Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b02-1
- Update to ITK 6.0 beta 2
- Fix Source0 and build paths

* Tue Feb 24 2026 Morgan Hough <morgan.hough@gmail.com> - 6.0.0~b01-1
- Initial package for ITK 6.0 beta 1
