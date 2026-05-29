Name:           python-trame-vtk
Version:        2.11.8
Release:        1%{?dist}
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
%doc README.rst

%changelog
* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 2.11.8-1
- Initial package for the trame-slicer dependency chain.
