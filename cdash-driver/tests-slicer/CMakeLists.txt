cmake_minimum_required(VERSION 3.16)
project(neurofedora-slicer-smoke NONE)

include(CTest)

# /usr/bin/slicer is the launcher symlink installed by the 3dslicer RPM
# (-> /usr/lib/slicer*/Slicer). Accept either name.
find_program(SLICER_LAUNCHER NAMES slicer Slicer REQUIRED)

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
