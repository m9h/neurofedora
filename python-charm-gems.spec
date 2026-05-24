%define debug_package %{nil}

%global pypi_name charm-gems
%global pkg_name charm_gems

Name:           python-%{pypi_name}
Version:        1.3.3
Release:        2%{?dist}
Summary:        Python bindings for the GEMS segmentation package

License:        GPL-3.0-only
URL:            https://github.com/simnibs/charm-gems
Source0:        %{url}/archive/v%{version}/%{pypi_name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.9
BuildRequires:  make
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-numpy
BuildRequires:  python3-pybind11
BuildRequires:  pybind11-devel
BuildRequires:  InsightToolkit5-devel >= 5.4.5
BuildRequires:  zlib-devel
# ITK 5.4.5 VtkGlue cmake config transitively requires VTK at find_package time
BuildRequires:  vtk-devel < 9.3
BuildRequires:  java-devel
BuildRequires:  libtheora-devel

%description
charm-gems provides Python bindings for the GEMS (Generative Model for
brain MRI segmentation) library. It is used by SimNIBS's CHARM tool for
creating individualized head models from MRI scans.

%package -n python3-%{pkg_name}
Summary:        %{summary}
Requires:       python3-numpy

%description -n python3-%{pkg_name}
Python bindings for the GEMS segmentation package used by SimNIBS.

%prep
%autosetup -n %{pypi_name}-%{version}

# Remove bundled ITK and pybind11 submodule stubs (use system packages)
rm -rf ITK pybind11

# Patch CMakeLists.txt to use system pybind11 via find_package
sed -i 's|add_subdirectory(pybind11)|find_package(pybind11 REQUIRED)|' CMakeLists.txt

# Relax -Werror (GCC 15 triggers new warnings on old code)
sed -i 's/-Werror//' CMakeLists.txt

# Fix x86-only SSE flags for aarch64 compatibility
sed -i 's/-msse2 -mfpmath=sse//' gems/CMakeLists.txt
sed -i 's/-msse2 -mfpmath=sse//' gems_python/CMakeLists.txt

# Patch setup.py to pass ITK_DIR and pybind11_DIR to cmake
sed -i "s|'-H.'|'-H.', '-DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4', '-Dpybind11_DIR=%{_datadir}/cmake/pybind11'|" setup.py

# Fix C++11 → C++17 for ITK 5.4 compatibility
sed -i 's/CMAKE_CXX_STANDARD 11/CMAKE_CXX_STANDARD 17/' CMakeLists.txt
sed -i 's/CMAKE_CXX_STANDARD 11/CMAKE_CXX_STANDARD 17/' gems/CMakeLists.txt

# ---- ITK 4.13 → 5.4 API migration ----
# itkExceptionObject.h must not be included directly
find . \( -name '*.h' -o -name '*.cxx' -o -name '*.cpp' \) \
  -exec grep -l 'itkExceptionObject' {} + | \
  xargs -r sed -i 's|itkExceptionObject\.h|itkMacro.h|g'

# Threading API changes
find . \( -name '*.h' -o -name '*.cxx' \) -exec sed -i \
  -e 's|ITK_THREAD_RETURN_TYPE|itk::ITK_THREAD_RETURN_TYPE|g' \
  -e 's|ITK_THREAD_RETURN_VALUE|itk::ITK_THREAD_RETURN_DEFAULT_VALUE|g' \
  -e 's|itk::MultiThreader::ThreadInfoStruct|itk::PlatformMultiThreader::WorkUnitInfo|g' \
  -e 's|->ThreadID|->WorkUnitID|g' \
  -e 's|->NumberOfThreads|->NumberOfWorkUnits|g' \
  -e 's|itk::SimpleFastMutexLock|std::mutex|g' \
  -e 's|\.Lock()|.lock()|g' \
  -e 's|\.Unlock()|.unlock()|g' \
  -e 's|itk::MultiThreader::GetGlobalDefaultNumberOfThreads|itk::MultiThreaderBase::GetGlobalDefaultNumberOfThreads|g' \
  -e 's|itk::MultiThreader::Pointer|itk::PlatformMultiThreader::Pointer|g' \
  -e 's|itk::MultiThreader::New|itk::PlatformMultiThreader::New|g' \
  {} +
# Add missing ITK 5 threading headers
sed -i '/#include "kvlAtlasMesh.h"/a #include "itkPlatformMultiThreader.h"' gems/kvlAtlasMeshRasterizor.h
sed -i '1i #include <mutex>' gems/kvlAtlasMeshRasterizor.cxx
sed -i '1i #include "itkMultiThreaderBase.h"' gems/kvlAtlasParameterEstimator.cxx

# ITK 5.x SmartPointer: convert '= 0' to '= nullptr' for known Pointer members
# Whitelist approach avoids false positives on int/double member assignments
for m in m_CostFunction m_BinnedImage m_Image m_MeshCollection \
         m_CompressionLookupTable m_LabelImage m_ProbabilityImage \
         m_PositionGradient m_TargetPoints m_LabelStatistics \
         m_PointParameters m_Cells m_ReferenceTetrahedronInfos \
         m_ReferencePosition m_CellLinks m_Mesh m_Calculator \
         m_Position m_Gradient m_OldGradient m_OldSearchDirection; do
  find gems gems_python \( -name '*.cxx' -o -name '*.h' \) \
    -exec sed -i "s/${m} = 0;/${m} = nullptr;/g" {} +
done
# Convert 'Pointer/ConstPointer varname = 0' local variable declarations
find gems gems_python \( -name '*.cxx' -o -name '*.h' \) \
  -exec sed -i -E 's/(Pointer\s+\w+)\s*=\s*0;/\1 = nullptr;/g' {} +
# Convert 'return 0;' → 'return nullptr;' (all instances are in Pointer-returning functions)
find gems gems_python \( -name '*.cxx' -o -name '*.h' \) \
  -exec sed -i 's/return 0;/return nullptr;/g' {} +

%build
export ITK_DIR=%{_prefix}/lib/cmake/ITK-5.4
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pkg_name}

%check
export PYTHONPATH=%{buildroot}%{python3_sitearch}
%{python3} -c "import charm_gems; print('charm_gems imported successfully')"

%files -n python3-%{pkg_name} -f %{pyproject_files}
%license LICENSE

%changelog
* Wed Mar 11 2026 Morgan Hough <morgan.hough@gmail.com> - 1.3.3-2
- Fix SmartPointer nullptr conversion: use whitelist instead of blanket regex

* Tue Mar 10 2026 Morgan Hough <morgan.hough@gmail.com> - 1.3.3-1
- Initial package
