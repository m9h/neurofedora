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

# Move binaries from /usr/LabRecorder to /usr/bin
mkdir -p %{buildroot}%{_bindir}
mv %{buildroot}/usr/LabRecorder/LabRecorder %{buildroot}%{_bindir}/
mv %{buildroot}/usr/LabRecorder/LabRecorderCLI %{buildroot}%{_bindir}/

# Move Libraries (The Fix!)
mkdir -p %{buildroot}%{_libdir}
mv %{buildroot}/usr/LabRecorder/*.so* %{buildroot}%{_libdir}/

# Move the configuration file to /etc or share (optional, but cleaner)
# For now, let's just keep it where the app expects it or delete the empty dir
# If the app strictly requires the config next to the binary, we might need a wrapper script.
# Assuming standard behavior for now:
rm -rf %{buildroot}/usr/LabRecorder

# Create a desktop entry 
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

# Validate the desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# Remove invalid RPATHs
chrpath --delete %{buildroot}%{_bindir}/LabRecorder
chrpath --delete %{buildroot}%{_bindir}/LabRecorderCLI

%files
%license LICENSE
%doc README.md
%{_bindir}/LabRecorder
%{_bindir}/LabRecorderCLI
%{_datadir}/applications/%{name}.desktop
%{_libdir}/libxdfwriter.so*

%changelog
* Wed Jan 07 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.4-1
- Initial RPM package for LabRecorder 1.16.4
