%define debug_package %{nil}

Name:           plastimatch
Version:        1.10.0
Release:        4%{?dist}
Summary:        Medical image registration and segmentation for radiation therapy

License:        BSD-3-Clause
URL:            https://plastimatch.org/
Source0:        https://gitlab.com/plastimatch/plastimatch/-/archive/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4
BuildRequires:  dcmtk-devel
BuildRequires:  fftw-devel
BuildRequires:  sqlite-devel
BuildRequires:  hdf5-devel
# VTK transitive deps (ITK5 cmake config loads ITKVtkGlue → find_package(VTK))
BuildRequires:  python3-devel
BuildRequires:  qt6-qtdeclarative-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif

%description
Plastimatch is an open-source software for medical image registration,
segmentation, and computational geometry. It is primarily used in radiation
therapy research and supports deformable registration, DRR generation,
dose computation, and DICOM-RT structure processing. The single
'plastimatch' command provides 40+ subcommands for image operations.

%prep
%autosetup -n %{name}-%{version}

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
export CFLAGS="%{optflags} -std=gnu17 -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"
%cmake \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DPLM_SYSTEM_ITK:STRING=YES \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DPLM_SYSTEM_DCMTK:STRING=YES \
    -DPLM_CONFIG_ENABLE_CUDA:BOOL=OFF \
    -DPLM_CONFIG_ENABLE_OPENCL:BOOL=OFF \
    -DPLM_CONFIG_ENABLE_QT:BOOL=OFF \
    -DPLM_CONFIG_ENABLE_PYTHON:BOOL=OFF \
    -DPLM_CONFIG_ENABLE_CSHARP:BOOL=OFF \
    -DPLM_CONFIG_ENABLE_SUPERBUILD:BOOL=OFF \
    -DPLM_CONFIG_INSTALL_LIBRARIES:BOOL=ON \
    -DPLM_INSTALL_LIB_DIR:PATH=%{_lib} \
    -DPLM_BUILD_TESTING:BOOL=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install

# Remove development files — no -devel subpackage initially
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -f %{buildroot}%{_libdir}/*.so

%ldconfig_scriptlets

%files
%license LICENSE.TXT
%doc README.TXT AUTHORS.TXT
%{_bindir}/plastimatch
%{_libdir}/lib*.so.*
%{_datadir}/doc/plastimatch/

%changelog
* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.10.0-4
- Switch to shared libs (upstream has proper SOVERSION)
- Enable PLM_CONFIG_INSTALL_LIBRARIES (required for cmake export set)
- Add VTK transitive BuildRequires (python3-devel, qt6-qtdeclarative-devel)

* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.10.0-1
- Initial package of plastimatch 1.10.0
- Built against system InsightToolkit5 and DCMTK
- CPU-only build (CUDA/OpenCL/Qt disabled), static internal libraries
