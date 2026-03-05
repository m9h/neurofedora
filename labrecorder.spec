Name:           labrecorder
Version:        1.16.4
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
* Wed Jan 07 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.4-1
- Initial RPM package for LabRecorder 1.16.4
