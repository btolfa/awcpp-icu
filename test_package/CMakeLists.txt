project(tst_icu)
cmake_minimum_required(VERSION 3.1 FATAL_ERROR)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(tst_icu icu.cpp)
target_link_libraries(tst_icu ${CONAN_LIBS} ${CMAKE_DL_LIBS})
