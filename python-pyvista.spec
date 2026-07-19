%global pypi_name pyvista

Name:           python-%{pypi_name}
Version:        0.48.4
Release:        1%{?dist}
Summary:        3D plotting and mesh analysis through a streamlined interface to VTK

License:        MIT
URL:            https://github.com/pyvista/pyvista
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
PyVista is a helper module for the Visualization Toolkit (VTK) that wraps the
VTK library through NumPy and provides a Pythonic, well-documented interface for
3D plotting and mesh/volume analysis. It is the actively-developed, modern
successor to mayavi for VTK-based scientific visualization in Python.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
# Soft deps for the optional interactive web/Jupyter (trame) backend.
Recommends:     python3-trame
Recommends:     python3-trame-vtk
Recommends:     python3-trame-vuetify
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}

%check
# Top-level import smoke test (offscreen — no GPU/display in the builder). A full
# submodule scan trips on modules not meant to be imported standalone (pytest
# conftest, the Sphinx ext.* directives, and the optional trame/jupyter backends).
export PYVISTA_OFF_SCREEN=true
%{python3} -c "import pyvista; print('pyvista', pyvista.__version__)"

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.rst
%license LICENSE
%{_bindir}/pyvista

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.48.4-1
- Update to 0.48.4

* Sat Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 0.48.0-1
- Initial package: PyVista 0.48.0, the actively-developed Pythonic VTK interface
  for 3D plotting and mesh analysis (modern successor to mayavi). Net-new to
  Fedora; pure-Python (noarch) on system python3-vtk + the scientific stack.
