Name:           labrecorder
Version:        1.16.4
Release:        3%{?dist}
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
# This will now be satisfied by the package you just installed
BuildRequires:  liblsl-devel >= 1.16.0 
BuildRequires:  desktop-file-utils

Requires:       liblsl%{?_isa} >= 1.16.0
Requires:       hicolor-icon-theme

%description
The LabRecorder is the default recording program that comes with LSL.
It allows recording of all streams on the lab network (or a subset)
into a single file (XDF format), with time synchronization between streams.

%prep
%autosetup -p1 -n App-LabRecorder-%{version}

# Upstream calls installLSLApp() (from LSLCMake.cmake) but only does
# find_package(LSL) — which loads LSLConfig.cmake but NOT LSLCMake.cmake.
# In the upstream dev tree the macros file is included implicitly via the
# parent liblsl CMakeLists.txt; standalone builds need an explicit include.
# Append `include(LSLCMake)` AFTER the find_package(LSL ...) endif() block
# (find_package adds the lsl cmake dir to CMAKE_MODULE_PATH so the include
# can find LSLCMake.cmake).
# Previous sed (range with /endif()/a) was matching the wrong endif().
# Use Python instead — find the exact line "endif()" that immediately
# follows the find_package(LSL ...) line.
python3 -c '
import re
with open("CMakeLists.txt") as f:
    text = f.read()
# Find the find_package(LSL REQUIRED ... endif() block
m = re.search(r"find_package\(LSL REQUIRED.*?endif\(\)\n", text, re.DOTALL)
if m is None:
    raise SystemExit("could not find find_package(LSL ...) endif() block")
insert_at = m.end()
patch = ("\n# Bring in installLSLApp() and friends (not auto-loaded by\n"
         "# LSLConfig.cmake). find_package(LSL) above puts the cmake dir\n"
         "# on CMAKE_MODULE_PATH; include() resolves from there.\n"
         "include(LSLCMake)\n")
new_text = text[:insert_at] + patch + text[insert_at:]
with open("CMakeLists.txt", "w") as f:
    f.write(new_text)
'

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

# 1. Create directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_sysconfdir}/labrecorder

# 2. Move Binaries to /usr/bin
mv %{buildroot}/usr/LabRecorder/LabRecorder %{buildroot}%{_bindir}/
mv %{buildroot}/usr/LabRecorder/LabRecorderCLI %{buildroot}%{_bindir}/

# 3. Move Libraries (libxdfwriter.so) to /usr/lib64
# Using a wildcard *.so* handles symlinks (so.1, so.1.0) automatically
mv %{buildroot}/usr/LabRecorder/*.so* %{buildroot}%{_libdir}/

# 4. Move Configuration to /etc/labrecorder
# (Check if the source installed a .cfg; if not, we rely on defaults)
if [ -f %{buildroot}/usr/LabRecorder/LabRecorder.cfg ]; then
    mv %{buildroot}/usr/LabRecorder/LabRecorder.cfg %{buildroot}%{_sysconfdir}/labrecorder/
fi

# 5. Cleanup the non-standard install dir
rm -rf %{buildroot}/usr/LabRecorder

# 6. Create Desktop Entry
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
# Conditionally own the config dir if we put stuff there
%dir %{_sysconfdir}/labrecorder
%{_sysconfdir}/labrecorder/*.cfg

%changelog

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
