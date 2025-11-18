CMAKE_MINIMUM_REQUIRED(VERSION 3.15)
if(POLICY CMP0025)
  # detect Apple's Clang
  cmake_policy(SET CMP0025 NEW)
endif()
if(POLICY CMP0054)
  cmake_policy(SET CMP0054 NEW)
endif()

if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
   if("$ENV{SDKROOT}")
      SET(CMAKE_OSX_SYSROOT "$ENV{SDKROOT}")
      # SET(CMAKE_OSX_SYSROOT /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk)
   endif()
endif()

set(LIB_MAJOR_VERSION "1")
set(LIB_MINOR_VERSION "1")
set(LIB_PATCH_VERSION "0")
set(LIB_EXTEN_VERSION "1")
set(LIB_VERSION_STRING "${LIB_MAJOR_VERSION}.${LIB_MINOR_VERSION}.${LIB_PATCH_VERSION}.${LIB_EXTEN_VERSION}")

PROJECT(YggdrasilRapidJSON VERSION "${LIB_VERSION_STRING}" LANGUAGES C CXX)
set(PROJECT_NAME_LOWER "yggdrasil_rapidjson")
set(PROJECT_INCLUDE_DIR "include/yggdrasil_rapidjson")

if(POLICY CMP0094)  # https://cmake.org/cmake/help/latest/policy/CMP0094.html
    cmake_policy(SET CMP0094 NEW)  # FindPython should return the first matching Python
endif()

SET(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/CMakeModules)

option(YGGDRASIL_RAPIDJSON_NEST_HEADERS "Nest the headers during install under the package name (in addition to the directly containing the headers)" OFF)
option(DISABLE_YGGDRASIL_RAPIDJSON "Build without yggdrasil extensions" OFF)
option(YGGDRASIL_PYGIL_NO_MANAGEMENT "Disable any handling of the Python GIL" OFF)
option(YGGDRASIL_DISABLE_PYTHON_C_API "Disable the Python C API" OFF)
option(YGGDRASIL_RAPIDJSON_CREATE_METASCHEMA "Re-create the metaschema" OFF)
option(YGGDRASIL_RAPIDJSON_CREATE_METASCHEMA_FULL "Re-create the metaschema and the full_schema.yaml file" OFF)
option(YGGDRASIL_RAPIDJSON_SCHEMA_TESTS "Build tests using the yggdrasil schema" OFF)



set(INTERFACE_COMPILATION_OPTIONS -D_USE_MATH_DEFINES)
set(INTERFACE_INCLUDE_DIRECTORIES)
set(INTERFACE_LIBRARIES)

if(DISABLE_YGGDRASIL_RAPIDJSON)
  list(APPEND INTERFACE_COMPILATION_OPTIONS -DDISABLE_YGGDRASIL_RAPIDJSON)
  set(YGGDRASIL_PYGIL_NO_MANAGEMENT OFF)
  set(YGGDRASIL_DISABLE_PYTHON_C_API OFF)
  set(RAPIDJSON_CREATE_METASCHEMA OFF)
  set(RAPIDJSON_CREATE_METASCHEMA_FULL OFF)
  set(RAPIDJSON_YGGDRASIL_TESTS OFF)
endif()

if (YGGDRASIL_PYGIL_NO_MANAGEMENT)
    add_definitions(-DYGGDRASIL_PYGIL_NO_MANAGEMENT)
endif()

if(YGGDRASIL_DISABLE_PYTHON_C_API)
    add_definitions(-DYGGDRASIL_DISABLE_PYTHON_C_API)
else()
    # needed on GitHub Actions CI: actions/setup-python does not touch registry/frameworks on Windows/macOS
    # this mirrors PythonInterp behavior which did not consult registry/frameworks first
    if (NOT DEFINED Python_FIND_REGISTRY)
        set(Python_FIND_REGISTRY "LAST")
    endif ()
    if (NOT DEFINED Python_FIND_FRAMEWORK)
        set(Python_FIND_FRAMEWORK "LAST")
    endif ()

    message(STATUS "Python executable is ${Python3_EXECUTABLE}")
    if(NOT Python3_ROOT_DIR)
        set(CONDA_PREFIX "$ENV{CONDA_PREFIX}")
        if(CONDA_PREFIX)
            message(STATUS "CONDA_PREFIX = ${CONDA_PREFIX}")
            set(Python3_ROOT_DIR "${CONDA_PREFIX}")
        else()
            if(Python3_EXECUTABLE)
                exec_program(${Python3_EXECUTABLE}
	                     ARGS "-c \"import sysconfig; print(sysconfig.get_config_var('base'))\""
		             OUTPUT_VARIABLE PYTHON_ROOT
		             RETURN_VALUE ROOT_NOT_FOUND)
                if(ROOT_NOT_FOUND)
     	            message(FATAL_ERROR "Python root not found")
                endif()
	        set(Python3_ROOT_DIR "${RETURN_VALUE}")
            endif()
         endif()
    endif()
    if(Python3_ROOT_DIR)
        message(STATUS "Python root directory is ${Python3_ROOT_DIR}")
    endif()
    find_package(Python3 COMPONENTS Interpreter Development NumPy REQUIRED)
    if(NOT Python3_NumPy_FOUND)
        message(FATAL_ERROR "NumPy headers not found")
    endif()
    if(NOT Python3_FOUND)
        message(FATAL_ERROR "Python libraries not found")
    endif()

    # include_directories(
    #     SYSTEM ${Python3_INCLUDE_DIRS} ${Python3_NumPy_INCLUDE_DIRS}
    # )
    list(
        APPEND INTERFACE_COMPILATION_OPTIONS
        -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
    )
    list(
        APPEND INTERFACE_INCLUDE_DIRECTORIES
        ${Python3_INCLUDE_DIRS} ${Python3_NumPy_INCLUDE_DIRS}
    )
    list(
        APPEND INTERFACE_LIBRARIES
        ${Python3_LIBRARIES}
    )

    # Set environment variables required for embedding Python
    set(YGGDRASIL_RAPIDJSON_PYTHON_ENV "DATADIR=${CMAKE_SOURCE_DIR}/test;YGG_PYTHON_EXEC=${Python3_EXECUTABLE}")

    # There is an issue with embedding Python on Windows in conda environments
    # https://github.com/ContinuumIO/anaconda-issues/issues/11374
    if(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        set(YGGDRASIL_RAPIDJSON_PYTHON_ENV "${YGGDRASIL_RAPIDJSON_PYTHON_ENV};PYTHONHOME=${Python3_RUNTIME_LIBRARY_DIRS}")
    endif()
endif()

# Generate the metaschema header file
if(YGGDRASIL_RAPIDJSON_CREATE_METASCHEMA_FULL)
  set(YGGDRASIL_RAPIDJSON_CREATE_METASCHEMA ON)
endif()
if(YGGDRASIL_DISABLE_PYTHON_C_API)
  set(YGGDRASIL_RAPIDJSON_CREATE_METASCHEMA OFF)
endif()
if(YGGDRASIL_RAPIDJSON_CREATE_METASCHEMA)
    set(YGGDRASIL_RAPIDJSON_METASCHEMA_FLAGS "")
    if(YGGDRASIL_RAPIDJSON_SCHEMA_TESTS)
        set(YGGDRASIL_RAPIDJSON_METASCHEMA_FLAGS "--ygg-tests")
    endif()
    if(YGGDRASIL_RAPIDJSON_CREATE_METASCHEMA_FULL)
        set(YGGDRASIL_RAPIDJSON_METASCHEMA_FLAGS "${YGGDRASIL_RAPIDJSON_METASCHEMA_FLAGS} --create-full-schema")
    endif()
    exec_program(${Python3_EXECUTABLE}
                 ARGS "${CMAKE_CURRENT_SOURCE_DIR}/create_metaschema.py ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_INCLUDE_DIR}/metaschema.h ${YGGDRASIL_RAPIDJSON_METASCHEMA_FLAGS}")
endif()

# compile in release with debug info mode by default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "RelWithDebInfo" CACHE STRING "Choose the type of build, options are: Debug Release RelWithDebInfo MinSizeRel." FORCE)
endif()

# Build all binaries in a separate directory
SET(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

option(YGGDRASIL_RAPIDJSON_BUILD_DOC "Build yggdrasil_rapidjson documentation." ON)
option(YGGDRASIL_RAPIDJSON_BUILD_EXAMPLES "Build yggdrasil_rapidjson examples." ON)
option(YGGDRASIL_RAPIDJSON_BUILD_TESTS "Build yggdrasil_rapidjson perftests and unittests." ON)
option(YGGDRASIL_RAPIDJSON_BUILD_UNITTESTS "Build yggdrasil_rapidjson unittests." ON)
option(YGGDRASIL_RAPIDJSON_BUILD_PERFTESTS "Build yggdrasil_rapidjson perftests." ON)
option(YGGDRASIL_RAPIDJSON_BUILD_THIRDPARTY_GTEST
    "Use gtest installation in `thirdparty/gtest` by default if available" OFF)

option(YGGDRASIL_RAPIDJSON_BUILD_CXXMIN "Build yggdrasil_rapidjson with minimum C++ standard" OFF)
option(YGGDRASIL_RAPIDJSON_BUILD_CXX11 "Build yggdrasil_rapidjson with C++11" ON)
option(YGGDRASIL_RAPIDJSON_BUILD_CXX17 "Build yggdrasil_rapidjson with C++17" OFF)
option(YGGDRASIL_RAPIDJSON_BUILD_CXX20 "Build yggdrasil_rapidjson with C++20" OFF)
if(YGGDRASIL_RAPIDJSON_BUILD_CXX11)
    set(CMAKE_CXX_STANDARD 11)
    set(CMAKE_CXX_STANDARD_REQUIRED TRUE)
endif()
if(YGGDRASIL_RAPIDJSON_BUILD_CXXMIN)
    set(YGGDRASIL_RAPIDJSON_BUILD_CXX11 OFF)
    set(YGGDRASIL_RAPIDJSON_BUILD_CXX17 OFF)
    set(CMAKE_CXX_STANDARD 98)
    set(CMAKE_CXX_STANDARD_REQUIRED TRUE)
endif()

option(YGGDRASIL_RAPIDJSON_BUILD_ASAN "Build yggdrasil_rapidjson with address sanitizer (gcc/clang)" OFF)
option(YGGDRASIL_RAPIDJSON_BUILD_UBSAN "Build yggdrasil_rapidjson with undefined behavior sanitizer (gcc/clang)" OFF)

option(YGGDRASIL_RAPIDJSON_ENABLE_INSTRUMENTATION_OPT "Build yggdrasil_rapidjson with -march or -mcpu options" ON)

option(YGGDRASIL_RAPIDJSON_HAS_STDSTRING "" OFF)
if(YGGDRASIL_RAPIDJSON_HAS_STDSTRING)
    add_definitions(-DYGGDRASIL_RAPIDJSON_HAS_STDSTRING)
endif()

option(YGGDRASIL_RAPIDJSON_USE_MEMBERSMAP "" OFF)
if(YGGDRASIL_RAPIDJSON_USE_MEMBERSMAP)
    add_definitions(-DYGGDRASIL_RAPIDJSON_USE_MEMBERSMAP=1)
endif()

find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
    if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Qunused-arguments -fcolor-diagnostics")
    endif()
endif(CCACHE_FOUND)

find_program(VALGRIND_FOUND valgrind)

if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    if(YGGDRASIL_RAPIDJSON_ENABLE_INSTRUMENTATION_OPT AND NOT CMAKE_CROSSCOMPILING)
        if(CMAKE_SYSTEM_PROCESSOR STREQUAL "powerpc" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc64" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc64le")
          set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mcpu=native")
        else()
          #FIXME: x86 is -march=native, but doesn't mean every arch is this option. To keep original project's compatibility, I leave this except POWER.
          set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native")
        endif()
    endif()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Werror")
    set(EXTRA_CXX_FLAGS -Weffc++ -Wswitch-default -Wfloat-equal -Wconversion -Wsign-conversion)
    if (YGGDRASIL_RAPIDJSON_BUILD_CXXMIN)
       set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++03 -Wc++0x-compat -Werror=unused-parameter")
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX11 AND CMAKE_VERSION VERSION_LESS 3.1)
        if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS "4.7.0")
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
        else()
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
        endif()
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX17 AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS "5.0")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX20 AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS "8.0")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20")
    endif()
    if (YGGDRASIL_RAPIDJSON_BUILD_ASAN)
        if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS "4.8.0")
            message(FATAL_ERROR "GCC < 4.8 doesn't support the address sanitizer")
        else()
            add_compile_options(-fsanitize=address)
            add_link_options(-fsanitize=address)
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
        endif()
    endif()
    if (YGGDRASIL_RAPIDJSON_BUILD_UBSAN)
        if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS "4.9.0")
            message(FATAL_ERROR "GCC < 4.9 doesn't support the undefined behavior sanitizer")
        else()
            add_compile_options(-fsanitize=undefined)
            add_link_options(-fsanitize=undefined)
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined")
        endif()
    endif()
elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    if(NOT CMAKE_CROSSCOMPILING)
      if(CMAKE_SYSTEM_PROCESSOR STREQUAL "powerpc" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc64" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc64le")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mcpu=native")
      else()
        if(CMAKE_HOST_SYSTEM_PROCESSOR STREQUAL "arm64")
	  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mcpu=apple-m1")
	else()
          #FIXME: x86 is -march=native, but doesn't mean every arch is this option. To keep original project's compatibility, I leave this except POWER.
          set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native")
        endif()
      endif()
    endif()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Werror -Wno-missing-field-initializers")
    set(EXTRA_CXX_FLAGS -Weffc++ -Wswitch-default -Wfloat-equal -Wconversion -Wimplicit-fallthrough)
    if (YGGDRASIL_RAPIDJSON_BUILD_CXXMIN)
       set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++03 -Wc++0x-compat -Werror=unused-parameter")
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX11 AND CMAKE_VERSION VERSION_LESS 3.1)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX17 AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS "4.0")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX20 AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS "10.0")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20")
    endif()
    if (YGGDRASIL_RAPIDJSON_BUILD_ASAN)
        add_compile_options(-fsanitize=address)
        add_link_options(-fsanitize=address)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
    endif()
    if (YGGDRASIL_RAPIDJSON_BUILD_UBSAN)
        if (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
            add_compile_options(-fsanitize=undefined-trap -fsanitize-undefined-trap-on-error)
            add_link_options(-fsanitize=undefined-trap -fsanitize-undefined-trap-on-error)
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined-trap -fsanitize-undefined-trap-on-error")
        else()
            add_compile_options(-fsanitize=undefined)
            add_link_options(-fsanitize=undefined)
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined")
        endif()
    endif()
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    add_definitions(-D_CRT_SECURE_NO_WARNINGS=1)
    add_definitions(-DNOMINMAX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc /bigobj /Zm10")
    # CMake >= 3.10 should handle the above CMAKE_CXX_STANDARD fine, otherwise use /std:c++XX with MSVC >= 19.10
    if (YGGDRASIL_RAPIDJSON_BUILD_CXXMIN)
       set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++03 /Wc++0x-compat")
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX11 AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS "19.10")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++14") # c++11 not allowed
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX17 AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS "19.14")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++17")
    elseif (YGGDRASIL_RAPIDJSON_BUILD_CXX20 AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS "19.29")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++20")
    endif()
    # Always compile with /WX
    if(CMAKE_CXX_FLAGS MATCHES "/WX-")
        string(REGEX REPLACE "/WX-" "/WX" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
    else()
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /WX")
    endif()
elseif (CMAKE_CXX_COMPILER_ID MATCHES "XL")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -qarch=auto")
endif()

#add extra search paths for libraries and includes
include(GNUInstallDirs)
SET(INCLUDE_INSTALL_DIR "include" CACHE PATH "The directory the headers are installed in")
SET(LIB_INSTALL_DIR ${CMAKE_INSTALL_LIBDIR} CACHE STRING "Directory where lib will install")
SET(DOC_INSTALL_DIR "share/doc/${PROJECT_NAME}" CACHE PATH "Path to the documentation")
IF(UNIX OR CYGWIN)
    SET(_CMAKE_INSTALL_DIR "${LIB_INSTALL_DIR}/cmake/${PROJECT_NAME}")
ELSEIF(WIN32)
    SET(_CMAKE_INSTALL_DIR "cmake")
ENDIF()
SET(CMAKE_INSTALL_DIR "${_CMAKE_INSTALL_DIR}" CACHE PATH "The directory cmake files are installed in")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

include_directories(${INTERFACE_INCLUDE_DIRECTORIES})
add_definitions(${INTERFACE_COMPILATION_OPTIONS})
link_libraries(${INTERFACE_LIBRARIES})

if(YGGDRASIL_RAPIDJSON_BUILD_DOC)
    add_subdirectory(doc)
endif()

add_custom_target(travis_doc)
add_custom_command(TARGET travis_doc
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/travis-doxygen.sh)

if(YGGDRASIL_RAPIDJSON_BUILD_EXAMPLES)
    add_subdirectory(example)
endif()

if(YGGDRASIL_RAPIDJSON_BUILD_TESTS)
    if(MSVC11)
        # required for VS2012 due to missing support for variadic templates
        add_definitions(-D_VARIADIC_MAX=10)
    endif(MSVC11)
    add_subdirectory(test)
    include(CTest)
endif()

# ===============================
# Interface for export
# ===============================

add_library(${PROJECT_NAME} INTERFACE)

if (YGGDRASIL_RAPIDJSON_NEST_HEADERS)
    target_include_directories(
        ${PROJECT_NAME} INTERFACE
        $<INSTALL_INTERFACE:include/${PROJECT_NAME_LOWER}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    )
else()
    target_include_directories(
        ${PROJECT_NAME} INTERFACE
        $<INSTALL_INTERFACE:include>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    )
endif()
target_compile_options(
    ${PROJECT_NAME} INTERFACE ${INTERFACE_COMPILATION_OPTIONS}
)
target_include_directories(
    ${PROJECT_NAME} INTERFACE ${INTERFACE_INCLUDE_DIRECTORIES}
)
target_link_libraries(
    ${PROJECT_NAME} INTERFACE ${INTERFACE_LIBRARIES}
)

# ===============================
# Install
# ===============================

include(CMakePackageConfigHelpers)

# pkg-config
IF (UNIX OR CYGWIN)
  CONFIGURE_FILE (${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}.pc.in
                  ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.pc
                  @ONLY)
  INSTALL (FILES ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.pc
      DESTINATION "${LIB_INSTALL_DIR}/pkgconfig"
      COMPONENT pkgconfig)
ENDIF()

install(FILES readme.md
        DESTINATION "${DOC_INSTALL_DIR}"
        COMPONENT doc)

if (YGGDRASIL_RAPIDJSON_NEST_HEADERS)
    install(
        DIRECTORY ${PROJECT_INCLUDE_DIR}
        DESTINATION "${INCLUDE_INSTALL_DIR}/${PROJECT_NAME_LOWER}"
        COMPONENT dev
    )
else()
    install(
        DIRECTORY "${PROJECT_INCLUDE_DIR}"
        DESTINATION "${INCLUDE_INSTALL_DIR}"
        COMPONENT dev
    )
endif()

install(DIRECTORY example/
    DESTINATION "${DOC_INSTALL_DIR}/examples"
    COMPONENT examples
    # Following patterns are for excluding the intermediate/object files
    # from an install of in-source CMake build.
    PATTERN "CMakeFiles" EXCLUDE
    PATTERN "Makefile" EXCLUDE
    PATTERN "cmake_install.cmake" EXCLUDE)

# Provide config and version files to be used by other applications
# ===============================

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/${PROJECT_NAME}ConfigVersion.cmake
    COMPATIBILITY AnyNewerVersion
)

################################################################################
# Export package for use from the build tree
EXPORT( PACKAGE ${PROJECT_NAME} )

# Create the YggdrasilRapidjsonConfig.cmake file for other cmake projects.
# ... for the build tree
SET( CONFIG_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR})
SET( CONFIG_DIR ${CMAKE_CURRENT_BINARY_DIR})

CONFIGURE_FILE( ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}Config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake @ONLY )

# ... for the install tree

SET( CONFIG_SOURCE_DIR )
SET( CONFIG_DIR )
configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}Config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/${PROJECT_NAME}Config.cmake
  INSTALL_DESTINATION "${CMAKE_INSTALL_DIR}"
)

# Install files
IF(CMAKE_INSTALL_DIR)
    INSTALL(FILES
        ${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/${PROJECT_NAME}Config.cmake
        ${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/${PROJECT_NAME}ConfigVersion.cmake
        DESTINATION "${CMAKE_INSTALL_DIR}"
        COMPONENT dev)

    INSTALL(TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}-targets)
    INSTALL(EXPORT ${PROJECT_NAME}-targets DESTINATION ${CMAKE_INSTALL_DIR})
ENDIF()
