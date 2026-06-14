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
BuildRequires:  qt5-qtbase-devel
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
# LSLAPPS_LabRecorder=ON ensures we build the main app.
# We point to the system Qt5 installation explicitly.
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DLSLAPPS_LabRecorder=ON \
    -DQt5_DIR=%{_libdir}/cmake/Qt5

%cmake_build

%install
%cmake_install

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
%{_bindir}/testxdfwriter
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
