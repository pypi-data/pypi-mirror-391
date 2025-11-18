#ifndef YGGDRASIL_RAPIDJSON_PRECISION_H_
#define YGGDRASIL_RAPIDJSON_PRECISION_H_

/*! \file precision.h */

#include "internal/meta.h"
#include "yggdrasil_rapidjson.h"
#include <iostream>
#include <cfloat>
#include <typeinfo>

// 8 bit
#ifndef INT8_MAX
#define INT8_MAX 127
#endif // INT8_MAX
#ifndef INT8_MIN
#define INT8_MIN (-128)
#endif // INT8_MIN
#ifndef UINT8_MAX
#define UINT8_MAX 255U
#endif // UINT8_MAX
// 16 bit
#ifndef INT16_MAX
#define INT16_MAX 32767
#endif // INT16_MAX
#ifndef INT16_MIN
#define INT16_MIN (-32768)
#endif // INT16_MIN
#ifndef UINT16_MAX
#define UINT16_MAX 65535U
#endif // UINT16_MAX
// 32 bit
#ifndef INT32_MAX
#define INT32_MAX 2147483647
#endif // INT32_MAX
#ifndef INT32_MIN
#define INT32_MIN (-2147483647 - 1)
#endif // INT32_MIN
#ifndef UINT32_MAX
#define UINT32_MAX 4294967295U
#endif // UINT32_MAX
// 64 bit
#ifndef INT64_MAX
#define INT64_MAX 9223372036854775807LL
#endif // INT64_MAX
#ifndef INT64_MIN
#define INT64_MIN (-9223372036854775807LL - 1)
#endif // INT64_MIN
#ifndef UINT64_MAX
#define UINT64_MAX 18446744073709551615ULL
#endif // UINT64_MAX


YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

#ifndef DISABLE_YGGDRASIL_RAPIDJSON

#define YGGDRASIL_IS_CASTABLE(T1, T2)					\
  internal::OrExpr<							\
    internal::AndExpr<YGGDRASIL_IS_INT_TYPE(T1),			\
		      YGGDRASIL_IS_INT_TYPE(T2)>,			\
    internal::OrExpr<							\
    internal::AndExpr<YGGDRASIL_IS_INT_TYPE(T1),			\
		      YGGDRASIL_IS_FLOAT_TYPE(T2)>,			\
    internal::OrExpr<							\
    internal::AndExpr<YGGDRASIL_IS_UINT_TYPE(T1),			\
		      YGGDRASIL_IS_UINT_TYPE(T2)>,			\
    internal::OrExpr<							\
    internal::AndExpr<YGGDRASIL_IS_UINT_TYPE(T1),			\
		      YGGDRASIL_IS_INT_TYPE(T2)>,			\
    internal::OrExpr<							\
    internal::AndExpr<YGGDRASIL_IS_UINT_TYPE(T1),			\
		      YGGDRASIL_IS_FLOAT_TYPE(T2)>,			\
    internal::OrExpr<							\
    internal::AndExpr<YGGDRASIL_IS_FLOAT_TYPE(T1),			\
		      YGGDRASIL_IS_FLOAT_TYPE(T2)>,			\
    internal::AndExpr<YGGDRASIL_IS_COMPLEX_TYPE(T1), \
		      YGGDRASIL_IS_COMPLEX_TYPE(T2)> > > > > > >
#define CASE_SUBTYPE_PRECISION(T, function, param, args)		\
  case sizeof(T): { return function<T, UNPACK_MACRO(param)> args; }
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
#define CASE_FLOAT_SUBTYPE(precision, function, param, args, error)	\
  case kYggFloatSubType: {						\
    switch (precision) {						\
    CASE_SUBTYPE_PRECISION(float16_t, function, param, args)		\
    CASE_SUBTYPE_PRECISION(float, function, param, args)	       	\
    CASE_SUBTYPE_PRECISION(double, function, param, args)	       	\
    CASE_SUBTYPE_PRECISION((long double), function, param, args)	\
    default: { error; }							\
    }									\
    break;								\
  }
#define CASE_COMPLEX_SUBTYPE(precision, function, param, args, error)	\
  case kYggComplexSubType: {						\
    switch (precision) {						\
    CASE_SUBTYPE_PRECISION(std::complex<float>, function, param, args)  \
    CASE_SUBTYPE_PRECISION(std::complex<double>, function, param, args) \
    CASE_SUBTYPE_PRECISION(std::complex<long double>, function, param, args) \
    default: { error; }							\
    }									\
    break;								\
  }
#else // YGGDRASIL_LONG_DOUBLE_AVAILABLE
#define CASE_FLOAT_SUBTYPE(precision, function, param, args, error)	\
  case kYggFloatSubType: {						\
    switch (precision) {						\
    CASE_SUBTYPE_PRECISION(float16_t, function, param, args)		\
    CASE_SUBTYPE_PRECISION(float, function, param, args)       	        \
    CASE_SUBTYPE_PRECISION(double, function, param, args)	        \
    default: { error; }							\
    }									\
    break;								\
  }
#define CASE_COMPLEX_SUBTYPE(precision, function, param, args, error)	\
  case kYggComplexSubType: {						\
    switch (precision) {						\
    CASE_SUBTYPE_PRECISION(std::complex<float>, function, param, args)  \
    CASE_SUBTYPE_PRECISION(std::complex<double>, function, param, args) \
    default: { error; }							\
    }									\
    break;								\
  }
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE

#define SWITCH_SUBTYPE(subtype, precision, function, param, args, error)	\
  switch (subtype) {							\
  case kYggIntSubType: {						\
    switch (precision) {						\
    CASE_SUBTYPE_PRECISION(int8_t, function, param, args)       	\
    CASE_SUBTYPE_PRECISION(int16_t, function, param, args)      	\
    CASE_SUBTYPE_PRECISION(int32_t, function, param, args)      	\
    CASE_SUBTYPE_PRECISION(int64_t, function, param, args)      	\
    default: { error; }							\
    }									\
    break;								\
  }									\
  case kYggUintSubType: {						\
    switch (precision) {						\
    CASE_SUBTYPE_PRECISION(uint8_t, function, param, args)      	\
    CASE_SUBTYPE_PRECISION(uint16_t, function, param, args)     	\
    CASE_SUBTYPE_PRECISION(uint32_t, function, param, args)     	\
    CASE_SUBTYPE_PRECISION(uint64_t, function, param, args)    	        \
    default: { error; }							\
    }									\
    break;								\
  }									\
  CASE_FLOAT_SUBTYPE(precision, function, param, args, error);	        \
  CASE_COMPLEX_SUBTYPE(precision, function, param, args, error) 	\
  default: { error; }							\
  }


template <typename T1, typename T2>
bool canCast(bool allowDecreasedPrecision=true,
	     YGGDRASIL_RAPIDJSON_ENABLEIF((YGGDRASIL_IS_CASTABLE(T1, T2)))) {
  if (!allowDecreasedPrecision && (sizeof(T2) < sizeof(T1)))
    return false;
  return true;
}
template <typename T1, typename T2>
bool canCast(bool=true,
	     YGGDRASIL_RAPIDJSON_DISABLEIF((YGGDRASIL_IS_CASTABLE(T1, T2)))) {
  return false;
}
template <typename T2, size_t>
bool canCast(YggSubType S1, SizeType P1, bool allowDecreasedPrecision=true) {
  SWITCH_SUBTYPE(S1, P1, canCast, PACK_MACRO(T2), (allowDecreasedPrecision),
		 return false);
}
static inline
bool canCast(YggSubType S1, SizeType P1,
	     YggSubType S2, SizeType P2,
	     bool allowDecreasedPrecision=true) {
  SWITCH_SUBTYPE(S2, P2, canCast, PACK_MACRO(1), (S1, P1, allowDecreasedPrecision),
		 return false);
}

template <typename T1, typename T2>
T2 castPrecision(const T1& v1,
		 YGGDRASIL_RAPIDJSON_DISABLEIF((internal::OrExpr<YGGDRASIL_IS_COMPLEX_TYPE(T1),
				      YGGDRASIL_IS_COMPLEX_TYPE(T2)>)))
{ return static_cast<const T2>(v1); }
template <typename T1, typename T2>
T2 castPrecision(const T1& v1,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<YGGDRASIL_IS_COMPLEX_TYPE(T1),
				     YGGDRASIL_IS_COMPLEX_TYPE(T2)>)))
{ return T2(static_cast<typename T2::value_type>(v1.real()),
	    static_cast<typename T2::value_type>(v1.imag())); }
template <typename T1, typename T2>
T2 castPrecision(const T1& v1,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<YGGDRASIL_IS_COMPLEX_TYPE(T1),
				     internal::NotExpr<YGGDRASIL_IS_COMPLEX_TYPE(T2)> >)))
{ return static_cast<const T2>(v1.real()); }
template <typename T1, typename T2>
T2 castPrecision(const T1& v1,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<internal::NotExpr<
				     internal::OrExpr<internal::IsSame<long, T1>,
				     internal::OrExpr<internal::IsSame<unsigned long, T1>,
				     internal::OrExpr<internal::IsSame<long long, T1>,
				     internal::OrExpr<internal::IsSame<unsigned long long, T1>,
				     YGGDRASIL_IS_COMPLEX_TYPE(T1)> > > > >,
				     YGGDRASIL_IS_COMPLEX_TYPE(T2)>)))
{ return T2(v1); }
template <typename T1, typename T2>
const T2 castPrecision(const T1& v1,
		       YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
					   internal::OrExpr<internal::IsSame<long, T1>,
					   internal::OrExpr<internal::IsSame<unsigned long, T1>,
					   internal::OrExpr<internal::IsSame<long long, T1>,
					   internal::IsSame<unsigned long long, T1> > > >,
					   YGGDRASIL_IS_COMPLEX_TYPE(T2)>)))
{ return T2(static_cast<const int>(v1)); }

#define CAST_SOURCE					\
  const T1* src = reinterpret_cast<const T1*>(bytes);
#define SAME_PRECISION							\
  if ((GetYggSubType<T1>() == GetYggSubType<T2>()) && (sizeof(T2) == sizeof(T1))) { \
    memcpy((void*)dst, (void*)src, nelements * sizeof(T2));		\
    return;								\
  }
#define DIFF_PRECISION				\
  for (SizeType i = 0; i < nelements; i++)	\
    dst[i] = castPrecision<T1, T2>(src[i]);

/*
  if (sizeof(T2) < sizeof(T1))			\
    printf("WARNING: Loosing precision.");	\
*/

template <typename T1, typename T2>
void changePrecision(const unsigned char* bytes, T2* dst, SizeType nelements,
		     YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<T1, T2>))) {
  CAST_SOURCE;
  memcpy((void*)dst, (void*)src, nelements * sizeof(T2));
}

template <typename T1, typename T2>
void changePrecision(const unsigned char* bytes, T2* dst, SizeType nelements,
		     YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
					 internal::NotExpr<
					 internal::IsSame<T1, T2> >,
					 YGGDRASIL_IS_CASTABLE(T1,T2)>))) {
  CAST_SOURCE;
  SAME_PRECISION;
  DIFF_PRECISION;
}

template <typename T1, typename T2>
void changePrecision(const unsigned char*, T2*, SizeType,
		     YGGDRASIL_RAPIDJSON_DISABLEIF((YGGDRASIL_IS_CASTABLE(T1,T2)))) {
  std::cerr << typeid(T1).name() << " cannot be cast to " << typeid(T2).name() << std::endl;
  YGGDRASIL_RAPIDJSON_ASSERT(!sizeof("Cannot change from T1 to T2"));
}

#undef SAME_PRECISION
#undef DIFF_PRECISION

template <typename T1, typename T2, typename Allocator>
T2* changePrecision(const unsigned char* bytes, SizeType nelements,
		    Allocator& allocator) {
  T2* v2 = (T2*)allocator.Malloc(nelements * sizeof(T2));
  YGGDRASIL_RAPIDJSON_ASSERT(v2);
  changePrecision<T1,T2>(bytes, v2, nelements);
  // YGGDRASIL_RAPIDJSON_ASSERT(GetYggSubType<T1>() == GetYggSubType<T2>());
  // if (sizeof(T2) == sizeof(T1))
  //   return (T2*)bytes;
  // else if (sizeof(T2) < sizeof(T1))
  //   printf("WARNING: Loosing precision.");
  // T1* v1 = reinterpret_cast<T1*>(bytes);
  // T2* v2 = static_cast<T2*>(malloc(nelements * sizeof(T2)));
  // for (SizeType i = 0; i < nelements; i++)
  //   v2[i] = castPrecision<T1, T2>(v1[i]);
  return v2;
}

template <typename T>
void changePrecision(YggSubType subtype, SizeType precision,
		     const unsigned char* bytes, T* dst,
		     SizeType nelements) {
  SWITCH_SUBTYPE(subtype, precision, changePrecision,
		 PACK_MACRO(T), (bytes, dst, nelements),
		 YGGDRASIL_RAPIDJSON_ASSERT(false));
}

template <typename T, size_t>
SizeType _sizeOf() { return sizeof(T); }

static inline
SizeType sizeOfSubtype(const YggSubType subtype, const SizeType precision) {
  SWITCH_SUBTYPE(subtype, precision, _sizeOf, PACK_MACRO(1), (), return 0);
}

template <typename T, size_t>
void changePrecision(YggSubType subtype, SizeType precision,
		     const unsigned char* src_bytes,
		     unsigned char* dst_bytes, SizeType& dst_nbytes,
		     SizeType nelements) {
  YGGDRASIL_RAPIDJSON_ASSERT((nelements * sizeof(T)) <= dst_nbytes);
  SWITCH_SUBTYPE(subtype, precision, changePrecision,
		 PACK_MACRO(T), (src_bytes, (T*)dst_bytes, nelements),
		 YGGDRASIL_RAPIDJSON_ASSERT(false));
  dst_nbytes = nelements * (SizeType)sizeof(T);
}

static inline
void changePrecision(const YggSubType src_subtype, const SizeType src_precision,
		     const unsigned char* src_bytes, const SizeType src_nbytes,
		     YggSubType dst_subtype, SizeType dst_precision,
		     unsigned char* dst_bytes, SizeType& dst_nbytes,
		     const SizeType nelements) {
  (void)src_nbytes;
  // SizeType src_size = sizeOfSubtype(src_subtype, src_precision);
  // SizeType dst_size = sizeOfSubtype(dst_subtype, dst_precision);
  // YGGDRASIL_RAPIDJSON_ASSERT((nelements * src_size) == src_nbytes);
  // YGGDRASIL_RAPIDJSON_ASSERT((nelements * dst_size) <= dst_nbytes);
  // YGGDRASIL_RAPIDJSON_ASSERT(dst_size <= src_size);
  SWITCH_SUBTYPE(dst_subtype, dst_precision, changePrecision,
		 PACK_MACRO(1), (src_subtype, src_precision, src_bytes,
				 dst_bytes, dst_nbytes, nelements),
		 YGGDRASIL_RAPIDJSON_ASSERT(false));
}

#define MIN_MAX_(TT, min, max)			\
  template<typename T>				\
  T get_max_(const T, YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<T, TT>))) {	\
    return max;					\
  }						\
  template<typename T>				\
  T get_min_(const T, YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<T, TT>))) {	\
    return min;					\
  }
#define MIN_MAX_S_(T, base)			\
  MIN_MAX_(T, base ## _MIN, base ## _MAX)
#define MIN_MAX_U_(T, base)			\
  MIN_MAX_(T, 0, base ## _MAX)
#define MIN_MAX_F_(T, base)			\
  MIN_MAX_(T, -base ## _MAX, base ## _MAX)

MIN_MAX_S_(int8_t, INT8)
MIN_MAX_S_(int16_t, INT16)
MIN_MAX_S_(int32_t, INT32)
MIN_MAX_S_(int64_t, INT64)
MIN_MAX_U_(uint8_t, UINT8)
MIN_MAX_U_(uint16_t, UINT16)
MIN_MAX_U_(uint32_t, UINT32)
MIN_MAX_U_(uint64_t, UINT64)
MIN_MAX_(float16_t, -65504, 65504)
MIN_MAX_F_(float, FLT)
MIN_MAX_F_(double, DBL)
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
MIN_MAX_F_(long double, LDBL)
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE

#undef MIN_MAX_S_
#undef MIN_MAX_U_
#undef MIN_MAX_F_
#undef MIN_MAX_

#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
#define DISPLAY_LIMITS_(x)						\
  std::cerr << "limits: " << static_cast<long double>(x) << ", min = " << static_cast<long double>(get_min_((T2)0)) << ", max = " << static_cast<long double>(get_max_((T2)0)) << std::endl
#define COMPARE_LIMITS_(x)						\
  (static_cast<long double>(x) >= static_cast<long double>(get_min_((T2)0)) && \
   static_cast<long double>(x) <= static_cast<long double>(get_max_((T2)0)))
#else
#define DISPLAY_LIMITS_(x)						\
  std::cerr << "limits: " << static_cast<double>(x) << ", min = " << static_cast<double>(get_min_((T2)0)) << ", max = " << static_cast<double>(get_max_((T2)0)) << std::endl
#define COMPARE_LIMITS_(x)						\
  (static_cast<double>(x) >= static_cast<double>(get_min_((T2)0)) && \
   static_cast<double>(x) <= static_cast<double>(get_max_((T2)0)))
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE

template <typename T1, typename T2>
bool canTruncate(const T1& x,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				     YGGDRASIL_IS_FLOAT_TYPE(T1),
				     internal::OrExpr<
				     YGGDRASIL_IS_INT_TYPE(T2),
				     YGGDRASIL_IS_UINT_TYPE(T2)> >))) {
  T1 x_int = internal::value_floor(x); // std::floor(x);
  if (!internal::values_eq(x_int, x))
    return false;
  return COMPARE_LIMITS_(x_int);
}
template <typename T1, typename T2>
bool canTruncate(const T1& x,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::OrExpr<
				     internal::AndExpr<
				     internal::OrExpr<
				     YGGDRASIL_IS_INT_TYPE(T1),
				     YGGDRASIL_IS_UINT_TYPE(T1)>,
				     internal::NotExpr<
				     YGGDRASIL_IS_COMPLEX_TYPE(T2)> >,
				     internal::AndExpr<
				     YGGDRASIL_IS_FLOAT_TYPE(T1),
				     YGGDRASIL_IS_FLOAT_TYPE(T2)> >))) {
  return COMPARE_LIMITS_(x);
}
template <typename T1, typename T2>
bool canTruncate(const T1& x,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				     YGGDRASIL_IS_COMPLEX_TYPE(T1),
				     YGGDRASIL_IS_COMPLEX_TYPE(T2)>))) {
  return (canTruncate<typename T1::value_type, typename T2::value_type>(x.real()) &&
	  canTruncate<typename T1::value_type, typename T2::value_type>(x.imag()));
}
template <typename T1, typename T2>
bool canTruncate(const T1& x,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				     internal::NotExpr<
				     YGGDRASIL_IS_COMPLEX_TYPE(T1)>,
				     YGGDRASIL_IS_COMPLEX_TYPE(T2)>))) {
  return canTruncate<T1, typename T2::value_type>(x);
}
template <typename T1, typename T2>
bool canTruncate(const T1& x,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				     YGGDRASIL_IS_COMPLEX_TYPE(T1),
				     internal::NotExpr<
				     YGGDRASIL_IS_COMPLEX_TYPE(T2)> >))) {
  if (!internal::values_eq(x.imag(), 0))
    return false;
  return canTruncate<typename T1::value_type, T2>(x.imag());
}
#undef COMPARE_LIMITS_
#undef DISPLAY_LIMITS_
  
template <typename T1, typename T2>
bool canTruncate(const unsigned char* bytes, SizeType nelements) {
  CAST_SOURCE;
  for (SizeType i = 0; i < nelements; i++)
    if (!canTruncate<T1, T2>(src[i]))
      return false;
  return true;
}

template <typename T, size_t>
bool canTruncate(YggSubType subtype, SizeType precision,
		 const unsigned char* src_bytes,
		 SizeType nelements) {
  SWITCH_SUBTYPE(subtype, precision, canTruncate,
		 PACK_MACRO(T), (src_bytes, nelements),
		 YGGDRASIL_RAPIDJSON_ASSERT(false));
  return false;
}

static inline
bool canTruncate(const YggSubType src_subtype, const SizeType src_precision,
		  const unsigned char* src_bytes,
		  YggSubType dst_subtype, SizeType dst_precision,
		  const SizeType nelements) {
  SWITCH_SUBTYPE(dst_subtype, dst_precision, canTruncate,
		 PACK_MACRO(1), (src_subtype, src_precision, src_bytes,
				 nelements),
		 YGGDRASIL_RAPIDJSON_ASSERT(false));
  return false;
}

template <typename T1, typename T2>
T2 truncateCast(const T1& x,
		YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				    internal::NotExpr<
				    YGGDRASIL_IS_COMPLEX_TYPE(T1)>,
				    internal::NotExpr<
				    YGGDRASIL_IS_COMPLEX_TYPE(T2)> >)))
{ return static_cast<const T2>(x); }
template <typename T1, typename T2>
T2 truncateCast(const T1& x,
		YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				    internal::NotExpr<
				    YGGDRASIL_IS_COMPLEX_TYPE(T1)>,
				    YGGDRASIL_IS_COMPLEX_TYPE(T2)>)))
{ return T2(truncateCast<T1, typename T2::value_type>(x)); }
template <typename T1, typename T2>
T2 truncateCast(const T1& x,
		YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				    YGGDRASIL_IS_COMPLEX_TYPE(T1),
				    internal::NotExpr<
				    YGGDRASIL_IS_COMPLEX_TYPE(T2)> >)))
{ return truncateCast<typename T1::value_type, T2>(x.real()); }
template <typename T1, typename T2>
T2 truncateCast(const T1& x,
		YGGDRASIL_RAPIDJSON_ENABLEIF((internal::AndExpr<
				    YGGDRASIL_IS_COMPLEX_TYPE(T1),
				    YGGDRASIL_IS_COMPLEX_TYPE(T2)>))) {
  return T2(truncateCast<typename T1::value_type, typename T2::value_type>(x.real()),
	    truncateCast<typename T1::value_type, typename T2::value_type>(x.imag()));
}

template <typename T1, typename T2>
void truncateCast(const unsigned char* bytes, T2* dst, SizeType nelements) {
  CAST_SOURCE;
  for (SizeType i = 0; i < nelements; i++)
    dst[i] = truncateCast<T1, T2>(src[i]);
}

// template <typename T>
// void truncateCast(YggSubType subtype, SizeType precision,
// 		  const unsigned char* bytes, T* dst,
// 		  SizeType nelements) {
//   SWITCH_SUBTYPE(subtype, precision, truncateCast,
// 		 PACK_MACRO(T), (bytes, dst, nelements),
// 		 YGGDRASIL_RAPIDJSON_ASSERT(false));
// }

template <typename T, size_t>
void truncateCast(YggSubType subtype, SizeType precision,
		  const unsigned char* src_bytes,
		  unsigned char* dst_bytes, SizeType nelements) {
  SWITCH_SUBTYPE(subtype, precision, truncateCast,
		 PACK_MACRO(T), (src_bytes, (T*)dst_bytes, nelements),
		 YGGDRASIL_RAPIDJSON_ASSERT(false));
}

static inline
void truncateCast(const YggSubType src_subtype, const SizeType src_precision,
		  const unsigned char* src_bytes,
		  YggSubType dst_subtype, SizeType dst_precision,
		  unsigned char* dst_bytes,
		  const SizeType nelements) {
  SWITCH_SUBTYPE(dst_subtype, dst_precision, truncateCast,
		 PACK_MACRO(1), (src_subtype, src_precision, src_bytes,
				 dst_bytes, nelements),
		 YGGDRASIL_RAPIDJSON_ASSERT(false));
}
#undef CAST_SOURCE

#endif // DISABLE_YGGDRASIL_RAPIDJSON

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // YGGDRASIL_RAPIDJSON_PRECISION_H_
