Name:           python-wslink
Version:        2.5.7
Release:        2%{?dist}
Summary:        Python/JavaScript WebSocket transport layer used by trame

License:        BSD-3-Clause
URL:            https://github.com/Kitware/wslink
Source:         %{pypi_source wslink}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
wslink is the WebSocket-based RPC transport layer Kitware uses to bridge
Python servers with JavaScript clients. It is the channel trame-server,
trame-rca, and trame itself use to push state updates and stream rendered
frames to the browser. Requires aiohttp and msgpack at runtime.}

%description %_description

%package -n     python3-wslink
Summary:        %{summary}

%description -n python3-wslink %_description

%prep
%autosetup -p1 -n wslink-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files wslink

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-wslink -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Thu Jun 26 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.7-2
- Rebuild against Python 3.15 (rawhide). Release bump so the py3.15
  build strictly supersedes the lingering same-NVR py3.14 RPM that
  was still winning in the COPR buildroot repo.

* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.7-1
- Initial package for the trame-slicer dependency chain.
