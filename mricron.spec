%global debug_package %{nil}
%global commit_date 20250101
%global git_commit master

Name:           mricron
Version:        1.2.%{commit_date}
Release:        2%{?dist}
Summary:        Medical image visualization and analysis (Lazarus/Qt5)

License:        BSD-2-Clause
URL:            https://github.com/neurolabusc/MRIcron
Source0:        https://github.com/neurolabusc/MRIcron/archive/%{git_commit}/%{name}-%{version}.tar.gz

BuildRequires:  lazarus >= 2.0
BuildRequires:  fpc
BuildRequires:  fpc-src
BuildRequires:  qt5pas-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  lazarus-lcl-qt5
BuildRequires:  dos2unix

Requires:       qt5pas
Requires:       dcm2niix

%description
MRIcron is a cross-platform NIfTI format image viewer. It allows viewing
multiple layers of images, generating volume renderings, and drawing volumes
of interest (VOI). This is the native compiled version built with Lazarus
and Qt5.

%prep
%autosetup -n MRIcron-%{git_commit}

# 1. Fix Line Endings (CRLF -> LF)
find . -type f \( -name "*.ini" -o -name "*.lut" -o -name "*.txt" -o -name "*.md" \) -exec dos2unix {} \;

# 2. Fix Permissions (remove executable bit from non-binaries)
find . -type f -exec chmod 644 {} \;

%build
# Re-enable execute on the project file so lazbuild can read it
chmod 644 mricron.lpi
lazbuild -B --ws=qt5 mricron.lpi

%install
rm -rf %{buildroot}

# 1. Prepare directories
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps

# 2. Install Binary
install -m 755 MRIcron %{buildroot}%{_libexecdir}/%{name}/%{name}

# 3. Install Resources
cp -r render %{buildroot}%{_libexecdir}/%{name}/
cp -r Resources/templates %{buildroot}%{_libexecdir}/%{name}/
cp -r Resources/lut %{buildroot}%{_libexecdir}/%{name}/
cp *.txt %{buildroot}%{_libexecdir}/%{name}/

# 4. Create Wrapper Script
cat > %{buildroot}%{_bindir}/%{name} <<EOF
#!/bin/bash
exec %{_libexecdir}/%{name}/%{name} "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/%{name}

# 5. Symlink dcm2niix (Relative path fix)
ln -s ../../bin/dcm2niix %{buildroot}%{_libexecdir}/%{name}/dcm2niix

# 6. Install Desktop Entry
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=MRIcron
Comment=Medical Image Viewer
Exec=%{name}
Icon=%{name}
Terminal=false
Type=Application
Categories=Science;MedicalSoftware;
EOF

# 7. Install Icon
install -m 644 mricron.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

%files
%license license.txt
%doc README.md
%{_bindir}/%{name}
%{_libexecdir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

%changelog
* Sun Jan 04 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.20250101-2
- Fix permissions on templates and LUTs
- Fix line endings (dos2unix) for docs and config files
- Use relative symlink for dcm2niix to satisfy rpmlint

* Sun Jan 04 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.20250101-1
- Initial RPM release built with Lazarus and Qt5
