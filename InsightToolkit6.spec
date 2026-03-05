%global _lto_cflags %{nil}

%global itk_ver 6.0b01

Name:           InsightToolkit6
Version:        6.0.0~b01
Release:        1%{?dist}
Summary:        Insight Segmentation and Registration Toolkit (ITK) v6

License:        Apache-2.0
URL:            https://itk.org/
Source0:        https://github.com/InsightSoftwareConsortium/ITK/releases/download/v%{itk_ver}/InsightToolkit-%{itk_ver}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16.3
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
BuildRequires:  openjpeg2-devel
BuildRequires:  double-conversion-devel
BuildRequires:  eigen3-devel
BuildRequires:  gtest-devel
BuildConflicts: InsightToolkit-devel
BuildConflicts: InsightToolkit5-devel

%description
The Insight Toolkit (ITK) is an open-source, cross-platform system that provides
developers with an extensive suite of software tools for image analysis.
This package provides version 6 of the toolkit.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Transitive cmake find_package deps
Requires:       fftw-devel
Requires:       hdf5-devel
Requires:       expat-devel
Requires:       libjpeg-devel
Requires:       libpng-devel
Requires:       libtiff-devel
Requires:       zlib-devel
Requires:       gdcm-devel
Requires:       openjpeg2-devel
Requires:       double-conversion-devel
Requires:       eigen3-devel
Requires:       gtest-devel
%if 0%{?fedora}
Requires:       libminc-devel
%endif

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -n InsightToolkit-%{itk_ver}

# Fedora 44+ eigen3-devel 5.0.1 uses SameMajorVersion compat,
# breaking ITK's find_package(Eigen3 3.3). We remove the version
# requirement entirely to allow any system Eigen3.
sed -i 's/${_Eigen3_min_version}//g' Modules/ThirdParty/Eigen3/CMakeLists.txt

%build
# ITK 6 requires C++17
export CXXFLAGS="%{optflags} -D_GNU_SOURCE"

%cmake -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DITK_BUILD_DEFAULT_MODULES:BOOL=ON \
    -DITK_USE_SYSTEM_LIBRARIES:BOOL=ON \
    -DITK_USE_SYSTEM_DOUBLECONVERSION:BOOL=ON \
    -DITK_USE_SYSTEM_EIGEN:BOOL=ON \
    -DITK_USE_SYSTEM_EXPAT:BOOL=ON \
    -DITK_USE_SYSTEM_FFTW:BOOL=ON \
    -DITK_USE_SYSTEM_HDF5:BOOL=ON \
    -DITK_USE_SYSTEM_JPEG:BOOL=ON \
    -DITK_USE_SYSTEM_PNG:BOOL=ON \
    -DITK_USE_SYSTEM_TIFF:BOOL=ON \
    -DITK_USE_SYSTEM_ZLIB:BOOL=ON \
    -DITK_USE_SYSTEM_GDCM:BOOL=ON \
    -DITK_USE_SYSTEM_OPENJPEG:BOOL=ON \
    -DModule_ITKGoogleTest:BOOL=OFF \
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
# Remove zero-length stub headers
find %{buildroot}%{_includedir} -name stub.h -empty -delete

%files
%license LICENSE
%doc NOTICE README.md
%{_libdir}/libITK*.so.1
%{_libdir}/libitk*.so.1

%files devel
%{_includedir}/ITK-6.0/
%{_includedir}/itkopenjpeg-2.5/
%{_prefix}/lib/cmake/ITK-6.0/
%{_libdir}/libITK*.so
%{_libdir}/libitk*.so
%{_bindir}/itkTestDriver

%changelog
* Tue Feb 24 2026 Morgan Hough <morgan@example.com> - 6.0.0~b01-1
- Initial package for ITK 6.0 beta 1
