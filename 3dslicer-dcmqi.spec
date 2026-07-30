# dcmqi — DICOM Quantitative Imaging converters. Not strictly a Slicer
# extension in the catalog sense (it's an independent QIICR project), but
# Slicer uses it via the SlicerDcmqi extension. Packaged independently so
# other DICOM tools (ITK-SNAP plugins, dcm2niix workflows) can use it too.
#
# Library: libdcmqi.so + a few command-line converters (itkimage2segimage,
# segimage2itkimage, tid1500writer, tid1500reader).

Name:           3dslicer-dcmqi
Version:        1.5.6
Release:        3%{?dist}
Summary:        DICOM Quantitative Imaging converters

License:        BSD-3-Clause
URL:            https://github.com/QIICR/dcmqi
Source0:        %{url}/archive/refs/tags/v%{version}/dcmqi-%{version}.tar.gz

BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  dcmtk-devel
# apps/*/CMakeLists.txt do find_package(SlicerExecutionModel) to build the CLIs
# (DCMQI_BUILD_APPS=ON). It was never declared -- masked until now because the
# bogus itkjsonkit-devel aborted the buildroot before configure ever ran.
BuildRequires:  SlicerExecutionModel-devel
BuildRequires:  zlib-devel
BuildRequires:  jsoncpp-devel
Requires:       jsoncpp
BuildRequires:  rapidjson-devel
# (BuildRequires: itkjsonkit-devel removed -- no such package exists in Fedora or
# this COPR, and dcmqi references no ITKJsonKit/itkjson target anywhere in its
# CMake. It made every build of this package unsatisfiable: 3dslicer-dcmqi has
# never had a successful build, including at 1.3.1.)
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
%autosetup -p1 -n dcmqi-%{version}

%build
# DCMQI_SUPERBUILD defaults to ON upstream and would ExternalProject_Add its own
# ITK/DCMTK at build time -- no network in mock/COPR, and against Fedora policy.
# Must be explicit; the 1.3.1 packaging never passed it.
#
# The three DCMQI_INSTALL_*_DIR variables default to VERSIONED private paths
# (lib/dcmqi-1.5, lib/dcmqi-1.5/CMake, include/dcmqi-1.5). They are all
# `if(NOT ...)` guarded, so override them to the Fedora layout rather than patch,
# and keep %%files stable across future minor bumps.
#
# JsonCpp: dcmqi bundles a copy and only uses the system one when BOTH
# JsonCpp_LIBRARY and JsonCpp_INCLUDE_DIR point at existing paths
# (DCMQI_BUILTIN_JSONCPP is derived from that test, not from an option). Sources
# include <json/json.h>, so the include dir is %%{_includedir}, not its json/
# subdir.
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DDCMQI_SUPERBUILD:BOOL=OFF \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DDCMQI_BUILD_APPS:BOOL=ON \
    -DDCMQI_BUILD_SLICER_EXTENSION:BOOL=OFF \
    -DDCMQI_INSTALL_LIB_DIR:STRING=%{_lib} \
    -DDCMQI_INSTALL_CMAKE_DIR:STRING=%{_lib}/cmake/dcmqi \
    -DDCMQI_INSTALL_INCLUDE_DIR:STRING=include/dcmqi \
    -DJsonCpp_INCLUDE_DIR:PATH=%{_includedir} \
    -DJsonCpp_LIBRARY:FILEPATH=%{_libdir}/libjsoncpp.so \
    `# Fedora ships these configs directly under %{_libdir}/<pkg>/ rather than` \
    `# the canonical %{_libdir}/cmake/<pkg>/, so find_package cannot discover` \
    `# them unaided -- same hint set 3dslicer.spec needs.` \
    -DSlicerExecutionModel_DIR:PATH=%{_libdir}/SlicerExecutionModel \
    -DGenerateCLP_DIR:PATH=%{_libdir}/GenerateCLP \
    -DModuleDescriptionParser_DIR:PATH=%{_libdir}/ModuleDescriptionParser \
    -DTCLAP_DIR:PATH=%{_libdir}/tclap \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
%cmake_build

%install
%cmake_install

%ldconfig_scriptlets

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/itkimage2segimage
%{_bindir}/segimage2itkimage
# New in 1.5.x: converts a set of binary masks to a labelmap segmentation.
%{_bindir}/bin2labelsegimage
%{_bindir}/itkimage2paramap
%{_bindir}/paramap2itkimage
%{_bindir}/tid1500writer
%{_bindir}/tid1500reader
# SOVERSION is MAJOR.MINOR upstream, so this is libdcmqi.so.1.5 at 1.5.x.
%{_libdir}/libdcmqi.so.*

%files devel
%{_includedir}/dcmqi/
%{_libdir}/libdcmqi.so
%{_libdir}/cmake/dcmqi/


%changelog
* Thu Jul 30 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.6-3
- Fix the configure failure exposed once the buildroot was satisfiable: apps/*
  find_package(SlicerExecutionModel) for the CLIs (DCMQI_BUILD_APPS=ON), but it was
  never in BuildRequires and Fedora ships its config under %%{_libdir}/<pkg>/ rather
  than the canonical %%{_libdir}/cmake/<pkg>/, so find_package cannot discover it
  unaided. Add the BuildRequires and the same _DIR hint set 3dslicer.spec already
  carries (SlicerExecutionModel, GenerateCLP, ModuleDescriptionParser, TCLAP).

* Thu Jul 30 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.6-2
- Remove BuildRequires: itkjsonkit-devel -- no such package exists in Fedora or
  this COPR, and dcmqi references no ITKJsonKit/itkjson target anywhere in its CMake.
  It made the buildroot unsatisfiable, which is why 3dslicer-dcmqi has NEVER had a
  successful build, 1.3.1 included. (zlib-devel is fine: provided by
  zlib-ng-compat-devel.)

* Thu Jul 30 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.6-1
- Update to 1.5.6 (was a 1.3.1-labelled commit snapshot; upstream is on 1.5.x).
  Switch Source0 from the pinned commit to the v1.5.6 release tag and drop the
  zero-padded longcommit.
  - DCMQI_SUPERBUILD defaults to ON upstream and would ExternalProject_Add its own
    ITK/DCMTK at build time; the old packaging never disabled it. Now explicit OFF.
  - 1.5.x moved the install dirs to versioned private paths (lib/dcmqi-1.5,
    include/dcmqi-1.5). They are if(NOT ...) guarded, so override the three
    DCMQI_INSTALL_*_DIR variables to the Fedora layout instead of patching -- keeps
    %%files stable across future minor bumps.
  - Unbundle JsonCpp: dcmqi only uses the system copy when BOTH JsonCpp_LIBRARY and
    JsonCpp_INCLUDE_DIR resolve (DCMQI_BUILTIN_JSONCPP is derived from that test, not
    an option). Sources include <json/json.h> so the include dir is %%{_includedir}.
  - Ship the new bin2labelsegimage CLI and add %%ldconfig_scriptlets, which was
    missing for a package installing a shared library.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.3.1-0.1.20260518git3e326428
- Initial COPR package. Builds against system ITK 5.4.6 + dcmtk.
- DCMQI_BUILD_APPS=ON to ship the converter CLIs alongside libdcmqi.
- Named 3dslicer-dcmqi so dnf groups it with 3dslicer; the library is
  independently usable (used by other QIICR projects too).
