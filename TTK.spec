%define debug_package %{nil}

Name:           TTK
Version:        4.0.1
Release:        4%{?dist}
Summary:        Tensor ToolKit for diffusion MRI (INRIA)

License:        BSD-2-Clause
URL:            https://github.com/medInria/TTK
Source0:        https://github.com/medInria/TTK/archive/refs/tags/v%{version}/TTK-%{version}.tar.gz

BuildRequires:  cmake >= 3.24
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit5-devel >= 5.4.6
# TTK uses VTK's stable PolyData/Points/CellArray/SmartPointer/IdType
# surface; that API hasn't changed 9.2 -> 9.5+. The historical
# `vtk-devel < 9.3` pin was for medInria-chain Qt5 coexistence on F43,
# which F44 no longer requires.
BuildRequires:  vtk-devel
# java-devel was needed because old VTK 9.2.6 cmake targets referenced
# JVM include paths transitively; with newer VTK it's not required, but
# keeping it cheap-as-insurance.
BuildRequires:  java-devel

%description
TTK (Tensor ToolKit) is a library for processing diffusion tensor images
(DTI) built on ITK and VTK. It provides tensor estimation, scalar map
computation, fiber tractography, and related algorithms. Developed at INRIA
for use with medInria.

Note: This is INRIA's Tensor ToolKit, not Kitware's Topology ToolKit.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       InsightToolkit5-devel >= 5.4.5
Requires:       vtk-devel

%description devel
Headers and cmake config files for TTK (Tensor ToolKit).

%prep
%autosetup -n TTK-%{version}

# Inject SOVERSION for shared libraries (upstream lacks versioning)
# Upstream uses ADD_LIBRARY(${TARGET_NAME} ...) so append to each CMakeLists.txt
for f in Common/CMakeLists.txt Algorithms/CMakeLists.txt IPF/CMakeLists.txt \
         Commands/ttkCommands/CMakeLists.txt Commands/ttkConvertCommands/CMakeLists.txt \
         Commands/ttkUtilCommands/CMakeLists.txt; do
  printf '\nset_target_properties(${TARGET_NAME} PROPERTIES VERSION %{version} SOVERSION 1)\n' >> "$f"
done

# Fix hardcoded lib/ install destinations to respect CMAKE_INSTALL_LIBDIR
sed -i 's|LIBRARY   DESTINATION lib$|LIBRARY   DESTINATION ${CMAKE_INSTALL_LIBDIR}|' CMake/export_and_install_libs.cmake
sed -i 's|ARCHIVE   DESTINATION lib$|ARCHIVE   DESTINATION ${CMAKE_INSTALL_LIBDIR}|' CMake/export_and_install_libs.cmake
# Fix cmake config install paths (only INSTALL_DESTINATION and DESTINATION lines, not build-tree paths)
sed -i 's|INSTALL_DESTINATION lib/cmake/|INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|' CMake/export_and_install_libs.cmake
sed -i '/^SET(ConfigPackageLocation/s|lib/cmake/|${CMAKE_INSTALL_LIBDIR}/cmake/|' CMake/export_and_install_libs.cmake
sed -i '/^  DESTINATION lib\/cmake/s|lib/cmake/|${CMAKE_INSTALL_LIBDIR}/cmake/|' CMake/export_and_install_libs.cmake
# Fix top-level CMakeLists.txt install paths (only DESTINATION, not build-tree paths)
sed -i 's|INSTALL_DESTINATION lib/cmake/|INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|' CMakeLists.txt
sed -i 's| DESTINATION lib/cmake/| DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/|g' CMakeLists.txt
sed -i 's| DESTINATION  lib/cmake/| DESTINATION  ${CMAKE_INSTALL_LIBDIR}/cmake/|g' CMakeLists.txt

# ---------------------------------------------------------
# FIX: VTK 9.2.6 GetNextCell takes const vtkIdType*& (not vtkIdType*&)
# Fix all non-const vtkIdType pointer vars used with GetNextCell
# ---------------------------------------------------------
sed -i 's/vtkIdType\* ptids/const vtkIdType* ptids/' Algorithms/itkFiberBundleStatisticsCalculator.cxx
sed -i 's/vtkIdType \*pts = 0/const vtkIdType *pts = 0/' Algorithms/itkVTKFibersToITKFibers.txx
sed -i 's/vtkIdType npt, \*pto/vtkIdType npt; const vtkIdType *pto/' Commands/itkConsolidateFiberBundleCommand.cxx

# ---------------------------------------------------------
# FIX: ITK 5.4 NumericTraits::GetLength passes rvalue — need const ref
# ---------------------------------------------------------
sed -i 's/GetLength(Tensor<\([^>]*\)> &t)/GetLength(const Tensor<\1> \&t)/g' \
  Common/itkNumericTraitsTensorPixel2.h Common/itkNumericTraitsTensorPixel2.cxx

# ---------------------------------------------------------
# FIX: ApplyMatrix ambiguity — vnl_matrix_fixed converts to both
# itk::Matrix and vnl_matrix. Disambiguate with explicit cast.
# Affects itkTensor.txx, itkMatrixOffsetTensorTransformBase.txx,
# and itkResampleTensorImageFilter.txx.
# ---------------------------------------------------------
sed -i 's/tensor\.ApplyMatrix ( m_Rigid\.GetTranspose() )/tensor.ApplyMatrix ( vnl_matrix<TScalarType>(m_Rigid.GetTranspose()) )/' \
  Common/itkMatrixOffsetTensorTransformBase.txx
sed -i 's/tensor\.ApplyMatrix ( m_Rigid\.GetVnlMatrix() )/tensor.ApplyMatrix ( vnl_matrix<TScalarType>(m_Rigid.GetVnlMatrix()) )/' \
  Common/itkMatrixOffsetTensorTransformBase.txx
# Internal delegation in ApplyMatrix(const MatrixType&) — R.GetVnlMatrix() returns vnl_matrix_fixed
sed -i 's/this->ApplyMatrix (R\.GetVnlMatrix() )/this->ApplyMatrix (vnl_matrix<T>(R.GetVnlMatrix()) )/' \
  Common/itkTensor.txx
# GetDirection().GetTranspose() returns vnl_matrix_fixed
sed -i 's/value\.ApplyMatrix (this->GetOutput()->GetDirection()\.GetTranspose())/value.ApplyMatrix (vnl_matrix<double>(this->GetOutput()->GetDirection().GetTranspose()))/' \
  Algorithms/itkResampleTensorImageFilter.txx

# ---------------------------------------------------------
# FIX: itkTypeMacro wrong class names (GCC 15 -Wtemplate-body)
# ---------------------------------------------------------
sed -i 's/itkTypeMacro (AddGaussianNoiseTensorImageFilter,/itkTypeMacro (AddGaussianNoiseImageFilter,/' \
  Algorithms/itkAddGaussianNoiseImageFilter.h
sed -i 's/itkTypeMacro (AddRicianNoiseTensorImageFilter,/itkTypeMacro (AddRicianNoiseImageFilter,/' \
  Algorithms/itkAddRicianNoiseImageFilter.h

# ---------------------------------------------------------
# FIX: ITK 5.4 BooleanStdVectorType is vector<itk::Boolean> not vector<bool>
# ---------------------------------------------------------
sed -i 's/std::vector <bool> ValidTimeStepList/BooleanStdVectorType ValidTimeStepList/' \
  Common/itkDenseFiniteDifferenceImageFilter2.h

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"

%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_CXX_STANDARD=17 \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4 \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_EXECUTABLES=OFF \
    -DTTK_USE_GMM=OFF \
    -DTTK_USE_MKL=OFF \
    -DTTK_USE_ACML=OFF

%cmake_build

%install
%cmake_install

%ldconfig_scriptlets

%files
%license LICENSE.txt
%{_libdir}/libITKTensor.so.*
%{_libdir}/libttkAlgorithms.so.*
%{_libdir}/libITKProgramFactory.so.*
%{_libdir}/libttkCommands.so.*
%{_libdir}/libttkConvertCommands.so.*
%{_libdir}/libttkUtilCommands.so.*

%files devel
%{_includedir}/Common/
%{_includedir}/IPF/
%{_includedir}/Algorithms/
%{_includedir}/Commands/
%{_includedir}/Registration/
%{_includedir}/ttkConfigure.h
%{_libdir}/libITKTensor.so
%{_libdir}/libttkAlgorithms.so
%{_libdir}/libITKProgramFactory.so
%{_libdir}/libttkCommands.so
%{_libdir}/libttkConvertCommands.so
%{_libdir}/libttkUtilCommands.so
%{_libdir}/cmake/TTK/
%{_libdir}/cmake/ITKTensor/
%{_libdir}/cmake/ttkAlgorithms/
%{_libdir}/cmake/ITKProgramFactory/
%{_libdir}/cmake/Registration/
%{_libdir}/cmake/ttkCommands/
%{_libdir}/cmake/ttkConvertCommands/
%{_libdir}/cmake/ttkUtilCommands/

%changelog
* Tue May 19 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-4
- Drop vtk-devel < 9.3 BR for F44 — TTK's VTK API surface
  (PolyData/Points/CellArray/SmartPointer/IdType) is stable across
  VTK 9.2 -> 9.5+; the existing `const vtkIdType*` GetNextCell sed
  patches still apply against VTK 9.5.2. Qt-free at the source level
  (zero QObject/QString hits).
- Bump InsightToolkit5-devel requirement to 5.4.6

* Tue Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-3
- Fix VTK 9.2.6 GetNextCell const vtkIdType* API change
- Fix ITK 5.4 NumericTraits::GetLength rvalue binding (const ref)
- Fix ApplyMatrix ambiguity with vnl_matrix_fixed to vnl_matrix cast
- Fix itkTypeMacro wrong class names (GCC 15 -Wtemplate-body)
- Fix ITK 5.4 BooleanStdVectorType (vector of itk::Boolean, not bool)
- Add java-devel BuildRequires: VTK 9.2.6 cmake targets reference JVM paths

* Tue Mar 03 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.1-1
- Initial package for TTK 4.0.1 (INRIA Tensor ToolKit)
- Shared libraries with injected SOVERSION
- Disable executables and optional GMM/MKL/ACML features
