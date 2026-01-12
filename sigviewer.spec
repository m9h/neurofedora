Name:           sigviewer
Version:        0.6.4
Release:        1%{?dist}
Summary:        Viewing and inspection of biosignals (EEG, EMG, ECG)
License:        GPL-3.0-or-later
URL:            https://github.com/cbrnr/sigviewer
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
# Use the QMake build system for Qt5
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  boost-devel

# Link against system libraries
BuildRequires:  liblsl-devel
BuildRequires:  libxdf-devel
BuildRequires:  biosig4c++-devel

Requires:       qt5-qtbase
Requires:       qt5-qtsvg

%description
SigViewer is a powerful viewing and scoring application for biosignals. 
It supports various data formats (including XDF, GDF, EDF, BDF).

%prep
%setup -q

# --- PATCHING ---
# 1. Remove internal library paths to force system linking
sed -i '/\$\$PWD\/external\/include/d' sigviewer.pro
sed -i '/\$\$PWD\/external\/lib/d' sigviewer.pro

# 2. Clean up existing hardcoded links in the .pro file
sed -i 's/-lbiosig//g' sigviewer.pro
sed -i 's/-lxdf//g' sigviewer.pro
sed -i 's/-llsl//g' sigviewer.pro

# 3. Manually link System Libraries
# We do NOT use PKGCONFIG here because your custom builds likely
# didn't generate .pc files for liblsl or libxdf.
# We explicitly link them, assuming they are in standard /usr/lib64.

echo "LIBS += -lbiosig -llsl -lxdf" >> sigviewer.pro

# Note: We do NOT add "PKGCONFIG += ..." lines for these.

%build
# We explicitly link against the system libraries here
# qmake-qt5 handles the Makefile generation
%qmake_qt5 \
    "INCLUDEPATH += %{_includedir}" \
    "LIBS += -L%{_libdir} -lxdf -lbiosig" \
    sigviewer.pro

%make_build

%install
# Create directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps

# Install the binary
# (We verify both potential output locations to be safe)
if [ -f bin/release/sigviewer ]; then
    install -m 0755 bin/release/sigviewer %{buildroot}%{_bindir}/sigviewer
else
    install -m 0755 bin/sigviewer %{buildroot}%{_bindir}/sigviewer
fi

# Install the desktop file (Found in deploy/debian)
install -m 644 deploy/debian/sigviewer.desktop %{buildroot}%{_datadir}/applications/sigviewer.desktop

# Install the icon (Found in the root directory)
install -m 644 sigviewer.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/sigviewer.svg

%files
%license LICENSE
%doc README.md
%{_bindir}/sigviewer
%{_datadir}/applications/sigviewer.desktop
%{_datadir}/icons/hicolor/scalable/apps/sigviewer.svg

%changelog
* Wed Jan 07 2026 Your Name <your.email@example.com> - 0.6.4-1
- Initial package for Fedora
- Switched to QMake build system
- Patched to link against system libxdf and biosig4c++
