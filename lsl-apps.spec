Name:           lsl-apps
Version:        1.0
Release:        2%{?dist}
Summary:        Lab Streaming Layer applications (meta-package)

License:        MIT
URL:            https://labstreaminglayer.org/
BuildArch:      noarch

# Recording + format viewer
Requires:       labrecorder
Requires:       App-XDFStreamer
Requires:       App-SigVisualizer

# Generic acquisition apps (no proprietary hardware SDK required)
Requires:       App-AudioCapture
Requires:       App-Gamepad

# Open eye-tracker integration
Requires:       App-PupilLabs

%description
Meta-package that pulls in the Lab Streaming Layer (LSL) user-facing
applications shipped by the mhough/neurofedora COPR:

  * labrecorder         — record one or more LSL streams to XDF on disk
  * App-XDFStreamer     — replay XDF files back as live LSL streams
  * App-SigVisualizer   — PyQt5/pylsl interactive signal viewer
  * App-AudioCapture    — microphone capture into an LSL stream
  * App-Gamepad         — generic gamepad input as an LSL stream
  * App-PupilLabs       — Pupil Capture relay/recorder plugins

Library prerequisites (liblsl, libxdf, python3-pylsl, python3-pyxdf)
are pulled in as transitive dependencies of the apps above.

%files
# Meta-package — no payload

%changelog
* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-2
- Drop sigviewer from Requires. Despite reading XDF, sigviewer is an
  independent cbrnr/sigviewer project, not part of the labstreaminglayer
  organization. Users who want it can install it directly.

* Mon Jun 02 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-1
- Initial lsl-apps meta-package for the mhough/neurofedora COPR.
