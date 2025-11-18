# include(CTest)
enable_testing()
find_package(GTestSrc)
# find_package(GTest)

# if(GTEST_FOUND)
#     include_directories(SYSTEM ${GTEST_INCLUDE_DIR})
#     set(TEST_LIBRARIES ${GTEST_LIBRARY} ${GTEST_MAIN_LIBRARY})
# endif()
    
if(GTESTSRC_FOUND)

    if (WIN32 AND (NOT CYGWIN) AND (NOT MINGW))
        set(gtest_disable_pthreads ON)
        set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    endif()

    IF(GTEST_SOURCE_DIR)
        add_subdirectory(${GTEST_SOURCE_DIR} ${CMAKE_BINARY_DIR}/googletest)
    endif()
    include_directories(SYSTEM ${GTEST_INCLUDE_DIR})

    set(TEST_LIBRARIES gtest gtest_main)

endif()

if(TEST_LIBRARIES)
    option(YGGDRASIL_RAPIDJSON_ENABLE_COVERAGE "Enable coverage reporting" OFF)
    set(COVERAGE_DIR ${CMAKE_BINARY_DIR}/coverage)
    if(YGGDRASIL_RAPIDJSON_ENABLE_COVERAGE AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang|AppleClang|ARMClang")
        
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0")
        # set(CMAKE_CXX_FLAGS "-g -O0 --coverage -fprofile-arcs -ftest-coverage -fprofile-filter-files=\"${CMAKE_SOURCE_DIR}/include/*\" -fprofile-exclude-files=\"${CMAKE_SOURCE_DIR}/include/rapidjson/fwd.h\"")
        # set(CMAKE_C_FLAGS "-g -O0 --coverage -fprofile-arcs -ftest-coverage -fprofile-filter-files=\"${CMAKE_SOURCE_DIR}/include/*\" -fprofile-exclude-files=\"${CMAKE_SOURCE_DIR}/include/rapidjson/fwd.h\"")

        include(CodeCoverage)
        set(CODE_COVERAGE_VERBOSE TRUE)
	set(
            COVERAGE_COMPILER_FLAGS
            "${COVERAGE_COMPILER_FLAGS} --coverage -fprofile-arcs -ftest-coverage -fno-inline -fprofile-filter-files=\"${CMAKE_SOURCE_DIR}/include/*\" -fprofile-exclude-files=\"${CMAKE_SOURCE_DIR}/include/rapidjson/fwd.h\""
        )
	if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|AppleClang|ARMClang")
            set(CTEST_COVERAGE_COMMAND "llvm-cov")
            set(CTEST_COVERAGE_EXTRA_FLAGS "gcov")
	    set(COVERAGE_COMPILER_FLAGS
                "${COVERAGE_COMPILER_FLAGS} -fprofile-instr-generate -fcoverage-mapping")
            # set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-instr-generate -fcoverage-mapping")
            # set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fprofile-instr-generate -fcoverage-mapping")
        else()
            set(CTEST_COVERAGE_COMMAND "gcov")
            set(CTEST_COVERAGE_EXTRA_FLAGS "")
            set(COVERAGE_COMPILER_FLAGS
	        "${COVERAGE_COMPILER_FLAGS} -fno-inline-small-functions -fno-default-inline")
        endif()
        append_coverage_compiler_flags()
        list(
            APPEND GCOVR_ADDITIONAL_ARGS
            -v
            --coveralls=${COVERAGE_DIR}/coverage.info
            --exclude-lines-by-pattern=\".*RAPIDJSON_ASSERT.*\"
            --exclude-lines-by-pattern=\".*GCOVR_EXCL_LINE.*\"
            --exclude-lines-by-pattern=\".*GCOVR_EXCL_STOP.*\"
            --merge-mode-functions=separate
        )
    else()
        set(YGGDRASIL_RAPIDJSON_ENABLE_COVERAGE OFF)
    endif()

    add_custom_target(tests ALL)
    if(YGGDRASIL_RAPIDJSON_BUILD_PERFTESTS)
        add_subdirectory(perftest)
    endif()
    if(YGGDRASIL_RAPIDJSON_BUILD_UNITTESTS)
        add_subdirectory(unittest)
    endif()
    
    if(YGGDRASIL_RAPIDJSON_ENABLE_COVERAGE)
        # setup_target_for_coverage_gcovr_html(
        #     NAME coverage
        #     EXECUTABLE ctest
        #     DEPENDENCIES unittest perftest
        #     BASE_DIRECTORY "${CMAKE_SOURCE_DIR}/include"
        # )
        # add_dependencies(tests coverage)
        find_program(GCOVR_FOUND gcovr)
        if(GCOVR_FOUND)
            file(MAKE_DIRECTORY ${COVERAGE_DIR})
            set(GCOVR_HTML_CMD
                ${GCOVR_PATH} --html --html-details
                -r "${CMAKE_SOURCE_DIR}/include"
                ${GCOVR_ADDITIONAL_ARGS}
                --object-directory=${CMAKE_BINARY_DIR}
                -o ${COVERAGE_DIR}/coverage.html
            )
            add_test(NAME coverage
                     COMMAND ${GCOVR_HTML_CMD}
                     # COMMAND sh -c "gcovr ${CMAKE_BINARY_DIR} --gcov-executable=\"${CTEST_COVERAGE_COMMAND} ${CTEST_COVERAGE_EXTRA_FLAGS}\" --exclude-lines-by-pattern=\".*RAPIDJSON_ASSERT.*\" --exclude-lines-by-pattern=\".*GCOVR_EXCL_LINE.*\" --exclude-lines-by-pattern=\".*GCOVR_EXCL_STOP.*\" --coveralls ${CMAKE_BINARY_DIR}/coverage/coverage.info --html-details ${CMAKE_BINARY_DIR}/coverage/coverage.html"
                     WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
            set_tests_properties(coverage PROPERTIES DEPENDS "perftest;unittest")
        endif()
    endif()

endif()
