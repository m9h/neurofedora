# SlicerJupyter — Jupyter kernel that runs Slicer's Python interpreter
# inside a notebook. Critical for educational / clinical-research use:
# clinicians and educators can build reproducible notebooks that drive
# Slicer's processing pipeline.

%global commit       d89a282d
%global longcommit   d89a282d54d7249fce07f62320779f82c5eb4604
%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.12

%global snapdate     20260420

Name:           3dslicer-jupyter
Version:        0
Release:        0.3.%{snapdate}git%{commit}%{?dist}
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

# Canonical Slicer-extension buildroot, grafted from 3dslicer-dmri.spec.
# This spec predates the 5.12 retarget and was never built, so it carried
# only a handful of BuildRequires -- find_package(Slicer) then failed inside
# SlicerConfig.cmake:672 on find_package(RapidJSON), the first of ~38 missing.
# Full Qt6 set find_package(Slicer)'s Qt check demands.
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Sql)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  cmake(Qt6Xml)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6PrintSupport)
BuildRequires:  cmake(Qt6Multimedia)
BuildRequires:  cmake(Qt6MultimediaWidgets)
BuildRequires:  cmake(Qt6Core5Compat)
BuildRequires:  cmake(Qt6StateMachine)
BuildRequires:  cmake(Qt6WebEngineCore)
BuildRequires:  cmake(Qt6WebEngineWidgets)
BuildRequires:  cmake(Qt6WebChannel)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickWidgets)
BuildRequires:  cmake(Qt6Test)
BuildRequires:  cmake(Qt6UiTools)
BuildRequires:  qt6-qttools-devel
BuildRequires:  InsightToolkit5-devel >= 5.4.6-7
BuildRequires:  InsightToolkit5-vtk-devel
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  ctk-devel
BuildRequires:  qttesting-devel
BuildRequires:  vtkAddon-devel
BuildRequires:  qRestAPI-devel
BuildRequires:  python-pythonqt-devel
BuildRequires:  commontk-applauncher-devel
BuildRequires:  dcmtk-devel
BuildRequires:  teem-devel

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
    `# Was %{_prefix}/lib/slicer-5.10.0/lib/cmake/Slicer -- a Slicer 5.10 layout` \
    `# that has not existed since the 5.12 retarget. This spec was written then` \
    `# and never built, so nothing ever caught it.` \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
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
* Sun Aug 02 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.3.20260420gitd89a282d
- Graft the canonical Slicer-extension buildroot (~34 BuildRequires) from
  3dslicer-dmri.spec. This spec predates the 5.12 retarget and was never built, so it
  carried only a handful; find_package(Slicer) then failed inside
  SlicerConfig.cmake:672 on find_package(RapidJSON) -- the first of the missing set,
  which also covers the full Qt6 component list, ITK/VTK/CTK/DCMTK devel,
  SlicerExecutionModel, PythonQt, qRestAPI, teem and vtkAddon.

* Sun Aug 02 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.2.20260420gitd89a282d
- Point Slicer_DIR at the 5.12 layout: it was %%{_prefix}/lib/slicer-5.10.0/lib/
  cmake/Slicer, a path that has not existed since the 5.12 retarget. The spec was
  written then and never built, so nothing caught it.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260420gitd89a282d
- Initial COPR package tracking SlicerJupyter master.
- Jupyter kernel runs Slicer's embedded Python; pairs with Fedora's
  python3-jupyter / Jupyter Lab on the user side.
