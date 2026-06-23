Name:           python-napari
Version:        0.7.1
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

%check
# Headless Qt; top-level import only (-t). The full GUI/_qt/_vispy submodules
# need a real display/GL context not present in mock.
export QT_QPA_PLATFORM=offscreen
%pyproject_check_import -t

%files -n python3-napari -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/napari

%files -n napari
# metapackage: no payload

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.7.1-1
- Initial package: napari 0.7.1 (multi-dimensional image viewer) — chain root.
- base+meta split: python3-napari (library, Qt-agnostic, Recommends pyqt6) and
  a napari metapackage that guarantees the PyQt6 backend.
- Pinned deps app-model <0.6 and vispy <0.17 satisfied by the COPR chain.
