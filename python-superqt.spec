Name:           python-superqt
Version:        0.8.2
Release:        1%{?dist}
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
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.2-1
- Update to 0.8.2 for the napari chain: napari 0.7.1 requires superqt >=0.7.8,
  but Fedora F44/rawhide ship only 0.7.7. Pure-Python; deps (pygments, qtpy,
  typing-extensions; iconify->pyconify) all already in Fedora.
