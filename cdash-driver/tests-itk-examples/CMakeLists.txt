cmake_minimum_required(VERSION 3.16)
project(neurofedora-itk-examples CXX)

include(CTest)

find_package(ITK 5 REQUIRED)
include(${ITK_USE_FILE})

# The upstream examples CMakeLists fatal-errors unless this is ON. The flag
# only gates the assertion — find_package(ITK) above already wires the modules.
set(ITK_BUILD_DEFAULT_MODULES ON CACHE BOOL "" FORCE)

# Some example modules require components not present on every install. Limit
# build noise by allowing the upstream gating to skip them.
set(ITK_USE_FFTWF ${ITK_USE_FFTWF} CACHE BOOL "" FORCE)
set(ITK_USE_FFTWD ${ITK_USE_FFTWD} CACHE BOOL "" FORCE)

set(ITK_EXAMPLES_SRC "/usr/share/InsightToolkit5/examples")
if(NOT EXISTS "${ITK_EXAMPLES_SRC}/CMakeLists.txt")
  message(FATAL_ERROR "InsightToolkit5-examples not installed (no ${ITK_EXAMPLES_SRC})")
endif()

# Build the upstream examples tree out-of-source under our binary dir.
add_subdirectory("${ITK_EXAMPLES_SRC}" "${CMAKE_BINARY_DIR}/examples-build")
