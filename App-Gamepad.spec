%global commit 6771a03989ad2b1b38bac0bd0454d202359dc147
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260602

Name:           App-Gamepad
Version:        1.16.1
Release:        1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Stream gamepad (Xbox controller) state over the Lab Streaming Layer (LSL)

License:        MIT
URL:            https://github.com/labstreaminglayer/App-Gamepad
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  liblsl-devel >= 1.17.7
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  qt5-qtgamepad-devel

Requires:       liblsl%{?_isa} >= 1.17.7
Requires:       qt5-qtgamepad%{?_isa}
Requires:       hicolor-icon-theme

%description
GamepadLSL streams Xbox-style controller analog stick positions and button
events over the Lab Streaming Layer (LSL).  Built on top of Qt5 Quick (QML)
and qt5-qtgamepad, it is one of the standard input apps maintained by the
labstreaminglayer project.

%prep
%autosetup -p1 -n %{name}-%{commit}

# Inject include(LSLCMake) so installLSLApp() resolves.  Same reasoning as
# the labrecorder spec: LSLConfig.cmake does not touch CMAKE_MODULE_PATH.
python3 -c '
import re
with open("CMakeLists.txt") as f:
    text = f.read()
m = re.search(r"find_package\(LSL REQUIRED.*?\)\n", text, re.DOTALL)
if m is None:
    raise SystemExit("could not find find_package(LSL ...) block")
patch = ("\nlist(APPEND CMAKE_MODULE_PATH \"${LSL_DIR}\")\n"
         "include(LSLCMake)\n")
text = text[:m.end()] + patch + text[m.end():]
with open("CMakeLists.txt", "w") as f:
    f.write(text)
'

# Drop the WIN32 marker on the executable target (Qt sources reference
# windows-specific subsystem; harmless on Linux but suppress the warning).

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON

%cmake_build

%install
%cmake_install

chrpath --delete %{buildroot}%{_bindir}/GamepadLSL 2>/dev/null || :

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=GamepadLSL
Comment=Stream gamepad state over LSL
Exec=GamepadLSL
Icon=input-gaming
Terminal=false
Type=Application
Categories=Science;Game;
EOF

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/GamepadLSL
%{_datadir}/applications/%{name}.desktop

%changelog
* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.1-1.20260602git6771a03
- Initial RPM package for App-Gamepad / GamepadLSL (master commit 6771a03).
- Injects include(LSLCMake) after find_package(LSL) so installLSLApp() resolves.
