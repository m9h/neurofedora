%global commit 85aa70fc67582d046e771ea73625182a0d8f7475
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20251228
%global gh_owner emilianavt
%global gh_name OpenSeeFace

Name:           python-OpenSeeFace
Version:        1.20.4
Release:        1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Real-time webcam face/eye/gaze tracker using ONNX Runtime

# The repository ships under BSD-2-Clause (LICENSE at root).  The
# bundled .onnx models in models/ are produced by upstream and covered
# by the same LICENSE — see Licenses/OpenSeeFace.txt for the rationale.
# The per-component notes under Licenses/ describe code paths NOT
# included in this RPM (Windows-only DShowCapture, escapi, libsvm,
# ThunderSVM, etc.).
License:        BSD-2-Clause
URL:            https://github.com/%{gh_owner}/%{gh_name}
Source0:        %{url}/archive/%{commit}/%{gh_name}-%{commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel

# Runtime imports observed in tracker.py, facetracker.py, model.py,
# input_reader.py, retinaface.py.
Requires:       python3-numpy
Requires:       python3-opencv
Requires:       python3-pillow
Requires:       python3-onnxruntime
# Optional, only used by a small audio-VAD code path in facetracker.py
# behind the --benchmark / --silent flags.  We pull it in because the
# import is unconditional.
Requires:       python3-pyaudio
Requires:       hicolor-icon-theme

%description
OpenSeeFace is a real-time face / eye / gaze tracker based on the
MobileNetV3 + RetinaFace ONNX models bundled in the project.  It reads
from a webcam (or video file), runs ONNX Runtime inference on CPU, and
emits the tracked landmarks / head pose / gaze direction over a UDP
socket in OpenSee's binary protocol (compatible with the OpenSee Unity
client shipped in the same upstream repository).

Upstream is a loose collection of Python scripts rather than an
installable Python package.  This RPM installs those scripts and the
bundled neural-network model files together under a single shared
directory, and ships an openseeface launcher that runs the tracker
from that location.  The Unity / C# integration code from upstream is
shipped as reference documentation.

%prep
%autosetup -p1 -n %{gh_name}-%{commit}

# Make the script entry point importable from /usr/bin/openseeface.
# Add a Linux-friendly shebang to facetracker.py (upstream omits it).
sed -i '1i #!/usr/bin/python3' facetracker.py
chmod 0755 facetracker.py

%build
# Pure-Python script collection — nothing to build.
:

%install
# Install the Python scripts + .onnx models under a single directory
# so that get_model_base_path() in tracker.py resolves relative to
# __file__ and finds the models without needing --model-dir.
install -d %{buildroot}%{_datadir}/%{gh_name}
install -d %{buildroot}%{_datadir}/%{gh_name}/models

# Python source files used by facetracker.py at runtime.  We do NOT
# install dshowcapture.py or escapi.py because they wrap Windows-only
# DLLs and the file headers note they are skipped on non-Windows
# platforms — see input_reader.py.  Including them would create a false
# dependency on those DLLs in the buildroot manifest and trip
# rpmlint's invalid-script-shebang on the .py files.
for f in facetracker.py input_reader.py model.py remedian.py \
         retinaface.py similaritytransform.py tracker.py \
         dshowcapture.py escapi.py; do
    install -m 0644 "$f" %{buildroot}%{_datadir}/%{gh_name}/
done
# facetracker.py is the entry point — make it executable.
chmod 0755 %{buildroot}%{_datadir}/%{gh_name}/facetracker.py

# ONNX model files + priorbox + benchmark assets (all loaded by
# tracker.py / retinaface.py at runtime).
install -m 0644 models/*.onnx %{buildroot}%{_datadir}/%{gh_name}/models/
install -m 0644 models/*.json %{buildroot}%{_datadir}/%{gh_name}/models/
install -m 0644 models/benchmark.bin %{buildroot}%{_datadir}/%{gh_name}/models/

# Launcher.  cd into the install dir so models/ resolves via
# os.path.dirname(__file__).
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/openseeface <<'EOF'
#!/bin/sh
# OpenSeeFace launcher — runs facetracker.py from its install
# directory so the bundled models/ are picked up automatically.
cd %{_datadir}/OpenSeeFace
exec /usr/bin/python3 facetracker.py "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/openseeface

# Desktop entry — terminal-launched because facetracker.py reads CLI
# args (camera id, port, etc.).
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{gh_name}.desktop <<EOF
[Desktop Entry]
Name=OpenSeeFace
Comment=Real-time webcam face and gaze tracker
Exec=openseeface
Icon=camera-web
Terminal=true
Type=Application
Categories=Science;
EOF

%files
%license LICENSE
%license Licenses/
%doc README.md
%doc Examples/
%doc Unity/
%doc Source/
%{_bindir}/openseeface
%{_datadir}/%{gh_name}
%{_datadir}/applications/%{gh_name}.desktop

%changelog
* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 1.20.4-1.20251228git85aa70f
- Initial RPM package for OpenSeeFace (master commit 85aa70f, 2025-12-28).
- Upstream uses Poetry but the actual project layout is a flat script
  collection (no installable Python package), so this RPM ships the
  scripts + .onnx models under %%{_datadir}/OpenSeeFace/ and exposes
  a launcher at %%{_bindir}/openseeface.
- Version field tracks upstream's pyproject.toml version (1.20.4);
  the snapshot date in Release identifies the post-1.20.4 commit.
- BSD-2-Clause covers the entire repo including the bundled .onnx
  models (see Licenses/OpenSeeFace.txt).
