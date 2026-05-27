cmake_minimum_required(VERSION 3.16)
project(neurofedora-vtk-smoke CXX)

include(CTest)

find_package(VTK REQUIRED COMPONENTS
  CommonCore
  CommonDataModel
  FiltersSources
  IOXML
  ImagingCore
)

add_executable(smoke_vtk smoke_vtk.cxx)
target_link_libraries(smoke_vtk PRIVATE ${VTK_LIBRARIES})
vtk_module_autoinit(TARGETS smoke_vtk MODULES ${VTK_LIBRARIES})

add_test(NAME vtk-version COMMAND smoke_vtk version)
add_test(NAME vtk-sphere-pipeline COMMAND smoke_vtk sphere)
add_test(NAME vtk-image-write COMMAND smoke_vtk image)
