%define debug_package %{nil}
%define _python_dist_allow_version_zero 1

%global pypi_name samseg
%global commit e86d8762c9140d5e3d4250e90d7ec947a575c355
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           python-%{pypi_name}
Version:        0.5a0
Release:        1%{?dist}
Summary:        Sequence Adaptive Multimodal SEGmentation

License:        MIT
URL:            https://github.com/freesurfer/samseg
Source0:        %{url}/archive/%{commit}/%{pypi_name}-%{shortcommit}.tar.gz
Patch0:         samseg-system-deps.patch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-versioneer
BuildRequires:  python3-pybind11
BuildRequires:  pybind11-devel
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4.5
BuildRequires:  zlib-devel
# ITK 5.4.5 VtkGlue cmake config transitively requires VTK at find_package time
BuildRequires:  vtk-devel < 9.3
BuildRequires:  java-devel
BuildRequires:  libtheora-devel
BuildRequires:  qt5-qtbase-devel
# Needed for %check (samseg __init__.py imports surfa and sklearn at top level)
BuildRequires:  python3-surfa
BuildRequires:  python3-scikit-learn
BuildRequires:  python3-scipy
BuildRequires:  python3-nibabel
BuildRequires:  python3-pillow
BuildRequires:  python3-xxhash

%description
SAMSEG (Sequence Adaptive Multimodal SEGmentation) is a tool for robustly
segmenting various brain structures from head MRI scans without requiring
extensive preprocessing.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-surfa
Requires:       python3-scikit-learn
Requires:       python3-numba

%description -n python3-%{pypi_name}
SAMSEG (Sequence Adaptive Multimodal SEGmentation) is a tool for robustly
segmenting various brain structures from head MRI scans without requiring
extensive preprocessing.

%prep
%setup -q -n %{pypi_name}-%{commit}
%patch -P 0 -p0

# Remove bundled dirs to ensure we use system libraries
rm -rf pybind11 ITK

# Fix C++11 -> C++17 for ITK 5.4 / GCC 15 compatibility
sed -i 's/CMAKE_CXX_STANDARD 11/CMAKE_CXX_STANDARD 17/' CMakeLists.txt

# Remove -Werror flags from subdirectory cmake files
find . -name CMakeLists.txt -exec sed -i 's/-Werror//' {} +

# Fix x86-only SSE flags for aarch64
find . -name CMakeLists.txt -exec sed -i 's/-msse2 -mfpmath=sse//' {} +

# itkExceptionObject.h must not be included directly in ITK 5
find . \( -name '*.h' -o -name '*.cxx' -o -name '*.cpp' \) \
  -exec grep -l 'itkExceptionObject' {} + | \
  xargs -r sed -i 's|itkExceptionObject\.h|itkMacro.h|g'

# ITK 5.x SmartPointer: convert '= 0' to '= nullptr' for known Pointer members
for m in m_CostFunction m_BinnedImage m_Image m_MeshCollection \
         m_CompressionLookupTable m_LabelImage m_ProbabilityImage \
         m_PositionGradient m_TargetPoints m_LabelStatistics \
         m_PointParameters m_Cells m_ReferenceTetrahedronInfos \
         m_ReferencePosition m_CellLinks m_Mesh m_Calculator \
         m_Position m_Gradient m_OldGradient m_OldSearchDirection; do
  find gems \( -name '*.cxx' -o -name '*.h' \) \
    -exec sed -i "s/${m} = 0;/${m} = nullptr;/g" {} +
done
# Convert 'Pointer/ConstPointer varname = 0' local variable declarations
find gems \( -name '*.cxx' -o -name '*.h' \) \
  -exec sed -i -E 's/(Pointer\s+\w+)\s*=\s*0;/\1 = nullptr;/g' {} +
# Convert 'return 0;' -> 'return nullptr;' in Pointer-returning functions
find gems \( -name '*.cxx' -o -name '*.h' \) \
  -exec sed -i 's/return 0;/return nullptr;/g' {} +

# Remove pinned ml-dtypes version and git-pinned surfa URL from setup.cfg
sed -i '/ml-dtypes==/d' setup.cfg
sed -i '/surfa @ git+/d' setup.cfg

# Relax numpy pinning
sed -i 's/numpy >= 2.0/numpy/' setup.cfg

%build
export ITK_DIR=%{_prefix}/lib/cmake/ITK-5.4
export pybind11_DIR=%{_datadir}/cmake/pybind11
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
# Load the C extension .so directly -- samseg __init__.py imports numba which may not be available
cd /
%{python3} -c "
import importlib.util, sys, os
so_dir = '%{buildroot}%{python3_sitearch}/samseg/gems'
for f in os.listdir(so_dir):
    if f.startswith('gemsbindings') and f.endswith('.so'):
        spec = importlib.util.spec_from_file_location('gemsbindings', os.path.join(so_dir, f))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print('gemsbindings loaded successfully')
        break
"

%files -n python3-%{pypi_name} -f %{pyproject_files}
%{_bindir}/computeTissueConcentrations
%{_bindir}/gems_compute_atlas_probs
%{_bindir}/merge_add_mesh_alphas
%{_bindir}/prepareAtlasDirectory
%{_bindir}/run_samseg
%{_bindir}/run_samseg_long
%{_bindir}/sbtiv
%{_bindir}/segment_subregions

%changelog
* Wed Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 0.5a0-1
- Update to 0.5a (new commit e86d876)
- Remove pinned ml-dtypes and git-pinned surfa from setup.cfg
- Relax numpy version requirement

* Wed Mar 11 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4a0-3
- Add VTK transitive BuildRequires (ITK VtkGlue cmake config)
- Add ITK 5 SmartPointer nullptr conversion and itkExceptionObject fix
- Suppress empty debug package

* Tue Mar 10 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4a0-2
- Fix: use InsightToolkit5-devel instead of nonexistent InsightToolkit6-devel
- Fix: use C++17 for ITK 5.4 / GCC 15 compatibility
- Add surfa, scikit-learn, numba runtime Requires

* Tue Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4a0-1
- Initial package for SimNIBS dependency
