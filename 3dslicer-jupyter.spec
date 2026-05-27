# SlicerJupyter — Jupyter kernel that runs Slicer's Python interpreter
# inside a notebook. Critical for educational / clinical-research use:
# clinicians and educators can build reproducible notebooks that drive
# Slicer's processing pipeline.

%global commit       d89a282d
%global longcommit   d89a282d00000000000000000000000000000000
%global snapdate     20260420

Name:           3dslicer-jupyter
Version:        0
Release:        0.1.%{snapdate}git%{commit}%{?dist}
Summary:        Jupyter kernel for 3D Slicer (run Slicer Python from notebooks)

License:        BSD-3-Clause
URL:            https://github.com/Slicer/SlicerJupyter
Source0:        %{url}/archive/%{commit}/SlicerJupyter-%{commit}.tar.gz

BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  3dslicer-devel >= 5.10.0
BuildRequires:  qt6-qtbase-devel
BuildRequires:  zeromq-devel

Requires:       3dslicer >= 5.10.0
Requires:       python3-jupyter
Requires:       python3-zmq
Requires:       python3-tornado

%description
SlicerJupyter installs a Jupyter kernel that hosts 3D Slicer's embedded
Python interpreter. This lets users build reproducible analysis
notebooks that drive Slicer's MRML scene, modules, and visualization
from a familiar notebook UI — without needing the Slicer GUI to be
open.

Critical for:
  * Educational use (workshops, online courses, NA-MIC training)
  * Clinical-research workflows that need reproducible scripted pipelines
  * Remote-collaboration scenarios where notebooks travel between sites
  * CI/CD of imaging analyses (test notebooks via papermill/nbval)

%prep
%autosetup -p1 -n SlicerJupyter-%{longcommit}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_DIR:PATH=%{_prefix}/lib/slicer-5.10.0/lib/cmake/Slicer \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix}/lib/slicer-5.10.0
%cmake_build

%install
%cmake_install

%files
%license License.txt 2>/dev/null || true
%doc README.md
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-loadable-modules/*Jupyter*
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-scripted-modules/*Jupyter*
%{_prefix}/lib/slicer-5.10.0/share/Slicer-5.10/qt-loadable-modules/*Jupyter*

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260420gitd89a282d
- Initial COPR package tracking SlicerJupyter master.
- Jupyter kernel runs Slicer's embedded Python; pairs with Fedora's
  python3-jupyter / Jupyter Lab on the user side.
