cmake_minimum_required(VERSION 3.16)
project(neurofedora-vmtk-smoke NONE)

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
find_program(VMTK_BIN vmtk)

add_test(NAME vmtk-python-import
         COMMAND ${PYTHON3} -c "import vmtk; from vmtk import vmtkscripts; print(vmtk.__file__)")

add_test(NAME vmtk-pypes-import
         COMMAND ${PYTHON3} -c "from vmtk import pypes; print(pypes.__file__)")

# Many vmtk operations are exposed as vmtkX scripts via pypes; verify a couple resolve.
add_test(NAME vmtk-image-reader-help
         COMMAND ${PYTHON3} -c "from vmtk import pypes; pypes.PypeRun('vmtkimagereader --help')")

if(VMTK_BIN)
  add_test(NAME vmtk-launcher-help
           COMMAND ${VMTK_BIN} --help)
endif()
