cmake_minimum_required(VERSION 3.16)
project(neurofedora-slicer-smoke NONE)

include(CTest)

# /usr/bin/Slicer is the launcher installed by the 3dslicer RPM (-> /usr/lib/
# slicer*/Slicer); /usr/bin/slicer is a lowercase alias. The name alone is NOT
# enough to identify it: FSL ships its own unrelated "slicer" (a volume-slice
# screenshot tool), and on a box with FSL ahead of /usr/bin in PATH a bare
# find_program picks that one. It then treats --python-script as a volume to
# read, so every test fails with "No image files match" -- a launcher-resolution
# bug that looks exactly like a broken Slicer install. Probe each candidate with
# --version and keep the first that identifies itself as Slicer.
set(SLICER_LAUNCHER "SLICER_LAUNCHER-NOTFOUND")
find_program(_slicer_cap NAMES Slicer)
find_program(_slicer_low NAMES slicer)
foreach(_cand IN ITEMS "${_slicer_cap}" "${_slicer_low}")
  if(SLICER_LAUNCHER)
    break()
  endif()
  if(_cand AND EXISTS "${_cand}")
    execute_process(COMMAND "${_cand}" --version
                    OUTPUT_VARIABLE _cand_out ERROR_QUIET
                    RESULT_VARIABLE _cand_rc TIMEOUT 120)
    if(_cand_rc EQUAL 0 AND _cand_out MATCHES "^Slicer ")
      set(SLICER_LAUNCHER "${_cand}")
    endif()
  endif()
endforeach()
if(NOT SLICER_LAUNCHER)
  message(FATAL_ERROR
    "No 3D Slicer launcher found. Candidates probed: "
    "'${_slicer_cap}' '${_slicer_low}' (neither reported 'Slicer <version>').")
endif()
message(STATUS "Slicer launcher: ${SLICER_LAUNCHER}")

set(_smoke "${CMAKE_CURRENT_SOURCE_DIR}/slicer_smoke.py")

# Headless launch: no splash, no main window, exit once startup + script done.
# QT_QPA_PLATFORM=offscreen keeps it display-free on the nightly cron host.
add_test(NAME slicer-headless-smoke
         COMMAND ${SLICER_LAUNCHER}
                 --no-splash --no-main-window --exit-after-startup
                 --python-script ${_smoke})
set_tests_properties(slicer-headless-smoke PROPERTIES
  ENVIRONMENT "QT_QPA_PLATFORM=offscreen"
  TIMEOUT 600)

# Cheap independent check that the launcher resolves and reports a version,
# so a totally broken install fails fast and distinctly from the smoke script.
add_test(NAME slicer-version
         COMMAND ${SLICER_LAUNCHER}
                 --no-splash --no-main-window --exit-after-startup
                 --python-code "import slicer,sys; sys.stdout.write(slicer.app.applicationVersion)")
set_tests_properties(slicer-version PROPERTIES
  ENVIRONMENT "QT_QPA_PLATFORM=offscreen"
  TIMEOUT 300)
