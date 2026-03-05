%global commit      d853f053d83aa8098caeddc001d276c3c5ecf8f4
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date        20260104
# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the
# debuginfo stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

Name:           mricrogl
# Using the date as the version is common for untagged scientific software
Version:        1.2.%{date}
Release:        2.git%{shortcommit}%{?dist}
Summary:        GL-accelerated medical image viewer with Python scripting

License:        BSD-2-Clause
URL:            https://github.com/rordenlab/MRIcroGL
# Download the archive for the specific commit, save as name-shortcommit.tar.gz
Source0:        %{url}/archive/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz

BuildRequires:  lazarus >= 2.0
BuildRequires:  fpc
BuildRequires:  fpc-src
BuildRequires:  qt5pas-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  lazarus-lcl-qt5
BuildRequires:  python3-devel
BuildRequires:  dos2unix
BuildRequires:  desktop-file-utils

Requires:       qt5pas
Requires:       python3-libs
Requires:       dcm2niix
Requires:       hicolor-icon-theme

%description
MRIcroGL is a cross-platform NIfTI format image viewer that uses your graphics
card's hardware acceleration (OpenGL) to provide interactive volume rendering.
It includes embedded Python scripting for automated analysis.

%prep
# GitHub commit archives extract to RepoName-FullCommitHash
%autosetup -n MRIcroGL-%{commit}

# 1. Clean up Permissions & Line Endings
find . -type f \( -name "*.ini" -o -name "*.lut" -o -name "*.txt" -o -name "*.py" -o -name "*.glsl" \) -exec dos2unix {} \;
find . -type f -exec chmod 644 {} \;

%build
# 1. Dynamically locate the source root
PROJECT_FILE=$(find . -name "MRIcroGL.lpi" -print -quit)
SOURCE_DIR=$(dirname "$PROJECT_FILE")

# 2. Dynamically determine Python version and linker flags
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_LIBS=$(python3-config --libs)

# 3. FIX: Link against system python instead of bundled static lib
sed -i "s|{\$linklib ./PythonBridge/x86_64-linux/libpython3.7m.a}|{\$linklib python${PY_VER}}|" "$SOURCE_DIR/mainunit.pas"

# 4. Inject flags into the .lpi project file
#    -Cg: generate PIC code
#    -k-no-pie: disable PIE to avoid conflict with non-PIC FPC RTL
sed -i "s|<CustomOptions Value=\"|<CustomOptions Value=\"-Cg -k-no-pie |" "$PROJECT_FILE"

# 5. Build
lazbuild \
    --lazarusdir=%{_libdir}/lazarus \
    --ws=qt5 \
    "$PROJECT_FILE"

%install
rm -rf %{buildroot}

# 1. Prepare Directories
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps

# 2. Install Binary
install -m 755 MRIcroGL %{buildroot}%{_libexecdir}/%{name}/%{name}

# 3. Install Resources
# Copy all resources
cp -r Resources/* %{buildroot}%{_libexecdir}/%{name}/

# CLEANUP: Remove bundled artifacts that confuse Linux packaging
rm -rf %{buildroot}%{_libexecdir}/%{name}/python37
rm -rf %{buildroot}%{_libexecdir}/%{name}/*.bat
rm -rf %{buildroot}%{_libexecdir}/%{name}/*.command

# Copy docs
cp *.txt %{buildroot}%{_libexecdir}/%{name}/

# 4. Create Wrapper Script
cat > %{buildroot}%{_bindir}/%{name} <<EOF
#!/bin/bash
exec %{_libexecdir}/%{name}/%{name} "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/%{name}

# 5. Symlink dcm2niix (Relative path validation)
# Target: /usr/libexec/mricrogl/dcm2niix -> ../../bin/dcm2niix -> /usr/bin/dcm2niix
ln -s ../../bin/dcm2niix %{buildroot}%{_libexecdir}/%{name}/dcm2niix

# 6. Desktop Entry
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=MRIcroGL
Comment=Advanced Medical Image Viewer
Exec=%{name}
Icon=%{name}
Terminal=false
Type=Application
Categories=Science;MedicalSoftware;
EOF

# 7. Install Icon
install -m 644 mricrogl.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%license license.txt
%doc README.md
%{_bindir}/%{name}
%{_libexecdir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

%changelog
* Thu Feb 26 2026 Morgan Hough <morgan@example.com> - 1.2.20260104-2.gitd853f05
- Switch debug_package suppression from global to define scope; fixes EPEL 9
  SRPM rebuild failure caused by auto-injected debuginfo stanza

* Sun Jan 04 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.20260104-1.gitd853f05
- Initial RPM release for MRIcroGL
