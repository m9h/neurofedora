Name:           neuromore-studio
Version:        1.7.3
Release:        1%{?dist}
Summary:        Biofeedback and Neurofeedback Software Platform
License:        Apache-2.0
URL:            https://github.com/neuromore/studio
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  clang
BuildRequires:  llvm
BuildRequires:  lld
BuildRequires:  make
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  glib2-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  libSM-devel
BuildRequires:  libX11-devel
BuildRequires:  libxcb-devel
BuildRequires:  xcb-util-devel
BuildRequires:  xcb-util-image-devel
BuildRequires:  xcb-util-keysyms-devel
BuildRequires:  xcb-util-renderutil-devel
BuildRequires:  xcb-util-wm-devel
BuildRequires:  expat-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  alsa-lib-devel
# Qt5 Dependencies
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtmultimedia-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qtconnectivity-devel
# System Libraries
BuildRequires:  brainflow-devel
BuildRequires:  libxdf-devel

%description
neuromore Studio is a visual programming environment for processing biosignals.

%prep
%autosetup -n studio-%{version} -p1

# --- FIX 1: RapidJSON (C++ Conformance) ---
sed -i 's|const SizeType length;|SizeType length;|g' deps/include/rapidjson/document.h

# --- FIX 2: Qt Tools Symlinks ---
mkdir -p deps/build/make/bin/linux-x64/
ln -sf /usr/bin/moc-qt5 deps/build/make/bin/linux-x64/qt-moc
ln -sf /usr/bin/uic-qt5 deps/build/make/bin/linux-x64/qt-uic
ln -sf /usr/bin/rcc-qt5 deps/build/make/bin/linux-x64/qt-rcc

# --- FIX 3: DELETE CONFLICTING HEADERS ---
rm -rf deps/include/Qt*
rm -rf deps/include/qt*
rm -rf deps/include/opencv*
rm -rf deps/include/brainflow*

# --- FIX 4: PATCH BRAINFLOW INCLUDES (AGGRESSIVE) ---
# Neuromore and the C++ headers expect "brainflow/utils/file.h", but we have "brainflow/file.h".
# We strip the subdirectory prefixes from all include statements.

# 1. Flatten "brainflow/cpp-package/" -> "brainflow/"
find src -type f \( -name "*.h" -o -name "*.cpp" \) -exec sed -i 's|brainflow/cpp-package/|brainflow/|g' {} +

# 2. Flatten "brainflow/utils/" -> "brainflow/"
find src -type f \( -name "*.h" -o -name "*.cpp" \) -exec sed -i 's|brainflow/utils/|brainflow/|g' {} +

# 3. Flatten "brainflow/board_controller/" -> "brainflow/"
find src -type f \( -name "*.h" -o -name "*.cpp" \) -exec sed -i 's|brainflow/board_controller/|brainflow/|g' {} +

# 4. Flatten "brainflow/data_handler/" -> "brainflow/"
find src -type f \( -name "*.h" -o -name "*.cpp" \) -exec sed -i 's|brainflow/data_handler/|brainflow/|g' {} +

# 5. Flatten "brainflow/ml/" -> "brainflow/"
find src -type f \( -name "*.h" -o -name "*.cpp" \) -exec sed -i 's|brainflow/ml/|brainflow/|g' {} +

# --- FIX 5: INJECT INCLUDES & DEFINES ---
find build/make -name "*.mk" -exec sed -i 's|-Werror||g' {} +
for mkfile in build/make/*.mk; do
    echo "INCLUDES += -I/usr/include/qt5 -I/usr/include/qt5/QtCore -I/usr/include/qt5/QtGui -I/usr/include/qt5/QtWidgets -I/usr/include/qt5/QtNetwork -I/usr/include/qt5/QtMultimedia -I/usr/include/qt5/QtBluetooth -I/usr/include/qt5/QtConnectivity -I%{_includedir}/brainflow -I%{_includedir}/libxdf" >> "$mkfile"
    echo "DEFINES += -DQT_CORE_LIB -DQT_GUI_LIB -DQT_WIDGETS_LIB -DQT_NETWORK_LIB -DQT_MULTIMEDIA_LIB -DQT_BLUETOOTH_LIB -DQT_CONNECTIVITY_LIB" >> "$mkfile"
done

%build
export CC=clang
export CXX=clang++

# Pass the Defines to the compiler flags as well
MY_FLAGS="-O3 -fPIC -std=c++17 -fpermissive -w \
  -DQT_CORE_LIB -DQT_GUI_LIB -DQT_WIDGETS_LIB \
  -DQT_NETWORK_LIB -DQT_MULTIMEDIA_LIB \
  -DQT_BLUETOOTH_LIB -DQT_CONNECTIVITY_LIB"

# Build
make MODE=release TARGET_OS=linux TARGET_ARCH=x64 Studio \
     CFLAGS="$MY_FLAGS" \
     CXXFLAGS="$MY_FLAGS"

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/neuromore
mkdir -p %{buildroot}%{_datadir}/applications

# Install Binary
find Bin -type f -executable -name "Studio" -exec install -m 755 {} %{buildroot}%{_bindir}/neuromore-studio \;

# Install Assets
cp -r Assets %{buildroot}%{_datadir}/neuromore/

# Desktop File
cat > %{buildroot}%{_datadir}/applications/neuromore-studio.desktop <<EOF
[Desktop Entry]
Name=neuromore Studio
Comment=Neurofeedback Platform
Exec=neuromore-studio
Icon=neuromore-studio
Terminal=false
Type=Application
Categories=Science;Medical;
EOF

%files
%license LICENSE
%doc README.md
%{_bindir}/neuromore-studio
%{_datadir}/neuromore/
%{_datadir}/applications/neuromore-studio.desktop

%changelog
* Wed Jan 07 2026 Your Name <your.email@example.com> - 1.7.3-1
- Initial package for Fedora
