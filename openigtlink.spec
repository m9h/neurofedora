# OpenIGTLink 3.x — the open network protocol library for image-guided therapy.
# Fedora ships only the ancient 2.1 (2017); OpenIGTLinkIO and SlicerOpenIGTLink
# require protocol v3 / a 3.x library, so this COPR build supersedes it.
# Chain: openigtlink -> openigtlinkio -> 3dslicer-openigtlink.

%global commit      94244fed7051e00cbcd4c341a7d7656be8ac404a
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260614

Name:           openigtlink
Version:        3.1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Network protocol library for image-guided therapy (OpenIGTLink)

# Revised BSD (Insight Software Consortium)
License:        BSD-3-Clause
URL:            https://github.com/openigtlink/OpenIGTLink
Source0:        %{url}/archive/%{commit}/OpenIGTLink-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.15
BuildRequires:  gcc-c++
BuildRequires:  ninja-build

%description
OpenIGTLink is an open, simple, and extensible network communication protocol
for image-guided therapy. It standardizes the real-time exchange of tracking
data, images, transforms, and device control messages between imaging systems,
navigation/robotic devices, and visualization software such as 3D Slicer.

This is a protocol-version-3 capable 3.x build (Fedora ships only 2.1).

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and CMake config files for building applications against %{name}.

%prep
%autosetup -n OpenIGTLink-%{commit}

%build
%cmake -G Ninja \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DBUILD_EXAMPLES:BOOL=OFF \
    -DOpenIGTLink_BUILD_DOCUMENTATION:BOOL=OFF \
    -DOpenIGTLink_PROTOCOL_VERSION_2:BOOL=ON \
    -DOpenIGTLink_PROTOCOL_VERSION_3:BOOL=ON \
    -DOpenIGTLink_SUPERBUILD:BOOL=OFF \
    -DOpenIGTLink_INSTALL_LIB_DIR:STRING=%{_lib} \
    -DOpenIGTLink_INSTALL_ARCHIVE_DIR:STRING=%{_lib} \
    -DOpenIGTLink_INSTALL_PACKAGE_DIR:STRING=%{_lib}/cmake/OpenIGTLink \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE.txt
%{_libdir}/libOpenIGTLink.so.3*
%{_libdir}/libigtlutil.so.3*

%files devel
%{_includedir}/igtl/
%{_libdir}/libOpenIGTLink.so
%{_libdir}/libigtlutil.so
%{_libdir}/cmake/OpenIGTLink/

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 3.1.0-0.1.20260614git94244fed
- Initial 3.x package (git master snapshot, protocol v3) for the OpenIGTLinkIO
  and SlicerOpenIGTLink build chain. Supersedes Fedora's 2.1.
