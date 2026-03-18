%define debug_package %{nil}

Name:           niftyreg
Version:        2.0.0
Release:        2%{?dist}
Summary:        Tools for rigid, affine, and non-linear medical image registration

License:        BSD-3-Clause
URL:            https://github.com/KCL-BMEIS/niftyreg
Source0:        https://github.com/KCL-BMEIS/niftyreg/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  zlib-devel
BuildRequires:  libpng-devel

%description
NiftyReg is an open-source software for efficient medical image registration.
It provides tools for rigid, affine (reg_aladin), and non-linear free-form
deformation (reg_f3d) registration, along with utilities for resampling,
transformation composition, and Jacobian map computation.

%prep
%autosetup -n %{name}-%{version}

# Patch out git requirement for version string — no .git in SRPM.
# Must replace from find_package(Git) through the NR_VERSION lines that follow
# endif(GIT_FOUND), otherwise line 55 overwrites NR_VERSION with empty.
sed -i '/find_package(Git)/,/message(STATUS "NiftyReg version/c\
set(NiftyReg_VERSION "%{version}")\
set(NR_VERSION "%{version}")\
add_definitions(-DNR_VERSION="${NR_VERSION}")\
message(STATUS "NiftyReg version: ${NR_VERSION}")' CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
export CFLAGS="%{optflags} -std=gnu17 -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"
%cmake \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_SHARED_LIBS:BOOL=OFF \
    -DUSE_CUDA:BOOL=OFF \
    -DUSE_OPENCL:BOOL=OFF \
    -DUSE_OPENMP:BOOL=ON \
    -DUSE_SSE:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install

# Remove static libraries and cmake config — no -devel subpackage
rm -rf %{buildroot}%{_prefix}/lib/cmake
rm -f %{buildroot}%{_prefix}/lib/*.a

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/reg_aladin
%{_bindir}/reg_average
%{_bindir}/reg_f3d
%{_bindir}/reg_jacobian
%{_bindir}/reg_measure
%{_bindir}/reg_resample
%{_bindir}/reg_tools
%{_bindir}/reg_transform
%{_bindir}/groupwise_niftyreg_params.sh
%{_bindir}/groupwise_niftyreg_run.sh

%changelog
* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-2
- Fix git version patch: extend sed range to cover NR_VERSION override on line 55
  (WRITE_BASIC_PACKAGE_VERSION_FILE was getting empty VERSION)

* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.0.0-1
- Initial package of NiftyReg 2.0.0
- CPU-only build (CUDA/OpenCL disabled), static internal libraries
- Patched out git version requirement for SRPM builds
