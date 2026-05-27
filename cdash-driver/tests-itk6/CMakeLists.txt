cmake_minimum_required(VERSION 3.16)
project(neurofedora-itk6-smoke CXX)

include(CTest)

# Pin to ITK 6.x — coexists with ITK 5.x on the system.
find_package(ITK 6 REQUIRED COMPONENTS
  ITKCommon
  ITKIOImageBase
  ITKIONIFTI
  ITKImageFilterBase
  ITKSmoothing
)
include(${ITK_USE_FILE})

add_executable(smoke_itk6 smoke_itk6.cxx)
target_link_libraries(smoke_itk6 PRIVATE ${ITK_LIBRARIES})

add_test(NAME itk6-version COMMAND smoke_itk6 version)
add_test(NAME itk6-gaussian-filter COMMAND smoke_itk6 gaussian)
add_test(NAME itk6-nifti-roundtrip COMMAND smoke_itk6 nifti)
