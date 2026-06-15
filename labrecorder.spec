Name:           labrecorder
Version:        1.17.1
Release:        1%{?dist}
Summary:        Default recording program for the Lab Streaming Layer (LSL)

License:        MIT
URL:            https://github.com/labstreaminglayer/App-LabRecorder
Source0:        %{url}/archive/v%{version}/App-LabRecorder-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
# 1.17.x migrated the GUI from Qt5 to Qt6 (find_package(Qt6 REQUIRED ...)).
BuildRequires:  qt6-qtbase-devel
BuildRequires:  boost-devel
BuildRequires:  chrpath
# 1.17.1 CMakeLists self-includes "${LSL_DIR}/LSLCMake.cmake" once
# find_package(LSL) succeeds; liblsl >= 1.17.7-2 ships LSLCMake.cmake there.
BuildRequires:  liblsl-devel >= 1.17.7
BuildRequires:  desktop-file-utils

Requires:       liblsl%{?_isa} >= 1.17.7
Requires:       hicolor-icon-theme

%description
The LabRecorder is the default recording program that comes with LSL.
It allows recording of all streams on the lab network (or a subset)
into a single file (XDF format), with time synchronization between streams.

%prep
%autosetup -p1 -n App-LabRecorder-%{version}

# NOTE: 1.17.x reworked the liblsl discovery. The CMakeLists now resolves
# liblsl with find_package(LSL QUIET ...) and, on success, includes the
# macros file itself: include("${LSL_DIR}/LSLCMake.cmake") (CMakeLists.txt
# line ~105). liblsl >= 1.17.7-2 ships LSLCMake.cmake at ${LSL_DIR}
# (/usr/lib64/cmake/lsl), so installLSLApp()/installLSLAuxFiles() resolve
# with no help from us. The old %%prep injection that appended ${LSL_DIR}
# to CMAKE_MODULE_PATH and did include(LSLCMake) is now obsolete AND broke
# %%prep (its regex no longer matched the restructured file) — dropped.

%build
# LABRECORDER_BUILD_GUI defaults ON and pulls Qt6 (auto-found in
# %{_libdir}/cmake/Qt6). The old LSLAPPS_LabRecorder / Qt5_DIR flags were
# removed upstream in the 1.17.x Qt6 migration.
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release

%cmake_build

%install
%cmake_install

# 1.17.x calls LSL_install_liblsl(DESTINATION ${INSTALL_LIBDIR}) which copies
# the resolved liblsl (liblsl.so.*) into our libdir for redistribution. On
# Fedora liblsl is provided by the liblsl package (a Requires), so drop the
# bundled copy to avoid duplicate-ownership / unpackaged-file errors.
rm -f %{buildroot}%{_libdir}/liblsl.so*

# installLSLApp() / installLSLAuxFiles() from liblsl >= 1.17.7-2 place
# binaries in %{_bindir}, libxdfwriter.so in %{_libdir}, and aux files
# (LabRecorder.cfg, LICENSE, README.md) in %{_datadir}/LabRecorder/.
# Strip the duplicate LICENSE/README — we ship them via %license/%doc
# from the source tree instead.
rm -f %{buildroot}%{_datadir}/LabRecorder/LICENSE
rm -f %{buildroot}%{_datadir}/LabRecorder/README.md

# Create Desktop Entry
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=LabRecorder
Comment=Record Lab Streaming Layer (LSL) data streams
Exec=LabRecorder
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=Science;DataVisualization;
EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# 7. Remove RPATHs (The binaries now look in system folders)
chrpath --delete %{buildroot}%{_bindir}/LabRecorder
chrpath --delete %{buildroot}%{_bindir}/LabRecorderCLI

%files
%license LICENSE
%doc README.md
%{_bindir}/LabRecorder
%{_bindir}/LabRecorderCLI
%{_libdir}/libxdfwriter.so*
%{_datadir}/applications/%{name}.desktop
%dir %{_datadir}/LabRecorder
%{_datadir}/LabRecorder/LabRecorder.cfg

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 1.17.1-1
- Update to 1.17.1 (current upstream; freshness sweep 2026-06-14).
- Drop the obsolete %%prep LSLCMake injection: 1.17.x reworked liblsl
  discovery and the CMakeLists now self-includes "${LSL_DIR}/LSLCMake.cmake"
  on a successful find_package(LSL). The old python regex no longer matched
  and was failing %%prep. Bump liblsl floor to 1.17.7 (ships LSLCMake.cmake
  at ${LSL_DIR}, which upstream's include() now relies on).
- Migrate Qt5 -> Qt6: 1.17.x switched the GUI to find_package(Qt6 REQUIRED).
  Swap qt5-qtbase-devel -> qt6-qtbase-devel and drop the obsolete
  -DLSLAPPS_LabRecorder / -DQt5_DIR cmake flags (LABRECORDER_BUILD_GUI is ON
  by default; Qt6 is auto-found).
- Drop /usr/bin/testxdfwriter from %%files: 1.17.x no longer installs the
  xdfwriter test helper.
- Strip the bundled liblsl.so.* that LSL_install_liblsl() copies into our
  libdir: liblsl is provided by the liblsl package, not vendored here.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.4-5
- Drop the manual /usr/LabRecorder/ → /usr/{bin,lib64,etc} mv block.
  With liblsl 1.17.7-2 shipping LSLCMake.cmake, installLSLApp() now
  resolves and places binaries and libs in standard paths directly;
  the rescue moves became stale (and broke -4 install: "mv: cannot
  stat '/usr/LabRecorder/LabRecorder'"). Move LabRecorder.cfg to
  %%{_datadir}/LabRecorder/ (where installLSLAuxFiles puts it) and
  strip duplicate LICENSE/README that the same helper installs.
  Add /usr/bin/testxdfwriter to %%files.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.4-4
- Append ${LSL_DIR} to CMAKE_MODULE_PATH before include(LSLCMake) — the
  -3 attempt assumed find_package(LSL) extended CMAKE_MODULE_PATH but
  LSLConfig.cmake is an auto-generated target-export file that only
  defines LSL::lsl; it never touches the module path. Result: -3 build
  10517252 failed with "include could not find requested file: LSLCMake".

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.4-3
- Rewrite the include(LSLCMake) injection in Python: the previous
  sed range matched the WRONG endif() and inserted the include
  before find_package(LSL), so LSLCMake.cmake couldn't be found.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.4-2
- Inject include(LSLCMake) after find_package(LSL): standalone builds need
  the macros file loaded explicitly (only auto-loaded by the parent liblsl
  tree). Provides installLSLApp/installLSLAuxFiles used at CMakeLists.txt:99.
* Wed Jan 07 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.4-1
- Initial RPM package for LabRecorder 1.16.4
