Name:           python-fsleyes-props
Version:        1.11.0
Release:        1%{?dist}
Summary:        Object-attribute management for Python

License:        Apache-2.0
URL:            https://git.fmrib.ox.ac.uk/fsl/fsleyes/props
Source0:        %{pypi_source fsleyes-props}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-numpy

%description
fsleyes-props is a library which allows you to define object attributes,
and to automatically generate a GUI (wxPython) or CLI to edit those
attributes.

%package -n     python3-fsleyes-props
Summary:        %{summary}
Requires:       python3-numpy
Suggests:       python3-wxpython

%description -n python3-fsleyes-props
fsleyes-props is a library which allows you to define object attributes,
and to automatically generate a GUI (wxPython) or CLI to edit those
attributes.

%prep
%autosetup -n fsleyes-props-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fsleyes_props

%files -n python3-fsleyes-props -f %{pyproject_files}
%doc README.rst

%changelog
* Mon May 04 2026 Morgan Hough <morgan.hough@gmail.com> - 1.11.0-1
- Initial package
