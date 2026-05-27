# ctest -S driver for the ITK smoke dashboard.
# Usage:
#   ctest -V -S neurofedora-itk.cmake -DDASHBOARD_MODEL=Experimental
# Models: Experimental | Continuous | Nightly
# Parallelism capped at 8 (half the legion). See feedback_legion_resource_cap memory.

cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED DASHBOARD_MODEL)
  set(DASHBOARD_MODEL "Experimental")
endif()
if(NOT DEFINED PARALLEL)
  set(PARALLEL 8)
endif()

set(CTEST_SOURCE_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/tests-itk")
set(CTEST_BINARY_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/build-itk-${DASHBOARD_MODEL}")

configure_file(
  "${CTEST_SCRIPT_DIRECTORY}/CTestConfig.cmake"
  "${CTEST_SOURCE_DIRECTORY}/CTestConfig.cmake"
  COPYONLY)

execute_process(COMMAND hostname OUTPUT_VARIABLE HOSTNAME OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND rpm -q --qf "%{VERSION}-%{RELEASE}" InsightToolkit5-devel
                OUTPUT_VARIABLE ITK_RPM_VER OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE ITK_RPM_RC ERROR_QUIET)
execute_process(COMMAND rpm -E "%{?fedora}"
                OUTPUT_VARIABLE FEDORA_VER OUTPUT_STRIP_TRAILING_WHITESPACE)

if(NOT ITK_RPM_RC EQUAL 0)
  # Try the unversioned name too (some EPEL/Fedora variants ship plain itk-devel).
  execute_process(COMMAND rpm -q --qf "%{VERSION}-%{RELEASE}" itk-devel
                  OUTPUT_VARIABLE ITK_RPM_VER OUTPUT_STRIP_TRAILING_WHITESPACE
                  RESULT_VARIABLE ITK_RPM_RC ERROR_QUIET)
endif()
if(NOT ITK_RPM_RC EQUAL 0)
  message(FATAL_ERROR "InsightToolkit5-devel is not installed — cannot run ITK dashboard")
endif()

set(CTEST_SITE "${HOSTNAME}")
set(CTEST_BUILD_NAME "f${FEDORA_VER}-itk-${ITK_RPM_VER}")
set(CTEST_CMAKE_GENERATOR "Ninja")
set(CTEST_BUILD_CONFIGURATION "Release")
set(CTEST_BUILD_FLAGS "-j${PARALLEL}")
set(CTEST_TEST_ARGS PARALLEL_LEVEL ${PARALLEL})

ctest_empty_binary_directory("${CTEST_BINARY_DIRECTORY}")
ctest_start("${DASHBOARD_MODEL}")
ctest_configure(OPTIONS "-DCMAKE_BUILD_TYPE=Release")
ctest_build(FLAGS "-j${PARALLEL}")
ctest_test(PARALLEL_LEVEL ${PARALLEL})
ctest_submit()
