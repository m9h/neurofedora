# Findargs.cmake — find module for the Taywee/args header-only argument
# parser (https://github.com/Taywee/args). QUIT vendors this as a bundled
# header (External/include/args.hxx) since args is not packaged in Fedora.
#
# Sets:
#   args_FOUND           - args was found
#   args_INCLUDE_DIR     - directory containing args.hxx
#   args_INCLUDE_DIRS    - alias of args_INCLUDE_DIR
# Imported target:
#   args::args           - INTERFACE target with the include dir set

find_path(args_INCLUDE_DIR
    NAMES args.hxx
    HINTS ${External_Include_DIR} ${CMAKE_SOURCE_DIR}/External/include
)
set(args_INCLUDE_DIRS ${args_INCLUDE_DIR})

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(args
    REQUIRED_VARS args_INCLUDE_DIR
)

if(args_FOUND AND NOT TARGET args::args)
    add_library(args::args INTERFACE IMPORTED)
    set_target_properties(args::args PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${args_INCLUDE_DIR}"
    )
endif()

mark_as_advanced(args_INCLUDE_DIR)
