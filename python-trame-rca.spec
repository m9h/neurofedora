Name:           python-trame-rca
Version:        2.7.0
Release:        1%{?dist}
Summary:        Remote Controlled Area image streaming for trame

License:        Apache-2.0
URL:            https://github.com/Kitware/trame-rca
Source:         %{pypi_source trame_rca}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-trame-client
BuildRequires:  python3-trame-common
BuildRequires:  python3-wslink
BuildRequires:  python3-numpy
BuildRequires:  python3-packaging
BuildRequires:  python3-pillow

%global _description %{expand:
trame-rca (Remote Controlled Area) streams rendered images and frames
from a Python server to a browser-side viewport over WebSocket.
trame-slicer uses it to push 2D/3D slice views and DICOM renderings
to the web client without copying full meshes over the wire.}

%description %_description

%package -n     python3-trame-rca
Summary:        %{summary}
Requires:       python3-trame-client
Requires:       python3-trame-common
Requires:       python3-wslink
Requires:       python3-numpy
Requires:       python3-packaging
Requires:       python3-pillow

%description -n python3-trame-rca %_description

%prep
%autosetup -p1 -n trame_rca-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files trame trame_rca

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame-rca -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.7.0-1
- Update to 2.7.0

* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 2.4.3-2
- Rebuild against Python 3.15 (rawhide). Release bump so the py3.15 build
  supersedes the lingering same-NVR py3.14 RPM in the COPR repo.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 2.4.3-1
- Initial package for the trame-slicer dependency chain.
