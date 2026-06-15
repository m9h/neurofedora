Name:           cc3d-twedit5
Version:        4.8.0
Release:        1%{?dist}
Summary:        Twedit++ — model/Python editor (IDE) for CompuCell3D

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
# marker (see %%install).
Requires:       python3-compucell3d
# setup.py declares no install_requires; the editor imports these directly.
Requires:       %{py3_dist pyqt5}
Requires:       %{py3_dist numpy}

%description
Twedit++ is the CompuCell3D integrated editor for authoring CC3D models,
Python steppables, and MorpheusML/CC3DML. It ships CC3D-aware plugins
(project wizard, snippet/template helpers, CC3DML and C++/Python helpers)
and is part of the CompuCell3D desktop experience alongside the Player.

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
%{_bindir}/cc3d-twedit5
# Own only our namespace subpackage + dist metadata, NOT the cc3d/ root.
%{python3_sitelib}/cc3d/twedit5/
%{python3_sitelib}/cc3d_twedit5-%{version}.dist-info/

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 4.8.0-1
- Initial package: Twedit++ editor companion for CompuCell3D 4.8.0.
- noarch Python app installing into the cc3d.twedit5 namespace; depends on
  python3-compucell3d for the cc3d namespace root and drops the duplicate
  cc3d/__init__.py marker to avoid file-ownership conflict.
