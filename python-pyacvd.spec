# pyacvd — uniform surface remeshing via ACVD (Approximated Centroidal Voronoi
# Diagrams) clustering, exposed as a pyvista accessor. Pulled in as a hard
# runtime dependency by 3D Slicer's EvolutionarySRep module
# (SlicerSkeletalRepresentation), which without it pip-installs at import.
#
# Compiled: a nanobind C++ extension built through scikit-build-core/CMake.
# Unrelated to the separately packaged `acvd` (the original C++/VTK ACVD tool) —
# pyacvd carries its own clustering implementation and does not link it.

%global pypi_name pyacvd

Name:           python-%{pypi_name}
Version:        0.4.0
Release:        1%{?dist}
Summary:        Uniform surface remeshing for pyvista meshes (ACVD clustering)

License:        MIT
URL:            https://github.com/pyvista/pyacvd
Source0:        %{pypi_source %{pypi_name}}

BuildRequires:  python3-devel
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  python3-scikit-build-core
BuildRequires:  python3-nanobind

%global _description %{expand:
pyacvd uniformly remeshes triangular surface meshes using ACVD (Approximated
Centroidal Voronoi Diagram) clustering: it clusters the surface into
near-equal-area regions and rebuilds the mesh from the cluster centroids,
producing well-conditioned, near-isotropic triangles. It plugs into pyvista as
an `acvd` mesh accessor.}

%description %_description

%package -n     python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %_description

%prep
%autosetup -p1 -n %{pypi_name}-%{version}

# Upstream pins `vtk~=9.5` on aarch64 only, purely because PyPI had no ARM64 vtk
# wheels below 9.5 -- it is a wheel-availability workaround, not an API bound.
# Against distro VTK it is actively wrong: it excludes 9.6, which is what this
# COPR ships, so the dependency would be unsatisfiable on aarch64. VTK comes in
# via pyvista's own dependency anyway; drop the line.
sed -i '/^  "vtk~=9\.5 ; sys_platform/d' pyproject.toml
grep -q 'vtk~=9.5' pyproject.toml && exit 1 || :

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.rst

%changelog
* Mon Jul 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4.0-1
- Initial package. Required by 3D Slicer's EvolutionarySRep module, whose
  EvolutionarySRepUtil bootstrap otherwise attempts a network pip install of
  pyacvd at import time.
- Drop the aarch64-only `vtk~=9.5` pin: it is a PyPI-wheel workaround that
  excludes the VTK 9.6.2 this COPR ships.
