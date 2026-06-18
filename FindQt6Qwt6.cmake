# FindQt6Qwt6.cmake - Find the Qwt library for Qt6
#
# Creates imported target Qwt::Qwt (as expected by MITK)
# Sets:
#   Qt6Qwt6_FOUND       - True if Qwt was found
#   QWT_INCLUDE_DIRS     - Qwt include directories
#   QWT_LIBRARIES        - Qwt libraries

find_path(QWT_INCLUDE_DIR
  NAMES qwt_plot.h
  PATHS
    /usr/include/qt6/qwt
    /usr/include/qwt
    /usr/local/include/qwt
  PATH_SUFFIXES qwt qwt6
)

find_library(QWT_LIBRARY
  NAMES qwt-qt6 qwt6 qwt
  PATHS /usr/lib64 /usr/lib /usr/local/lib64 /usr/local/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Qt6Qwt6
  REQUIRED_VARS QWT_LIBRARY QWT_INCLUDE_DIR
)

if(Qt6Qwt6_FOUND)
  set(QWT_LIBRARIES ${QWT_LIBRARY})
  set(QWT_INCLUDE_DIRS ${QWT_INCLUDE_DIR})

  if(NOT TARGET Qwt::Qwt)
    add_library(Qwt::Qwt UNKNOWN IMPORTED)
    set_target_properties(Qwt::Qwt PROPERTIES
      IMPORTED_LOCATION "${QWT_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${QWT_INCLUDE_DIR}"
    )
  endif()
endif()

mark_as_advanced(QWT_INCLUDE_DIR QWT_LIBRARY)
