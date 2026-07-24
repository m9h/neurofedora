cmake_minimum_required(VERSION 3.16)
project(neurofedora-itk-smoke CXX)

include(CTest)

# Pin ITK 5.4: on a box with both ITK5 and ITK6 devel installed, an
# unconstrained find_package(ITK) resolves to the higher-versioned ITK6 (its
# config-version file is AnyNewerVersion, so even "find_package(ITK 5.4)" accepts
# 6.0). The "itk" (ITK5) component would then silently build against ITK6 and, on
# aarch64 where ITK6's private libdir is off the loader path, fail 0/3 at runtime.
# Point find_package at the ITK-5.4 config dir directly (glob covers lib vs lib64
# and any 5.4.x patch level); the separate itk6 component covers 6.x.
file(GLOB _itk5_config_dirs /usr/lib*/cmake/ITK-5.4)
find_package(ITK 5.4 REQUIRED
  PATHS ${_itk5_config_dirs} NO_DEFAULT_PATH
  COMPONENTS
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
