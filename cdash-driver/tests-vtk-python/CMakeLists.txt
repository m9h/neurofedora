cmake_minimum_required(VERSION 3.16)
project(neurofedora-vtk-python-smoke NONE)

include(CTest)

# Use the SYSTEM interpreter, not whatever "python3" happens to be first on PATH.
# These tests exist to verify RPM-installed modules, which live in the system
# interpreter's site-packages. A conda/miniforge or pyenv python earlier on PATH
# has a different site-packages entirely, so every import fails and the component
# reports a total wipeout that looks like a broken package. Seen live on
# rpi-the-great, where python3 is miniforge3's 3.13 while the RPMs install into
# /usr/lib64/python3.14 -- VTK-python and SimpleITK reported 0/4 while the system
# interpreter imported both fine.
# (The mirror of this is legion, where a pip --user joblib made a MISSING RPM
# dependency look satisfied. Both directions corrupt the dashboard.)
set(PYTHON3 /usr/bin/python3)
if(NOT EXISTS "${PYTHON3}")
  message(FATAL_ERROR "system interpreter ${PYTHON3} not found")
endif()

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
