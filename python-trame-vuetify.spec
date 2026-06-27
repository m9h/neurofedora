Name:           python-trame-vuetify
Version:        3.2.2
Release:        2%{?dist}
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
%doc README.rst

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 3.2.2-2
- Rebuild against Python 3.15 (rawhide). Release bump so the py3.15 build
  supersedes the lingering same-NVR py3.14 RPM in the COPR repo.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 3.2.2-1
- Initial package for the trame-slicer dependency chain.
