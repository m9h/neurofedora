# gifticlib-config.cmake
# CMake config shim for system gifticlib (Fedora package gifticlib-devel).
# Provides imported target gifticlib::gifticlib.

if(TARGET gifticlib::gifticlib)
  return()
endif()

find_library(GIFTIIO_LIBRARY
  NAMES giftiio
  PATHS /usr/lib64 /usr/lib
  NO_DEFAULT_PATH
)

find_path(GIFTIIO_INCLUDE_DIR
  NAMES gifti_io.h
  PATH_SUFFIXES gifti
  PATHS /usr/include
  NO_DEFAULT_PATH
)

if(GIFTIIO_LIBRARY AND GIFTIIO_INCLUDE_DIR)
  add_library(gifticlib::gifticlib SHARED IMPORTED)
  set_target_properties(gifticlib::gifticlib PROPERTIES
    IMPORTED_LOCATION             "${GIFTIIO_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${GIFTIIO_INCLUDE_DIR}"
  )
  set(gifticlib_FOUND TRUE)
  set(GIFTICLIB_FOUND TRUE)
  set(gifticlib_LIBRARIES gifticlib::gifticlib)
  set(GIFTICLIB_LIBRARIES "${GIFTIIO_LIBRARY}")
  set(gifticlib_INCLUDE_DIRS "${GIFTIIO_INCLUDE_DIR}")
  set(GIFTICLIB_INCLUDE_DIRS "${GIFTIIO_INCLUDE_DIR}")
else()
  set(gifticlib_FOUND FALSE)
  set(GIFTICLIB_FOUND FALSE)
  if(gifticlib_FIND_REQUIRED)
    message(FATAL_ERROR "gifticlib: could not find libgiftiio or gifti_io.h. Install gifticlib-devel.")
  endif()
endif()

unset(GIFTIIO_LIBRARY CACHE)
unset(GIFTIIO_INCLUDE_DIR CACHE)
