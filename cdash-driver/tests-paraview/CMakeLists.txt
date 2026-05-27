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
