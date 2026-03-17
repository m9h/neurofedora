%define debug_package %{nil}

Name:           simnibs
Version:        4.5.0
Release:        4%{?dist}
Summary:        Simulation of Non-Invasive Brain Stimulation

License:        GPL-3.0-only
URL:            http://simnibs.org
Source0:        https://github.com/simnibs/simnibs/archive/v%{version}/simnibs-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools >= 68
BuildRequires:  python3-setuptools_scm >= 8
BuildRequires:  python3-Cython
BuildRequires:  python3-numpy
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-build
# For CGAL mesh extensions
BuildRequires:  CGAL-devel
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  zlib-devel
BuildRequires:  tbb-devel
BuildRequires:  eigen3-devel

%description
SimNIBS is a software package for the simulation of non-invasive brain
stimulation (NIBS). It enables realistic calculations of the electric
field induced by transcranial magnetic stimulation (TMS) and transcranial
direct current stimulation (tDCS).

%package -n     python3-simnibs
Summary:        Python 3 module for SimNIBS
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
Requires:       python3-charm_gems
Requires:       python3-petsc4py
Requires:       python3-qt5
Suggests:       fsl

%description -n python3-simnibs
Python 3 module for SimNIBS.

%package        data
Summary:        Data files for SimNIBS

%description    data
Data files for SimNIBS including templates and coil models.

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

# Relax pinned version requirements
sed -i 's/fmm3dpy==1.0.0/fmm3dpy>=1.0.0/' pyproject.toml
sed -i 's/pygpc==0.4.1/pygpc>=0.4.1/' pyproject.toml

# Remove conda-only deps that are system libs on Fedora
sed -i '/mkl ;/d' pyproject.toml
sed -i '/tbb ;/d' pyproject.toml

# Pin numpy < 2 for build (upstream requirement)
sed -i "s/'numpy >= 1.26, < 2'/'numpy'/" pyproject.toml

# Remove petsc4py from build deps (not yet packaged, only needed at runtime)
sed -i '/"petsc4py"/d' pyproject.toml

# ---- Patch setup.py for system (non-conda) build ----
# Remove conda requirement check
sed -i '/is_conda/d; /No conda/d; /Cannot run setup without conda/d' setup.py

# Replace CONDA_PREFIX library/include paths with system paths (Linux block)
sed -i "s|os.path.join(os.environ\['CONDA_PREFIX'\], 'lib')|'/usr/%{_lib}'|g" setup.py
sed -i "s|os.path.join(os.environ\['CONDA_PREFIX'\], 'include','eigen3')|'/usr/include/eigen3'|g" setup.py

# Fix C++ standard from gnu++14 to gnu++17 (CGAL 5.x / GCC 15)
sed -i "s/-std=gnu++14/-std=gnu++17/" setup.py

# Remove distutils import (removed in Python 3.12+)
sed -i '/from distutils.dep_util import newer_group/d' setup.py
# Remove the changed_meshing block that used newer_group (assigned but never used)
sed -i '/changed_meshing = (/,/^        )$/d' setup.py

# ---- Fix C source files for GCC 15 / Cython compilation ----
# Python.h defines I as _Complex_I (C99 complex macro); this clashes with
# parameter names in CAT C utilities included via Cython 'cdef extern from'
sed -i '/#include "limits.h"/a #undef I' simnibs/segmentation/cat_c_utils/cat_vol_eidist.c
sed -i '/#include "float.h"/a #undef I' simnibs/segmentation/cat_c_utils/cat_vbdist.c

# Fix FINFINITY macro trailing semicolons (causes parse errors in expressions)
sed -i 's/#define FINFINITY (FLT_MAX+FLT_MAX);/#define FINFINITY (FLT_MAX+FLT_MAX)/' \
    simnibs/segmentation/cat_c_utils/cat_vol_eidist.c
sed -i 's|#define FINFINITY 1.0f/0.0f;|#define FINFINITY (1.0f/0.0f)|' \
    simnibs/segmentation/cat_c_utils/cat_vol_eidist.c

# ---- Fix CGAL 6 const-correctness bug ----
# CGAL 6.0.3 Add_features_in_domain<false>::operator() takes Image_3& (non-const)
# but Labeled_mesh_domain_3 passes const Image_3 weights_. Create local patched copy.
mkdir -p cgal_fix/CGAL
cp /usr/include/CGAL/Labeled_mesh_domain_3.h cgal_fix/CGAL/
sed -i 's/void operator()(const CGAL::Image_3&, CGAL::Image_3&,/void operator()(const CGAL::Image_3\&, const CGAL::Image_3\&,/' \
    cgal_fix/CGAL/Labeled_mesh_domain_3.h

# ---- Port _cgal_intersect.cpp from CGAL 5 to CGAL 6 ----
# CGAL 6 replaced boost::optional with std::optional
sed -i 's/boost::optional/std::optional/g' simnibs/mesh_tools/cgal/_cgal_intersect.cpp
# In CGAL 6, inter->second is directly SM_Face_index (not a variant)
sed -i 's/boost::get<CGAL::SM_Face_index>(inter->second)/(std::size_t)inter->second/g' \
    simnibs/mesh_tools/cgal/_cgal_intersect.cpp
# In CGAL 6, inter->first is std::variant<Point, Segment>; use std::get_if for pointer access
sed -i 's/boost::get<Point>(\&(inter->first))/std::get_if<Point>(\&(inter->first))/g' \
    simnibs/mesh_tools/cgal/_cgal_intersect.cpp
sed -i 's/boost::get<Segment>(\&(inter->first))/std::get_if<Segment>(\&(inter->first))/g' \
    simnibs/mesh_tools/cgal/_cgal_intersect.cpp

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -I$PWD/cgal_fix"
export CFLAGS="%{optflags} -Wno-error=implicit-function-declaration -Wno-error=incompatible-pointer-types"
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files simnibs

%check
# Full import requires scipy, numba, h5py, etc. — just verify extensions built
cd /
%{python3} -c "
import os, struct
site = '%{buildroot}%{python3_sitearch}/simnibs'
so_files = []
for root, dirs, files in os.walk(site):
    for f in files:
        if f.endswith('.so'):
            path = os.path.join(root, f)
            with open(path, 'rb') as fh:
                assert fh.read(4) == b'\x7fELF', f'{f} is not a valid ELF'
            so_files.append(f)
assert len(so_files) >= 4, f'Expected at least 4 .so files, found {len(so_files)}'
print(f'Found {len(so_files)} extension modules: {so_files}')
"

%files -n python3-simnibs -f %{pyproject_files}
%license LICENSE.txt
%{_bindir}/add_tissues_to_upsampled
%{_bindir}/calc_B
%{_bindir}/charm
%{_bindir}/charm_tms
%{_bindir}/coil2nifti
%{_bindir}/convert_3_to_4
%{_bindir}/download_coils
%{_bindir}/eeg_positions
%{_bindir}/expand_to_center_surround
%{_bindir}/get_eeg_positions
%{_bindir}/get_fields_at_coordinates
%{_bindir}/maskmesh
%{_bindir}/meshmesh
%{_bindir}/mni2subject
%{_bindir}/mni2subject_coords
%{_bindir}/msh2cortex
%{_bindir}/msh2nii
%{_bindir}/nii2msh
%{_bindir}/postinstall_simnibs
%{_bindir}/prepare_eeg_forward
%{_bindir}/prepare_eeg_montage
%{_bindir}/prepare_tdcs_leadfield
%{_bindir}/register
%{_bindir}/simnibs
%{_bindir}/subject2mni
%{_bindir}/subject2mni_coords
%{_bindir}/subject_atlas
%exclude %{python3_sitearch}/simnibs/resources/
%exclude %{python3_sitearch}/simnibs/_internal_resources/
%exclude %{python3_sitearch}/simnibs/examples/
%exclude %{python3_sitearch}/simnibs/GUI/

%files data
%{python3_sitearch}/simnibs/resources/
%{python3_sitearch}/simnibs/_internal_resources/
%{python3_sitearch}/simnibs/examples/

%files gui
%{python3_sitearch}/simnibs/GUI/
%{_bindir}/simnibs_gui

%changelog
* Wed Mar 11 2026 Morgan Hough <morgan.hough@gmail.com> - 4.5.0-4
- Fix C99 complex I macro clash with CAT C utilities (undef I)
- Fix FINFINITY macro trailing semicolons
- Fix distutils newer_group removal for Python 3.12+
- Add CFLAGS for GCC 15 C compilation compatibility
- Work around CGAL 6.0.3 const-correctness bug in Add_features_in_domain

* Wed Mar 11 2026 Morgan Hough <morgan.hough@gmail.com> - 4.5.0-3
- Patch setup.py for non-conda system build
- Use system CGAL/eigen3/gmp/mpfr paths instead of CONDA_PREFIX
- Fix C++ standard to gnu++17 for GCC 15 / CGAL 5.x
- Set SETUPTOOLS_SCM_PRETEND_VERSION for non-git tarball builds
- Remove petsc4py from build deps (not yet available)

* Tue Mar 10 2026 Morgan Hough <morgan.hough@gmail.com> - 4.5.0-2
- Fix package names: cgal-devel to CGAL-devel, setuptools-scm to setuptools_scm
- Add charm_gems and petsc4py runtime Requires
- Remove tools subpackage (extensions are in python3-simnibs)
- Remove mkl/tbb conda-only deps from pyproject.toml

* Tue Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 4.5.0-1
- Initial package for SimNIBS 4.5.0
