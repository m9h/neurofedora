Name:           cc3d-player5
Version:        4.8.0
Release:        1%{?dist}
Summary:        CC3D Player — interactive CompuCell3D simulation viewer

# LICENSE.txt is the GNU LGPL.
License:        LGPL-3.0-or-later
URL:            https://compucell3d.org
Source0:        https://github.com/CompuCell3D/%{name}/archive/refs/tags/%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# Companion GUI to the CompuCell3D engine. It installs into the cc3d.* python
# namespace, whose root (%%{python3_sitelib}/cc3d/) is owned by
# python3-compucell3d — so we depend on it and drop our duplicate namespace
# marker (see %%install). The Player drives the engine + VTK rendering, both
# pulled in transitively by python3-compucell3d (which Requires python3-vtk).
Requires:       python3-compucell3d
# setup.py declares no install_requires; the player imports these directly.
Requires:       %{py3_dist pyqt5}
Requires:       %{py3_dist pyqtgraph}
Requires:       %{py3_dist numpy}
Requires:       %{py3_dist pandas}
Requires:       %{py3_dist deprecated}
Requires:       python3-vtk

%description
The CompuCell3D Player is the real-time, interactive graphical front end for
running and visualizing Cellular Potts Model simulations. It renders cell
fields, concentration fields, and vector fields via VTK, with playback
controls, configuration panels, and parameter-scan launching. It is part of
the CompuCell3D desktop experience alongside the Twedit++ editor.

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install

# The cc3d namespace root and its (empty) cc3d/__init__.py marker are owned by
# python3-compucell3d. Remove the copy our wheel drops so the two packages do
# not both own cc3d/__init__.py.
rm -f %{buildroot}%{python3_sitelib}/cc3d/__init__.py

%files
%license LICENSE.txt
%doc README.rst ReleaseNotes.rst
%{_bindir}/cc3d-player5
%{_bindir}/cc3d-player5ParamScan
# Own only our namespace subpackage + dist metadata, NOT the cc3d/ root.
%{python3_sitelib}/cc3d/player5/
%{python3_sitelib}/cc3d_player5-%{version}.dist-info/

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 4.8.0-1
- Initial package: CC3D Player visualization companion for CompuCell3D 4.8.0.
- noarch Python app installing into the cc3d.player5 namespace; depends on
  python3-compucell3d for the cc3d namespace root (and transitive VTK) and
  drops the duplicate cc3d/__init__.py marker to avoid file-ownership conflict.
