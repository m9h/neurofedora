# ctest -S driver for ITK5 examples dashboard.
# Builds the upstream examples tree (271 programs, 206 tests) and runs all of them.
# Heavy: ~30-60 minutes of compile at -j8 on the legion. Designed for nightly cron.

cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED DASHBOARD_MODEL)
  set(DASHBOARD_MODEL "Experimental")
endif()
if(NOT DEFINED PARALLEL)
  set(PARALLEL 8)
endif()

set(CTEST_SOURCE_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/tests-itk-examples")
set(CTEST_BINARY_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/build-itk-examples-${DASHBOARD_MODEL}")

configure_file(
  "${CTEST_SCRIPT_DIRECTORY}/CTestConfig.cmake"
  "${CTEST_SOURCE_DIRECTORY}/CTestConfig.cmake"
  COPYONLY)

execute_process(COMMAND hostname OUTPUT_VARIABLE HOSTNAME OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND rpm -q --qf "%{VERSION}-%{RELEASE}" InsightToolkit5-examples
                OUTPUT_VARIABLE ITKEX_RPM_VER OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE ITKEX_RPM_RC ERROR_QUIET)
execute_process(COMMAND rpm -E "%{?fedora}"
                OUTPUT_VARIABLE FEDORA_VER OUTPUT_STRIP_TRAILING_WHITESPACE)

if(NOT ITKEX_RPM_RC EQUAL 0)
  message(FATAL_ERROR "InsightToolkit5-examples not installed — cannot run itk-examples dashboard")
endif()

set(CTEST_SITE "${HOSTNAME}")
set(CTEST_BUILD_NAME "f${FEDORA_VER}-itk-examples-${ITKEX_RPM_VER}")
set(CTEST_CMAKE_GENERATOR "Ninja")
set(CTEST_BUILD_CONFIGURATION "Release")
set(CTEST_BUILD_FLAGS "-j${PARALLEL}")

# Test stage runs ~206 tests; give them generous parallelism and a per-test cap.
set(CTEST_TEST_TIMEOUT 300)

ctest_empty_binary_directory("${CTEST_BINARY_DIRECTORY}")
ctest_start("${DASHBOARD_MODEL}")
ctest_configure(OPTIONS "-DCMAKE_BUILD_TYPE=Release")
ctest_build(FLAGS "-j${PARALLEL}")
ctest_test(PARALLEL_LEVEL ${PARALLEL})
ctest_submit()
