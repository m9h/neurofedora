# lapy — differential geometry on triangle/tetrahedra meshes: Laplace-Beltrami
# FEM solvers, ShapeDNA spectral shape descriptors, geodesics-in-heat, conformal
# mapping. Pulled in as a hard runtime dependency by 3D Slicer's EvolutionarySRep
# module (SlicerSkeletalRepresentation), which without it pip-installs at import.
# Pure Python; the numpy>=2 build requirement is only for the setuptools backend.

%global pypi_name lapy

Name:           python-%{pypi_name}
Version:        1.6.0
Release:        1%{?dist}
Summary:        Differential geometry on meshes (Laplace-Beltrami, FEM, ShapeDNA)

License:        MIT
URL:            https://github.com/Deep-MI/LaPy
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
LaPy computes Laplace-Beltrami eigenvalues and eigenfunctions on triangle and
tetrahedra meshes using a linear finite-element method, plus the geometry built
on top of that spectrum: ShapeDNA spectral shape descriptors, geodesics in heat,
mean-curvature flow, conformal mapping to the sphere, and mesh I/O for the
common neuroimaging surface formats.}

%description %_description

%package -n     python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %_description

%prep
%autosetup -p1 -n %{pypi_name}-%{version}

%generate_buildrequires
# No extras: the declared ones are build/doc/style/test tooling plus `chol`
# (scikit-sparse, not in Fedora). The runtime set (nibabel, numpy, plotly,
# psutil, scipy) is all packaged.
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md

%changelog
* Mon Jul 27 2026 Morgan Hough <morgan.hough@gmail.com> - 1.6.0-1
- Initial package. Required by 3D Slicer's EvolutionarySRep module, whose
  EvolutionarySRepUtil bootstrap otherwise attempts a network pip install of
  lapy at import time.
