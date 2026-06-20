%global commit      4cb2a42047ad6ac763349693a4dbf10513fa31ae
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20230612

Name:           App-Wiimote
Version:        0.2.0
Release:        1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Stream Nintendo Wii Remote buttons and motion over Lab Streaming Layer (LSL)

License:        MIT
URL:            https://github.com/labstreaminglayer/App-Wiimote
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  liblsl-devel >= 1.17.7
BuildRequires:  qt6-qtbase-devel
# De-vendored: the bundled FetchContent(wiiuse) is replaced with the system lib.
BuildRequires:  wiiuse-devel

Requires:       liblsl%{?_isa} >= 1.17.7
Requires:       hicolor-icon-theme

%description
Wiimote is a Lab Streaming Layer (LSL) connector that pairs with a Nintendo
Wii Remote over Bluetooth (via wiiuse) and streams its button states and
accelerometer/IR motion data as LSL outlets, for synchronized recording
alongside other biosignal streams.

%prep
%autosetup -p1 -n %{name}-%{commit}

# Patch CMakeLists.txt:
#  1. Inject include(LSLCMake) after find_package(LSL) so installLSLApp() resolves
#     (LSLConfig.cmake does not touch CMAKE_MODULE_PATH).
#  2. De-vendor wiiuse: replace the network FetchContent clone (forbidden in
#     mock/COPR, and Fedora policy) with the system wiiuse-devel via find_library/
#     find_path; link ${WIIUSE_LIBRARY}; drop WIIUSE_STATIC (system lib is shared).
python3 - <<'PY'
import re
src = open("CMakeLists.txt").read()

# 1. LSLCMake
m = re.search(r"find_package\(LSL REQUIRED.*?\)\n", src, re.DOTALL)
if not m:
    raise SystemExit("find_package(LSL ...) not found")
src = (src[:m.end()]
       + '\nlist(APPEND CMAKE_MODULE_PATH "${LSL_DIR}")\ninclude(LSLCMake)\n'
       + src[m.end():])

# 2a. Replace the whole FetchContent(wiiuse) block (incl. the BUILD_SHARED_LIBS
#     override) with a system-library lookup.
fetch = re.search(
    r"(set\(BUILD_SHARED_LIBS OFF.*?\)\n)?include\(FetchContent\).*?FetchContent_MakeAvailable\(wiiuse\)\n",
    src, re.DOTALL)
if not fetch:
    raise SystemExit("wiiuse FetchContent block not found")
src = (src[:fetch.start()]
       + 'find_library(WIIUSE_LIBRARY NAMES wiiuse REQUIRED)\n'
         'find_path(WIIUSE_INCLUDE_DIRS NAMES wiiuse.h REQUIRED)\n'
       + src[fetch.end():])

# 2b. Link the system library object instead of the removed bundled target.
src = src.replace("\n        wiiuse\n", "\n        ${WIIUSE_LIBRARY}\n")

# 2c. Drop the static-link define (system wiiuse is a shared library).
src = re.sub(r"target_compile_definitions\(\$\{PROJECT_NAME\} PRIVATE WIIUSE_STATIC\)\n",
             "", src)

open("CMakeLists.txt", "w").write(src)
PY

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON
%cmake_build

%install
%cmake_install

# Strip any leftover RPATH for Fedora compliance.
chrpath --delete %{buildroot}%{_bindir}/Wiimote 2>/dev/null || :

# Desktop entry.
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=Wiimote LSL
Comment=Stream Wii Remote buttons and motion over LSL
Exec=Wiimote
Icon=input-gaming
Terminal=false
Type=Application
Categories=Science;Game;
EOF

%files
%license LICENSE
%doc README.md
%{_bindir}/Wiimote
%{_datadir}/applications/%{name}.desktop

%changelog
* Sat Jun 20 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.0-1.20230612git4cb2a42
- Initial RPM package for App-Wiimote (master commit 4cb2a42, the LSL Wii Remote
  connector). De-vendored the bundled FetchContent(wiiuse) to Fedora's
  wiiuse-devel (no network at build, per Fedora/COPR policy). Qt6 build; injects
  include(LSLCMake) so installLSLApp() resolves.
