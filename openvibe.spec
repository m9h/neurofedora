# Pinned submodule commits for 3.7.0 tag
%global sdk_commit      cbcc6e0cac025a277464a81c24b45cc8140c7405
%global designer_commit 50ac3772d5a21b01bc5a41bbfc4fbffeebd73974
%global extras_commit   97cdd0f70e9e749858aaca0f35a7d4424c59b778

Name:           openvibe
Version:        3.7.0
Release:        1%{?dist}
Summary:        Brain-Computer Interface platform for EEG/MEG signal processing

License:        AGPL-3.0-or-later
URL:            http://openvibe.inria.fr
Source0:        https://gitlab.inria.fr/openvibe/meta/-/archive/%{version}/meta-%{version}.tar.gz
Source1:        https://gitlab.inria.fr/openvibe/sdk/-/archive/%{sdk_commit}/sdk-%{sdk_commit}.tar.gz
Source2:        https://gitlab.inria.fr/openvibe/designer/-/archive/%{designer_commit}/designer-%{designer_commit}.tar.gz
Source3:        https://gitlab.inria.fr/openvibe/extras/-/archive/%{extras_commit}/extras-%{extras_commit}.tar.gz

# Tiny bundled sources with no system-package equivalent
Provides:       bundled(lepton)
Provides:       bundled(r8brain)
Provides:       bundled(wavelib)
Provides:       bundled(dsp-filters)
Provides:       bundled(SuperEasyJSON)

BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  gcc-c++

# Core dependencies
BuildRequires:  boost-devel >= 1.71
BuildRequires:  eigen3-devel
BuildRequires:  lua-devel
BuildRequires:  xerces-c-devel
BuildRequires:  tinyxml2-devel
BuildRequires:  expat-devel
BuildRequires:  zlib-devel

# GTK2 — used for the designer GUI and visualization plugins
BuildRequires:  gtk2-devel
BuildRequires:  pkgconfig(gtk+-2.0)

# OpenGL (GLX) — used for 3D visualization rendering
BuildRequires:  mesa-libGL-devel
BuildRequires:  libX11-devel

# Audio
BuildRequires:  openal-soft-devel
BuildRequires:  freealut-devel
BuildRequires:  libogg-devel
BuildRequires:  libvorbis-devel

# Signal processing
BuildRequires:  fftw-devel

# External device/streaming protocols
BuildRequires:  vrpn-devel

# Lab Streaming Layer — from mhough/neurofedora COPR.
# Several extras plugins (games, network-io, acquisition-server) unconditionally
# link LSL::lsl, so this is effectively required despite find_package lacking REQUIRED.
BuildRequires:  liblsl-devel >= 1.16

# Scripting
BuildRequires:  python3-devel

# GTest — required by cmake configure even when tests are disabled
BuildRequires:  gtest-devel


Requires:       gtk2%{?_isa}

%description
OpenViBE is an open-source software platform for Brain-Computer Interfaces
(BCI). It can be used to acquire, filter, process, classify, and visualize
brain signals in real time. OpenViBE supports EEG and MEG data from a wide
range of acquisition hardware through its acquisition server, and provides
a visual designer for building signal-processing pipelines using a
drag-and-drop box paradigm.

%package        devel
Summary:        Development headers for OpenViBE SDK
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and development files for building plugins and applications against
the OpenViBE SDK (modules: ebml, xml, socket, fs, csv, communication,
system, toolkit, visualization-toolkit).

%prep
%autosetup -n meta-%{version}

# Unpack submodules into their directories
tar -xf %{SOURCE1} --strip-components=1 -C sdk
tar -xf %{SOURCE2} --strip-components=1 -C designer
tar -xf %{SOURCE3} --strip-components=1 -C extras

# Fix hardcoded CMAKE_INSTALL_LIBDIR — upstream forces "lib" but Fedora needs
# the arch-specific libdir (lib64 on x86_64)
sed -i '/^set(CMAKE_INSTALL_LIBDIR lib)/d' CMakeLists.txt
sed -i '/^SET(CMAKE_INSTALL_LIBDIR lib)/d' designer/CMakeLists.txt

# Fix DIST_LIBDIR to use CMAKE_INSTALL_LIBDIR instead of hardcoded "lib"
sed -i 's|set(DIST_LIBDIR ${DIST_ROOT}/lib)|set(DIST_LIBDIR ${DIST_ROOT}/${CMAKE_INSTALL_LIBDIR})|' CMakeLists.txt

# Fix Eigen3 version check for Fedora 44+ (Eigen 5.x SameMajorVersion compat)
sed -i 's/find_package(Eigen3 3.3.7)/find_package(Eigen3)/' CMake/FindThirdPartyEigen.cmake

# Fix Python3 version — upstream hardcodes 3.10 EXACT; Fedora 43 has 3.14
sed -i 's/find_package(Python3 3.10 EXACT/find_package(Python3 3/' CMake/FindThirdPartyPython.cmake

# Designer plugins: project() calls lack VERSION, resulting in literal "SOVERSION" filenames
for f in designer/plugins/visualization/ovp-advanced-visualization/CMakeLists.txt \
         designer/plugins/visualization/simple-visualization/CMakeLists.txt \
         designer/plugins/examples/CMakeLists.txt; do
    sed -i 's/^PROJECT(\(.*\))/PROJECT(\1 VERSION %{version})/' "$f"
    sed -i 's/^project(\(.*\))/project(\1 VERSION %{version})/' "$f"
done

# GCC 15: explicit qualification in declaration is now a hard error
# RiemannianPotato.cpp defines free functions with Riemannian:: qualifier
# inside the Riemannian namespace — remove the redundant qualifier
sed -i 's/void Riemannian::saveToXML/void saveToXML/' \
    extras/plugins/processing/riemannian/src/boxes/RiemannianPotato.cpp
sed -i 's/Riemannian::loadFromXML/loadFromXML/' \
    extras/plugins/processing/riemannian/src/boxes/RiemannianPotato.cpp

# GCC 15 / C++17: floor/log/etc. need <cmath> — add missing include
sed -i '1i #include <cmath>' \
    extras/plugins/processing/signal-processing/src/box-algorithms/CBoxAlgorithmEntropyMeasure.cpp

# VRPN: OpenViBE vrpn-simulator and vrpn-to-openvibe use vrpn_Button_Server
# which lives in libvrpnserver, not libvrpn — add it to the vrpn interface target
sed -i 's/target_link_libraries(vrpn INTERFACE ${VRPN_LIBRARY} ${QUAT_LIBRARY})/find_library(VRPNSERVER_LIBRARY NAMES vrpnserver)\ntarget_link_libraries(vrpn INTERFACE ${VRPN_LIBRARY} ${VRPNSERVER_LIBRARY} ${QUAT_LIBRARY})/' \
    CMake/FindThirdPartyVRPN.cmake

# IT++ library is not in Fedora — remove from contrib signal-processing link
sed -i '/^[[:space:]]*itpp[[:space:]]*$/d' \
    extras/contrib/plugins/processing/signal-processing/CMakeLists.txt

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_VALIDATION_TEST=OFF \
    -DBUILD_UNIT_TEST=OFF \
    -DBUILD_DOCUMENTATION=OFF \
    -DBUILD_GCOV=OFF \
    -DOV_PACKAGE=OFF

%cmake_build

%install
%cmake_install

# OpenViBE plugins are loaded by dlopen("libopenvibe-plugins-*.so") at runtime,
# so unversioned .so symlinks must stay in the main package

# Fix non-executable shell script
chmod +x %{buildroot}%{_datadir}/openvibe/plugins/simple-visualization/p300-magic-card/convert.sh

%ldconfig_scriptlets

%files
%license COPYING
%doc sdk/COPYING.md extras/COPYING

# Binaries
%{_bindir}/openvibe-*
%{_bindir}/sdk-examples-*

# Shared libraries — plugins need unversioned .so for dlopen at runtime
%{_libdir}/lib*.so
%{_libdir}/lib*.so.*

# Data files
%{_datadir}/openvibe/

%files devel
%{_includedir}/*.h
%{_includedir}/*.hpp
%{_includedir}/communication/
%{_includedir}/csv/
%{_includedir}/ebml/
%{_includedir}/fs/
%{_includedir}/geometry/
%{_includedir}/openvibe/
%{_includedir}/socket/
%{_includedir}/system/
%{_includedir}/toolkit/
%{_includedir}/visualization-toolkit/
%{_includedir}/xml/
%{_libdir}/*.a

%changelog
* Wed Mar 04 2026 Morgan Hough <mhough@fedoraproject.org> - 3.7.0-1
- Initial package of OpenViBE 3.7.0 for Fedora
