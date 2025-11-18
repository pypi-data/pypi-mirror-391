cmake_minimum_required(VERSION 3.16)
project(dune-polygongrid CXX)

find_package(dune-common)
list(APPEND CMAKE_MODULE_PATH ${dune-common_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/modules")

include(DuneMacros)
dune_project()

add_subdirectory(cmake/modules)
add_subdirectory(dune)
add_subdirectory(test)

# if Python bindings are enabled, include necessary sub directories.
if( DUNE_ENABLE_PYTHONBINDINGS )
  add_subdirectory(python)
endif()

finalize_dune_project(GENERATE_CONFIG_H_CMAKE)
