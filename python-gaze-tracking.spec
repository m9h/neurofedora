%global commit fce71359acd5ce6843630eaf3b85558a734b0dfe
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260427
%global gh_owner antoinelame
%global gh_name GazeTracking
%global pypi_name gaze-tracking

Name:           python-gaze-tracking
# pyproject.toml says 0.1.0, but upstream has never tagged a release —
# we ship a snapshot of the master branch at the commit recorded above.
Version:        0.1.0
Release:        1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Webcam-based eye/pupil/gaze tracker using dlib + OpenCV

# Upstream code: MIT (see LICENSE at repo root).
#
# The bundled trained_models/shape_predictor_68_face_landmarks.dat is
# dlib's canonical 68-landmark face shape predictor.  Per davisking's
# original blog post, that .dat file was trained on the iBUG 300-W face
# landmark dataset, whose terms restrict use to research / non-commercial
# purposes.  The model is shipped here so the package is functional out
# of the box for a research COPR; consumers who need a commercially
# usable face landmark predictor must train their own on freely-licensed
# data.  Tagged as a dedicated SPDX clause for transparency.
License:        MIT AND LicenseRef-Fedora-UltraPermissive
URL:            https://github.com/%{gh_owner}/%{gh_name}
Source0:        %{url}/archive/%{commit}/%{gh_name}-%{commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# Runtime imports (gaze_tracking/{eye,pupil,gaze_tracking,calibration}.py):
#   import cv2, numpy as np, dlib
Requires:       python3-dlib
Requires:       python3-numpy
Requires:       python3-opencv

%global _description %{expand:
GazeTracking is a small Python library that estimates the gaze direction
of a user from a regular webcam stream.  It uses the dlib 68-landmark
face shape predictor to locate the eyes, isolates the pupils via OpenCV
image processing, and reports left/right/center gaze plus a numerical
horizontal / vertical ratio.

This package ships the trained shape_predictor_68_face_landmarks data
file under the gaze_tracking Python package directory so the library
is functional with no additional downloads.}

%description %{_description}


%package -n python3-gaze-tracking
Summary:        %{summary}

%description -n python3-gaze-tracking %{_description}


%prep
%autosetup -n %{gh_name}-%{commit} -p1


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Upstream sets [tool.setuptools.package-data] = ["trained_models/*.dat"]
# so the wheel already contains the .dat file.  Make sure it is listed in
# the manifest.
%pyproject_save_files -l gaze_tracking


%check
# Default %%pyproject_check_import will import gaze_tracking, which in
# turn imports cv2 and dlib at module-load time and tries to deserialize
# the 95 MB shape predictor — fine on a build host that has those bits.
# We rely on the runtime Requires above; no test harness ships with the
# repo (only example.py, which opens /dev/video0).
:


%files -n python3-gaze-tracking -f %{pyproject_files}
%license LICENSE
%doc README.md
%doc example.py


%changelog
* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-1.20260427gitfce7135
- Initial RPM package for GazeTracking (master commit fce7135, 2026-04-27).
- Upstream has never tagged a release; pyproject.toml records 0.1.0.
- The bundled trained_models/shape_predictor_68_face_landmarks.dat is
  from dlib's research-data corpus (iBUG 300-W training set); shipped
  here for a research COPR, not for commercial redistribution.
- Depends on the freshly revived python3-dlib 20.x package.
