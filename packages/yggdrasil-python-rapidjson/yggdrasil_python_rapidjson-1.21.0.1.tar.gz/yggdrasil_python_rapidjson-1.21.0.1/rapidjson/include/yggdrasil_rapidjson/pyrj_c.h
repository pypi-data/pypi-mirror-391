#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES // required for M_PI in units
#endif

#ifdef __cplusplus
#include <cmath> // required before Python to allow use of hypot w/ MSVC
#else
#include <math.h>
#endif // __cplusplus

#ifdef __cplusplus /* If this is a C++ compiler, use C linkage */
extern "C" {
#endif

#ifdef YGGDRASIL_DISABLE_PYTHON_C_API

#ifndef PyObject
#define PyObject void*
#endif
#ifndef npy_intp
#define npy_intp int
#endif

#else // YGGDRASIL_DISABLE_PYTHON_C_API

#ifdef YGGDRASIL_RAPIDJSON_FORCE_IMPORT_ARRAY
#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#else // YGGDRASIL_RAPIDJSON_FORCE_IMPORT_ARRAY
#ifndef NO_IMPORT_ARRAY
#define NO_IMPORT_ARRAY
#endif
#endif // YGGDRASIL_RAPIDJSON_FORCE_IMPORT_ARRAY
#ifndef PY_ARRAY_UNIQUE_SYMBOL
#define PY_ARRAY_UNIQUE_SYMBOL yggdrasil_rapidjson_ARRAY_API
#endif
#ifndef NPY_NO_DEPRECATED_API
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#endif
// Force default visibility for Numpy symbols (changed to hidden in
//   numpy > 2.0.2) so they can be used by executables linking against
//   the shared library.
#ifndef NPY_API_SYMBOL_ATTRIBUTE
#define NPY_API_SYMBOL_ATTRIBUTE 
#endif

#ifndef CHECK_UNICODE_NO_NUMPY
#ifdef YGGDRASIL_RAPIDJSON_DONT_IMPORT_NUMPY
#define CHECK_UNICODE_NO_NUMPY(x) PyUnicode_Check(x)
#else
#define CHECK_UNICODE_NO_NUMPY(x) PyUnicode_Check(x) && !PyArray_CheckScalar(x)
#endif
#endif

#ifdef _DEBUG
#undef _DEBUG
#include <Python.h>
#include "pythoncapi_compat.h"
#include <numpy/arrayobject.h>
#include <numpy/ndarrayobject.h>
#include <numpy/npy_common.h>
#define _DEBUG
#else
#include <Python.h>
#include "pythoncapi_compat.h"
#include <numpy/arrayobject.h>
#include <numpy/ndarrayobject.h>
#include <numpy/npy_common.h>
#endif

#include "npy_2_compat.h"

#ifndef NUMPY_CORE_INCLUDE_NUMPY_NPY_2_COMPAT_EXTRAS_H_
#define NUMPY_CORE_INCLUDE_NUMPY_NPY_2_COMPAT_EXTRAS_H_
  
#if NPY_FEATURE_VERSION >= NPY_2_0_API_VERSION || NPY_ABI_VERSION < 0x02000000
  #define DESCR_SETTER(FIELD, field, type, legacy_only)			\
    static inline int							\
    PyDataType_SET_##FIELD(PyArray_Descr *dtype, type value) {		\
      if (legacy_only && !PyDataType_ISLEGACY(dtype)) {			\
	return -1;							\
      }									\
      ((_PyArray_LegacyDescr *)dtype)->field = value;			\
      return 0;								\
    }
#else  /* compiling for both 1.x and 2.x */
  #define DESCR_SETTER(FIELD, field, type, legacy_only)			\
    static inline int							\
    PyDataType_SET_##FIELD(PyArray_Descr *dtype, type value) {		\
      if (legacy_only && !PyDataType_ISLEGACY(dtype)) {			\
	return -1;							\
      }									\
      if (PyArray_RUNTIME_VERSION >= NPY_2_0_API_VERSION) {		\
	((_PyArray_LegacyDescr *)dtype)->field = value;			\
      }									\
      else {								\
	((PyArray_DescrProto *)dtype)->field = value;			\
      }									\
      return 0;								\
    }
#endif
  
DESCR_SETTER(NAMES, names, PyObject *, 1)
DESCR_SETTER(FIELDS, fields, PyObject *, 1)

#undef DESCR_SETTER

#endif // NUMPY_CORE_INCLUDE_NUMPY_NPY_2_COMPAT_EXTRAS_H_

#endif // YGGDRASIL_DISABLE_PYTHON_C_API

#ifdef __cplusplus /* If this is a C++ compiler, end C linkage */
}
#endif

