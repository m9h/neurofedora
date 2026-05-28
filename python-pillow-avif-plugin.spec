Name:           python-pillow-avif-plugin
Version:        1.5.5
Release:        1%{?dist}
Summary:        Pillow plugin adding AVIF image format support via libavif

License:        MIT
URL:            https://github.com/fdintino/pillow-avif-plugin
Source:         %{pypi_source pillow_avif_plugin}

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pillow
BuildRequires:  gcc
BuildRequires:  libavif-devel

%global _description %{expand:
A Pillow plugin that adds AVIF read/write support via libavif. Registers
the AVIF codec into PIL.Image so calling code can open and save .avif
files transparently. Used by trame-slicer for AVIF screenshot/snapshot
handling.}

%description %_description

%package -n     python3-pillow-avif-plugin
Summary:        %{summary}
Requires:       python3-pillow

%description -n python3-pillow-avif-plugin %_description

%prep
%autosetup -p1 -n pillow_avif_plugin-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pillow_avif

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-pillow-avif-plugin -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.5-1
- Initial package for the trame-slicer dependency chain.
- Links against Fedora system libavif (no vendored copies).
