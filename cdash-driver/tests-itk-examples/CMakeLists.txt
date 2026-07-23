cmake_minimum_required(VERSION 3.16)
project(neurofedora-itk-examples CXX)

# BUILD_TESTING must be OFF before any include(CTest)/add_subdirectory so the
# upstream examples skip their test/ subdirs. Those subdirs call itk_add_test
# (an ITK-source-tree macro absent from the install) and reference
# ITK_DATA_ROOT / ExternalData paths that aren't shipped with the RPM. We
# only want the example *programs* built — that's the packaging signal.
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)

find_package(ITK 5 REQUIRED)
include(${ITK_USE_FILE})

set(ITK_BUILD_DEFAULT_MODULES ON CACHE BOOL "" FORCE)
set(ITK_USE_FFTWF ${ITK_USE_FFTWF} CACHE BOOL "" FORCE)
set(ITK_USE_FFTWD ${ITK_USE_FFTWD} CACHE BOOL "" FORCE)

set(ITK_EXAMPLES_SRC "/usr/share/InsightToolkit5/examples")
if(NOT EXISTS "${ITK_EXAMPLES_SRC}/CMakeLists.txt")
  message(FATAL_ERROR "InsightToolkit5-examples not installed (no ${ITK_EXAMPLES_SRC})")
endif()

add_subdirectory("${ITK_EXAMPLES_SRC}" "${CMAKE_BINARY_DIR}/examples-build")

# One smoke test that runs a known example with valid args, confirming the
# build linked correctly. Build success itself is the main signal — submitted
# via Build.xml regardless of this test's outcome.
enable_testing()
# ImageReadWrite's hardcoded pixel type is signed short — PNG round-trip
# fails because PNG only supports unsigned. Use the MetaImage round-trip,
# which works with the default pixel type.
add_test(NAME itk-examples-smoke-ImageReadWrite
         COMMAND $<TARGET_FILE:ImageReadWrite>
                 "${ITK_EXAMPLES_SRC}/Data/BrainProtonDensity3Slices.mha"
                 "${CMAKE_BINARY_DIR}/BrainProtonDensity3Slices-roundtrip.mha")
