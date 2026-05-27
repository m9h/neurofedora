# ctest -S driver for the VTK smoke dashboard.
# Usage:
#   ctest -V -S neurofedora-vtk.cmake -DDASHBOARD_MODEL=Experimental
# Models: Experimental | Continuous | Nightly
# Parallelism capped at 8 (half the legion). See feedback_legion_resource_cap memory.

cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED DASHBOARD_MODEL)
  set(DASHBOARD_MODEL "Experimental")
endif()
if(NOT DEFINED PARALLEL)
  set(PARALLEL 8)
endif()

set(CTEST_SOURCE_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/tests-vtk")
set(CTEST_BINARY_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/build-vtk-${DASHBOARD_MODEL}")

# Copy CTestConfig.cmake into the source dir so ctest finds CDash settings.
configure_file(
  "${CTEST_SCRIPT_DIRECTORY}/CTestConfig.cmake"
  "${CTEST_SOURCE_DIRECTORY}/CTestConfig.cmake"
  COPYONLY)

# Identify the build for CDash.
execute_process(COMMAND hostname OUTPUT_VARIABLE HOSTNAME OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND rpm -q --qf "%{VERSION}-%{RELEASE}" vtk-devel
                OUTPUT_VARIABLE VTK_RPM_VER OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE VTK_RPM_RC ERROR_QUIET)
execute_process(COMMAND rpm -E "%{?fedora}"
                OUTPUT_VARIABLE FEDORA_VER OUTPUT_STRIP_TRAILING_WHITESPACE)

if(NOT VTK_RPM_RC EQUAL 0)
  message(FATAL_ERROR "vtk-devel is not installed — cannot run VTK dashboard")
endif()

set(CTEST_SITE "${HOSTNAME}")
set(CTEST_BUILD_NAME "f${FEDORA_VER}-vtk-${VTK_RPM_VER}")
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
