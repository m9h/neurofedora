Name:           python-trame-vtk
Version:        2.11.13
Release:        2%{?dist}
Summary:        VTK web rendering bindings for trame

License:        BSD-3-Clause
URL:            https://github.com/Kitware/trame-vtk
Source:         %{pypi_source trame_vtk}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-trame-client

%global _description %{expand:
trame-vtk integrates VTK's web rendering pipeline into trame
applications. It bridges Python-side VTK rendering objects with the
JavaScript-side viewer widgets that ship in trame-client, enabling
remote (server-side) and client-side rendering of 3D scenes.}

%description %_description

%package -n     python3-trame-vtk
Summary:        %{summary}
Requires:       python3-trame-client
# Owns the shared trame/ namespace stubs excluded from %%files below.
Requires:       python3-trame

%description -n python3-trame-vtk %_description

%prep
%autosetup -p1 -n trame_vtk-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files trame trame_vtk

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame-vtk -f %{pyproject_files}
%license LICENSE
# The trame/ namespace is shared by python3-trame, -trame-vtk and -trame-vuetify:
# every wheel ships its own copy of the four namespace __init__.py stubs, and RPM
# byte-compiles each copy separately, so the .pyc contents differ and dnf refuses
# the transaction with "file ... conflicts between attempted installs". Installing
# any two of the three was impossible -- which in turn made 3dslicer-srep
# uninstallable, because python3-pyvista Recommends all three.
# Let python3-trame own the namespace stubs (it is the package the other two
# already depend on transitively) and exclude them here. Directories may be
# co-owned; only the regular files conflict.
%exclude %{python3_sitelib}/trame/__init__.py
%exclude %{python3_sitelib}/trame/__pycache__/__init__.*
%exclude %{python3_sitelib}/trame/modules/__init__.py
%exclude %{python3_sitelib}/trame/modules/__pycache__/__init__.*
%exclude %{python3_sitelib}/trame/tools/__init__.py
%exclude %{python3_sitelib}/trame/tools/__pycache__/__init__.*
%exclude %{python3_sitelib}/trame/widgets/__init__.py
%exclude %{python3_sitelib}/trame/widgets/__pycache__/__init__.*
%doc README.rst

%changelog
* Fri Jul 31 2026 Morgan Hough <morgan.hough@gmail.com> - 2.11.13-2
- Stop claiming the shared trame/ namespace stubs. All three trame packages
  (-trame, -trame-vtk, -trame-vuetify) shipped their own copy of the four namespace
  __init__.py files, and RPM byte-compiles each copy separately, so the .pyc contents
  differ and dnf aborts with "file ... conflicts between attempted installs".
  Installing any two of the three was impossible, which also made 3dslicer-srep
  uninstallable since python3-pyvista Recommends all three. Let python3-trame own the
  stubs, %%exclude them here, and Require it. Directories may be co-owned; only the
  regular files conflicted.

* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.11.13-1
- Update to 2.11.13

* Thu Jun 26 2026 Morgan Hough <morgan.hough@gmail.com> - 2.11.12-2
- Rebuild against Python 3.15 (rawhide). Release bump so the py3.15
  build strictly supersedes the lingering same-NVR py3.14 RPM that
  was still winning in the COPR buildroot repo.

* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 2.11.12-1
- Update to 2.11.12 (current upstream; freshness sweep 2026-06-14)

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 2.11.8-1
- Initial package for the trame-slicer dependency chain.
