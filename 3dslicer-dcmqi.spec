# dcmqi — DICOM Quantitative Imaging converters. Not strictly a Slicer
# extension in the catalog sense (it's an independent QIICR project), but
# Slicer uses it via the SlicerDcmqi extension. Packaged independently so
# other DICOM tools (ITK-SNAP plugins, dcm2niix workflows) can use it too.
#
# Library: libdcmqi.so + a few command-line converters (itkimage2segimage,
# segimage2itkimage, tid1500writer, tid1500reader).

%global commit       3e326428
%global longcommit   3e3264288d4f0000000000000000000000000000
%global snapdate     20260518

Name:           3dslicer-dcmqi
Version:        1.3.1
Release:        0.1.%{snapdate}git%{commit}%{?dist}
Summary:        DICOM Quantitative Imaging converters

License:        BSD-3-Clause
URL:            https://github.com/QIICR/dcmqi
Source0:        %{url}/archive/%{commit}/dcmqi-%{commit}.tar.gz

BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  dcmtk-devel
BuildRequires:  zlib-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  rapidjson-devel
BuildRequires:  itkjsonkit-devel
# Optional dependency for the Slicer-side wrapping; the standalone dcmqi
# library and CLIs build without it.

Requires:       dcmtk

%description
dcmqi (DICOM for Quantitative Imaging) is a library and command-line tool
suite for converting between research-format quantitative imaging data
(NIfTI/NRRD + metadata JSON) and DICOM-conformant representations
(Segmentation, Parametric Maps, Structured Report TID 1500).

Used by 3D Slicer's DCMQI extension and by standalone DICOM workflows in
QIICR (NCI Quantitative Imaging Network) studies.

%package devel
Summary:        Development files for dcmqi
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       InsightToolkit5-devel >= 5.4.6

%description devel
Headers, cmake config files, and link-time symlinks for building against
libdcmqi.

%prep
%autosetup -p1 -n dcmqi-%{longcommit}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DDCMQI_BUILD_APPS:BOOL=ON \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/itkimage2segimage
%{_bindir}/segimage2itkimage
%{_bindir}/itkimage2paramap
%{_bindir}/paramap2itkimage
%{_bindir}/tid1500writer
%{_bindir}/tid1500reader
%{_libdir}/libdcmqi.so.*

%files devel
%{_includedir}/dcmqi/
%{_libdir}/libdcmqi.so
%{_libdir}/cmake/dcmqi/

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.3.1-0.1.20260518git3e326428
- Initial COPR package. Builds against system ITK 5.4.6 + dcmtk.
- DCMQI_BUILD_APPS=ON to ship the converter CLIs alongside libdcmqi.
- Named 3dslicer-dcmqi so dnf groups it with 3dslicer; the library is
  independently usable (used by other QIICR projects too).
