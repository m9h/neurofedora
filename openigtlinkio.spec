# OpenIGTLinkIO (IGSIO) — VTK-based wrapper layers on top of OpenIGTLink, shared
# between Slicer, CustusX, IBIS, MITK, etc. Originates from openigtlink/OpenIGTLinkIF.
# SlicerOpenIGTLink builds this as an external project; we package it as a system
# library so SlicerOpenIGTLink can build against it (and our openigtlink 3.x).
# Chain: openigtlink -> openigtlinkio -> 3dslicer-openigtlink.
#
# Upstream has no release tags, so the version is nominal (1.0); the git snapshot
# is recorded in the Release. Built with GUI and Examples OFF (Slicer provides its
# own UI via the OpenIGTLinkIF loadable module).

%global commit      d7f6aef826d934577a39b48d9485bc0848f27cb8
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20250718

Name:           openigtlinkio
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        VTK-based interface library for OpenIGTLink (IGSIO)

License:        Apache-2.0
URL:            https://github.com/IGSIO/OpenIGTLinkIO
Source0:        %{url}/archive/%{commit}/OpenIGTLinkIO-%{shortcommit}.tar.gz

BuildRequires:  cmake >= 3.10
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  openigtlink-devel >= 3.1.0
BuildRequires:  vtk-devel

%description
OpenIGTLinkIO provides several wrapper layers on top of the OpenIGTLink network
protocol, exposing OpenIGTLink devices, converters, and logic as VTK objects.
It is the code-sharing layer used by 3D Slicer (SlicerOpenIGTLink), CustusX,
IBIS, MITK, and other image-guided-therapy systems.

This build targets the protocol-version-3 openigtlink 3.x library and the system
VTK; the GUI and example programs are disabled.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       openigtlink-devel%{?_isa}
Requires:       vtk-devel

%description    devel
Headers and CMake package configuration for building applications against
%{name}.

%prep
%autosetup -n OpenIGTLinkIO-%{commit}

%build
%cmake -G Ninja \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DIGTLIO_USE_GUI:BOOL=OFF \
    -DIGTLIO_USE_EXAMPLES:BOOL=OFF \
    -DIGTLIO_QT_VERSION:STRING=6 \
    -DOpenIGTLinkIO_LIBRARY_INSTALL:STRING=%{_lib} \
    -DOpenIGTLinkIO_ARCHIVE_INSTALL:STRING=%{_lib} \
    -DOpenIGTLinkIO_CMAKE_INSTALL:STRING=%{_lib}/cmake \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE.md
%{_libdir}/libigtlio*.so*

%files devel
%{_includedir}/igtlio/
%{_libdir}/cmake/igtlio/

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20250718gitd7f6aef8
- Initial package. IGSIO OpenIGTLinkIO git snapshot built against openigtlink 3.x
  and system VTK (GUI/examples off) for the SlicerOpenIGTLink build chain.
