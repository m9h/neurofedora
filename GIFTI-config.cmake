# GIFTIConfig.cmake
# CMake config shim providing find_package(GIFTI) with GIFTI::giftiio target.
# This is the target name expected by AFNI's cmake build system.
# Wraps the system gifticlib-devel package.

if(TARGET GIFTI::giftiio)
  return()
endif()

find_library(_GIFTI_LIBRARY
  NAMES giftiio
  PATHS /usr/lib64 /usr/lib
  NO_DEFAULT_PATH
)

find_path(_GIFTI_INCLUDE_DIR
  NAMES gifti_io.h
  PATH_SUFFIXES gifti
  PATHS /usr/include
  NO_DEFAULT_PATH
)

if(_GIFTI_LIBRARY AND _GIFTI_INCLUDE_DIR)
  add_library(GIFTI::giftiio SHARED IMPORTED)
  set_target_properties(GIFTI::giftiio PROPERTIES
    IMPORTED_LOCATION             "${_GIFTI_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${_GIFTI_INCLUDE_DIR}"
  )
  set(GIFTI_FOUND TRUE)
  set(GIFTI_LIBRARIES GIFTI::giftiio)
  set(GIFTI_INCLUDE_DIRS "${_GIFTI_INCLUDE_DIR}")
else()
  set(GIFTI_FOUND FALSE)
  if(GIFTI_FIND_REQUIRED)
    message(FATAL_ERROR "GIFTI: could not find libgiftiio or gifti_io.h. Install gifticlib-devel.")
  endif()
endif()

unset(_GIFTI_LIBRARY CACHE)
unset(_GIFTI_INCLUDE_DIR CACHE)
