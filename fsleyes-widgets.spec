Name:           python-fsleyes-widgets
Version:        0.14.3
Release:        1%{?dist}
Summary:        Custom wxPython widgets used by FSLeyes

License:        Apache-2.0
URL:            https://git.fmrib.ox.ac.uk/fsl/fsleyes/widgets
Source0:        %{pypi_source fsleyes-widgets}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-numpy
BuildRequires:  python3-matplotlib
BuildRequires:  python3-wxpython

%description
fsleyes-widgets is a collection of custom wxPython widgets used by FSLeyes.

%package -n     python3-fsleyes-widgets
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-matplotlib
Requires:       python3-wxpython

%description -n python3-fsleyes-widgets
fsleyes-widgets is a collection of custom wxPython widgets used by FSLeyes.

%prep
%autosetup -n fsleyes-widgets-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fsleyes_widgets

%files -n python3-fsleyes-widgets -f %{pyproject_files}
%doc README.rst

%changelog
* Mon May 04 2026 Morgan Hough <morgan.hough@gmail.com> - 0.14.3-1
- Initial package
