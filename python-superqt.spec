Name:           python-superqt
Version:        0.8.2
Release:        2%{?dist}
Summary:        Missing widgets and components for Qt-python

License:        BSD-3-Clause
URL:            https://github.com/pyapp-kit/superqt
Source0:        %{pypi_source superqt}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# A Qt binding (qtpy) and the iconify backend must import for %check.
BuildRequires:  python3-pyqt6
BuildRequires:  python3-pyconify

%global _description %{expand:
superqt provides a collection of high-quality Qt widgets and utilities for
Python (range sliders, labeled sliders, enum/font/color combo boxes, elidable
labels, icon support, threading helpers) usable with PyQt5/6 or PySide2/6 via
qtpy. It is a core building block of magicgui and napari.}

%description %{_description}

%package -n python3-superqt
Summary:        %{summary}
%description -n python3-superqt %{_description}

# Extras-as-subpackages, matching Fedora's superqt set so this 0.8.2 cleanly
# supersedes the 0.7.7 split (otherwise the stale python3-superqt+iconify-0.7.7,
# which magicgui pulls via superqt[iconify], pins back to superqt = 0.7.7 and
# conflicts).
%pyproject_extras_subpkg -n python3-superqt cmap
%pyproject_extras_subpkg -n python3-superqt iconify
%pyproject_extras_subpkg -n python3-superqt pyqt5
%pyproject_extras_subpkg -n python3-superqt pyqt6
%pyproject_extras_subpkg -n python3-superqt pyside6
%pyproject_extras_subpkg -n python3-superqt quantity

%prep
%autosetup -n superqt-%{version}

%generate_buildrequires
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files superqt

%check
export QT_QPA_PLATFORM=offscreen
# superqt.cmap is an optional colormap helper needing the `cmap` extra.
%pyproject_check_import -e 'superqt.cmap'

%files -n python3-superqt -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.2-2
- Generate the extras subpackages (cmap, iconify, pyqt5, pyqt6, pyside6,
  quantity) matching Fedora's split, so 0.8.2 fully supersedes the 0.7.7 set;
  fixes a conflict where python3-superqt+iconify-0.7.7 (pulled by magicgui)
  pinned superqt back to 0.7.7.

* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.2-1
- Update to 0.8.2 for the napari chain: napari 0.7.1 requires superqt >=0.7.8,
  but Fedora F44/rawhide ship only 0.7.7. Pure-Python; deps (pygments, qtpy,
  typing-extensions; iconify->pyconify) all already in Fedora.
