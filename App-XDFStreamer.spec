%global commit b329ae79abc85a54f5cd72fb778c2a6c4c837571
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           App-XDFStreamer
Version:        1.15.0
Release:        1%{?dist}
Summary:        Replay XDF files as Lab Streaming Layer (LSL) streams

License:        GPL-3.0-or-later
URL:            https://github.com/labstreaminglayer/App-XDFStreamer
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
# liblsl >= 1.17.7-2 ships LSLCMake.cmake (needed for installLSLApp()).
BuildRequires:  liblsl-devel >= 1.17.7
BuildRequires:  libxdf-devel
BuildRequires:  qt5-qtbase-devel

Requires:       liblsl%{?_isa} >= 1.17.7
Requires:       libxdf%{?_isa}

%description
XDFStreamer is a small Qt application that replays signals stored in an XDF
file as Lab Streaming Layer (LSL) streams.  It is useful for prototyping and
debugging downstream LSL clients without re-running the original experiment.

%prep
%autosetup -p1 -n %{name}-%{commit}

# Inject include(LSLCMake) so installLSLApp()/installLSLAuxFiles() resolve.
# (LSLConfig.cmake never appends to CMAKE_MODULE_PATH; we have to do it.)
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

# libxdf in this COPR does NOT ship cmake config files (the upstream
# CMakeLists is set up for it, but our libxdf spec installs only
# /usr/include/xdf.h + /usr/lib64/libxdf.so).  Replace the
# find_package(libxdf) call with a direct find_library / find_path.
python3 <<'PYEOF'
import re
with open("CMakeLists.txt") as f:
    text = f.read()
new = re.sub(
    r'find_package\(libxdf REQUIRED.*?\)\n',
    ("# libxdf in neurofedora COPR is installed without cmake config files;\n"
     "# wire up XDF::xdf manually.\n"
     "find_path(XDF_INCLUDE_DIR NAMES xdf.h)\n"
     "find_library(XDF_LIBRARY NAMES xdf)\n"
     "if(NOT XDF_INCLUDE_DIR OR NOT XDF_LIBRARY)\n"
     "    message(FATAL_ERROR \"libxdf headers / library not found\")\n"
     "endif()\n"
     "add_library(XDF::xdf UNKNOWN IMPORTED)\n"
     "set_target_properties(XDF::xdf PROPERTIES\n"
     "    IMPORTED_LOCATION \"${XDF_LIBRARY}\"\n"
     "    INTERFACE_INCLUDE_DIRECTORIES \"${XDF_INCLUDE_DIR}\")\n"),
    text, count=1, flags=re.DOTALL)
with open("CMakeLists.txt", "w") as f:
    f.write(new)
PYEOF

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON

%cmake_build

%install
%cmake_install

# installLSLApp() installs the binary in %%{_bindir} (GNUInstallDirs).
# installLSLAuxFiles() drops LICENSE + README.md in %%{_datadir}/XDFStreamer/ —
# strip those duplicates; we ship them via %%license / %%doc instead.
rm -f %{buildroot}%{_datadir}/XDFStreamer/LICENSE
rm -f %{buildroot}%{_datadir}/XDFStreamer/README.md
rmdir %{buildroot}%{_datadir}/XDFStreamer 2>/dev/null || :

chrpath --delete %{buildroot}%{_bindir}/XDFStreamer 2>/dev/null || :

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=XDFStreamer
Comment=Replay XDF files as LSL streams
Exec=XDFStreamer
Icon=media-playback-start
Terminal=false
Type=Application
Categories=Science;DataVisualization;
EOF

%files
%license LICENSE
%doc README.md
%{_bindir}/XDFStreamer
%{_datadir}/applications/%{name}.desktop

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 1.15.0-1
- Update to upstream release 1.15.0 (tag v1.15.0, commit b329ae7). Convert from
  the post-1.14.0 commit snapshot to a proper tagged release (drop snapdate;
  Release 1). Freshness sweep 2026-06-14.

* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.14.0-1.20260602gitd718398
- Initial RPM package for App-XDFStreamer (master commit d718398).
- Inject include(LSLCMake) after find_package(LSL) for installLSLApp().
- Replace find_package(libxdf) with direct find_library/find_path because
  the COPR libxdf does not yet ship cmake config files.
