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

#ifndef YGGDRASIL_RAPIDJSON_YGGDRASIL_RAPIDJSON_H_
#define YGGDRASIL_RAPIDJSON_YGGDRASIL_RAPIDJSON_H_

/*!\file rapidjson.h
    \brief common definitions and configuration

    \see YGGDRASIL_RAPIDJSON_CONFIG
 */

/*! \defgroup YGGDRASIL_RAPIDJSON_CONFIG RapidJSON configuration
    \brief Configuration macros for library features

    Some RapidJSON features are configurable to adapt the library to a wide
    variety of platforms, environments and usage scenarios.  Most of the
    features can be configured in terms of overridden or predefined
    preprocessor macros at compile-time.

    Some additional customization is available in the \ref YGGDRASIL_RAPIDJSON_ERRORS APIs.

    \note These macros should be given on the compiler command-line
          (where applicable)  to avoid inconsistent values when compiling
          different translation units of a single application.
 */

#include <cstdlib>  // malloc(), realloc(), free(), size_t
#include <cstring>  // memset(), memcpy(), memmove(), memcmp()
#ifndef DISABLE_YGGDRASIL_RAPIDJSON
#include <complex>
#endif // DISABLE_YGGDRASIL_RAPIDJSON

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_VERSION_STRING
//
// ALWAYS synchronize the following 3 macros with corresponding variables in /CMakeLists.txt.
//

//!@cond YGGDRASIL_RAPIDJSON_HIDDEN_FROM_DOXYGEN
// token stringification
#define YGGDRASIL_RAPIDJSON_STRINGIFY(x) YGGDRASIL_RAPIDJSON_DO_STRINGIFY(x)
#define YGGDRASIL_RAPIDJSON_DO_STRINGIFY(x) #x

// token concatenation
#define YGGDRASIL_RAPIDJSON_JOIN(X, Y) YGGDRASIL_RAPIDJSON_DO_JOIN(X, Y)
#define YGGDRASIL_RAPIDJSON_DO_JOIN(X, Y) YGGDRASIL_RAPIDJSON_DO_JOIN2(X, Y)
#define YGGDRASIL_RAPIDJSON_DO_JOIN2(X, Y) X##Y
//!@endcond

/*! \def YGGDRASIL_RAPIDJSON_MAJOR_VERSION
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Major version of RapidJSON in integer
    that this version of YggdrasilRapidJSON is based on.
*/
/*! \def YGGDRASIL_RAPIDJSON_MINOR_VERSION
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Minor version of RapidJSON in integer
    that this version of YggdrasilRapidJSON is based on.
*/
/*! \def YGGDRASIL_RAPIDJSON_PATCH_VERSION
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Patch version of RapidJSON in integer
    that this version of YggdrasilRapidJSON is based on.
*/
/*! \def YGGDRASIL_RAPIDJSON_EXTEN_VERSION
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Version of YggdrasilRapidJSON based on RapidJSON.
*/
/*! \def YGGDRASIL_RAPIDJSON_VERSION_STRING
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Version of RapidJSON in "<major>.<minor>.<patch>.<exten>" string format.
*/
#define YGGDRASIL_RAPIDJSON_MAJOR_VERSION 1
#define YGGDRASIL_RAPIDJSON_MINOR_VERSION 1
#define YGGDRASIL_RAPIDJSON_PATCH_VERSION 0
#define YGGDRASIL_RAPIDJSON_EXTEN_VERSION 1
#define YGGDRASIL_RAPIDJSON_VERSION_STRING \
    YGGDRASIL_RAPIDJSON_STRINGIFY(YGGDRASIL_RAPIDJSON_MAJOR_VERSION.YGGDRASIL_RAPIDJSON_MINOR_VERSION.YGGDRASIL_RAPIDJSON_PATCH_VERSION.YGGDRASIL_RAPIDJSON_EXTEN_VERSION)

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_NAMESPACE_(BEGIN|END)
/*! \def YGGDRASIL_RAPIDJSON_NAMESPACE
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief   provide custom rapidjson namespace

    In order to avoid symbol clashes and/or "One Definition Rule" errors
    between multiple inclusions of (different versions of) RapidJSON in
    a single binary, users can customize the name of the main RapidJSON
    namespace.

    In case of a single nesting level, defining \c YGGDRASIL_RAPIDJSON_NAMESPACE
    to a custom name (e.g. \c MyRapidJSON) is sufficient.  If multiple
    levels are needed, both \ref YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN and \ref
    YGGDRASIL_RAPIDJSON_NAMESPACE_END need to be defined as well:

    \code
    // in some .cpp file
    #define YGGDRASIL_RAPIDJSON_NAMESPACE my::rapidjson
    #define YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN namespace my { namespace rapidjson {
    #define YGGDRASIL_RAPIDJSON_NAMESPACE_END   } }
    #include "yggdrasil_rapidjson/..."
    \endcode

    \see rapidjson
 */
/*! \def YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief   provide custom rapidjson namespace (opening expression)
    \see YGGDRASIL_RAPIDJSON_NAMESPACE
*/
/*! \def YGGDRASIL_RAPIDJSON_NAMESPACE_END
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief   provide custom rapidjson namespace (closing expression)
    \see YGGDRASIL_RAPIDJSON_NAMESPACE
*/
#ifndef YGGDRASIL_RAPIDJSON_NAMESPACE
#define YGGDRASIL_RAPIDJSON_NAMESPACE yggdrasil_rapidjson
#endif
#ifndef YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN
#define YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN namespace YGGDRASIL_RAPIDJSON_NAMESPACE {
#endif
#ifndef YGGDRASIL_RAPIDJSON_NAMESPACE_END
#define YGGDRASIL_RAPIDJSON_NAMESPACE_END }
#endif

///////////////////////////////////////////////////////////////////////////////
// __cplusplus macro

//!@cond YGGDRASIL_RAPIDJSON_HIDDEN_FROM_DOXYGEN

#if defined(_MSC_VER)
#define YGGDRASIL_RAPIDJSON_CPLUSPLUS _MSVC_LANG
#else
#define YGGDRASIL_RAPIDJSON_CPLUSPLUS __cplusplus
#endif

//!@endcond

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_HAS_STDSTRING

#ifndef YGGDRASIL_RAPIDJSON_HAS_STDSTRING
#ifdef YGGDRASIL_RAPIDJSON_DOXYGEN_RUNNING
#define YGGDRASIL_RAPIDJSON_HAS_STDSTRING 1 // force generation of documentation
#else
#define YGGDRASIL_RAPIDJSON_HAS_STDSTRING 0 // no std::string support by default
#endif
/*! \def YGGDRASIL_RAPIDJSON_HAS_STDSTRING
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Enable RapidJSON support for \c std::string

    By defining this preprocessor symbol to \c 1, several convenience functions for using
    \ref yggdrasil_rapidjson::GenericValue with \c std::string are enabled, especially
    for construction and comparison.

    \hideinitializer
*/
#endif // !defined(YGGDRASIL_RAPIDJSON_HAS_STDSTRING)

#if YGGDRASIL_RAPIDJSON_HAS_STDSTRING
#include <string>
#endif // YGGDRASIL_RAPIDJSON_HAS_STDSTRING

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_USE_MEMBERSMAP

/*! \def YGGDRASIL_RAPIDJSON_USE_MEMBERSMAP
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Enable RapidJSON support for object members handling in a \c std::multimap

    By defining this preprocessor symbol to \c 1, \ref yggdrasil_rapidjson::GenericValue object
    members are stored in a \c std::multimap for faster lookup and deletion times, a
    trade off with a slightly slower insertion time and a small object allocat(or)ed
    memory overhead.

    \hideinitializer
*/
#ifndef YGGDRASIL_RAPIDJSON_USE_MEMBERSMAP
#define YGGDRASIL_RAPIDJSON_USE_MEMBERSMAP 0 // not by default
#endif

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_NO_INT64DEFINE

/*! \def YGGDRASIL_RAPIDJSON_NO_INT64DEFINE
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Use external 64-bit integer types.

    RapidJSON requires the 64-bit integer types \c int64_t and  \c uint64_t types
    to be available at global scope.

    If users have their own definition, define YGGDRASIL_RAPIDJSON_NO_INT64DEFINE to
    prevent RapidJSON from defining its own types.
*/
#ifndef YGGDRASIL_RAPIDJSON_NO_INT64DEFINE
#ifndef __STDC_LIMIT_MACROS
#define __STDC_LIMIT_MACROS
#endif
#ifndef __STDC_CONSTANT_MACROS
#define __STDC_CONSTANT_MACROS
#endif
//!@cond YGGDRASIL_RAPIDJSON_HIDDEN_FROM_DOXYGEN
#if defined(_MSC_VER) && (_MSC_VER < 1800) // Visual Studio 2013
#include "msinttypes/stdint.h"
#include "msinttypes/inttypes.h"
#else
// Other compilers should have this.
#include <stdint.h>
#include <inttypes.h>
#endif
//!@endcond
#ifdef YGGDRASIL_RAPIDJSON_DOXYGEN_RUNNING
#define YGGDRASIL_RAPIDJSON_NO_INT64DEFINE
#endif
#endif // YGGDRASIL_RAPIDJSON_NO_INT64TYPEDEF

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_FORCEINLINE

#ifndef YGGDRASIL_RAPIDJSON_FORCEINLINE
//!@cond YGGDRASIL_RAPIDJSON_HIDDEN_FROM_DOXYGEN
#if defined(_MSC_VER) && defined(NDEBUG)
#define YGGDRASIL_RAPIDJSON_FORCEINLINE __forceinline
#elif defined(__GNUC__) && __GNUC__ >= 4 && defined(NDEBUG)
#define YGGDRASIL_RAPIDJSON_FORCEINLINE __attribute__((always_inline))
#else
#define YGGDRASIL_RAPIDJSON_FORCEINLINE
#endif
//!@endcond
#endif // YGGDRASIL_RAPIDJSON_FORCEINLINE

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_ENDIAN
#define YGGDRASIL_RAPIDJSON_LITTLEENDIAN  0   //!< Little endian machine
#define YGGDRASIL_RAPIDJSON_BIGENDIAN     1   //!< Big endian machine

//! Endianness of the machine.
/*!
    \def YGGDRASIL_RAPIDJSON_ENDIAN
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG

    GCC 4.6 provided macro for detecting endianness of the target machine. But other
    compilers may not have this. User can define YGGDRASIL_RAPIDJSON_ENDIAN to either
    \ref YGGDRASIL_RAPIDJSON_LITTLEENDIAN or \ref YGGDRASIL_RAPIDJSON_BIGENDIAN.

    Default detection implemented with reference to
    \li https://gcc.gnu.org/onlinedocs/gcc-4.6.0/cpp/Common-Predefined-Macros.html
    \li http://www.boost.org/doc/libs/1_42_0/boost/detail/endian.hpp
*/
#ifndef YGGDRASIL_RAPIDJSON_ENDIAN
// Detect with GCC 4.6's macro
#  ifdef __BYTE_ORDER__
#    if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
#      define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_LITTLEENDIAN
#    elif __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#      define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_BIGENDIAN
#    else
#      error Unknown machine endianness detected. User needs to define YGGDRASIL_RAPIDJSON_ENDIAN.
#    endif // __BYTE_ORDER__
// Detect with GLIBC's endian.h
#  elif defined(__GLIBC__)
#    include <endian.h>
#    if (__BYTE_ORDER == __LITTLE_ENDIAN)
#      define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_LITTLEENDIAN
#    elif (__BYTE_ORDER == __BIG_ENDIAN)
#      define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_BIGENDIAN
#    else
#      error Unknown machine endianness detected. User needs to define YGGDRASIL_RAPIDJSON_ENDIAN.
#   endif // __GLIBC__
// Detect with _LITTLE_ENDIAN and _BIG_ENDIAN macro
#  elif defined(_LITTLE_ENDIAN) && !defined(_BIG_ENDIAN)
#    define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_LITTLEENDIAN
#  elif defined(_BIG_ENDIAN) && !defined(_LITTLE_ENDIAN)
#    define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_BIGENDIAN
// Detect with architecture macros
#  elif defined(__sparc) || defined(__sparc__) || defined(_POWER) || defined(__powerpc__) || defined(__ppc__) || defined(__ppc64__) || defined(__hpux) || defined(__hppa) || defined(_MIPSEB) || defined(_POWER) || defined(__s390__)
#    define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_BIGENDIAN
#  elif defined(__i386__) || defined(__alpha__) || defined(__ia64) || defined(__ia64__) || defined(_M_IX86) || defined(_M_IA64) || defined(_M_ALPHA) || defined(__amd64) || defined(__amd64__) || defined(_M_AMD64) || defined(__x86_64) || defined(__x86_64__) || defined(_M_X64) || defined(__bfin__)
#    define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_LITTLEENDIAN
#  elif defined(_MSC_VER) && (defined(_M_ARM) || defined(_M_ARM64))
#    define YGGDRASIL_RAPIDJSON_ENDIAN YGGDRASIL_RAPIDJSON_LITTLEENDIAN
#  elif defined(YGGDRASIL_RAPIDJSON_DOXYGEN_RUNNING)
#    define YGGDRASIL_RAPIDJSON_ENDIAN
#  else
#    error Unknown machine endianness detected. User needs to define YGGDRASIL_RAPIDJSON_ENDIAN.
#  endif
#endif // YGGDRASIL_RAPIDJSON_ENDIAN

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_64BIT

//! Whether using 64-bit architecture
#ifndef YGGDRASIL_RAPIDJSON_64BIT
#if defined(__LP64__) || (defined(__x86_64__) && defined(__ILP32__)) || defined(_WIN64) || defined(__EMSCRIPTEN__)
#define YGGDRASIL_RAPIDJSON_64BIT 1
#else
#define YGGDRASIL_RAPIDJSON_64BIT 0
#endif
#endif // YGGDRASIL_RAPIDJSON_64BIT

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_ALIGN

//! Data alignment of the machine.
/*! \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \param x pointer to align

    Some machines require strict data alignment. The default is 8 bytes.
    User can customize by defining the YGGDRASIL_RAPIDJSON_ALIGN function macro.
*/
#ifndef YGGDRASIL_RAPIDJSON_ALIGN
#define YGGDRASIL_RAPIDJSON_ALIGN(x) (((x) + static_cast<size_t>(7u)) & ~static_cast<size_t>(7u))
#endif

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_UINT64_C2

//! Construct a 64-bit literal by a pair of 32-bit integer.
/*!
    64-bit literal with or without ULL suffix is prone to compiler warnings.
    UINT64_C() is C macro which cause compilation problems.
    Use this macro to define 64-bit constants by a pair of 32-bit integer.
*/
#ifndef YGGDRASIL_RAPIDJSON_UINT64_C2
#define YGGDRASIL_RAPIDJSON_UINT64_C2(high32, low32) ((static_cast<uint64_t>(high32) << 32) | static_cast<uint64_t>(low32))
#endif

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_48BITPOINTER_OPTIMIZATION

//! Use only lower 48-bit address for some pointers.
/*!
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG

    This optimization uses the fact that current X86-64 architecture only implement lower 48-bit virtual address.
    The higher 16-bit can be used for storing other data.
    \c GenericValue uses this optimization to reduce its size form 24 bytes to 16 bytes in 64-bit architecture.
*/
#ifndef YGGDRASIL_RAPIDJSON_48BITPOINTER_OPTIMIZATION
#if defined(__amd64__) || defined(__amd64) || defined(__x86_64__) || defined(__x86_64) || defined(_M_X64) || defined(_M_AMD64)
#define YGGDRASIL_RAPIDJSON_48BITPOINTER_OPTIMIZATION 1
#else
#define YGGDRASIL_RAPIDJSON_48BITPOINTER_OPTIMIZATION 0
#endif
#endif // YGGDRASIL_RAPIDJSON_48BITPOINTER_OPTIMIZATION

#if YGGDRASIL_RAPIDJSON_48BITPOINTER_OPTIMIZATION == 1
#if YGGDRASIL_RAPIDJSON_64BIT != 1
#error YGGDRASIL_RAPIDJSON_48BITPOINTER_OPTIMIZATION can only be set to 1 when YGGDRASIL_RAPIDJSON_64BIT=1
#endif
#define YGGDRASIL_RAPIDJSON_SETPOINTER(type, p, x) (p = reinterpret_cast<type *>((reinterpret_cast<uintptr_t>(p) & static_cast<uintptr_t>(YGGDRASIL_RAPIDJSON_UINT64_C2(0xFFFF0000, 0x00000000))) | reinterpret_cast<uintptr_t>(reinterpret_cast<const void*>(x))))
#define YGGDRASIL_RAPIDJSON_GETPOINTER(type, p) (reinterpret_cast<type *>(reinterpret_cast<uintptr_t>(p) & static_cast<uintptr_t>(YGGDRASIL_RAPIDJSON_UINT64_C2(0x0000FFFF, 0xFFFFFFFF))))
#else
#define YGGDRASIL_RAPIDJSON_SETPOINTER(type, p, x) (p = (x))
#define YGGDRASIL_RAPIDJSON_GETPOINTER(type, p) (p)
#endif

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_SSE2/YGGDRASIL_RAPIDJSON_SSE42/YGGDRASIL_RAPIDJSON_NEON/YGGDRASIL_RAPIDJSON_SIMD

/*! \def YGGDRASIL_RAPIDJSON_SIMD
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief Enable SSE2/SSE4.2/Neon optimization.

    RapidJSON supports optimized implementations for some parsing operations
    based on the SSE2, SSE4.2 or NEon SIMD extensions on modern Intel
    or ARM compatible processors.

    To enable these optimizations, three different symbols can be defined;
    \code
    // Enable SSE2 optimization.
    #define YGGDRASIL_RAPIDJSON_SSE2

    // Enable SSE4.2 optimization.
    #define YGGDRASIL_RAPIDJSON_SSE42
    \endcode

    // Enable ARM Neon optimization.
    #define YGGDRASIL_RAPIDJSON_NEON
    \endcode

    \c YGGDRASIL_RAPIDJSON_SSE42 takes precedence over SSE2, if both are defined.

    If any of these symbols is defined, RapidJSON defines the macro
    \c YGGDRASIL_RAPIDJSON_SIMD to indicate the availability of the optimized code.
*/
#if defined(YGGDRASIL_RAPIDJSON_SSE2) || defined(YGGDRASIL_RAPIDJSON_SSE42) \
    || defined(YGGDRASIL_RAPIDJSON_NEON) || defined(YGGDRASIL_RAPIDJSON_DOXYGEN_RUNNING)
#define YGGDRASIL_RAPIDJSON_SIMD
#endif

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_NO_SIZETYPEDEFINE

#ifndef YGGDRASIL_RAPIDJSON_NO_SIZETYPEDEFINE
/*! \def YGGDRASIL_RAPIDJSON_NO_SIZETYPEDEFINE
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \brief User-provided \c SizeType definition.

    In order to avoid using 32-bit size types for indexing strings and arrays,
    define this preprocessor symbol and provide the type yggdrasil_rapidjson::SizeType
    before including RapidJSON:
    \code
    #define YGGDRASIL_RAPIDJSON_NO_SIZETYPEDEFINE
    namespace rapidjson { typedef ::std::size_t SizeType; }
    #include "yggdrasil_rapidjson/..."
    \endcode

    \see yggdrasil_rapidjson::SizeType
*/
#ifdef YGGDRASIL_RAPIDJSON_DOXYGEN_RUNNING
#define YGGDRASIL_RAPIDJSON_NO_SIZETYPEDEFINE
#endif
YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN
//! Size type (for string lengths, array sizes, etc.)
/*! RapidJSON uses 32-bit array/string indices even on 64-bit platforms,
    instead of using \c size_t. Users may override the SizeType by defining
    \ref YGGDRASIL_RAPIDJSON_NO_SIZETYPEDEFINE.
*/
typedef unsigned SizeType;
YGGDRASIL_RAPIDJSON_NAMESPACE_END
#endif

// always import std::size_t to rapidjson namespace
YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN
using std::size_t;
YGGDRASIL_RAPIDJSON_NAMESPACE_END

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_ASSERT

//! Assertion.
/*! \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    By default, rapidjson uses C \c assert() for internal assertions.
    User can override it by defining YGGDRASIL_RAPIDJSON_ASSERT(x) macro.

    \note Parsing errors are handled and can be customized by the
          \ref YGGDRASIL_RAPIDJSON_ERRORS APIs.
*/
#ifndef YGGDRASIL_RAPIDJSON_ASSERT
#include <cassert>
#define YGGDRASIL_RAPIDJSON_ASSERT(x) assert(x)
#endif // YGGDRASIL_RAPIDJSON_ASSERT

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_STATIC_ASSERT

// Prefer C++11 static_assert, if available
#ifndef YGGDRASIL_RAPIDJSON_STATIC_ASSERT
#if YGGDRASIL_RAPIDJSON_CPLUSPLUS >= 201103L || ( defined(_MSC_VER) && _MSC_VER >= 1800 )
#define YGGDRASIL_RAPIDJSON_STATIC_ASSERT(x) \
   static_assert(x, YGGDRASIL_RAPIDJSON_STRINGIFY(x))
#endif // C++11
#endif // YGGDRASIL_RAPIDJSON_STATIC_ASSERT

// Adopt C++03 implementation from boost
#ifndef YGGDRASIL_RAPIDJSON_STATIC_ASSERT
#ifndef __clang__
//!@cond YGGDRASIL_RAPIDJSON_HIDDEN_FROM_DOXYGEN
#endif
YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN
template <bool x> struct STATIC_ASSERTION_FAILURE;
template <> struct STATIC_ASSERTION_FAILURE<true> { enum { value = 1 }; };
template <size_t x> struct StaticAssertTest {};
YGGDRASIL_RAPIDJSON_NAMESPACE_END

#if defined(__GNUC__) || defined(__clang__)
#define YGGDRASIL_RAPIDJSON_STATIC_ASSERT_UNUSED_ATTRIBUTE __attribute__((unused))
#else
#define YGGDRASIL_RAPIDJSON_STATIC_ASSERT_UNUSED_ATTRIBUTE 
#endif
#ifndef __clang__
//!@endcond
#endif

/*! \def YGGDRASIL_RAPIDJSON_STATIC_ASSERT
    \brief (Internal) macro to check for conditions at compile-time
    \param x compile-time condition
    \hideinitializer
 */
#define YGGDRASIL_RAPIDJSON_STATIC_ASSERT(x) \
    typedef ::YGGDRASIL_RAPIDJSON_NAMESPACE::StaticAssertTest< \
      sizeof(::YGGDRASIL_RAPIDJSON_NAMESPACE::STATIC_ASSERTION_FAILURE<bool(x) >)> \
    YGGDRASIL_RAPIDJSON_JOIN(StaticAssertTypedef, __LINE__) YGGDRASIL_RAPIDJSON_STATIC_ASSERT_UNUSED_ATTRIBUTE
#endif // YGGDRASIL_RAPIDJSON_STATIC_ASSERT

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_LIKELY, YGGDRASIL_RAPIDJSON_UNLIKELY

//! Compiler branching hint for expression with high probability to be true.
/*!
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \param x Boolean expression likely to be true.
*/
#ifndef YGGDRASIL_RAPIDJSON_LIKELY
#if defined(__GNUC__) || defined(__clang__)
#define YGGDRASIL_RAPIDJSON_LIKELY(x) __builtin_expect(!!(x), 1)
#else
#define YGGDRASIL_RAPIDJSON_LIKELY(x) (x)
#endif
#endif

//! Compiler branching hint for expression with low probability to be true.
/*!
    \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    \param x Boolean expression unlikely to be true.
*/
#ifndef YGGDRASIL_RAPIDJSON_UNLIKELY
#if defined(__GNUC__) || defined(__clang__)
#define YGGDRASIL_RAPIDJSON_UNLIKELY(x) __builtin_expect(!!(x), 0)
#else
#define YGGDRASIL_RAPIDJSON_UNLIKELY(x) (x)
#endif
#endif

///////////////////////////////////////////////////////////////////////////////
// Helpers

//!@cond YGGDRASIL_RAPIDJSON_HIDDEN_FROM_DOXYGEN

#define YGGDRASIL_RAPIDJSON_MULTILINEMACRO_BEGIN do {
#define YGGDRASIL_RAPIDJSON_MULTILINEMACRO_END \
} while((void)0, 0)

// adopted from Boost
#define YGGDRASIL_RAPIDJSON_VERSION_CODE(x,y,z) \
  (((x)*100000) + ((y)*100) + (z))

#if defined(__has_builtin)
#define YGGDRASIL_RAPIDJSON_HAS_BUILTIN(x) __has_builtin(x)
#else
#define YGGDRASIL_RAPIDJSON_HAS_BUILTIN(x) 0
#endif

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_DIAG_PUSH/POP, YGGDRASIL_RAPIDJSON_DIAG_OFF

#if defined(__GNUC__)
#define YGGDRASIL_RAPIDJSON_GNUC \
    YGGDRASIL_RAPIDJSON_VERSION_CODE(__GNUC__,__GNUC_MINOR__,__GNUC_PATCHLEVEL__)
#endif

#if defined(__clang__) || (defined(YGGDRASIL_RAPIDJSON_GNUC) && YGGDRASIL_RAPIDJSON_GNUC >= YGGDRASIL_RAPIDJSON_VERSION_CODE(4,2,0))

#define YGGDRASIL_RAPIDJSON_PRAGMA(x) _Pragma(YGGDRASIL_RAPIDJSON_STRINGIFY(x))
#define YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(x) YGGDRASIL_RAPIDJSON_PRAGMA(GCC diagnostic x)
#define YGGDRASIL_RAPIDJSON_DIAG_OFF(x) \
    YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(ignored YGGDRASIL_RAPIDJSON_STRINGIFY(YGGDRASIL_RAPIDJSON_JOIN(-W,x)))

// push/pop support in Clang and GCC>=4.6
#if defined(__clang__) || (defined(YGGDRASIL_RAPIDJSON_GNUC) && YGGDRASIL_RAPIDJSON_GNUC >= YGGDRASIL_RAPIDJSON_VERSION_CODE(4,6,0))
#define YGGDRASIL_RAPIDJSON_DIAG_PUSH YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(push)
#define YGGDRASIL_RAPIDJSON_DIAG_POP  YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(pop)
#else // GCC >= 4.2, < 4.6
#define YGGDRASIL_RAPIDJSON_DIAG_PUSH /* ignored */
#define YGGDRASIL_RAPIDJSON_DIAG_POP /* ignored */
#endif

#elif defined(_MSC_VER)

// pragma (MSVC specific)
#define YGGDRASIL_RAPIDJSON_PRAGMA(x) __pragma(x)
#define YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(x) YGGDRASIL_RAPIDJSON_PRAGMA(warning(x))

#define YGGDRASIL_RAPIDJSON_DIAG_OFF(x) YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(disable: x)
#define YGGDRASIL_RAPIDJSON_DIAG_PUSH YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(push)
#define YGGDRASIL_RAPIDJSON_DIAG_POP  YGGDRASIL_RAPIDJSON_DIAG_PRAGMA(pop)

#else

#define YGGDRASIL_RAPIDJSON_DIAG_OFF(x) /* ignored */
#define YGGDRASIL_RAPIDJSON_DIAG_PUSH   /* ignored */
#define YGGDRASIL_RAPIDJSON_DIAG_POP    /* ignored */

#endif // YGGDRASIL_RAPIDJSON_DIAG_*

///////////////////////////////////////////////////////////////////////////////
// C++11 features

#ifndef YGGDRASIL_RAPIDJSON_HAS_CXX11
#define YGGDRASIL_RAPIDJSON_HAS_CXX11 (YGGDRASIL_RAPIDJSON_CPLUSPLUS >= 201103L)
#endif

#ifndef YGGDRASIL_RAPIDJSON_HAS_CXX20
#define YGGDRASIL_RAPIDJSON_HAS_CXX20 (YGGDRASIL_RAPIDJSON_CPLUSPLUS >= 202002L)
#endif

#ifndef YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS 1
#elif defined(__clang__)
#if __has_feature(cxx_rvalue_references) && \
    (defined(_MSC_VER) || defined(_LIBCPP_VERSION) || defined(__GLIBCXX__) && __GLIBCXX__ >= 20080306)
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS 1
#else
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS 0
#endif
#elif (defined(YGGDRASIL_RAPIDJSON_GNUC) && (YGGDRASIL_RAPIDJSON_GNUC >= YGGDRASIL_RAPIDJSON_VERSION_CODE(4,3,0)) && defined(__GXX_EXPERIMENTAL_CXX0X__)) || \
      (defined(_MSC_VER) && _MSC_VER >= 1600) || \
      (defined(__SUNPRO_CC) && __SUNPRO_CC >= 0x5140 && defined(__GXX_EXPERIMENTAL_CXX0X__))

#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS 1
#else
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS 0
#endif
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS

#if YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS
#include <utility> // std::move
#endif

#ifndef YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT 1
#elif defined(__clang__)
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT __has_feature(cxx_noexcept)
#elif (defined(YGGDRASIL_RAPIDJSON_GNUC) && (YGGDRASIL_RAPIDJSON_GNUC >= YGGDRASIL_RAPIDJSON_VERSION_CODE(4,6,0)) && defined(__GXX_EXPERIMENTAL_CXX0X__)) || \
    (defined(_MSC_VER) && _MSC_VER >= 1900) || \
    (defined(__SUNPRO_CC) && __SUNPRO_CC >= 0x5140 && defined(__GXX_EXPERIMENTAL_CXX0X__))
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT 1
#else
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT 0
#endif
#endif
#ifndef YGGDRASIL_RAPIDJSON_NOEXCEPT
#if YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT
#define YGGDRASIL_RAPIDJSON_NOEXCEPT noexcept
#else
#define YGGDRASIL_RAPIDJSON_NOEXCEPT throw()
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11_NOEXCEPT
#endif

// no automatic detection, yet
#ifndef YGGDRASIL_RAPIDJSON_HAS_CXX11_TYPETRAITS
#if (defined(_MSC_VER) && _MSC_VER >= 1700)
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_TYPETRAITS 1
#else
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_TYPETRAITS 0
#endif
#endif

#ifndef YGGDRASIL_RAPIDJSON_HAS_CXX11_RANGE_FOR
#if defined(__clang__)
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RANGE_FOR __has_feature(cxx_range_for)
#elif (defined(YGGDRASIL_RAPIDJSON_GNUC) && (YGGDRASIL_RAPIDJSON_GNUC >= YGGDRASIL_RAPIDJSON_VERSION_CODE(4,6,0)) && defined(__GXX_EXPERIMENTAL_CXX0X__)) || \
      (defined(_MSC_VER) && _MSC_VER >= 1700) || \
      (defined(__SUNPRO_CC) && __SUNPRO_CC >= 0x5140 && defined(__GXX_EXPERIMENTAL_CXX0X__))
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RANGE_FOR 1
#else
#define YGGDRASIL_RAPIDJSON_HAS_CXX11_RANGE_FOR 0
#endif
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11_RANGE_FOR

///////////////////////////////////////////////////////////////////////////////
// C++17 features

#ifndef YGGDRASIL_RAPIDJSON_HAS_CXX17
#define YGGDRASIL_RAPIDJSON_HAS_CXX17 (YGGDRASIL_RAPIDJSON_CPLUSPLUS >= 201703L)
#endif

#if YGGDRASIL_RAPIDJSON_HAS_CXX17
# define YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH [[fallthrough]]
#elif defined(__has_cpp_attribute)
# if __has_cpp_attribute(clang::fallthrough)
#  define YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH [[clang::fallthrough]]
# elif __has_cpp_attribute(fallthrough)
#  define YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH __attribute__((fallthrough))
# else
#  define YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH
# endif
#else
# if defined(__clang__)
#  define YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH [[clang::fallthrough]]
# else
#  define YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH
# endif
#endif

//!@endcond

//! Assertion (in non-throwing contexts).
 /*! \ingroup YGGDRASIL_RAPIDJSON_CONFIG
    Some functions provide a \c noexcept guarantee, if the compiler supports it.
    In these cases, the \ref YGGDRASIL_RAPIDJSON_ASSERT macro cannot be overridden to
    throw an exception.  This macro adds a separate customization point for
    such cases.

    Defaults to C \c assert() (as \ref YGGDRASIL_RAPIDJSON_ASSERT), if \c noexcept is
    supported, and to \ref YGGDRASIL_RAPIDJSON_ASSERT otherwise.
 */

///////////////////////////////////////////////////////////////////////////////
// YGGDRASIL_RAPIDJSON_NOEXCEPT_ASSERT

#ifndef YGGDRASIL_RAPIDJSON_NOEXCEPT_ASSERT
#ifdef YGGDRASIL_RAPIDJSON_ASSERT_THROWS
#include <cassert>
#define YGGDRASIL_RAPIDJSON_NOEXCEPT_ASSERT(x) assert(x)
#else
#define YGGDRASIL_RAPIDJSON_NOEXCEPT_ASSERT(x) YGGDRASIL_RAPIDJSON_ASSERT(x)
#endif // YGGDRASIL_RAPIDJSON_ASSERT_THROWS
#endif // YGGDRASIL_RAPIDJSON_NOEXCEPT_ASSERT

///////////////////////////////////////////////////////////////////////////////
// malloc/realloc/free

#ifndef YGGDRASIL_RAPIDJSON_MALLOC
///! customization point for global \c malloc
#define YGGDRASIL_RAPIDJSON_MALLOC(size) std::malloc(size)
#endif
#ifndef YGGDRASIL_RAPIDJSON_REALLOC
///! customization point for global \c realloc
#define YGGDRASIL_RAPIDJSON_REALLOC(ptr, new_size) std::realloc(ptr, new_size)
#endif
#ifndef YGGDRASIL_RAPIDJSON_FREE
///! customization point for global \c free
#define YGGDRASIL_RAPIDJSON_FREE(ptr) std::free(ptr)
#endif

///////////////////////////////////////////////////////////////////////////////
// new/delete

#ifndef YGGDRASIL_RAPIDJSON_NEW
///! customization point for global \c new
#define YGGDRASIL_RAPIDJSON_NEW(TypeName) new TypeName
#endif
#ifndef YGGDRASIL_RAPIDJSON_DELETE
///! customization point for global \c delete
#define YGGDRASIL_RAPIDJSON_DELETE(x) delete x
#endif

///////////////////////////////////////////////////////////////////////////////
// Type

/*! \namespace rapidjson
    \brief main RapidJSON namespace
    \see YGGDRASIL_RAPIDJSON_NAMESPACE
*/
YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

//! Type of JSON value
enum Type {
    kNullType = 0,      //!< null
    kFalseType = 1,     //!< false
    kTrueType = 2,      //!< true
    kObjectType = 3,    //!< object
    kArrayType = 4,     //!< array
    kStringType = 5,    //!< string
    kNumberType = 6     //!< number
};


#ifndef DISABLE_YGGDRASIL_RAPIDJSON

#ifndef _MSC_VER
// #define YGGDRASIL_LONG_DOUBLE_AVAILABLE
#endif // _MSC_VER

enum YggSubType {
    kYggNullSubType = 0,
    kYggIntSubType = 1,
    kYggUintSubType = 2,
    kYggFloatSubType = 3,
    kYggComplexSubType = 4,
    kYggStringSubType = 5
};

enum YggEncodingType {
  kYggNullEncodingType = 0,
  kYggASCIIEncodingType = 1,
  kYggUTF8EncodingType = 2,
  kYggUCS4EncodingType = 3
};


//  Produce value of bit n.  n must be less than 32.
#define Bit_(n, p)  ((uint ## p ## _t) 1 << (n))
//  Create a mask of n bits in the low bits.  n must be less than 32.
#define Mask_(n, p) (Bit_(n, p) - 1)
//  Produce value of bit n.  n must be less than 32.
#define Bit(n)  ((uint32_t) 1 << (n))
//  Create a mask of n bits in the low bits.  n must be less than 32.
#define Mask(n) (Bit(n) - 1)

typedef struct float16_t {
  uint16_t mem;
  float16_t() : mem(0) {}
  template <typename T>
  float16_t(const T x) : mem(0) {
    float y = static_cast<float>(x);
    from_float(y);
  }
  void from_float(const float& x) {
    union { uint32_t enc; float  value; } tmp;
    tmp.value = x;
    uint16_t s = static_cast<uint16_t>(tmp.enc >> 31);
    if ((tmp.enc >> 23 & Mask( 8)) != 255) {
      // Use float arithmetic to ensure values are properly rounded
#if YGGDRASIL_RAPIDJSON_HAS_CXX17
      tmp.value = (tmp.value * (1.0f + 0x1p-13f) - tmp.value) * 0x1p13f;
      tmp.value *= 0x1p112f;
      tmp.value *= 0x1p-112f;
      tmp.value *= 0x1p-112f;
#else // YGGDRASIL_RAPIDJSON_HAS_CXX17
      float p13 = static_cast<float>(pow(2.0, 13)),
	pn13 = static_cast<float>(pow(2.0, -13)),
	p122 = static_cast<float>(pow(2.0, 122)),
	pn122 = static_cast<float>(pow(2.0, -122));
      tmp.value = (tmp.value * (1.0f + pn13) - tmp.value) * p13;
      tmp.value *= p122;
      tmp.value *= pn122;
      tmp.value *= pn122;
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX17
    }
    mem = static_cast<uint16_t>(static_cast<uint16_t>(s << 15u) | static_cast<uint16_t>((tmp.enc >> 13u) & Mask_(15u, 16)));
    // uint32_t e = tmp.enc >> 23 & Mask( 8);
    // uint32_t f = tmp.enc       & Mask(23);
    // f >>= 23 - 10;
    // f &= Mask(10);
    // switch (e) {
    // case 0:
    //   if (f != 0) {
    // 	e = 1 + (15 - 127);
    // 	while (f > Bit(10)) {
    // 	  f >>= 1;
    // 	  e += 1;
    // 	}
    // 	f &= Mask(10);
    //   }
    //   break;
    // default:
    //   e += 15 - 127;
    //   break;
    // case 255:
    //   e = 31;
    //   break;
    // }
    // if (e == 255) {
    //   mem = s << 15 | 31 << 10 | f;
    // } else {
    //   mem = s << 15 | e << 10 | f;
    // }
  }
  operator float() const {
    union { uint32_t enc; float  value; } tmp;
    uint32_t s = static_cast<uint32_t>(mem >> 15);
    uint32_t e = static_cast<uint32_t>(mem >> 10) & Mask( 5);
    uint32_t f = static_cast<uint32_t>(mem)       & Mask(10);
    f <<= 23 - 10;
    // switch (e) {
    // case 0:
    //   if (f != 0) {
    // 	e = 1 + (127 - 15);
    // 	while (f < Bit(23)) {
    // 	  f <<= 1;
    // 	  e -= 1;
    // 	}
    // 	f &= Mask(23);
    //   }
    //   break;
    // default:
    //   e += 127 - 15;
    //   break;
    // case 31:
    //   e = 255;
    //   break;
    // }
    if (e == 31) {
      tmp.enc = s << 31 | 255 << 23 | f;
    } else {
      tmp.enc = s << 31 | e << 23 | f;
#if YGGDRASIL_RAPIDJSON_HAS_CXX17
      tmp.value *= 0x1p112f;
#else // YGGDRASIL_RAPIDJSON_HAS_CXX17
      tmp.value *= static_cast<float>(pow(2.0, 112));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX17
    }
    return tmp.value;
  }
#define OP_(type)				\
  operator type() const {			\
    float tmp = float(*this);			\
    return static_cast<type>(tmp);		\
  }
  OP_(double);
  OP_(int8_t);
  OP_(int16_t);
  OP_(int32_t);
  OP_(int64_t);
  OP_(uint8_t);
  OP_(uint16_t);
  OP_(uint32_t);
  OP_(uint64_t);
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
  OP_(long double);
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE
#undef OP_
} float16_t;

#undef Bit
#undef Mask


template <typename T> inline YggSubType GetYggSubType() { return kYggNullSubType; }
template<> inline YggSubType GetYggSubType<uint8_t>() { return kYggUintSubType; }
template<> inline YggSubType GetYggSubType<uint16_t>() { return kYggUintSubType; }
template<> inline YggSubType GetYggSubType<uint32_t>() { return kYggUintSubType; }
template<> inline YggSubType GetYggSubType<uint64_t>() { return kYggUintSubType; }
template<> inline YggSubType GetYggSubType<int8_t>() { return kYggIntSubType; }
template<> inline YggSubType GetYggSubType<int16_t>() { return kYggIntSubType; }
template<> inline YggSubType GetYggSubType<int32_t>() { return kYggIntSubType; }
template<> inline YggSubType GetYggSubType<int64_t>() { return kYggIntSubType; }
template<> inline YggSubType GetYggSubType<float16_t>() { return kYggFloatSubType; }
template<> inline YggSubType GetYggSubType<float>() { return kYggFloatSubType; }
template<> inline YggSubType GetYggSubType<double>() { return kYggFloatSubType; }
template<> inline YggSubType GetYggSubType<std::complex<float> >() { return kYggComplexSubType; }
template<> inline YggSubType GetYggSubType<std::complex<double> >() { return kYggComplexSubType; }
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
template<> inline YggSubType GetYggSubType<long double>() { return kYggFloatSubType; }
template<> inline YggSubType GetYggSubType<std::complex<long double> >() { return kYggComplexSubType; }
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE

#endif // DISABLE_YGGDRASIL_RAPIDJSON

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // YGGDRASIL_RAPIDJSON_YGGDRASIL_RAPIDJSON_H_
