Name:           anima
Version:        4.2
Release:        1%{?dist}
Summary:        Inria medical image analysis toolbox (registration, diffusion, segmentation)

# Anima public library — AGPL-3.0 (Inria).
License:        AGPL-3.0-or-later
URL:            https://github.com/Inria-Empenn/Anima-Public
Source0:        %{url}/archive/v%{version}/Anima-Public-%{version}.tar.gz
# Forward-compat fixes for GCC 15+/ITK 5.4: legacy code that newer toolchains reject.
Patch0:         anima-gcc-fixes.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
# Anima superbuilds these; we use the system versions instead (no superbuild).
BuildRequires:  InsightToolkit5-devel
BuildRequires:  vtk-devel
BuildRequires:  boost-devel
BuildRequires:  NLopt-devel
BuildRequires:  tinyxml2-devel
BuildRequires:  tclap-devel
# RPI ships the ITK-extension headers Anima's SVF registration needs
# (itkStationaryVelocityFieldTransform, itkFixedPointInverseDisplacementField...)
# in %%{_includedir}/RegistrationAddOn. The superbuild gets these from RPI.
BuildRequires:  RPI-devel
# VTK cmake config pulls these at find_package time.
BuildRequires:  freetype-devel pugixml-devel fmt-devel utf8cpp-devel
BuildRequires:  PEGTL-devel jsoncpp-devel nlohmann-json-devel hdf5-devel
BuildRequires:  double-conversion-devel expat-devel glew-devel lz4-devel
BuildRequires:  libxml2-devel libtiff-devel libjpeg-turbo-devel libpng-devel

%description
Anima is a set of libraries and command-line tools for medical image analysis
developed by the Empenn (formerly VisAGeS) team at Inria. It covers image
registration, diffusion imaging (DTI/multi-compartment models, tractography),
quantitative MRI (relaxometry, MR fingerprinting), segmentation and a large
collection of image-processing utilities (the anima* tools).

This build uses the system ITK, VTK, Boost, NLopt, TinyXML2 and TCLAP rather
than the upstream superbuild.

%prep
%autosetup -p1 -n Anima-Public-%{version}

%build
# Build the inner Anima project directly (Anima/), bypassing the superbuild.
mkdir -p anima-build
cd anima-build
cmake -GNinja ../Anima \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_CXX_FLAGS="%{optflags} -fpermissive -include cstdint -I%{_includedir}/vtk -I%{_includedir}/RegistrationAddOn" \
    -DCMAKE_C_FLAGS="%{optflags}" \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DUSE_VTK:BOOL=ON \
    -DUSE_NLOPT:BOOL=ON \
    -DUSE_RPI:BOOL=OFF \
    -DBUILD_ANIMA_TESTING:BOOL=OFF \
    -DBUILD_ANIMA_DOCUMENTATION:BOOL=OFF \
    -DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=OFF \
    -DCMAKE_INSTALL_RPATH='$ORIGIN:$ORIGIN/../%{_lib}/anima'
cmake --build . %{?_smp_mflags} --verbose

%install
DESTDIR=%{buildroot} cmake --install anima-build
# The private libAnima*.so libraries install to %{_libdir}/anima; binaries find
# them via the baked $ORIGIN-relative RPATH. Nothing else to relocate.

%check
test -x %{buildroot}%{_bindir}/animaDTIEstimator

%files
%license License.txt
%{_bindir}/anima*
%dir %{_libdir}/anima
%{_libdir}/anima/lib*.so

%changelog
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 4.2-1
- Initial package: Anima medical image analysis tools (Inria), built against
  system ITK/VTK/Boost/NLopt/TinyXML2/TCLAP with the superbuild disabled.
