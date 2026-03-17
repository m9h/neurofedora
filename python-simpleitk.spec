%define debug_package %{nil}

%global sitk_major 2
%global sitk_minor 5

Name:           python-simpleitk
Version:        2.5.3
Release:        2%{?dist}
Summary:        Simplified interface to the Insight Toolkit (ITK) for image analysis

License:        Apache-2.0
URL:            https://simpleitk.org/
Source0:        https://github.com/SimpleITK/SimpleITK/archive/refs/tags/v%{version}/SimpleITK-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16
BuildRequires:  ninja-build
BuildRequires:  swig >= 4.0
# Lua interpreter required for filter source code generation (not wrapping)
BuildRequires:  lua
BuildRequires:  InsightToolkit5-devel >= 5.4.5-14
# ITK VtkGlue is needed for image display support
BuildRequires:  InsightToolkit5-vtk-devel >= 5.4.5-14
# Python bindings
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
# ITK transitive cmake deps
BuildRequires:  fftw-devel
BuildRequires:  expat-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  zlib-devel
BuildRequires:  hdf5-devel
BuildRequires:  gdcm-devel
BuildRequires:  dcmtk-devel
BuildRequires:  openjpeg2-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif
# VTK transitive cmake deps (find_package in VTK's module config)
BuildRequires:  vtk-devel
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  json-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  double-conversion-devel
BuildRequires:  glew-devel
BuildRequires:  libxml2-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  proj-devel
BuildRequires:  gdal-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  cgnslib-devel
BuildRequires:  libarchive-devel
BuildRequires:  libpq-devel
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  openslide-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libGL-devel
BuildRequires:  cmake(Qt6)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  qt5-qtwebkit-devel
BuildRequires:  qt6-qtdeclarative-devel

%global _description %{expand:
SimpleITK is a simplified, open-source interface to the Insight Toolkit
(ITK), a C++ library for computational medical imaging. SimpleITK wraps
ITK's C++ code into Python (and other languages), providing a streamlined
API for image filtering, segmentation, registration, and I/O of 2D, 3D,
and 4D images.}

%description %{_description}

%package -n simpleitk
Summary:        C++ libraries for SimpleITK
Provides:       simpleitk = %{version}-%{release}

%description -n simpleitk
%{_description}

This package contains the core SimpleITK C++ shared libraries.

%package -n simpleitk-devel
Summary:        Development files for SimpleITK
Requires:       simpleitk%{?_isa} = %{version}-%{release}
Requires:       InsightToolkit5-devel >= 5.4.5

%description -n simpleitk-devel
Headers and cmake configuration files for developing C++ applications
with SimpleITK.

%package -n python3-simpleitk
Summary:        Python 3 bindings for SimpleITK
Requires:       simpleitk%{?_isa} = %{version}-%{release}
Requires:       python3-numpy
%{?python_provide:%python_provide python3-simpleitk}

%description -n python3-simpleitk
%{_description}

This package contains the Python 3 bindings for SimpleITK.

%prep
%autosetup -n SimpleITK-%{version}

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_DOXYGEN=OFF \
    -DSimpleITK_BUILD_DISTRIBUTE=ON \
    -DSimpleITK_FORBID_DOWNLOADS=ON \
    -DSimpleITK_INT64_PIXELIDS=ON \
    -DSimpleITK_EXPLICIT_INSTANTIATION=OFF \
    -DSimpleITK_USE_ELASTIX=OFF \
    -DSimpleITK_INSTALL_LIBRARY_DIR=%{_lib} \
    -DSimpleITK_INSTALL_ARCHIVE_DIR=%{_lib} \
    -DSimpleITK_INSTALL_PACKAGE_DIR=%{_lib}/cmake/SimpleITK-%{sitk_major}.%{sitk_minor} \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4 \
    -DWRAP_DEFAULT=OFF \
    -DWRAP_PYTHON=ON \
    -DSimpleITK_PYTHON_USE_LIMITED_API=OFF \
    -DWRAP_LUA=OFF \
    -DWRAP_JAVA=OFF \
    -DWRAP_CSHARP=OFF \
    -DWRAP_TCL=OFF \
    -DWRAP_R=OFF \
    -DWRAP_RUBY=OFF

%cmake_build

%install
%cmake_install

# SimpleITK's cmake LegacyPackaging path (non-SKBUILD) does not install the
# Python module. Manually install the SWIG-generated extension and Python
# package from the build tree into site-packages.
sitk_builddir=%{__cmake_builddir}
install -d %{buildroot}%{python3_sitearch}/SimpleITK

# SWIG-generated C extension (.so)
install -m 0755 ${sitk_builddir}/Wrapping/Python/SimpleITK/_SimpleITK*.so \
    %{buildroot}%{python3_sitearch}/SimpleITK/

# SWIG-generated Python wrapper
install -m 0644 ${sitk_builddir}/Wrapping/Python/SimpleITK/SimpleITK.py \
    %{buildroot}%{python3_sitearch}/SimpleITK/

# Python package files
for f in __init__.py extra.py py.typed; do
    install -m 0644 ${sitk_builddir}/Wrapping/Python/SimpleITK/${f} \
        %{buildroot}%{python3_sitearch}/SimpleITK/
done

# Version file (generated by cmake from _version.py.in)
install -m 0644 ${sitk_builddir}/Wrapping/Python/SimpleITK/_version.py \
    %{buildroot}%{python3_sitearch}/SimpleITK/

# Remove bundled docs installed by cmake (we use %doc/%license)
rm -rf %{buildroot}%{_datadir}/doc/SimpleITK-%{sitk_major}.%{sitk_minor}

%ldconfig_scriptlets -n simpleitk

%files -n simpleitk
%license LICENSE
%doc NOTICE Readme.md
# 48 shared libraries: 5 core + 42 ITK module wrappers + 1 SimpleITKFilters
%{_libdir}/libSimpleITK*-%{sitk_major}.%{sitk_minor}.so.1

%files -n simpleitk-devel
%{_includedir}/SimpleITK-%{sitk_major}.%{sitk_minor}/
%{_libdir}/libSimpleITK*-%{sitk_major}.%{sitk_minor}.so
%{_libdir}/cmake/SimpleITK-%{sitk_major}.%{sitk_minor}/

%files -n python3-simpleitk
# Python package with SWIG extension, wrapper, and supporting files
%{python3_sitearch}/SimpleITK/

%changelog
* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.3-2
- Add lua BuildRequires: needed for filter source code generation

* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.3-1
- Initial package for SimpleITK 2.5.3
- Python 3 bindings via SWIG
- Requires ITK 5.4.5 with SimpleITKFilters and LabelErodeDilate modules
