# FindANN.cmake - Find the ANN (Approximate Nearest Neighbor) library
#
# Sets:
#   ANN_FOUND        - True if ANN was found
#   ANN_INCLUDE_DIRS - ANN include directories
#   ANN_LIBRARIES    - ANN libraries to link against
#
# Also creates imported target ANN::ANN

find_path(ANN_INCLUDE_DIR
  NAMES ANN/ANN.h
  PATHS /usr/include /usr/local/include
)

find_library(ANN_LIBRARY
  NAMES ANN ann
  PATHS /usr/lib64 /usr/lib /usr/local/lib64 /usr/local/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(ANN
  REQUIRED_VARS ANN_LIBRARY ANN_INCLUDE_DIR
)

if(ANN_FOUND)
  set(ANN_LIBRARIES ${ANN_LIBRARY})
  set(ANN_INCLUDE_DIRS ${ANN_INCLUDE_DIR})

  if(NOT TARGET ANN::ANN)
    add_library(ANN::ANN UNKNOWN IMPORTED)
    set_target_properties(ANN::ANN PROPERTIES
      IMPORTED_LOCATION "${ANN_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${ANN_INCLUDE_DIR}"
    )
  endif()
endif()

mark_as_advanced(ANN_INCLUDE_DIR ANN_LIBRARY)
