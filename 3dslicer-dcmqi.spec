# dcmqi — DICOM Quantitative Imaging converters. Not strictly a Slicer
# extension in the catalog sense (it's an independent QIICR project), but
# Slicer uses it via the SlicerDcmqi extension. Packaged independently so
# other DICOM tools (ITK-SNAP plugins, dcm2niix workflows) can use it too.
#
# Library: libdcmqi.a (upstream builds it STATIC) + command-line converters
# segimage2itkimage, tid1500writer, tid1500reader).

Name:           3dslicer-dcmqi
Version:        1.5.4
Release:        4%{?dist}
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
# CMake/dcmqiConfigureVersionTarget.cmake does find_package(Git REQUIRED) at
# configure time to stamp a version string; it does not actually need a checkout.
BuildRequires:  git-core
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

# dcmqi derives its version metadata from git and offers no tarball fallback:
# dcmqiVersion.cmake calls GIT_WC_INFO() unconditionally, and
# dcmqiConfigureVersionTarget.cmake then FATAL_ERRORs on any of
# DCMQI_{VERSION_DATE,VERSION_QUALIFIER,WC_REVISION,WC_URL,WC_TAG} being undefined.
# A release tarball has no .git, so the build died with "DCMQI_WC_REVISION is
# mandatory" (and silently fell back to DCMQI_VERSION=0.0.0).
# Rather than patch their version logic, give them the repo they insist on: one
# commit, tagged with the real release tag so is_release is detected and the version
# qualifier stays empty, and an origin remote so GIT_WC_INFO does not warn.
# Deterministic -- author, committer and both dates come from SOURCE_DATE_EPOCH,
# which rpmbuild sets from the changelog, so the commit hash is reproducible.
_d=$(date -u -d "@${SOURCE_DATE_EPOCH:-0}" "+%%Y-%%m-%%dT%%H:%%M:%%S+00:00")
git init -q -b main .
git config user.name  "rpmbuild"
git config user.email "rpmbuild@localhost"
git remote add origin %{url}.git
git add -A
GIT_AUTHOR_DATE="$_d" GIT_COMMITTER_DATE="$_d" \
    git commit -q -m "dcmqi %{version} release tarball"
GIT_COMMITTER_DATE="$_d" git tag -a "v%{version}" -m "v%{version}"
git describe --tags

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
    `# NOTE: 1.5.4 declares DCMQI_INSTALL_*_DIR but does not USE them for the` \
    `# library or the cmake config -- libsrc/CMakeLists.txt references them zero` \
    `# times and hardcodes "ARCHIVE DESTINATION lib", and the top level hardcodes` \
    `# "DESTINATION cmake". Passing the variables (as STRING or PATH) changes` \
    `# nothing; the files land at /usr/lib and /usr/cmake regardless. They are` \
    `# relocated in %%install instead. (1.5.6 DOES honour them -- do not re-add` \
    `# these on a future version bump without re-checking.)` \
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

# 1.5.4 hardcodes its install destinations (see the %%build note): the static
# library lands in %%{buildroot}/usr/lib and the cmake config in
# %%{buildroot}/usr/cmake. Move both to the Fedora layout. Guarded so a future
# version that honours DCMQI_INSTALL_*_DIR (1.5.6 does) does not trip over this.
if [ -f %{buildroot}%{_prefix}/lib/libdcmqi.a ]; then
    install -D -p -m 0644 %{buildroot}%{_prefix}/lib/libdcmqi.a \
        %{buildroot}%{_libdir}/libdcmqi.a
# SEMMacroBuildCLI builds each CLI as a thin main() over a lib<name>Lib static
# archive. Link-time only, so they belong here beside libdcmqi.a.
%{_libdir}/lib*Lib.a
    rm -f %{buildroot}%{_prefix}/lib/libdcmqi.a
    rmdir --ignore-fail-on-non-empty %{buildroot}%{_prefix}/lib 2>/dev/null || :
fi
if [ -d %{buildroot}%{_prefix}/cmake ]; then
    mkdir -p %{buildroot}%{_libdir}/cmake/dcmqi
    mv %{buildroot}%{_prefix}/cmake/* %{buildroot}%{_libdir}/cmake/dcmqi/
    rmdir %{buildroot}%{_prefix}/cmake
fi

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
# Each CLI ships a SlicerExecutionModel .xml descriptor beside the binary -- that
# is how Slicer discovers a CLI module's parameters, so they belong with the CLIs.
%{_bindir}/*.xml


%files devel
# dcmqi hardcodes add_library(dcmqi STATIC ...) in libsrc/CMakeLists.txt -- there
# is no shared library and BUILD_SHARED_LIBS does not change that, so there is
# nothing for %%ldconfig_scriptlets to do and no libdcmqi.so.* to ship. The CLIs
# are the deliverable; the static lib and headers are for building against.
%{_includedir}/dcmqi/
%{_libdir}/libdcmqi.a
%{_libdir}/cmake/dcmqi/


%changelog
* Sun Aug 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.4-4
- Package the CLI .xml descriptors and the per-CLI lib*Lib.a archives -- both were
  installed but unpackaged. The .xml files are how Slicer discovers a CLI module's
  parameters; the lib*Lib.a archives are what SEMMacroBuildCLI builds each thin
  main() against.

* Sun Aug 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.4-3
- Relocate the library and cmake config in %%install: 1.5.4 ignores its own
  DCMQI_INSTALL_*_DIR variables. libsrc/CMakeLists.txt references them ZERO times
  and hardcodes "ARCHIVE DESTINATION lib"; the top level hardcodes
  "DESTINATION cmake". Passing them as STRING (-1) or PATH (-2) changed nothing --
  the files landed at /usr/lib and /usr/cmake both times. Move them in %%install
  instead, guarded so a version that does honour the variables (1.5.6 does) is
  unaffected.

* Sun Aug 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.4-2
- Fix %%files: dcmqi ships a STATIC library, not a shared one.
  -1 finally compiled and linked (dcmtk-3.7.0-3's OverlapUtil export did its job)
  and then failed packaging on "File not found: .../libdcmqi.so.*".
  libsrc/CMakeLists.txt hardcodes add_library(dcmqi STATIC ...); BUILD_SHARED_LIBS
  does not override it, so there is no libdcmqi.so at all -- ship libdcmqi.a in
  -devel and drop %%ldconfig_scriptlets, which had nothing to do.
  Also pass the three DCMQI_INSTALL_*_DIR overrides as PATH rather than STRING:
  as STRING they were ignored and the cmake config landed at /usr/cmake with the
  library at /usr/lib, instead of under %%{_libdir}.

* Sat Aug 01 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.4-1
- Target 1.5.4, not 1.5.6: 1.5.5+ needs an UNRELEASED DCMTK.
  dcmqi 1.5.5 bumped its pinned DCMTK to git 5708ba6 for the labelmap-background /
  Pixel Padding Value work, which introduced DcmSegmentation::setBackgroundPixelValue.
  That method exists in no DCMTK release: 3.7.0 is upstream's newest tag and this COPR
  already ships it (Fedora is still on 3.6.9), and the build fails with
  "class DcmSegmentation has no member named setBackgroundPixelValue".
  Building 1.5.6 would therefore mean shipping a git-snapshot DCMTK as a system
  library that 3dslicer, ITK-SNAP and MITK all link -- a much larger decision than a
  dcmqi bump, and one to take deliberately rather than as a side effect.
  1.5.4 is the newest release that builds against a released DCMTK (verified: it makes
  no setBackgroundPixelValue call) and it still has the same CLI set, the same
  versioned install dirs and the same git version machinery, so every fix in -1..-5
  carries over unchanged.
  Revisit if DCMTK cuts a release containing 5708ba6.

* Fri Jul 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.6-5
- Synthesize a git repo in %%prep so the version target can run. dcmqi derives its
  version metadata from git with no tarball fallback: dcmqiVersion.cmake calls
  GIT_WC_INFO() unconditionally and dcmqiConfigureVersionTarget.cmake FATAL_ERRORs if
  any of DCMQI_{VERSION_DATE,VERSION_QUALIFIER,WC_REVISION,WC_URL,WC_TAG} is undefined.
  A release tarball has no .git, so -3 died with "DCMQI_WC_REVISION is mandatory"
  after silently falling back to DCMQI_VERSION=0.0.0.
  Rather than patch upstream's version logic, give it the repo it insists on: one
  commit tagged v%%{version} (so is_release is detected and the version qualifier stays
  empty) plus an origin remote. Deterministic -- author/committer identity and both
  dates come from SOURCE_DATE_EPOCH, so the commit hash is reproducible.
  Verified by running dcmqiConfigureVersionTarget.cmake standalone against the
  synthesized tree: "building a release - yes (found tags v1.5.6)", DCMQI_VERSION
  [1.5.6], WC_REVISION/WC_TAG/WC_URL all populated.

* Fri Jul 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.6-4
- Add BuildRequires: git-core. dcmqiConfigureVersionTarget.cmake does
  find_package(Git REQUIRED) at configure time to stamp a version string. Third and
  hopefully last layer of a buildroot that had never been satisfiable: the fabricated
  itkjsonkit-devel masked the missing SlicerExecutionModel, which in turn masked
  this.

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
