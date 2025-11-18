// Tencent is pleased to support the open source community by making RapidJSON available.
// 
// Copyright (C) 2015 THL A29 Limited, a Tencent company, and Milo Yip.
//
// Licensed under the MIT License (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
// http://opensource.org/licenses/MIT
//
// Unless required by applicable law or agreed to in writing, software distributed 
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
// CONDITIONS OF ANY KIND, either express or implied. See the License for the 
// specific language governing permissions and limitations under the License.

#ifndef DISABLE_YGGDRASIL_RAPIDJSON
#define YGGDRASIL_RAPIDJSON_FORCE_IMPORT_ARRAY
#endif // DISABLE_YGGDRASIL_RAPIDJSON
#include "unittest.h"
#include "yggdrasil_rapidjson/yggdrasil_rapidjson.h"
#ifndef DISABLE_YGGDRASIL_RAPIDJSON
#include "yggdrasil_rapidjson/pyrj.h"
#endif // DISABLE_YGGDRASIL_RAPIDJSON

#ifdef __clang__
#pragma GCC diagnostic push
#if __has_warning("-Wdeprecated")
#pragma GCC diagnostic ignored "-Wdeprecated"
#endif
#endif

AssertException::~AssertException() throw() {}

#ifdef __clang__
#pragma GCC diagnostic pop
#endif

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);

    std::cout << "YggdrasilRapidJSON v" << YGGDRASIL_RAPIDJSON_VERSION_STRING << std::endl;

#ifndef DISABLE_YGGDRASIL_RAPIDJSON
#ifndef YGGDRASIL_DISABLE_PYTHON_C_API
    INIT_PYTHON();
#endif // YGGDRASIL_DISABLE_PYTHON_C_API
#endif // DISABLE_YGGDRASIL_RAPIDJSON
    
#ifdef _MSC_VER
    _CrtMemState memoryState = { 0 };
    (void)memoryState;
    _CrtMemCheckpoint(&memoryState);
    //_CrtSetBreakAlloc(X);
    //void *testWhetherMemoryLeakDetectionWorks = malloc(1);
#endif

    int ret = RUN_ALL_TESTS();

#ifdef _MSC_VER
    // Current gtest constantly leak 2 blocks at exit
    _CrtMemDumpAllObjectsSince(&memoryState);
#endif
    
#ifndef DISABLE_YGGDRASIL_RAPIDJSON
#ifndef YGGDRASIL_DISABLE_PYTHON_C_API
    FINALIZE_PYTHON();
#endif // YGGDRASIL_DISABLE_PYTHON_C_API
#endif // DISABLE_YGGDRASIL_RAPIDJSON
    
    return ret;
}
