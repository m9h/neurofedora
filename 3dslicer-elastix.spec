# SlicerElastix — image registration GUI for 3D Slicer wrapping the elastix
# registration toolbox. PURE-SCRIPTED (Python) module, so — like 3dslicer-openlifu
# — we replicate slicerMacroBuildScriptedModule directly (drop the module's
# Python + resources into Slicer's qt-scripted-modules) rather than running its
# CMake. This needs no find_package(Slicer) and no foundation -devel, so it is
# independent of the C++ extension-build (foundation -45) work.
#
# elastix itself runs as an external CLI (the `elastix` binary, packaged
# separately in this COPR); the module locates it at runtime.

%global commit      507db1994cfd717cbf77cbfb0e2c6920caf9bbb0
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260218

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11
%global qtsm          %{slicer_inst}/lib/%{slicer_subdir}/qt-scripted-modules

Name:           3dslicer-elastix
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        Elastix image-registration extension for 3D Slicer

License:        MIT
URL:            https://github.com/lassoan/SlicerElastix
Source0:        %{url}/archive/%{commit}/SlicerElastix-%{shortcommit}.tar.gz

BuildArch:      noarch

Requires:       3dslicer
Requires:       elastix >= 5.0
# Scripted modules need the bug#9 scriptability layer to load.
Requires:       ctk-python
Requires:       python3-vtkAddon

%description
SlicerElastix wraps the elastix intensity-based image-registration toolbox in
3D Slicer's GUI: rigid/affine/BSpline and multi-resolution registration driven
by a database of 100+ ready-made elastix parameter presets, with forward/inverse
transform application. elastix runs as an external command-line tool (packaged
separately); this extension provides the Slicer-side interface and presets.

%prep
%autosetup -n SlicerElastix-%{commit}

%build
# Pure-scripted: nothing to compile.

%install
mkdir -p %{buildroot}%{qtsm}/ElastixLib
mkdir -p %{buildroot}%{qtsm}/Resources/Icons
mkdir -p %{buildroot}%{qtsm}/Resources/UI
mkdir -p %{buildroot}%{qtsm}/Resources/RegistrationParameters

# Module script + its Python helper package
install -m0644 Elastix/Elastix.py            %{buildroot}%{qtsm}/
install -m0644 Elastix/ElastixLib/*.py       %{buildroot}%{qtsm}/ElastixLib/
# Resources (icon, UI, the registration-parameter preset database)
install -m0644 Elastix/Resources/Icons/Elastix.png %{buildroot}%{qtsm}/Resources/Icons/
install -m0644 Elastix/Resources/UI/*.ui     %{buildroot}%{qtsm}/Resources/UI/
install -m0644 Elastix/Resources/RegistrationParameters/*.txt \
        %{buildroot}%{qtsm}/Resources/RegistrationParameters/

%files
%license LICENSE
%doc README.md
%{qtsm}/Elastix.py
# Elastix-owned dirs (NOT the shared qt-scripted-modules / Resources / UI / Icons
# dirs, which the 3dslicer package owns).
%dir %{qtsm}/ElastixLib
%{qtsm}/ElastixLib/*.py
%dir %{qtsm}/Resources/RegistrationParameters
%{qtsm}/Resources/RegistrationParameters/*.txt
%{qtsm}/Resources/Icons/Elastix.png
%{qtsm}/Resources/UI/Elastix.ui
%{qtsm}/Resources/UI/PresetManager.ui

%changelog
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260218git507db199
- Initial package. SlicerElastix as a pure-scripted 3D Slicer extension:
  install the Elastix module + ElastixLib + 100+ registration-parameter presets
  into qt-scripted-modules (replicating slicerMacroBuildScriptedModule), no
  compilation / no foundation -devel needed. elastix CLI is a runtime Requires.
