# ctest -S driver for SimpleITK Python smoke dashboard.

cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED DASHBOARD_MODEL)
  set(DASHBOARD_MODEL "Experimental")
endif()
if(NOT DEFINED PARALLEL)
  set(PARALLEL 8)
endif()

set(CTEST_SOURCE_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/tests-simpleitk")
set(CTEST_BINARY_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/build-simpleitk-${DASHBOARD_MODEL}")

configure_file(
  "${CTEST_SCRIPT_DIRECTORY}/CTestConfig.cmake"
  "${CTEST_SOURCE_DIRECTORY}/CTestConfig.cmake"
  COPYONLY)

execute_process(COMMAND hostname OUTPUT_VARIABLE HOSTNAME OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND rpm -q --qf "%{VERSION}-%{RELEASE}" python3-simpleitk
                OUTPUT_VARIABLE SITK_RPM_VER OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE SITK_RPM_RC ERROR_QUIET)
execute_process(COMMAND rpm -E "%{?fedora}"
                OUTPUT_VARIABLE FEDORA_VER OUTPUT_STRIP_TRAILING_WHITESPACE)

if(NOT SITK_RPM_RC EQUAL 0)
  message(FATAL_ERROR "python3-simpleitk is not installed — cannot run SimpleITK dashboard")
endif()

set(CTEST_SITE "${HOSTNAME}")
set(CTEST_BUILD_NAME "f${FEDORA_VER}-simpleitk-${SITK_RPM_VER}")
set(CTEST_CMAKE_GENERATOR "Ninja")
set(CTEST_BUILD_CONFIGURATION "Release")

ctest_empty_binary_directory("${CTEST_BINARY_DIRECTORY}")
ctest_start("${DASHBOARD_MODEL}")
ctest_configure()
ctest_test(PARALLEL_LEVEL ${PARALLEL})
ctest_submit()
