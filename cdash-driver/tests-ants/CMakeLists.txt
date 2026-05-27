cmake_minimum_required(VERSION 3.16)
project(neurofedora-ants-smoke NONE)

include(CTest)

find_program(ANTS_REGISTRATION antsRegistration REQUIRED)
find_program(ANTS_APPLY_TRANSFORMS antsApplyTransforms REQUIRED)
find_program(N4_BIAS N4BiasFieldCorrection REQUIRED)
find_program(IMATH_INFO ImageMath REQUIRED)

add_test(NAME ants-version
         COMMAND ${ANTS_REGISTRATION} --version)
add_test(NAME ants-applytransforms-help
         COMMAND ${ANTS_APPLY_TRANSFORMS} --help)
add_test(NAME ants-n4-help
         COMMAND ${N4_BIAS} --help)
add_test(NAME ants-imagemath-help
         COMMAND ${IMATH_INFO} --help)
