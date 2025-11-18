set -e
INSTALL_DIR="$(pwd)/_install"
# rm -rf build
if [ ! -d build ]; then
    mkdir build
fi
if [ ! -d ${INSTALL_DIR} ]; then
    mkdir ${INSTALL_DIR}
fi
cd build

cmake .. \
      -DYGGDRASIL_RAPIDJSON_HAS_STDSTRING:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_SKIP_VALGRIND_TESTS:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_CREATE_METASCHEMA_FULL:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_ENABLE_COVERAGE:BOOL=OFF \
      -DYGGDRASIL_RAPIDJSON_BUILD_TESTS:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_BUILD_UNITTESTS:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_BUILD_PERFTESTS:BOOL=OFF \
      -DYGGDRASIL_RAPIDJSON_SCHEMA_TESTS:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_BUILD_UBSAN:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_BUILD_ASAN:BOOL=ON \
      -DYGGDRASIL_RAPIDJSON_BUILD_EXAMPLES:BOOL=OFF \
      -DYGGDRASIL_RAPIDJSON_BUILD_DOC:BOOL=OFF
# -DCMAKE_BUILD_TYPE=Debug
# Install in local directory
# -DCMAKE_INSTALL_PREFIX:FILEPATH=${INSTALL_DIR}

# Tests
cmake --build . --target=tests -- -j 8
ctest -R unittest --stop-on-failure
# ctest -R perftest --stop-on-failure

# Examples
# cmake --build . --target=examples -- -j 8
# ./bin/yggdrasil
# ./bin/${example_name}

# Install
# cmake --install .
# cmake --install . --prefix "${INSTALL_DIR}"


# # cmake --build . -- -j 8
# cmake --build . --target=tests -- -j 8
# # ctest -C Debug --output-on-failure --verbose --stop-on-failure
# ctest -R unittest --stop-on-failure
# ctest -R coverage
# # cmake .. -DYGGDRASIL_RAPIDJSON_SKIP_VALGRIND_TESTS=ON -DYGGDRASIL_RAPIDJSON_ENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
# # ctest -T Coverage
# # ./bin/unittest
# # export DATADIR=/Users/langmm/rapidjson/test
# # export YGG_PYTHON_EXEC=/Users/langmm/miniconda3/envs/conda37/bin/python
# # valgrind --leak-check=full   --show-leak-kinds=all --dsymutil=no --track-origins=yes -v --suppressions=/Users/langmm/valgrind-macos/darwin13.supp ./bin/unittest &> log.txt
# # --suppressions=/Users/langmm/valgrind-macos/default.supp ./bin/unittest &> log.txt
