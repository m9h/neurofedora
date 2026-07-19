Name:           python-napari
Version:        0.8.0
Release:        1%{?dist}
Summary:        Fast, interactive, multi-dimensional image viewer for Python

License:        BSD-3-Clause
URL:            https://napari.org
Source0:        %{pypi_source napari}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# A Qt binding must be importable for the %check (napari imports qtpy).
BuildRequires:  python3-pyqt6
# Desktop integration: validate the .desktop file and rasterize the app icon
# from upstream's icon.ico into the hicolor theme.
BuildRequires:  desktop-file-utils
BuildRequires:  ImageMagick

%global _description %{expand:
napari is a fast, interactive, multi-dimensional image viewer for Python. It is
designed for browsing, annotating and analysing large N-dimensional images, and
is built on Qt (via qtpy), vispy for GPU rendering, and the scientific Python
stack. It is the pure-Python, Java-free counterpart to ImageJ/Fiji and is widely
used in bioimaging.}

%description %{_description}

# Base package: the importable library + the `napari` launcher. It does NOT hard
# depend on a Qt binding, so plugins can depend on python3-napari without forcing
# a specific Qt stack (mirrors conda-forge's napari-base). A usable GUI binding
# is pulled by default via Recommends; the `napari` metapackage guarantees it.
%package -n python3-napari
Summary:        %{summary}
# scikit-image's `data` extra (de-pinned in %prep) only pulled pooch, used for
# downloading optional sample-data images — weak dep, not required to run.
Recommends:     python3-pooch
Recommends:     python3-pyqt6
%description -n python3-napari %{_description}

# Metapackage: `dnf install napari` gives a guaranteed-working GUI (base + Qt6).
%package -n napari
Summary:        Multi-dimensional image viewer with a Qt6 backend (metapackage)
BuildArch:      noarch
Requires:       python3-napari = %{version}-%{release}
Requires:       python3-pyqt6
%description -n napari
Convenience metapackage that installs the napari viewer together with the PyQt6
backend, giving a ready-to-run GUI. The library itself is python3-napari.

%prep
%autosetup -n napari-%{version}

# Fedora's python3-scikit-image does not advertise the `[data]` extra (which
# only pulls pooch for downloadable sample data). Depend on plain scikit-image
# and pull pooch explicitly (added as a Requires below).
sed -i 's/scikit-image\[data\]/scikit-image/' pyproject.toml

# napari 0.7 targets Qt6 and is not supported on PyQt5. When a Qt binding has
# not been explicitly selected (QT_API unset), qtpy picks the first binding it
# finds and prefers PyQt5 -- so on a system where a coinstalled python3-qt5
# (PyQt5) is present alongside our PyQt6, napari runs on PyQt5 and crashes on
# teardown ("QObject deleted directly" -> "free(): invalid pointer"). Prepend a
# small selector to napari's package __init__ that, only when QT_API is unset,
# prefers an importable Qt6 binding (PyQt6, then PySide6) before qtpy is first
# imported. No-op if the user set QT_API, or if no Qt6 binding is installed.
cat > src/napari/__init__.py.qtapi <<'PYEOF'
def _fedora_prefer_qt6():
    """Prefer a Qt6 binding when none was explicitly selected (see spec %prep)."""
    import os
    if os.environ.get("QT_API"):
        return
    for api, mod in (("pyqt6", "PyQt6"), ("pyside6", "PySide6")):
        try:
            __import__(mod)
        except ImportError:
            continue
        os.environ["QT_API"] = api
        return


_fedora_prefer_qt6()
PYEOF
cat src/napari/__init__.py >> src/napari/__init__.py.qtapi
mv src/napari/__init__.py.qtapi src/napari/__init__.py

%generate_buildrequires
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_install
# napari and the bundled napari_builtins plugin are both top-level modules in
# this distribution.
%pyproject_save_files napari napari_builtins

# --- Desktop integration (menu entry + icon) ---------------------------------
# Upstream ships no .desktop file and installs its logo only inside the Python
# package (src/napari/resources), so on Fedora the menu entry had no icon.
# Generate a launcher and install the brand logo into the hicolor icon theme as
# `napari`, matching the Icon= key below.
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/napari.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=napari
GenericName=Image Viewer
Comment=Fast, interactive, multi-dimensional image viewer
Exec=napari %F
Icon=napari
Terminal=false
Categories=Graphics;Science;
Keywords=imaging;microscopy;bioimaging;visualization;
StartupNotify=true
StartupWMClass=napari
EOF

# Scalable vector icon (the official napari gradient logo).
install -d %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m 0644 src/napari/resources/logos/gradient-plain-dark.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/napari.svg
# Raster sizes, rasterized losslessly from upstream's bundled icon.ico (its
# largest frame is a 256x256 PNG).
for s in 16 32 48 64 128 256; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps
    magick src/napari/resources/icon.ico[0] -resize ${s}x${s} \
        %{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps/napari.png
done

desktop-file-validate %{buildroot}%{_datadir}/applications/napari.desktop

%check
# Headless Qt; top-level import only (-t). The full GUI/_qt/_vispy submodules
# need a real display/GL context not present in mock.
export QT_QPA_PLATFORM=offscreen
%pyproject_check_import -t

%files -n python3-napari -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/napari
%{_datadir}/applications/napari.desktop
%{_datadir}/icons/hicolor/*/apps/napari.png
%{_datadir}/icons/hicolor/scalable/apps/napari.svg

%files -n napari
# metapackage: no payload

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.0-1
- Update to 0.8.0

* Tue Jun 30 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-3
- Add desktop integration: ship a napari.desktop launcher plus the brand logo
  in the hicolor icon theme (scalable SVG + 16-256px PNGs rasterized from
  upstream icon.ico). Fixes the missing menu icon on Fedora.

* Wed Jun 24 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-2
- Prefer a Qt6 binding (PyQt6, then PySide6) at import time when QT_API is unset,
  so napari never runs on a coinstalled PyQt5 (which it does not support and which
  crashes on teardown). No-op when QT_API is set or no Qt6 binding is present.

* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-1
- Initial package: napari 0.7.1 (multi-dimensional image viewer) — chain root.
- base+meta split: python3-napari (library, Qt-agnostic, Recommends pyqt6) and
  a napari metapackage that guarantees the PyQt6 backend.
- Pinned deps app-model <0.6 and vispy <0.17 satisfied by the COPR chain.
