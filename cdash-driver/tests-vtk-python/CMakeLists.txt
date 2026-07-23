cmake_minimum_required(VERSION 3.16)
project(neurofedora-vtk-python-smoke NONE)

include(CTest)

find_program(PYTHON3 python3 REQUIRED)

# Catches the python(abi) ABI breaks (e.g. the rawhide 3.14->3.15 cascade that
# left python3-vtk built for the wrong ABI) before downstream consumers FTBFS.
add_test(NAME vtk-py-import
         COMMAND ${PYTHON3} -c "import vtk; print('VTK', vtk.vtkVersion.GetVTKVersion())")

# Pure-compute filter pipeline — no GL/display required.
add_test(NAME vtk-py-pipeline
         COMMAND ${PYTHON3} -c "import vtk; s=vtk.vtkSphereSource(); s.SetThetaResolution(16); s.SetPhiResolution(16); t=vtk.vtkTriangleFilter(); t.SetInputConnection(s.GetOutputPort()); t.Update(); n=t.GetOutput().GetNumberOfCells(); assert n>0, n; print('cells', n)")

# .vtp write/read round-trip exercises the IOXML wrapping.
add_test(NAME vtk-py-xml-roundtrip
         COMMAND ${PYTHON3} -c "import vtk, os, tempfile; td=tempfile.mkdtemp(); p=os.path.join(td,'rt.vtp'); s=vtk.vtkSphereSource(); s.Update(); w=vtk.vtkXMLPolyDataWriter(); w.SetFileName(p); w.SetInputData(s.GetOutput()); w.Write(); r=vtk.vtkXMLPolyDataReader(); r.SetFileName(p); r.Update(); assert r.GetOutput().GetNumberOfPoints()==s.GetOutput().GetNumberOfPoints(); print('ok', p)")

# numpy_support bridges the VTK and numpy ABIs — a common break surface.
add_test(NAME vtk-py-numpy
         COMMAND ${PYTHON3} -c "import vtk, numpy as np; from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy; a=np.arange(12,dtype=np.float64); v=numpy_to_vtk(a); b=vtk_to_numpy(v); assert np.allclose(a,b), (a,b); print('roundtrip', b.sum())")
