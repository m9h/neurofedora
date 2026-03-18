%global commit d4d963629d7dfdca4b0607907f0e91827c22ea2a
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define debug_package %{nil}

Name:           c3d
Version:        1.4.2
Release:        4%{?dist}
Summary:        Medical image format conversion and processing tool

License:        GPL-3.0-or-later
URL:            https://github.com/pyushkevich/c3d
Source0:        https://github.com/pyushkevich/c3d/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4
BuildRequires:  hdf5-devel
# VTK transitive deps (ITK5 cmake config loads ITKVtkGlue → find_package(VTK))
# vtk-devel should Require these but does not yet
BuildRequires:  python3-devel
BuildRequires:  qt6-qtdeclarative-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif

%description
Convert3D (c3d) is a command-line tool for converting between medical image
formats and performing various image processing operations. It supports
NIfTI, DICOM, MetaImage, Analyze, and other common formats. The suite
includes c3d (3D), c2d (2D), c4d (4D), and c3d_affine_tool for working
with affine transformations.

%prep
%setup -q -n c3d-%{commit}

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
%cmake \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DBUILD_SHARED_LIBS:BOOL=OFF \
    -DBUILD_GUI:BOOL=OFF \
    -DBUILD_TESTING:BOOL=OFF \
    -DCONVERT3D_USE_ITK_REMOTE_MODULES:BOOL=OFF \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install

# Remove cmake export files generated in build dir (triggers check-files error)
rm -f %{_vpath_builddir}/Convert3DTargets*.cmake

# Remove development files — no -devel subpackage
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}/usr/lib/cmake
rm -f %{buildroot}%{_libdir}/*.a
rm -f %{buildroot}/usr/lib/*.a
rm -f %{buildroot}%{_libdir}/*.so
rm -f %{buildroot}/usr/lib/*.so

%files
%license COPYING.txt
%doc README.md
%{_bindir}/c2d
%{_bindir}/c3d
%{_bindir}/c4d
%{_bindir}/c3d_affine_tool

%changelog
* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.4.2-4
- Remove cmake export target files from build dir (unpackaged files error)
- Add VTK transitive BuildRequires (python3-devel, qt6-qtdeclarative-devel)

* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.4.2-1
- Initial package of Convert3D 1.4.2 (git snapshot %{shortcommit})
- Built against system InsightToolkit5 with static internal libraries
