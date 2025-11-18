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

#ifndef UNITTEST_H_
#define UNITTEST_H_

// gtest indirectly included inttypes.h, without __STDC_CONSTANT_MACROS.
#ifndef __STDC_CONSTANT_MACROS
#ifdef __clang__
#pragma GCC diagnostic push
#if __has_warning("-Wreserved-id-macro")
#pragma GCC diagnostic ignored "-Wreserved-id-macro"
#endif
#endif

#  define __STDC_CONSTANT_MACROS 1 // required by C++ standard

#ifdef __clang__
#pragma GCC diagnostic pop
#endif
#endif

#ifdef _MSC_VER
#define _CRTDBG_MAP_ALLOC
#include <crtdbg.h>
#pragma warning(disable : 4996) // 'function': was declared deprecated
#endif

#if defined(__clang__) || defined(__GNUC__) && (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 2))
#if defined(__clang__) || (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 6))
#pragma GCC diagnostic push
#endif
#pragma GCC diagnostic ignored "-Weffc++"
#endif

#include "gtest/gtest.h"
#include <stdexcept>

#if defined(__clang__) || defined(__GNUC__) && (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 6))
#pragma GCC diagnostic pop
#endif

#ifdef __clang__
// All TEST() macro generated this warning, disable globally
#pragma GCC diagnostic ignored "-Wglobal-constructors"
#endif

template <typename Ch>
inline unsigned StrLen(const Ch* s) {
    const Ch* p = s;
    while (*p) p++;
    return unsigned(p - s);
}

template<typename Ch>
inline int StrCmp(const Ch* s1, const Ch* s2) {
    while(*s1 && (*s1 == *s2)) { s1++; s2++; }
    return static_cast<unsigned>(*s1) < static_cast<unsigned>(*s2) ? -1 : static_cast<unsigned>(*s1) > static_cast<unsigned>(*s2);
}

template <typename Ch>
inline Ch* StrDup(const Ch* str) {
    size_t bufferSize = sizeof(Ch) * (StrLen(str) + 1);
    Ch* buffer = static_cast<Ch*>(malloc(bufferSize));
    memcpy(buffer, str, bufferSize);
    return buffer;
}

inline FILE* TempFile(char *filename) {
#if defined(__WIN32__) || defined(_MSC_VER)
    filename = tmpnam(filename);

    // For Visual Studio, tmpnam() adds a backslash in front. Remove it.
    if (filename[0] == '\\')
        for (int i = 0; filename[i] != '\0'; i++)
            filename[i] = filename[i + 1];
        
    return fopen(filename, "wb");
#else
    strcpy(filename, "/tmp/fileXXXXXX");
    int fd = mkstemp(filename);
    return fdopen(fd, "w");
#endif
}

// Use exception for catching assert
#ifdef _MSC_VER
#pragma warning(disable : 4127)
#endif

#ifdef __clang__
#pragma GCC diagnostic push
#if __has_warning("-Wdeprecated")
#pragma GCC diagnostic ignored "-Wdeprecated"
#endif
#endif

class AssertException : public std::logic_error {
public:
    AssertException(const char* w) : std::logic_error(w) {}
    AssertException(const AssertException& rhs) : std::logic_error(rhs) {}
    virtual ~AssertException() throw();
};

#ifdef __clang__
#pragma GCC diagnostic pop
#endif

// Not using noexcept for testing YGGDRASIL_RAPIDJSON_ASSERT()
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT 0

#ifndef YGGDRASIL_RAPIDJSON_ASSERT
#define YGGDRASIL_RAPIDJSON_ASSERT(x) (!(x) ? throw AssertException(YGGDRASIL_RAPIDJSON_STRINGIFY(x)) : (void)0u)
#ifndef YGGDRASIL_RAPIDJSON_ASSERT_THROWS
#define YGGDRASIL_RAPIDJSON_ASSERT_THROWS
#endif
#endif

#ifndef DISABLE_YGGDRASIL_RAPIDJSON
#ifndef YGGDRASIL_DISABLE_PYTHON_C_API
#define INIT_PYTHON()							\
  {									\
    yggdrasil_rapidjson::initialize_python("test");				\
    PyObject* path = PySys_GetObject("path");				\
    YGGDRASIL_RAPIDJSON_ASSERT(path);						\
    const char* datadir = std::getenv("DATADIR");			\
    YGGDRASIL_RAPIDJSON_ASSERT(datadir);						\
    PyObject* example_dir = PyUnicode_FromString(datadir);		\
    YGGDRASIL_RAPIDJSON_ASSERT(example_dir);					\
    PyList_Append(path, example_dir);					\
    Py_DECREF(example_dir);						\
  }
#define FINALIZE_PYTHON()			\
  {						\
    yggdrasil_rapidjson::finalize_python("test");		\
  }
#endif // YGGDRASIL_DISABLE_PYTHON_C_API
#define DISPLAY_STRING_ALLOC(name, value)		\
  {							\
    StringBuffer buffer;				\
    Writer<StringBuffer> writer(buffer);		\
    Value container;							\
    Value::AllocatorType allocator;					\
    Value v2(value, allocator);						\
    container.SetArray();						\
    container.PushBack(v2, allocator);					\
    YGGDRASIL_RAPIDJSON_ASSERT(container.Accept(writer));				\
    std::cerr << name << ": " << buffer.GetString() << std::endl;	\
  }
#define DISPLAY_STRING(name, value)			\
  {							\
    StringBuffer buffer;				\
    Writer<StringBuffer> writer(buffer);		\
    Value container;							\
    Value::AllocatorType allocator;					\
    Value v2 value;							\
    container.SetArray();						\
    container.PushBack(v2, allocator);					\
    YGGDRASIL_RAPIDJSON_ASSERT(container.Accept(writer));				\
    std::cerr << name << ": " << buffer.GetString() << std::endl;	\
  }
#ifndef YGGDRASIL_DISABLE_PYTHON_C_API
#define CREATE_PYTHON_INSTANCE(cls, var)				\
  PyObject* var = NULL;							\
  {									\
    PyObject* pyclass = import_python_class("example_python", #cls);	\
    YGGDRASIL_RAPIDJSON_ASSERT(pyclass);						\
    PyObject* pyargs_list = PyList_New(0);				\
    YGGDRASIL_RAPIDJSON_ASSERT(pyargs_list);					\
    PyObject* pyargs_item1 = PyUnicode_FromString("hello");		\
    PyObject* pyargs_item2 = PyFloat_FromDouble(0.5);			\
    YGGDRASIL_RAPIDJSON_ASSERT(PyList_Append(pyargs_list, pyargs_item1) == 0);	\
    YGGDRASIL_RAPIDJSON_ASSERT(PyList_Append(pyargs_list, pyargs_item2) == 0);	\
    PyObject* pyargs = PyList_AsTuple(pyargs_list);			\
    YGGDRASIL_RAPIDJSON_ASSERT(pyargs);						\
    Py_DECREF(pyargs_list);						\
    Py_DECREF(pyargs_item1);						\
    Py_DECREF(pyargs_item2);						\
    PyObject* pykwargs = PyDict_New();					\
    YGGDRASIL_RAPIDJSON_ASSERT(pykwargs);						\
    PyObject* pykwargs_key1 = PyUnicode_FromString("a");		\
    PyObject* pykwargs_key2 = PyUnicode_FromString("b");		\
    PyObject* pykwargs_val1 = PyUnicode_FromString("world");		\
    PyObject* pykwargs_val2 = PyLong_FromLong(1);			\
    YGGDRASIL_RAPIDJSON_ASSERT(PyDict_SetItem(pykwargs, pykwargs_key1, pykwargs_val1) == 0); \
    YGGDRASIL_RAPIDJSON_ASSERT(PyDict_SetItem(pykwargs, pykwargs_key2, pykwargs_val2) == 0); \
    Py_DECREF(pykwargs_key1);						\
    Py_DECREF(pykwargs_key2);						\
    Py_DECREF(pykwargs_val1);						\
    Py_DECREF(pykwargs_val2);						\
    var = PyObject_Call(pyclass, pyargs, pykwargs);			\
    YGGDRASIL_RAPIDJSON_ASSERT(var);						\
    Py_DECREF(pyclass);							\
    Py_DECREF(pyargs);							\
    Py_DECREF(pykwargs);						\
  }
#endif // YGGDRASIL_DISABLE_PYTHON_C_API
#define SIMPLE_TYPES_STRING				\
  "[\"array\","						\
  "\"boolean\","					\
  "\"integer\","						\
  "\"null\","							\
  "\"number\","							\
  "\"object\","							\
  "\"string\","							\
  "\"1darray\","						\
  "\"any\","							\
  "\"bytes\","							\
  "\"class\","							\
  "\"complex\","						\
  "\"float\","							\
  "\"function\","						\
  "\"instance\","						\
  "\"int\","							\
  "\"ndarray\","						\
  "\"obj\","							\
  "\"ply\","							\
  "\"scalar\","							\
  "\"schema\","							\
  "\"uint\","							\
  "\"unicode\"]"
#endif // DISABLE_YGGDRASIL_RAPIDJSON

class Random {
public:
    Random(unsigned seed = 0) : mSeed(seed) {}

    unsigned operator()() {
        mSeed = 214013 * mSeed + 2531011;
        return mSeed;
    }

private:
    unsigned mSeed;
};

#endif // UNITTEST_H_
