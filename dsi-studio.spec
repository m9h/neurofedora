Name:           dsi-studio
Version:        2025.01
Release:        4%{?dist}
Summary:        A Tractography Tool for Diffusion MRI
License:        MPLv2.0
URL:            https://dsi-studio.labsolver.org/
Source0:        https://github.com/frankyeh/DSI-Studio/archive/master.tar.gz#/DSI-Studio-%{version}.tar.gz
Source1:        https://github.com/frankyeh/TIPL/archive/master.tar.gz#/TIPL-master.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtcharts-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  boost-devel
BuildRequires:  zlib-devel
BuildRequires:  hdf5-devel
BuildRequires:  openblas-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libatomic

Requires:       qt5-qtbase
Requires:       qt5-qtcharts
Requires:       qt5-qtsvg

%description
DSI Studio is a tractography software tool that maps brain connections
and correlates findings with neuropsychological disorders.

%prep
# 1. Unpack main source
%setup -q -n DSI-Studio-master

# 2. Unpack TIPL source
%setup -q -T -D -a 1 -n DSI-Studio-master

# 3. Setup TIPL
# Rename the extracted TIPL-master folder to 'tipl'
if [ -d "TIPL-master" ]; then
    mv TIPL-master tipl
else
    # Fallback search
    TIPL_DIR=$(find . -maxdepth 1 -type d -name "TIPL*" | head -n 1)
    if [ -n "$TIPL_DIR" ]; then
        mv "$TIPL_DIR" tipl
    fi
fi

%build
mkdir build
cd build

# 4. GENERATE MISSING PROJECT FILE
# The upstream repo is missing dsi_studio.pro, so we create it.
cat <<EOF > dsi_studio.pro
TEMPLATE = app
TARGET = dsi_studio
QT += core gui widgets network charts svg printsupport opengl concurrent
CONFIG += c++17 release

# Include Paths
INCLUDEPATH += .. ../tipl

# Recursively add all source files from the parent directory
SOURCES += \$\$files(../*.cpp, true)
HEADERS += \$\$files(../*.h, true) \$\$files(../*.hpp, true)
FORMS += \$\$files(../*.ui, true)
RESOURCES += \$\$files(../*.qrc, true)

# Exclude CUDA files (CPU build) and build dir artifacts
SOURCES -= \$\$files(../cuda/*.cpp, true)
SOURCES -= \$\$files(./*.cpp, true)

# Link Libraries
LIBS += -lz -lhdf5 -lopenblas -lboost_system -lboost_filesystem
EOF

echo "Generated dsi_studio.pro with recursive file inclusion."

# 5. Build
%{qmake_qt5} dsi_studio.pro CONFIG+=release
make %{?_smp_mflags}

%install
cd build
install -d %{buildroot}%{_bindir}
install -m 755 dsi_studio %{buildroot}%{_bindir}/dsi-studio

# Install Desktop File
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/dsi-studio.desktop <<EOF
[Desktop Entry]
Name=DSI Studio
Comment=Diffusion MRI Analysis Tool
Exec=dsi-studio
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Science;Medical;Education;Qt;
EOF

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/dsi-studio.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/dsi-studio
%{_datadir}/applications/dsi-studio.desktop

%changelog
* Tue Jan 06 2026 User <user@example.com> - 2025.01-4
- Generated dsi_studio.pro dynamically to fix upstream missing file
