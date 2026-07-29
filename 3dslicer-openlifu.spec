# SlicerOpenLIFU — Openwater's Low-Intensity Focused Ultrasound (LIFU) research
# platform extension for 3D Slicer.
#
# This is a PURE SCRIPTED (Python) extension: every module is built with
# slicerMacroBuildScriptedModule (no C++ loadable/CLI modules), so it needs no
# compilation and no find_package(Slicer) / SlicerConfig.cmake. We therefore do
# NOT run its CMake at all — we replicate exactly what the macro installs (the
# MODULE_PYTHON_SCRIPTS / MODULE_PYTHON_RESOURCES lists from each module's
# CMakeLists, dropped into Slicer's qt-scripted-modules dir with their relative
# paths preserved, NO_INSTALL_SUBDIR being the default here). Source1 does that
# faithfully by parsing the CMakeLists, so no foundation rebuild is required.
#
# Runtime Python deps (openlifu, bcrypt, threadpoolctl, requests, segno) are NOT
# packaged here: the extension lazy-installs them via slicer.util.pip_install on
# first use (OpenLIFULib/lazyimport.py), prompting the user. The modules load and
# appear in Slicer without them present.

%global slicer_inst %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.12

Name:           3dslicer-openlifu
Version:        1.19.0
Release:        3%{?dist}
Summary:        OpenLIFU (Low-Intensity Focused Ultrasound) extension for 3D Slicer

# Extension source is AGPL-3.0; see the bundled LICENSE.txt.
License:        AGPL-3.0-or-later
URL:            https://github.com/OpenwaterHealth/SlicerOpenLIFU
Source0:        %{url}/archive/refs/tags/v%{version}/SlicerOpenLIFU-%{version}.tar.gz
# Faithful installer: parses each module's CMakeLists for MODULE_PYTHON_SCRIPTS /
# MODULE_PYTHON_RESOURCES and installs them into qt-scripted-modules, emitting the
# %%files list (owns OpenLIFU-specific dirs, leaves shared dirs to 3dslicer).
Source1:        olifu-install-modules.py

BuildArch:      noarch
BuildRequires:  python3

Requires:       3dslicer
# qt/ctk/vtkAddon scriptability (3D Slicer bug #9) is required for any scripted
# module to load; those live in the supporting packages.
Requires:       ctk-python
Requires:       python3-vtkAddon

%description
SlicerOpenLIFU is a 3D Slicer extension for Openwater's OpenLIFU (Low Intensity
Focused Ultrasound) research platform, providing an advanced interface to the
features of the OpenLIFU app: a local treatment database, photogrammetry-based
transducer localization for neuronavigation, sonication pre-planning with safety
checks and hardware-configuration generation, and real-time device control of
Openwater focused-ultrasound transducer hardware.

The extension's additional Python dependencies (openlifu, bcrypt,
threadpoolctl, requests, segno) are installed on first use from within
Slicer (it prompts to pip-install them), so they are not packaged here.

%prep
%autosetup -n SlicerOpenLIFU-%{version}

%build
# Nothing to compile — pure scripted (Python) extension.

%install
python3 %{SOURCE1} \
    "%{_builddir}/SlicerOpenLIFU-%{version}" \
    "%{buildroot}" \
    "%{slicer_inst}" \
    "%{_builddir}/openlifu.files" \
    "%{slicer_subdir}"

%files -f %{_builddir}/openlifu.files
%license LICENSE.txt
%doc README.md

%changelog
* Wed Jul 29 2026 Morgan Hough <morgan.hough@gmail.com>
- Actually install into Slicer-5.12. The 1.19.0-2 retarget bumped the spec's
  %%global slicer_subdir but olifu-install-modules.py hardcoded
  "lib/Slicer-5.11/qt-scripted-modules" and never saw it, so the modules kept
  landing in a directory the 5.12 launcher does not scan -- every OpenLIFU module
  silently failed to register (the package installed clean and looked fine).
  Pass slicer_subdir into the installer instead of hardcoding it. Caught by the
  CDash extension-group-OpenLIFUHome check.

* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 1.19.0-2
- Retarget from Slicer-5.11 to Slicer-5.12 core (3dslicer 5.12.1); bump
  3dslicer-devel floor to 5.12.1.

* Sat Jun 13 2026 Morgan Hough <morgan.hough@gmail.com> - 1.19.0-1
- Initial package. SlicerOpenLIFU v1.19.0 (Openwater Low-Intensity Focused
  Ultrasound research platform) as a pure-scripted 3D Slicer extension: install
  the 10 OpenLIFU* scripted modules + the OpenLIFULib Python helper package into
  Slicer's qt-scripted-modules, replicating slicerMacroBuildScriptedModule
  without compiling or needing an install-tree SlicerConfig.cmake. Runtime
  Python deps are lazy pip-installed by the extension on first use.
