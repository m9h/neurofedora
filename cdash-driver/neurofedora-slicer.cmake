# ctest -S driver for Slicer CLI smoke dashboard.
# CLI-only — no build step needed (CMakeLists has no targets).
# Parallelism capped at 8 (half the legion).

cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED DASHBOARD_MODEL)
  set(DASHBOARD_MODEL "Experimental")
endif()
if(NOT DEFINED PARALLEL)
  set(PARALLEL 8)
endif()

set(CTEST_SOURCE_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/tests-slicer")
set(CTEST_BINARY_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/build-slicer-${DASHBOARD_MODEL}")

configure_file(
  "${CTEST_SCRIPT_DIRECTORY}/CTestConfig.cmake"
  "${CTEST_SOURCE_DIRECTORY}/CTestConfig.cmake"
  COPYONLY)

execute_process(COMMAND hostname OUTPUT_VARIABLE HOSTNAME OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND rpm -q --qf "%{VERSION}-%{RELEASE}" 3dslicer
                OUTPUT_VARIABLE SLICER_RPM_VER OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE SLICER_RPM_RC ERROR_QUIET)
execute_process(COMMAND rpm -E "%{?fedora}"
                OUTPUT_VARIABLE FEDORA_VER OUTPUT_STRIP_TRAILING_WHITESPACE)

if(NOT SLICER_RPM_RC EQUAL 0)
  message(FATAL_ERROR "Slicer is not installed — cannot run Slicer dashboard")
endif()

set(CTEST_SITE "${HOSTNAME}")
set(CTEST_BUILD_NAME "f${FEDORA_VER}-slicer-${SLICER_RPM_VER}")
set(CTEST_CMAKE_GENERATOR "Ninja")
set(CTEST_BUILD_CONFIGURATION "Release")

ctest_empty_binary_directory("${CTEST_BINARY_DIRECTORY}")
ctest_start("${DASHBOARD_MODEL}")
ctest_configure()
ctest_test(PARALLEL_LEVEL ${PARALLEL})
ctest_submit()
