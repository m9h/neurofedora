cmake_minimum_required(VERSION 3.16)
project(neurofedora-vtk-extended NONE)

include(CTest)

# Scoped to known-headless modules. Add more once we know which need a display
# or vtk-data side-loading. Each binary's subtests are discovered at configure
# time by parsing its no-args catalog output (exit 255, output: "  N. SubName").
set(VTK_TEST_BINARIES
  vtkCommonArchiveCxxTests
  vtkCommonColorCxxTests
  vtkCommonComputationalGeometryCxxTests
  vtkCommonCoreCxxTests
  vtkCommonDataModelCxxTests
  vtkCommonExecutionModelCxxTests
  vtkCommonMathCxxTests
  vtkCommonMiscCxxTests
  vtkCommonSystemCxxTests
  vtkCommonTransformsCxxTests
  vtkFiltersCoreCxxTests
  vtkFiltersExtractionCxxTests
  vtkFiltersGeneralCxxTests
  vtkFiltersGeometryCxxTests
  vtkIOImageCxxTests
  vtkIOLegacyCxxTests
  vtkIOXMLCxxTests
)

set(VTK_DATA_DIR "/usr/share/vtkdata")

set(_registered 0)
foreach(bin_name IN LISTS VTK_TEST_BINARIES)
  find_program(BIN_${bin_name} NAMES ${bin_name})
  if(NOT BIN_${bin_name})
    message(STATUS "skip ${bin_name}: not on PATH")
    continue()
  endif()

  execute_process(COMMAND ${BIN_${bin_name}}
                  OUTPUT_VARIABLE catalog
                  ERROR_QUIET
                  TIMEOUT 30)

  # Catalog lines look like "  12. TestSomething"
  string(REGEX MATCHALL "[\n^][ \t]*[0-9]+\\.[ \t]+[A-Za-z_][A-Za-z0-9_]*"
         lines "${catalog}")

  set(_per_bin 0)
  foreach(line IN LISTS lines)
    string(REGEX REPLACE ".*[0-9]+\\.[ \t]+" "" subtest "${line}")
    string(STRIP "${subtest}" subtest)
    if(subtest STREQUAL "")
      continue()
    endif()
    add_test(NAME ${bin_name}/${subtest}
             COMMAND ${BIN_${bin_name}} ${subtest} -D ${VTK_DATA_DIR})
    set_tests_properties(${bin_name}/${subtest} PROPERTIES
                         TIMEOUT 120
                         LABELS "vtk-extended;${bin_name}")
    math(EXPR _per_bin "${_per_bin} + 1")
    math(EXPR _registered "${_registered} + 1")
  endforeach()
  message(STATUS "${bin_name}: ${_per_bin} subtests")
endforeach()

message(STATUS "vtk-extended: ${_registered} total ctest entries registered")
