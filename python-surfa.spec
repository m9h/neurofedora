%global pypi_name surfa

Name:           python-%{pypi_name}
Version:        0.6.3
Release:        1%{?dist}
Summary:        Utilities for medical image and surface processing

License:        MIT
URL:            https://github.com/freesurfer/surfa
Source0:        %{url}/archive/v%{version}/%{pypi_name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-Cython >= 3.0
BuildRequires:  python3-numpy
BuildRequires:  python3-scipy
BuildRequires:  python3-nibabel
BuildRequires:  python3-pillow
BuildRequires:  python3-xxhash

%description
Surfa is a collection of Python utilities for medical image analysis and
mesh-based surface processing. It provides tools that operate on 3D image
arrays and triangular meshes with consideration of their representation in
a world (or scanner) coordinate system.

%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-nibabel >= 2.1
Requires:       python3-pillow
Requires:       python3-xxhash

%description -n python3-%{pypi_name}
Surfa is a collection of Python utilities for medical image analysis and
mesh-based surface processing.

%prep
%autosetup -n %{pypi_name}-%{version}

# Remove abi3 wheel tag override — build a normal platform wheel
sed -i '/bdist_wheel_abi3/d' setup.py
sed -i '/from wheel.bdist_wheel import bdist_wheel/d' setup.py
sed -i '/class bdist_wheel_abi3/,/return python, abi, plat/d' setup.py
sed -i 's/"cmdclass": {"bdist_wheel": bdist_wheel_abi3}//' setup.py
sed -i '/Py_LIMITED_API/d' setup.py
sed -i '/py_limited_api/d' setup.py

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
# Run from / to avoid source tree shadowing the installed package
cd /
PYTHONPATH=%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib} \
  %{python3} -c "import surfa; print('surfa', surfa.__version__)"

%files -n python3-%{pypi_name} -f %{pyproject_files}
# License is MIT (declared in setup.py) but upstream has no standalone license file

%changelog
* Tue Mar 10 2026 Morgan Hough <morgan.hough@gmail.com> - 0.6.3-1
- Initial package
