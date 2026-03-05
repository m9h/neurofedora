Name:           simnibs
Version:        4.5.0
Release:        1%{?dist}
Summary:        Simulation of Non-Invasive Brain Stimulation

License:        GPL-3.0-only
URL:            http://simnibs.org
Source0:        https://github.com/simnibs/simnibs/archive/v%{version}/simnibs-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-setuptools-scm
BuildRequires:  python3-cython
BuildRequires:  python3-numpy
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
# For CGAL extensions
BuildRequires:  cgal-devel
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  zlib-devel
BuildRequires:  tbb-devel
BuildRequires:  eigen3-devel
BuildRequires:  python3-fmm3dpy
BuildRequires:  python3-pygpc
BuildRequires:  python3-samseg

%description
SimNIBS is a software package for the simulation of non-invasive brain
stimulation (NIBS).

%package -n     python3-simnibs
Summary:        Python 3 module for simnibs
Requires:       simnibs-data = %{version}-%{release}
Requires:       simnibs-tools = %{version}-%{release}
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-h5py
Requires:       python3-nibabel
Requires:       python3-pillow
Requires:       python3-requests
Requires:       python3-jsonschema
Requires:       python3-numba
Requires:       python3-fmm3dpy
Requires:       python3-pygpc
Requires:       python3-samseg
Suggests:       fsl

%description -n python3-simnibs
Python 3 module for simnibs.

%package        data
Summary:        Data files for SimNIBS
BuildArch:      noarch

%description    data
Data files for SimNIBS including templates and coil models.

%package        tools
Summary:        Compiled tools and extensions for SimNIBS
Requires:       gmsh
Requires:       mmg
# meshfix is currently missing from Fedora but requested by simnibs
# Requires:       meshfix

%description    tools
Compiled C++/Cython extensions and wrappers for SimNIBS.

%package        gui
Summary:        Graphical User Interface for SimNIBS
Requires:       python3-simnibs = %{version}-%{release}
Requires:       python3-qt5
Requires:       python3-pyopengl

%description    gui
Graphical User Interface for SimNIBS based on PyQt5.

%prep
%autosetup -n simnibs-%{version}

# Remove bundled binaries and wheels
rm -rf simnibs/external/bin/*
rm -rf simnibs/external/wheels/*

# Relax version requirements in pyproject.toml
sed -i 's/fmm3dpy==1.0.0/fmm3dpy>=1.0.0/' pyproject.toml
sed -i 's/pygpc==0.4.1/pygpc>=0.4.1/' pyproject.toml

%build
# Set CONDA_PREFIX to /usr to bypass the check in setup.py
export CONDA_PREFIX=%{_prefix}
export CXXFLAGS="%{optflags}"
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files simnibs

%check
# Basic import test
%pyproject_check_import

%files -n python3-simnibs -f %{pyproject_files}
%license LICENSE.txt
%exclude %{python3_sitearch}/simnibs/resources/
%exclude %{python3_sitearch}/simnibs/_internal_resources/
%exclude %{python3_sitearch}/simnibs/examples/
%exclude %{python3_sitearch}/simnibs/GUI/

%files data
%{python3_sitearch}/simnibs/resources/
%{python3_sitearch}/simnibs/_internal_resources/
%{python3_sitearch}/simnibs/examples/

%files tools
# Compiled extensions are included via pyproject_files in python3-simnibs
# This package acts as a metadata container for system tools dependencies

%files gui
%{python3_sitearch}/simnibs/GUI/
%{_bindir}/simnibs_gui

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 4.5.0-1
- Initial package for SimNIBS 4.5.0
- Refined dependencies and build process
