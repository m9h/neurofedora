cmake_minimum_required(VERSION 3.16)
project(neurofedora-paraview-smoke NONE)

include(CTest)

find_program(PVPYTHON pvpython REQUIRED)
find_program(PVBATCH pvbatch REQUIRED)

add_test(NAME paraview-pvpython-version
         COMMAND ${PVPYTHON} --version)
add_test(NAME paraview-pvbatch-version
         COMMAND ${PVBATCH} --version)

# Verify Python servermanager module loads and reports a sane version.
add_test(NAME paraview-servermanager-import
         COMMAND ${PVPYTHON} -c "from paraview import simple, servermanager; print('PV', servermanager.vtkSMProxyManager.GetVersionMajor(), servermanager.vtkSMProxyManager.GetVersionMinor(), servermanager.vtkSMProxyManager.GetVersionPatch())")

# Build a tiny pipeline (sphere → write VTU) headless via pvbatch.
add_test(NAME paraview-pipeline-sphere
         COMMAND ${PVBATCH} -c "from paraview.simple import *; s = Sphere(); UpdatePipeline(); SaveData('smoke_pv_sphere.vtp', s)")

set(VTK_DATA "/usr/share/vtkdata/Testing/Data")
set(READ_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/scripts/read_dataset.py")

function(pv_read_test name relpath pts cells)
  set(path "${VTK_DATA}/${relpath}")
  if(NOT EXISTS "${path}")
    message(STATUS "skip ${name}: ${path} not present (vtk-data missing?)")
    return()
  endif()
  add_test(NAME ${name}
           COMMAND ${PVBATCH} ${READ_SCRIPT} ${path} ${pts} ${cells})
  set_tests_properties(${name} PROPERTIES
                       TIMEOUT 60
                       LABELS "paraview;reader")
endfunction()

pv_read_test(paraview-read-exodus      disk_out_ref.ex2                8499 7472)
pv_read_test(paraview-read-legacy-vtk  RectGrid2.vtk                  17061 14720)
pv_read_test(paraview-read-xml-vtp     CuspySurface.vtp                3125 5507)
pv_read_test(paraview-read-xml-vtu     Disc_QuadraticQuads_0_0.vtu     1193  376)
pv_read_test(paraview-read-xml-vti     2DScalar.vti                     441  400)
pv_read_test(paraview-read-ensight     EnSight/RectGrid_ascii.case      704  450)
