# Disable LTO - causes linker issues with VTK/ITK on Fedora 43+
%global _lto_cflags %{nil}

%global soname_version 0.1

%global commit fd37b874033c6589e28f5cefdd56a5f605d09960
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate 20260126

Name:           ctk
Version:        2026.01.26
Release:        0.5.%{snapdate}git%{shortcommit}%{?dist}
Summary:        The Common Toolkit for biomedical imaging (Qt6 build with VTK/ITK)

# The entire source is Apache-2.0; CMake/CMakeFindDependencyMacro.cmake is
# BSD-3-Clause, but does not contribute to the licenses of the binary RPMs.
License:        Apache-2.0
URL:            https://commontk.org/
Source0:        https://github.com/commontk/CTK/archive/%{commit}/CTK-%{shortcommit}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

# This is the Qt6 CTK build for 3D Slicer, with VTK, ITK, and DICOM.
# It Conflicts with the Fedora stock ctk package (which is Qt5-only,
# has no VTK/ITK, and is at version 2023.07.13).
Conflicts:      ctk < 2026

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16
BuildRequires:  ninja-build
BuildRequires:  python3-devel

# Qt6 — COPR VTK 9.5 is Qt6-based, so CTK must also use Qt6
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qttools-static
BuildRequires:  qt6-qtshadertools-devel
BuildRequires:  qt6-qt5compat-devel
# Qt6::StateMachine lives in qtscxml (moved from qtbase in Qt6)
BuildRequires:  qt6-qtscxml-devel

# DCMTK
BuildRequires:  dcmtk-devel

# VTK (COPR 9.5.2)
BuildRequires:  vtk-devel
# VTK cmake config transitive deps (COPR vtk-devel doesn't Require these yet)
BuildRequires:  json-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  hdf5-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  fmt-devel
BuildRequires:  libglvnd-devel
BuildRequires:  libtheora-devel
BuildRequires:  libogg-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel
BuildRequires:  expat-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  sqlite-devel
BuildRequires:  libxml2-devel
BuildRequires:  netcdf-devel
BuildRequires:  pugixml-devel
BuildRequires:  proj-devel
BuildRequires:  tbb-devel
BuildRequires:  PEGTL-devel
BuildRequires:  libharu-devel
BuildRequires:  gl2ps-devel
BuildRequires:  double-conversion-devel
BuildRequires:  eigen3-devel
BuildRequires:  cli11-devel
BuildRequires:  boost-devel
BuildRequires:  gdal-devel
# postgresql-server-devel conflicts with libpq-devel on F43; use libpq-devel
BuildRequires:  libpq-devel

# ITK5 (COPR)
BuildRequires:  InsightToolkit5-devel

%global _description %{expand:
The Common Toolkit is a community effort to provide support code for medical
image analysis, surgical navigation, and related projects. This build uses
Qt6 and includes VTK visualization, ITK image processing, and DICOM support
for use by 3D Slicer and other Qt6-based medical imaging applications.}

%description %{_description}
This package contains the CTK Core library.

%package        widgets
Summary:        Qt6 widgets for biomedical imaging applications
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    widgets %{_description}
The Widgets library is a collection of Qt widgets for usage in biomedical
imaging applications.

%package        dicom
Summary:        High-level DICOM query/retrieve library
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-widgets%{?_isa} = %{version}-%{release}

%description    dicom %{_description}
DICOM library provides high-level classes supporting query and retrieve
operations from PACS and local databases.

%package        vtk
Summary:        CTK VTK visualization components
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-widgets%{?_isa} = %{version}-%{release}

%description    vtk %{_description}
VTK visualization widgets and core components for CTK.

%package        itk
Summary:        CTK ITK image processing components
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    itk %{_description}
ITK image processing core components for CTK.

%package        devel
Summary:        Development files for CTK
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-widgets%{?_isa} = %{version}-%{release}
Requires:       %{name}-dicom%{?_isa} = %{version}-%{release}
Requires:       %{name}-vtk%{?_isa} = %{version}-%{release}
Requires:       %{name}-itk%{?_isa} = %{version}-%{release}
Requires:       dcmtk-devel%{?_isa}
Requires:       qt6-qtbase-devel%{?_isa}
Requires:       qt6-qtscxml-devel%{?_isa}
Requires:       qt6-qt5compat-devel%{?_isa}
Requires:       vtk-devel
Requires:       InsightToolkit5-devel

%description    devel %{_description}
This package contains development files for building applications with CTK.

%prep
%autosetup -n CTK-%{commit}

# Change EOL encoding
tr -d '\r' < README.md > README
mv -vf README README.md

# Fix cmake_minimum_required for CMake 4 compatibility
for f in \
    Utilities/DGraph/CMakeLists.txt \
    CMake/ctkCheckoutRepo.cmake.in \
    CMake/ctkDashboardScript.TEMPLATE.cmake \
    CMake/ctkMacroSetupQt.cmake \
    CMakeLists.txt \
    Libs/Core/CMake/TestBFD/CMakeLists.txt
do
    if [ -f "${f}" ]; then
        sed -i 's/cmake_minimum_required(VERSION.*)/cmake_minimum_required(VERSION 3.16)/' "${f}"
    fi
done

%build
# GCC 15 / Fedora 43+ fixes
export CXXFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=c++17 -include cstdint -fpermissive"
export CFLAGS="$(echo "%{optflags}" | sed 's/-flto=auto//') -std=gnu17"

%cmake \
    -GNinja \
    -DCTK_SUPERBUILD=OFF \
    -DCTK_QT_VERSION=6 \
    -DBUILD_TESTING:BOOL=OFF \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCTK_INSTALL_LIB_DIR=%{_libdir} \
    -DCTK_INSTALL_CMAKE_DIR=%{_libdir}/cmake/ctk \
    -DCTK_INSTALL_PLUGIN_DIR=%{_libdir}/ctk/plugins \
    -DCTK_INSTALL_QTPLUGIN_DIR=%{_qt6_plugindir} \
    -DDOCUMENTATION_TARGET_IN_ALL=OFF \
    -DCTK_ENABLE_DICOM=ON \
    -DCTK_ENABLE_Widgets=ON \
    -DCTK_ENABLE_PluginFramework=OFF \
    -DCTK_LIB_Visualization/VTK/Widgets=ON \
    -DCTK_LIB_ImageProcessing/ITK/Core=ON \
    -DCTK_LIB_Scripting/Python/Core=OFF \
    -DCTK_LIB_Scripting/Python/Widgets=OFF \
    -DCTK_WRAP_PYTHONQT_LIGHT=OFF \
    -DCTK_USE_SYSTEM_VTK=ON \
    -DCTK_USE_SYSTEM_ITK=ON \
    -DCTK_USE_SYSTEM_DCMTK=ON \
    -DCTK_BUILD_QTDESIGNER_PLUGINS=ON \
    -DCTK_USE_QTTESTING=OFF \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4

%cmake_build

%install
%cmake_install

%files
%doc README.md
%license NOTICE LICENSE
%{_libdir}/libCTKCore.so.%{soname_version}{,.*}

%files widgets
%{_libdir}/libCTKWidgets.so.%{soname_version}{,.*}

%files dicom
%{_libdir}/libCTKDICOMCore.so.%{soname_version}{,.*}
%{_libdir}/libCTKDICOMWidgets.so.%{soname_version}{,.*}

%files vtk
%{_libdir}/libCTKVisualizationVTK*.so.%{soname_version}{,.*}

%files itk
%{_libdir}/libCTKImageProcessingITK*.so.%{soname_version}{,.*}

%files devel
%{_includedir}/ctk-%{soname_version}/
%{_libdir}/libCTKCore.so
%{_libdir}/libCTKWidgets.so
%{_libdir}/libCTKDICOMCore.so
%{_libdir}/libCTKDICOMWidgets.so
%{_libdir}/libCTKVisualizationVTK*.so
%{_libdir}/libCTKImageProcessingITK*.so
%{_qt6_plugindir}/designer/libCTK*.so
%{_libdir}/cmake/ctk/

%changelog
* Tue Mar 17 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.4.20260126gitfd37b874
- Fix build: add qt6-qtscxml-devel (provides Qt6::StateMachine for CTKCore)
- Add qt6-qttools-static (Qt6::UiTools)
- Add -fpermissive to CXXFLAGS for GCC 15 compatibility
- Disable CTK_USE_QTTESTING (requires XmlPatterns, removed in Qt6)
- Disable CTK_WRAP_PYTHONQT_LIGHT explicitly
- Remove python subpackage (PythonQt not rebuilt for Qt6 yet)

* Mon Mar 09 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.3.20260126gitfd37b874
- Add qt6-qtshadertools-devel for VTK transitive deps

* Fri Mar 06 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.2.20260126gitfd37b874
- Switch to Qt6 (COPR VTK 9.5 is Qt6-based, cannot mix with Qt5)

* Thu Mar 05 2026 Morgan Hough <morgan.hough@gmail.com> - 2026.01.26-0.1.20260126gitfd37b874
- Full CTK build for 3D Slicer (git snapshot from master)
- Enable VTK visualization, ITK image processing
- Enable DICOM support, disable PluginFramework (not needed by Slicer)
- Based on Slicer's pinned CTK commit fd37b874
- Uses Qt6, system VTK 9.5, ITK 5.4
