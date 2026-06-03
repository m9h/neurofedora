%global commit 37dedd64c6a7691f9d8d3900f46d9b89f8e35e7e
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260602

Name:           App-PupilLabs
Version:        0
Release:        1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Pupil Capture plugins that relay/record Lab Streaming Layer (LSL) streams

License:        LGPL-3.0-or-later
URL:            https://github.com/labstreaminglayer/App-PupilLabs
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
# Imported at runtime by both the relay plugin and the recorder script.
Requires:       python3-pylsl
# pyglui, plugin, version_utils come from the Pupil Capture runtime —
# they are NOT in Fedora and we therefore do not Require them.  These
# plugins are only useful inside a running Pupil Capture instance.

%description
A pair of plugins for Pupil Labs' Pupil Capture eye-tracking software:

  * pupil_capture_lsl_relay — publishes gaze, pupillometry, fixation and
    scene-camera data on the Lab Streaming Layer (LSL).
  * pupil_capture_lsl_recorder — records external LSL streams into a
    Pupil Capture recording.

These are Pupil Capture plugins, not standalone applications.  After
installing this package, copy or symlink the files from
%{_datadir}/%{name}/ into your Pupil Capture user plugin directory
(see https://docs.pupil-labs.com/developer/core/plugin-api/).

Pupil Capture itself is not packaged in Fedora; install it separately.

%prep
%autosetup -p1 -n %{name}-%{commit}

%build
# Pure-Python plugin files; nothing to build.
:

%install
install -d %{buildroot}%{_datadir}/%{name}

# Standalone recorder script (single file).
install -m 0644 pupil_capture/pupil_capture_lsl_recorder.py \
                %{buildroot}%{_datadir}/%{name}/

# Relay plugin package (directory).
cp -a pupil_capture/pupil_capture_lsl_relay \
      %{buildroot}%{_datadir}/%{name}/

%files
%license LICENSE
%doc README.md
%doc pupil_capture/README.md
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/pupil_capture_lsl_recorder.py
%{_datadir}/%{name}/pupil_capture_lsl_relay

%changelog
* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 0-1.20260602git37dedd6
- Initial RPM package for App-PupilLabs (master commit 37dedd6).
- Plugins (not standalone apps) shipped under %%{_datadir}/%%{name}/ for
  manual copy/symlink into the user's Pupil Capture plugin directory.
- Pupil Capture itself is not in Fedora; pyglui / plugin / version_utils
  imports are deliberately not turned into Requires:.
- Upstream does not declare a version; Version: 0 is intentional.
