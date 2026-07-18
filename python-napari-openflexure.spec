Name:           python-napari-openflexure
Version:        0.2.0
Release:        1%{?dist}
Summary:        Plugin to control an OpenFlexure microscope from napari

# New plugin written for this COPR (no upstream napari-openflexure exists).
License:        BSD-3-Clause
URL:            https://gitlab.com/morgan.hough/neurofedora
Source0:        napari-openflexure-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# napari + magicgui import a Qt binding; needed for the %check import.
BuildRequires:  python3-pyqt6

%global _description %{expand:
napari-openflexure is a napari plugin that adds an OpenFlexure microscope
control dock widget: connect by host or auto-discover over mDNS, capture
full-resolution images into a napari image layer, jog the stage in X/Y/Z, and
raster a whole-slide mosaic scan. It is a thin wrapper around
openflexure-microscope-client.}

%description %{_description}

%package -n python3-napari-openflexure
Summary:        %{summary}
%description -n python3-napari-openflexure %{_description}

%prep
%autosetup -n napari-openflexure-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files napari_openflexure

%check
export QT_QPA_PLATFORM=offscreen
%pyproject_check_import

%files -n python3-napari-openflexure -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Fri Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.0-1
- Add whole-slide mosaic scanning. Rasters an NxN snake grid over the slide,
  using the camera_stage_mapping image_to_stage_displacement matrix to convert a
  (overlapped) field-of-view pixel step into the stage move that produces it, so
  tiles land on a regular pixel grid. Two modes: full-res (one image layer per
  tile, translated into place -> a zoomable mosaic) and overview (fast
  preview-stream tiles painted into a single slide_overview canvas -> a cheap
  whole-slide map). Runs in a napari thread_worker yielding tiles to the GUI
  thread, optionally autofocuses first, and always returns the stage home.
- Add a full-resolution capture path: capture_image only returns the low-res
  preview stream, so trigger a temporary gallery capture, download its JPEG and
  delete it so the microscope gallery is not left cluttered. Exposed as a
  "Full resolution" toggle.
- Declare the requests and pillow dependencies the full-res download needs
  (previously undeclared; %%pyproject_check_import would fail without them).
* Wed Jun 24 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.1-1
- Fix the dock widget failing to open from the Plugins menu: napari only injects
  the active viewer when the widget __init__ parameter is named napari_viewer or
  annotated with the Viewer type. Rename the bare `viewer` parameter to
  `napari_viewer` (and annotate it) so OpenFlexureWidget instantiates correctly.
  Caught by the napari-smoke.sh dock-widget instantiation check.

* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-1
- Initial package: napari-openflexure 0.1.0 — the napari<->OpenFlexure connector
  (new plugin; none exists upstream). Completes the napari + OpenFlexure chain.
