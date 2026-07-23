# ctest -S driver for the vtk-mpich/vtk-openmpi smoke dashboard.
# MUST be invoked with an MPI module already loaded so find_package(VTK) resolves
# the MPI flavour's config (/usr/lib64/<flavour>/lib/cmake/vtk) and find_package(MPI)
# picks the matching mpiexec. run-dashboard.sh's run_one_mpi handles the load.
#   source /etc/profile.d/modules.sh; module load mpi/mpich-x86_64
#   ctest -V -S neurofedora-vtk-mpi.cmake -DDASHBOARD_MODEL=Experimental

cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED DASHBOARD_MODEL)
  set(DASHBOARD_MODEL "Experimental")
endif()
if(NOT DEFINED PARALLEL)
  set(PARALLEL 8)
endif()
if(NOT DEFINED MPI_FLAVOUR)
  set(MPI_FLAVOUR "mpich")
endif()

set(CTEST_SOURCE_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/tests-vtk-mpi")
set(CTEST_BINARY_DIRECTORY "${CTEST_SCRIPT_DIRECTORY}/build-vtk-mpi-${MPI_FLAVOUR}-${DASHBOARD_MODEL}")

configure_file(
  "${CTEST_SCRIPT_DIRECTORY}/CTestConfig.cmake"
  "${CTEST_SOURCE_DIRECTORY}/CTestConfig.cmake"
  COPYONLY)

execute_process(COMMAND hostname OUTPUT_VARIABLE HOSTNAME OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND rpm -q --qf "%{VERSION}-%{RELEASE}" vtk-${MPI_FLAVOUR}-devel
                OUTPUT_VARIABLE VTKMPI_RPM_VER OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE VTKMPI_RPM_RC ERROR_QUIET)
execute_process(COMMAND rpm -E "%{?fedora}"
                OUTPUT_VARIABLE FEDORA_VER OUTPUT_STRIP_TRAILING_WHITESPACE)

if(NOT VTKMPI_RPM_RC EQUAL 0)
  message(FATAL_ERROR "vtk-${MPI_FLAVOUR}-devel is not installed — cannot run VTK-MPI dashboard")
endif()

set(CTEST_SITE "${HOSTNAME}")
set(CTEST_BUILD_NAME "f${FEDORA_VER}-vtk-mpi-${MPI_FLAVOUR}-${VTKMPI_RPM_VER}")
set(CTEST_CMAKE_GENERATOR "Ninja")
set(CTEST_BUILD_CONFIGURATION "Release")
set(CTEST_BUILD_FLAGS "-j${PARALLEL}")

ctest_empty_binary_directory("${CTEST_BINARY_DIRECTORY}")
ctest_start("${DASHBOARD_MODEL}")
ctest_configure()
ctest_build(FLAGS "-j${PARALLEL}")
ctest_test(PARALLEL_LEVEL ${PARALLEL})
ctest_submit()
