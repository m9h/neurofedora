cmake_minimum_required(VERSION 3.16)
project(neurofedora-itk-smoke CXX)

include(CTest)

find_package(ITK REQUIRED COMPONENTS
  ITKCommon
  ITKIOImageBase
  ITKIONIFTI
  ITKImageFilterBase
  ITKSmoothing
)
include(${ITK_USE_FILE})

add_executable(smoke_itk smoke_itk.cxx)
target_link_libraries(smoke_itk PRIVATE ${ITK_LIBRARIES})

add_test(NAME itk-version COMMAND smoke_itk version)
add_test(NAME itk-gaussian-filter COMMAND smoke_itk gaussian)
add_test(NAME itk-nifti-roundtrip COMMAND smoke_itk nifti)
