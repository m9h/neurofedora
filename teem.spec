%bcond levmar %{defined fedora}

%global commit b83e5461cca0f734677b3043d48074059012c807
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           teem
Version:        1.12.0
%global so_version 1
Release:        1.20150414git%{shortcommit}%{?dist}
Summary:        Libraries for processing and visualizing scientific raster data

# The entire source is LGPL-2.1-or-later WITH Simple-Library-Usage-exception
License:        LGPL-2.1-or-later WITH Simple-Library-Usage-exception
SourceLicense:  %{license} AND BSD-3-Clause AND MIT AND Zlib
URL:            https://teem.sourceforge.net
Source0:        https://github.com/Slicer/teem/archive/%{commit}/teem-%{shortcommit}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  make

BuildRequires:  zlib-devel
BuildRequires:  libpng-devel
BuildRequires:  bzip2-devel
BuildRequires:  fftw-devel
%if %{with levmar}
BuildRequires:  levmar-devel
%endif

%global common_description %{expand:
Teem is a coordinated group of libraries for representing, processing,
and visualizing scientific raster data. Teem includes command-line tools
that permit the library functions to be quickly applied to files and streams.

The most important libraries are Nrrd (raster data I/O and processing),
Gage (convolution-based volume measurements), Mite (volume rendering),
and Ten (diffusion tensor processing).

This is the 1.12.0 development version from the Slicer fork, needed by
3D Slicer and related neuroimaging tools.}

%description %{common_description}

The teem package contains the command-line tools included with Teem.


%package libs
Summary:        Libraries for teem

%description libs %{common_description}

The teem-libs package contains libraries that may be required at runtime by
applications that use Teem.


%package devel
Summary:        Development files for teem

Requires:       teem-libs%{?_isa} = %{version}-%{release}

%description devel %{common_description}

The teem-devel package contains libraries and header files for developing
applications that use Teem.


%prep
%autosetup -n teem-%{commit}

# Remove files not applicable to this platform
rm -rvf arch/win32
rm -rvf python

# Fix install paths for FHS/lib64 (upstream hardcodes 'lib')
# NOTE: Must escape $ as \$ so shell doesn't expand cmake variables

# Bump cmake minimum version (separate from GNUInstallDirs)
sed -i 's|cmake_minimum_required(VERSION 2.8)|cmake_minimum_required(VERSION 3.5)|' CMakeLists.txt

# Remove cmake_policy(SET CMP0054 OLD) - not allowed in CMake 4+
sed -i '/if(POLICY CMP0054)/,/endif()/d' CMakeLists.txt

# Insert include(GNUInstallDirs) before the install paths section
# (must be after project() so architecture is known)
sed -i '/# Set up some library paths/i include(GNUInstallDirs)\n' CMakeLists.txt

# Fix library install destinations from lib to CMAKE_INSTALL_LIBDIR
sed -i 's|LIBRARY DESTINATION lib\${EXTRA_INSTALL_PATH}|LIBRARY DESTINATION \${CMAKE_INSTALL_LIBDIR}|' CMakeLists.txt
sed -i 's|ARCHIVE DESTINATION lib\${EXTRA_INSTALL_PATH}|ARCHIVE DESTINATION \${CMAKE_INSTALL_LIBDIR}|' CMakeLists.txt
# Fix cmake config file install path
sed -i 's|DESTINATION lib\${EXTRA_INSTALL_PATH}$|DESTINATION \${CMAKE_INSTALL_LIBDIR}/cmake|' CMakeLists.txt

# Remove hardcoded RPATH properties from main lib
sed -i '/INSTALL_RPATH \${CMAKE_INSTALL_PREFIX}/d' CMakeLists.txt
sed -i '/INSTALL_NAME_DIR \${CMAKE_INSTALL_PREFIX}/d' CMakeLists.txt
# Remove entire set_target_properties RPATH block from bin executables
sed -i '/set_target_properties.*PROPERTIES/,/)$/d' src/bin/CMakeLists.txt

# Comment out export() that conflicts with install() in CMake 3+
sed -i 's|^export(TARGETS teem|# export(TARGETS teem|' CMakeLists.txt
# Remove install of export-generated files (CMake 3 forbids this)
sed -i 's|.*TeemLibraryDepends.cmake.*|# \&|' CMakeLists.txt


%build
%cmake \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DTeem_USE_LIB_INSTALL_SUBDIR=OFF \
    -DTeem_FFTW3=ON \
    -DBUILD_TESTING=OFF \
    -DTeem_LEVMAR=%{?with_levmar:ON}%{?!with_levmar:OFF}

%cmake_build


%install
%cmake_install


%files
%doc README.txt
%{_bindir}/gprobe
%{_bindir}/ilk
%{_bindir}/miter
%{_bindir}/mrender
%{_bindir}/nrrdSanity
%{_bindir}/overrgb
%{_bindir}/puller
%{_bindir}/tend
%{_bindir}/unu
%{_bindir}/vprobe


%files libs
%license LICENSE.txt
%{_libdir}/libteem.so.%{so_version}
%{_libdir}/libteem.so.%{version}


%files devel
%{_includedir}/teem/
%{_libdir}/libteem.so
%{_libdir}/cmake/


%changelog
* Wed Mar 04 2026 Morgan Hough <morgan.hough@gmail.com> - 1.12.0-1.20150414gitb83e546
- Update to 1.12.0 from Slicer fork for 3D Slicer compatibility
- Switch source to github.com/Slicer/teem
