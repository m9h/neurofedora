%define debug_package %{nil}

%global pypi_name fmm3dpy
%global repo_name FMM3D
%global forgeurl https://github.com/flatironinstitute/%{repo_name}
%global tag v%{version}

Name:           python-%{pypi_name}
Version:        1.0.3
Release:        2%{?dist}
Summary:        Fast Multipole Method in Python (FMM3D wrapper)

License:        Apache-2.0
URL:            https://fmm3d.readthedocs.io/
Source0:        %{forgeurl}/archive/%{tag}/%{repo_name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  make
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-numpy
BuildRequires:  meson
BuildRequires:  sed

%description
fmm3dpy provides Python bindings for the Flatiron Institute's FMM3D library. 
It offers Fast Multipole Method (FMM) implementations for the Laplace, 
Helmholtz, and Maxwell equations.

%package -n python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy

%description -n python3-%{pypi_name}
This package provides the Python 3 library for fmm3dpy.

%prep
%autosetup -n %{repo_name}-%{version}

# FIX THE MAKEFILE
# The static lib must be compiled with -fPIC so it can be linked into the python shared object.
sed -i 's/FFLAGS =/FFLAGS = -fPIC -fallow-argument-mismatch/g' makefile
sed -i 's/CFLAGS =/CFLAGS = -fPIC/g' makefile

%build
# STEP 1: Build the static library (lib-static/libfmm3d.a)
export OMP_NUM_THREADS=1
%make_build lib

# STEP 2: Manually compile Python extensions using f2py
cd python

cat > manual_builder.py <<EOF
import os
import subprocess
import sys

# --- SETUP ABSOLUTE PATHS ---
cwd = os.getcwd()
root_dir = os.path.abspath(os.path.join(cwd, '..'))
src_dir = os.path.join(root_dir, 'src')
lib_dir = os.path.join(root_dir, 'lib-static')
inc_common = os.path.join(src_dir, 'Common')

# Helper to join paths
def get_sources(subfolder, file_list):
    return [os.path.join(src_dir, subfolder, f) for f in file_list]

# --- DEFINE FILE LISTS ---
list_helm = ['hfmm3dwrap.f','hfmm3dwrap_vec.f','helmkernels.f']
list_lap = ['lfmm3dwrap.f','lfmm3dwrap_vec.f','lapkernels.f']

st_opts = ['_s','_t','_st']
c_opts = ['_c','_d','_cd']
p_optsh = ['_p','_g']
p_optsl = ['_p','_g','_h']
c_opts2 = ['c','d','cd']
p_optsh2 = ['p','g']
p_optsl2 = ['p','g','h']

list_int_helm = []
list_int_helm_vec = []
for st in st_opts:
    for cd in c_opts:
        for pg in p_optsh:
            list_int_helm.append('hfmm3d'+st+cd+pg)
            list_int_helm_vec.append('hfmm3d'+st+cd+pg+'_vec')

list_int_lap = []
list_int_lap_vec = []
for st in st_opts:
    for cd in c_opts:
        for pg in p_optsl:
            list_int_lap.append('lfmm3d'+st+cd+pg)
            list_int_lap_vec.append('lfmm3d'+st+cd+pg+'_vec')

list_int_helm_dir = []
for cd in c_opts2:
    for pg in p_optsh2:
        list_int_helm_dir.append('h3ddirect'+cd+pg)

list_int_lap_dir = []
for cd in c_opts2:
    for pg in p_optsl2:
        list_int_lap_dir.append('l3ddirect'+cd+pg)

# --- DEFINE EXTENSIONS ---
extensions = [
    {
        'name': 'hfmm3d_fortran',
        'sources': get_sources('Helmholtz', list_helm),
        'only': list_int_helm + list_int_helm_vec + list_int_helm_dir
    },
    {
        'name': 'lfmm3d_fortran',
        'sources': get_sources('Laplace', list_lap),
        'only': list_int_lap + list_int_lap_vec + list_int_lap_dir
    },
    {
        'name': 'emfmm3d_fortran',
        'sources': get_sources('Helmholtz', list_helm) + [os.path.join(src_dir, 'Maxwell', 'emfmm3d.f90')],
        'only': ['emfmm3d', 'em3ddirect']
    },
    {
        'name': 'stfmm3d_fortran',
        'sources': get_sources('Laplace', list_lap) + [os.path.join(src_dir, 'Stokes', 'stfmm3d.f'), os.path.join(src_dir, 'Stokes', 'stokkernels.f')],
        'only': ['stfmm3d', 'st3ddirectstokg', 'st3ddirectstokstrsg']
    }
]

# --- BUILD LOOP ---
for ext in extensions:
    print(f"Building {ext['name']}...")
    cmd = [
        sys.executable, '-m', 'numpy.f2py',
        '-c',
        '--f90flags=-fallow-argument-mismatch -fPIC -O2 -fopenmp',
        '--f77flags=-fallow-argument-mismatch -fPIC -O2 -fopenmp',
        f'-I{inc_common}', 
        f'-L{lib_dir}', '-lfmm3d', '-lgomp',
        '-m', ext['name']
    ] + ext['sources'] + ['only:'] + ext['only'] + [':']
    
    subprocess.check_call(cmd)
    
    # Move the generated .so file into the package directory
    subprocess.check_call(f"mv {ext['name']}*.so fmm3dpy/", shell=True)

EOF

%{python3} manual_builder.py

# STEP 3: Create a minimal setup.py that includes the .so files
cat > setup.py <<EOF
from setuptools import setup, find_packages

setup(
    name="fmm3dpy",
    version="%{version}",
    packages=find_packages(),
    package_data={'fmm3dpy': ['*.so']},
    install_requires=["numpy"],
)
EOF

%pyproject_wheel

%install
cd python
%pyproject_install
%pyproject_save_files fmm3dpy

%check
export PYTHONPATH=%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}
%{python3} -c "import fmm3dpy; print('fmm3dpy imported successfully')"

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE

%changelog
* Tue Mar 10 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.3-2
- Add meson BuildRequires (numpy.f2py uses meson backend on Python 3.14+)

* Tue Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.3-1
- Update to 1.0.3 and use improved build process
