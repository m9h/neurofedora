cmake_minimum_required(VERSION 3.16)
project(neurofedora-elastix-smoke NONE)

include(CTest)

find_program(ELASTIX_BIN elastix REQUIRED)
find_program(TRANSFORMIX_BIN transformix REQUIRED)

add_test(NAME elastix-version
         COMMAND ${ELASTIX_BIN} --version)
add_test(NAME elastix-help
         COMMAND ${ELASTIX_BIN} --help)
add_test(NAME transformix-version
         COMMAND ${TRANSFORMIX_BIN} --version)
add_test(NAME transformix-help
         COMMAND ${TRANSFORMIX_BIN} --help)
