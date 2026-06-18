# Findlz4.cmake - Find the LZ4 compression library
#
# Creates imported targets:
#   LZ4::lz4_shared  - Shared library target (as expected by MITK)
# Sets:
#   lz4_FOUND         - True if LZ4 was found
#   LZ4_INCLUDE_DIRS  - LZ4 include directories
#   LZ4_LIBRARIES     - LZ4 libraries

find_path(LZ4_INCLUDE_DIR
  NAMES lz4.h
  PATHS /usr/include /usr/local/include
)

find_library(LZ4_LIBRARY
  NAMES lz4
  PATHS /usr/lib64 /usr/lib /usr/local/lib64 /usr/local/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(lz4
  REQUIRED_VARS LZ4_LIBRARY LZ4_INCLUDE_DIR
)

if(lz4_FOUND)
  set(LZ4_LIBRARIES ${LZ4_LIBRARY})
  set(LZ4_INCLUDE_DIRS ${LZ4_INCLUDE_DIR})

  if(NOT TARGET LZ4::lz4_shared)
    add_library(LZ4::lz4_shared UNKNOWN IMPORTED)
    set_target_properties(LZ4::lz4_shared PROPERTIES
      IMPORTED_LOCATION "${LZ4_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${LZ4_INCLUDE_DIR}"
    )
  endif()
endif()

mark_as_advanced(LZ4_INCLUDE_DIR LZ4_LIBRARY)
