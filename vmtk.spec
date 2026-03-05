%global commit 311f479266666666666666666666666666666666
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global checkout_date 20241029

Name:           vmtk
Version:        1.5.0^%{checkout_date}git%{shortcommit}
Release:        1%{?dist}
Summary:        The Vascular Modeling Toolkit

License:        BSD-3-Clause
URL:            http://www.vmtk.org/
Source0:        https://github.com/vmtk/vmtk/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  vtk-devel
BuildRequires:  InsightToolkit6-devel
BuildRequires:  vtkAddon-devel
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
BuildRequires:  python3-setuptools
BuildRequires:  python3-h5py
BuildRequires:  libX11-devel
BuildRequires:  libXt-devel
BuildRequires:  libGL-devel
BuildRequires:  libGLU-devel

%description
vmtk is a collection of libraries and tools for 3D reconstruction, 
geometric analysis, mesh generation and surface data analysis 
for image-based modeling of blood vessels.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package contains the header files and libraries for 
developing applications with %{name}.

%package -n     python3-%{name}
Summary:        Python 3 bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-vtk
Requires:       python3-vtkAddon

%description -n python3-%{name}
Python 3 bindings and scripts for the Vascular Modeling Toolkit.

%prep
%autosetup -n %{name}-%{commit}

%build
# Set VMTK_USE_SUPERBUILD=OFF to use system libraries
%cmake 
    -DVMTK_USE_SUPERBUILD:BOOL=OFF 
    -DUSE_SYSTEM_VTK:BOOL=ON 
    -DUSE_SYSTEM_ITK:BOOL=ON 
    -DVTK_VMTK_WRAP_PYTHON:BOOL=ON 
    -DVTK_VMTK_USE_VTK9:BOOL=ON 
    -DVMTK_PYTHON_VERSION:STRING=3 
    -DBUILD_SHARED_LIBS:BOOL=ON 
    -DVMTK_CONTRIB_SCRIPTS:BOOL=ON 
    -DBUILD_DOCUMENTATION:BOOL=OFF 
    -DITK_DIR:PATH=%{_libdir}/cmake/ITK-6.0 
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk-9.2

%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libdir}/lib*.so.*
%{_bindir}/vmtk*

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib*.so
%{_libdir}/cmake/%{name}/

%files -n python3-%{name}
%{python3_sitearch}/%{name}/

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.0^20241029git311f479-1
- Initial package for vmtk master branch (VTK9/ITK6 support)
