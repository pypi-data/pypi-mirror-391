cmake_minimum_required(VERSION 3.15)
if(NOT PROJECT_NAME)
  if(NOT SKBUILD)
    message(FATAL_ERROR "Must be built via scikit-build-core")
  endif()
  PROJECT(${SKBUILD_PROJECT_NAME} VERSION "${SKBUILD_PROJECT_VERSION}")
endif()

set(PYRJ_ALTERNATE_MODULE "yggdrasil_rapidjson" CACHE STRING "Name of the Python module that should be built")

set(CMAKE_VERBOSE_MAKEFILE ON)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ygg_options.cmake)

find_package(
  ${PYTHON_PREFIX} COMPONENTS
  Interpreter Development.Module NumPy REQUIRED
)
if (${PYTHON_PREFIX}_VERSION VERSION_LESS "3.9.0")
  message(FATAL_ERROR "Only Python 3.9+ is supported.")
endif()

set(PYRJ_TARGET "yggdrasil_python_rapidjson")
set(PYRJ_SRC "${CMAKE_CURRENT_SOURCE_DIR}/yggdrasil_rapidjson.cpp")

if (PYRJ_ALTERNATE_MODULE)
  if (NOT PYRJ_LIBNAME)
    string(FIND ${PYRJ_ALTERNATE_MODULE} "." IDX_LIBNAME REVERSE)
    message(STATUS "IDX_LIBNAME = ${IDX_LIBNAME}")
    if(IDX_LIBNAME EQUAL -1)
      set(PYRJ_LIBNAME "${PYRJ_ALTERNATE_MODULE}")
    else()
      MATH(EXPR IDX_LIBNAME "${IDX_LIBNAME}+1")
      string(
        SUBSTRING ${PYRJ_ALTERNATE_MODULE} ${IDX_LIBNAME} -1 PYRJ_LIBNAME
      )
    endif()
  endif()
  if((PYRJ_ALTERNATE_MODULE STREQUAL "yggdrasil_rapidjson") AND
     (PYRJ_LIBNAME STREQUAL "yggdrasil_rapidjson"))
    set(ALT_PYRJ_CPP)
  else()
    file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/replace_module.cmake"
    [=[
    file(READ "${SOURCE}" TEXT)
    string(REPLACE "\"yggdrasil_rapidjson\"" "\"${PYRJ_ALTERNATE_MODULE}\"" TEXT "${TEXT}")
    string(REPLACE "\"yggdrasil_rapidjson." "\"${PYRJ_ALTERNATE_MODULE}." TEXT "${TEXT}")
    string(REPLACE ":yggdrasil_rapidjson." ":${PYRJ_ALTERNATE_MODULE}." TEXT "${TEXT}")
    string(REPLACE "PyInit_yggdrasil_rapidjson" "PyInit_${PYRJ_LIBNAME}" TEXT "${TEXT}")
    file(WRITE "${TARGET}" "${TEXT}")
    ]=])

    file(GLOB PYRJ_CPP LIST_DIRECTORIES false
         "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")
    message(STATUS "PYRJ_CPP = ${PYRJ_CPP}")
    foreach(src IN LISTS PYRJ_CPP)
      set(base)
      cmake_path(GET src FILENAME base)
      cmake_path(APPEND CMAKE_CURRENT_BINARY_DIR ${base}
                 OUTPUT_VARIABLE dst)
      message(STATUS "Vendoring ${base} from ${src} to ${dst}")
      list(APPEND ALT_PYRJ_CPP ${dst})
      add_custom_command(
        OUTPUT "${dst}"
        COMMAND "${CMAKE_COMMAND}"
                "-DSOURCE=${src}"
	        "-DTARGET=${dst}"
	        "-DPYRJ_ALTERNATE_MODULE=${PYRJ_ALTERNATE_MODULE}"
                "-DPYRJ_LIBNAME=${PYRJ_LIBNAME}"
	        -P "${CMAKE_CURRENT_BINARY_DIR}/replace_module.cmake"
	        DEPENDS "${src}" "${CMAKE_CURRENT_BINARY_DIR}/replace_module.cmake")
    endforeach()
    set(PYRJ_SRC "${CMAKE_CURRENT_BINARY_DIR}/yggdrasil_rapidjson.cpp")
    add_custom_target(alt_rapidjson DEPENDS ${ALT_PYRJ_CPP})
  endif()
endif()

if (NOT PYRJ_LIBNAME)
  set(PYRJ_LIBNAME "yggdrasil_rapidjson")
endif()

message(STATUS "PYRJ_ALTERNATE_MODULE = ${PYRJ_ALTERNATE_MODULE}")
message(STATUS "PYRJ_LIBNAME = ${PYRJ_LIBNAME}")
message(STATUS "PYRJ_TARGET = ${PYRJ_TARGET}")

if (PYTHON_PREFIX STREQUAL "Python")
  Python_add_library(${PYRJ_TARGET} MODULE ${PYRJ_SRC})
else()
  Python3_add_library(${PYRJ_TARGET} MODULE ${PYRJ_SRC})
endif()
set_target_properties(
  ${PYRJ_TARGET} PROPERTIES OUTPUT_NAME ${PYRJ_LIBNAME}
)

if (PYRJ_ALTERNATE_MODULE AND ALT_PYRJ_CPP)
  add_dependencies(${PYRJ_TARGET} alt_rapidjson)
  target_include_directories(
    ${PYRJ_TARGET} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
  )
endif()

target_include_directories(${PYRJ_TARGET} PUBLIC ${YGGDRASIL_RAPIDJSON_INCLUDE_DIRS})
target_link_libraries(${PYRJ_TARGET} PUBLIC ${PYTHON_PREFIX}::NumPy)

target_compile_options(
  ${PYRJ_TARGET} PUBLIC
  -DYGGDRASIL_RAPIDJSON_PYTHON_WRAPPER
  -DYGGDRASIL_RAPIDJSON_HAS_STDSTRING
  -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
  -D_USE_MATH_DEFINES
  -DYGGDRASIL_RAPIDJSON_PYTHON_VERSION=${CMAKE_PROJECT_VERSION}
)
if (YGGDRASIL_RAPIDJSON_EXACT_VERSION)
  target_compile_options(
    ${PYRJ_TARGET} PUBLIC
    "-DYGGDRASIL_RAPIDJSON_EXACT_VERSION=${YGGDRASIL_RAPIDJSON_EXACT_VERSION}")
endif()
if (ASAN_COMPILE_FLAGS)
  target_compile_options(${PYRJ_TARGET} PUBLIC ${ASAN_COMPILE_FLAGS})
endif()
if (ASAN_LINK_FLAGS)
  target_link_options(${PYRJ_TARGET} PUBLIC ${ASAN_LINK_FLAGS})
endif()

if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  # Avoid warning about invalid flag for C++
  string(REPLACE "-Wstrict-prototypes" ""
         CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
  string(REPLACE "-Wstrict-prototypes" ""
         CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")

  # Ignore warnings about missing members in PyTypeObject objects
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-missing-field-initializers")

  # Add -pedantic, so we get a warning when using non-standard features, and
  # -Wno-long-long to pacify old gcc (or Apple's hybrids) that treat
  # "long long" as an error under C++ (see issue #69). C++11 is required
  # since commit
  # https://github.com/Tencent/rapidjson/commit/9965ab37f6cfae3d58a0a6e34c76112866ace0b1
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pedantic -Wno-long-long") # -std=c++11
  # Up to Python 3.7, some structures use "char*" instead of "const char*",
  # and ISO C++ forbids assigning string literal constants
  if (${PYTHON_PREFIX}_VERSION VERSION_LESS "3.7.0")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-write-strings")
  endif()
endif()

# Exact version file
cmake_path(APPEND ${CMAKE_CURRENT_SOURCE_DIR} yggdrasil_rapidjson_exact_version.txt
           OUTPUT_VARIABLE YGGDRASIL_RAPIDJSON_EXACT_VERSION_FILE)
if (EXISTS YGGDRASIL_RAPIDJSON_EXACT_VERSION_FILE)
  file(READ ${YGGDRASIL_RAPIDJSON_EXACT_VERSION_FILE} YGGDRASIL_RAPIDJSON_EXACT_VERSION)
  string(STRIP ${YGGDRASIL_RAPIDJSON_EXACT_VERSION} YGGDRASIL_RAPIDJSON_EXACT_VERSION)
  target_compile_options(
    ${PYRJ_TARGET} PUBLIC
    "-DYGGDRASIL_RAPIDJSON_EXACT_VERSION=${YGGDRASIL_RAPIDJSON_EXACT_VERSION}")
endif()

if (NOT ${PYTHON_PREFIX}_INSTALL_DIR)
  set(${PYTHON_PREFIX}_INSTALL_DIR ".")
endif()

install(TARGETS ${PYRJ_TARGET}
        LIBRARY DESTINATION ${${PYTHON_PREFIX}_INSTALL_DIR}
	RUNTIME DESTINATION ${${PYTHON_PREFIX}_INSTALL_DIR})
