Name:           python-trame-client
Version:        3.12.3
Release:        1%{?dist}
Summary:        Internal browser-side client of trame

License:        MIT
URL:            https://github.com/Kitware/trame-client
Source:         %{pypi_source trame_client}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-trame-common

%global _description %{expand:
trame-client ships the JavaScript bundle and the Python registration
shim that exposes Vue-component bindings to trame applications. It is
the browser-side runtime trame-server pairs with; every UI widget
(vuetify, vtk, deck.gl, etc.) builds on it.}

%description %_description

%package -n     python3-trame-client
Summary:        %{summary}
Requires:       python3-trame-common

%description -n python3-trame-client %_description

%prep
%autosetup -p1 -n trame_client-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# Two top-level modules: trame (namespace pkg with submodules) and trame_client.
%pyproject_save_files trame trame_client

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame-client -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 3.12.3-1
- Initial package for the trame-slicer dependency chain.
