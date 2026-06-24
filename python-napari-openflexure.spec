Name:           python-napari-openflexure
Version:        0.1.0
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
full-resolution images into a napari image layer, and jog the stage in X/Y/Z.
It is a thin wrapper around openflexure-microscope-client.}

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
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.0-1
- Initial package: napari-openflexure 0.1.0 — the napari<->OpenFlexure connector
  (new plugin; none exists upstream). Completes the napari + OpenFlexure chain.
