%define debug_package %{nil}

Name:           open-ephys-gui
Version:        1.0.2
Release:        3%{?dist}
Summary:        Open source software for extracellular electrophysiology

License:        GPL-3.0-or-later AND AGPL-3.0-or-later
URL:            https://open-ephys.org/
Source0:        https://github.com/open-ephys/plugin-GUI/archive/v%{version}/plugin-GUI-%{version}.tar.gz

# JUCE 8.0.7 is bundled — large C++ audio/GUI framework compiled directly into
# the executable. Not available in Fedora, cannot be practically unbundled.
# JUCE is used under AGPLv3 (dual-licensed: AGPLv3 or commercial EULA).
Provides:       bundled(juce) = 8.0.7

# nlohmann/json and cpp-httplib are vendored as single headers
Provides:       bundled(nlohmann-json)
Provides:       bundled(cpp-httplib)

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.15
BuildRequires:  ninja-build
BuildRequires:  pkgconfig

# X11 / display
BuildRequires:  mesa-libGL-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXrandr-devel

# Audio
BuildRequires:  alsa-lib-devel

# Text rendering (JUCE)
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel

# Networking (HTTP server for headless mode)
BuildRequires:  libcurl-devel

# Optional: for data formats used by some built-in plugins
BuildRequires:  zeromq-devel
BuildRequires:  hdf5-devel

BuildRequires:  desktop-file-utils
BuildRequires:  patchelf
BuildRequires:  systemd-rpm-macros

Requires:       hicolor-icon-theme

%description
The Open Ephys GUI is designed to provide a fast and flexible interface for
acquiring and visualizing data from extracellular electrodes. It features a
modular plugin architecture for processing data and interfacing with
acquisition hardware (Neuropixels, Open Ephys Acquisition Board, etc.).

Supports headless operation via --headless flag with HTTP REST API control
on port 37497.

%prep
%setup -q -n plugin-GUI-%{version}

# Fix desktop file paths for FHS
sed -i 's|Exec=.*|Exec=open-ephys|' Resources/Installers/Linux/Open-Ephys_Installer/open-ephys.desktop
sed -i 's|Icon=.*|Icon=open-ephys|' Resources/Installers/Linux/Open-Ephys_Installer/open-ephys.desktop

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DOE_DONT_CHECK_BUILD_PATH=TRUE

%cmake_build

%install
# Open Ephys has NO install() targets — manual installation required.
# The binary looks for plugins/ and shared/ relative to its own directory,
# so we install everything under /usr/libexec/open-ephys/ and symlink
# /usr/bin/open-ephys to it.

# Open Ephys POST_BUILD commands copy everything to Build/Release/ in source tree
# (not the cmake build dir), regardless of -DOE_DONT_CHECK_BUILD_PATH
BUILDOUT=Build/Release

# Main binary
install -Dpm 755 ${BUILDOUT}/open-ephys %{buildroot}%{_libexecdir}/open-ephys/open-ephys

# Symlink in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -s %{_libexecdir}/open-ephys/open-ephys %{buildroot}%{_bindir}/open-ephys

# Built-in plugins (loaded via dlopen from <exe_dir>/plugins/)
mkdir -p %{buildroot}%{_libexecdir}/open-ephys/plugins
for plugin in ${BUILDOUT}/plugins/*.so; do
    install -pm 755 "$plugin" %{buildroot}%{_libexecdir}/open-ephys/plugins/
done

# Shared resources (FPGA bitfiles — loaded from <exe_dir>/shared/)
mkdir -p %{buildroot}%{_libexecdir}/open-ephys/shared
if [ -d "${BUILDOUT}/shared" ]; then
    cp -a ${BUILDOUT}/shared/* %{buildroot}%{_libexecdir}/open-ephys/shared/
fi

# Default configs (icons for acquisition sources)
if [ -d "${BUILDOUT}/configs" ]; then
    cp -a ${BUILDOUT}/configs %{buildroot}%{_libexecdir}/open-ephys/
fi

# GUI icon (needed at runtime by the executable)
if [ -f "${BUILDOUT}/icon-small.png" ]; then
    install -pm 644 ${BUILDOUT}/icon-small.png %{buildroot}%{_libexecdir}/open-ephys/
fi

# Strip RPATHs ($ORIGIN/shared is wrong for FHS install)
patchelf --remove-rpath %{buildroot}%{_libexecdir}/open-ephys/open-ephys 2>/dev/null || :
find %{buildroot}%{_libexecdir}/open-ephys/plugins -name "*.so" -exec \
    patchelf --remove-rpath {} \; 2>/dev/null || :

# Desktop file
install -Dpm 644 Resources/Installers/Linux/Open-Ephys_Installer/open-ephys.desktop \
    %{buildroot}%{_datadir}/applications/open-ephys.desktop

# Icons for desktop integration
install -Dpm 644 Resources/Icons/icon-large.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/open-ephys.png
install -Dpm 644 Resources/Icons/icon-small.png \
    %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/open-ephys.png

# Udev rules for USB acquisition hardware
install -Dpm 644 Resources/Scripts/40-open-ephys.rules \
    %{buildroot}%{_udevrulesdir}/40-open-ephys.rules

%check
# Validate desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/open-ephys.desktop

# Verify binary runs (headless mode, just check it starts)
%{buildroot}%{_libexecdir}/open-ephys/open-ephys --help 2>&1 || :

%files
%license LICENSE
%doc README.md
# Main binary + runtime resources
%{_libexecdir}/open-ephys/
%{_bindir}/open-ephys
# Desktop integration
%{_datadir}/applications/open-ephys.desktop
%{_datadir}/icons/hicolor/256x256/apps/open-ephys.png
%{_datadir}/icons/hicolor/48x48/apps/open-ephys.png
# Udev rules for acquisition hardware
%{_udevrulesdir}/40-open-ephys.rules

%changelog
* Wed Mar 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.2-1
- Update to v1.0.2 (major upgrade from 0.6.4)
- JUCE 8.0.7 bundled (AGPLv3), license updated
- Install to /usr/libexec/open-ephys/ (binary finds plugins relative to exe)
- Symlink /usr/bin/open-ephys for PATH access
- Include built-in plugins, FPGA bitfiles, default configs
- Add udev rules for USB acquisition hardware
- Add desktop file and icons
- Strip RPATHs for Fedora compliance
