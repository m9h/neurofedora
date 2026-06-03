%global commit aa754e61e5e210b1e52960f3c119a45392e64734
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260602

Name:           App-SigVisualizer
Version:        0
Release:        1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Real-time PyQt5 signal viewer for Lab Streaming Layer (LSL) streams

License:        MIT
URL:            https://github.com/labstreaminglayer/App-SigVisualizer
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
# Runtime: PyQt5 + pylsl
Requires:       python3-qt5-base
Requires:       python3-pylsl
Requires:       hicolor-icon-theme

%description
SigVisualizer is a real-time PyQt5 viewer for Lab Streaming Layer (LSL)
streams.  It discovers available outlets on the local network and plots
their signals interactively.

%prep
%autosetup -p1 -n %{name}-%{commit}

# Upstream has no setup.py / pyproject.toml — the files are loose Python
# modules that import each other via from sigvisualizer import ... .  We
# install them under %%{_datadir}/%%{name}/ and ship a tiny launcher in
# %%{_bindir}.

%build
# Nothing to build (pure Python).
:

%install
# Module + UI directory.
install -d %{buildroot}%{_datadir}/%{name}
install -d %{buildroot}%{_datadir}/%{name}/icons
install -m 0644 sigvisualizer.py paintwidget.py LSL_sender.py \
                ui_sigvisualizer.py ui_sigvisualizer.ui \
                %{buildroot}%{_datadir}/%{name}/
install -m 0644 icons/*.svg %{buildroot}%{_datadir}/%{name}/icons/
install -m 0644 sigvisualizer.ico sigvisualizer.png \
                %{buildroot}%{_datadir}/%{name}/

# Launcher.
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/sigvisualizer <<EOF
#!/bin/sh
# Run the SigVisualizer GUI from its install dir so that relative
# resource paths (icons, .ui file) resolve correctly.
cd %{_datadir}/%{name}
exec %{__python3} sigvisualizer.py "\$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/sigvisualizer

# Desktop entry.
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=SigVisualizer
Comment=Real-time viewer for LSL signal streams
Exec=sigvisualizer
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=Science;DataVisualization;
EOF

%files
%license LICENSE
%doc README.md
%{_bindir}/sigvisualizer
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop

%changelog
* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 0-1.20260602gitaa754e6
- Initial RPM package for App-SigVisualizer (master commit aa754e6).
- Upstream has no setup.py — installs loose .py modules under
  %%{_datadir}/%%{name}/ and ships a wrapper /usr/bin/sigvisualizer that
  cd's into that dir so relative icon/ui paths resolve.
- Upstream does not declare a version; Version: 0 is intentional. Bump
  on every snapshot tag rotation.
