cmake_minimum_required(VERSION 3.16)
project(neurofedora-vtk-mpi-smoke C CXX)

include(CTest)

# Both find_package calls resolve to the mpich (or openmpi) flavour because the
# driver runs after `module load mpi/<flavour>-<arch>`, which prepends MPI_HOME
# to CMAKE_PREFIX_PATH and puts the matching mpiexec on PATH.
# C as well as CXX: VTK::mpi's link interface references MPI::MPI_C, so the C
# language must be enabled and the MPI C component found or generation fails.
find_package(MPI REQUIRED C CXX)
find_package(VTK REQUIRED COMPONENTS ParallelMPI CommonCore)

add_executable(smoke_vtk_mpi smoke_vtk_mpi.cxx)
target_link_libraries(smoke_vtk_mpi PRIVATE ${VTK_LIBRARIES} MPI::MPI_CXX)
vtk_module_autoinit(TARGETS smoke_vtk_mpi MODULES ${VTK_LIBRARIES})

add_test(NAME vtk-mpi-reduce-np2
         COMMAND ${MPIEXEC_EXECUTABLE} ${MPIEXEC_NUMPROC_FLAG} 2
                 ${MPIEXEC_PREFLAGS} $<TARGET_FILE:smoke_vtk_mpi> ${MPIEXEC_POSTFLAGS})
add_test(NAME vtk-mpi-reduce-np4
         COMMAND ${MPIEXEC_EXECUTABLE} ${MPIEXEC_NUMPROC_FLAG} 4
                 ${MPIEXEC_PREFLAGS} $<TARGET_FILE:smoke_vtk_mpi> ${MPIEXEC_POSTFLAGS})
