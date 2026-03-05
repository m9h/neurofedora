Name:           open-ephys-gui
Version:        0.6.4
# Note: Check upstream for the latest tag. 0.6.x is stable, 1.0 is in beta/recent release.
Release:        1%{?dist}
Summary:        Open source software for extracellular electrophysiology

License:        GPL-3.0-or-later
URL:            https://open-ephys.org/
Source0:        https://github.com/open-ephys/plugin-GUI/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  zeromq-devel
BuildRequires:  hdf5-devel
BuildRequires:  libcurl-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  freetype-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXrandr-devel
BuildRequires:  webkit2gtk4.1-devel

# It uses the JUCE framework (often bundled, but good to know)

%description
The Open Ephys GUI is designed to provide a fast and flexible interface for
acquiring and visualizing data from extracellular electrodes. It features a
plugin architecture that makes it easy to add new modules for processing data
and interfacing with external hardware.

%package        devel
Summary:        Development files for Open Ephys plugins
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and libraries required to build plugins for the Open Ephys GUI.

%prep
%setup -q -n plugin-GUI-%{version}

# FIX: Force CMake to use webkit2gtk-4.1 instead of 4.0
sed -i 's/webkit2gtk-4.0/webkit2gtk-4.1/g' CMakeLists.txt

# Fix permissions or remove bundled libs if necessary
# (The GUI often bundles JUCE. Unbundling JUCE is very hard, 
# so usually acceptable to build with the bundled version for complex audio apps)

%build
%cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DOE_DONT_CHECK_BUILD_PATH=ON \
    -DOPENEPHYS_UNIFIED_BUILD=ON

%cmake_build

%install
cd Build
%cmake_install

# Handle the binary installation location if CMake installs to /usr/local
# Sometimes custom CMake scripts behave badly.
# If the binary ends up in /usr/bin/open-ephys, great. 

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/open-ephys.desktop <<EOF
[Desktop Entry]
Name=Open Ephys GUI
Comment=Electrophysiology Acquisition System
Exec=open-ephys
Icon=open-ephys
Terminal=false
Type=Application
Categories=Science;DataVisualization;
EOF

%files
%license LICENSE
%doc README.md
%{_bindir}/open-ephys
%{_libdir}/open-ephys/
%{_datadir}/applications/open-ephys.desktop

%files devel
%{_includedir}/open-ephys/

%changelog
* Wed Jan 07 2026 m9h <mhough@morgans> - 0.6.4-1
- Initial packaging for NeuroFedora-Species
