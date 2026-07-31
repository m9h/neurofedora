Name:           python-trame-vuetify
Version:        3.2.2
Release:        3%{?dist}
Summary:        Vuetify (Material-Design) component bindings for trame

License:        MIT
URL:            https://github.com/Kitware/trame-vuetify
Source:         %{pypi_source trame_vuetify}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-trame-client

%global _description %{expand:
trame-vuetify exposes Vuetify's Material Design component set
(buttons, cards, sliders, dialogs, layouts, etc.) as Python widget
classes consumable from trame applications. The default UI layer for
most trame-based apps including trame-slicer.}

%description %_description

%package -n     python3-trame-vuetify
Summary:        %{summary}
Requires:       python3-trame-client
# Owns the shared trame/ namespace stubs excluded from %%files below.
Requires:       python3-trame

%description -n python3-trame-vuetify %_description

%prep
%autosetup -p1 -n trame_vuetify-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files trame trame_vuetify

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame-vuetify -f %{pyproject_files}
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
* Fri Jul 31 2026 Morgan Hough <morgan.hough@gmail.com> - 3.2.2-3
- Stop claiming the shared trame/ namespace stubs. All three trame packages
  (-trame, -trame-vtk, -trame-vuetify) shipped their own copy of the four namespace
  __init__.py files, and RPM byte-compiles each copy separately, so the .pyc contents
  differ and dnf aborts with "file ... conflicts between attempted installs".
  Installing any two of the three was impossible, which also made 3dslicer-srep
  uninstallable since python3-pyvista Recommends all three. Let python3-trame own the
  stubs, %%exclude them here, and Require it. Directories may be co-owned; only the
  regular files conflicted.

* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 3.2.2-2
- Rebuild against Python 3.15 (rawhide). Release bump so the py3.15 build
  supersedes the lingering same-NVR py3.14 RPM in the COPR repo.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 3.2.2-1
- Initial package for the trame-slicer dependency chain.
