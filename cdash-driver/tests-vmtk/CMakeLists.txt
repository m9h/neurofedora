cmake_minimum_required(VERSION 3.16)
project(neurofedora-vmtk-smoke NONE)

include(CTest)

find_program(PYTHON3 python3 REQUIRED)
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
