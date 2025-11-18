#ifndef YGGDRASIL_RAPIDJSON_VALIST_H_
#define YGGDRASIL_RAPIDJSON_VALIST_H_

#ifndef DISABLE_YGGDRASIL_RAPIDJSON

#include "internal/meta.h"

typedef struct complex_float_pod_t {
  float re;
  float im;
} complex_float_pod_t;
typedef struct complex_double_pod_t {
  double re;
  double im;
} complex_double_pod_t;
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
typedef struct complex_long_double {
  long double re;
  long double im;
} complex_long_double_pod_t;
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE

YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

#include <cstdarg>

#define YGGDRASIL_RAPIDJSON_BEGIN_VAR_ARGS(out, last_arg, nargs, realloc)	\
  VarArgList out(nargs, realloc);				\
  va_start(out.va, last_arg)

#define YGGDRASIL_RAPIDJSON_END_VAR_ARGS(out)

enum VarArgsFlag {
  kSetVarArgsFlag   = 0x0008,
  kGetVarArgsFlag   = 0x0010,
  kSkipVarArgsFlag  = 0x0020,
  kCountVarArgsFlag = 0x0040
};

//! Contains variable argument list in either C pointer list or explicit
//! pointer list from fortran.
class VarArgList {
public:
  VarArgList(size_t nargs0=0, bool allow_realloc0=false,
	     bool for_c0=false) :
    va(), nargs_(nargs0), nargs(NULL),
    ptrs(NULL), iptr(0), for_fortran(false), for_c(for_c0),
    allow_realloc(allow_realloc0), is_empty(false) {
    nargs = &nargs_;
  }
  VarArgList(size_t* nargs0, bool allow_realloc0=false,
	     bool for_c0=false) :
    va(), nargs_(0), nargs(nargs0),
    ptrs(NULL), iptr(0), for_fortran(false), for_c(for_c0),
    allow_realloc(allow_realloc0), is_empty(false) {}
  VarArgList(const size_t nptrs, void** ptrs0,
	     bool allow_realloc0=false, bool for_fortran0=false) :
    va(), nargs_(nptrs), nargs(NULL),
    ptrs(ptrs0), iptr(0), for_fortran(for_fortran0), for_c(false),
    allow_realloc(allow_realloc0), is_empty(false) {
    nargs = &nargs_;
    if (for_fortran)
      for_c = true;
  }
  VarArgList(VarArgList& other) :
    va(), nargs_(other.get_nargs()), nargs(),
    ptrs(other.ptrs), iptr(other.iptr), for_fortran(other.for_fortran),
    for_c(other.for_c), allow_realloc(other.allow_realloc),
    is_empty(other.is_empty) {
    nargs = &nargs_;
    if (!ptrs)
      va_copy(va, other.va);
  }
  ~VarArgList() {
    if (!is_empty)
      end();
  }
private:
  //! Copy constructor is not permitted.
#ifndef _MSC_VER
  VarArgList(const VarArgList& rhs) = delete;
#endif // _MSC_VER
  VarArgList& operator=(const VarArgList& rhs) = delete;
public:
  std::va_list va;  //!< Traditional variable argument list.
  size_t nargs_; //!< Storage for number of remaining arguments if not provided as a pointer.
  size_t *nargs; //!< The number of remaining arguments.
  void **ptrs; //!< Variable arguments stored as pointers.
  int iptr; //!< The index of the current variable argument pointer.
  int for_fortran; //!< Flag that is 1 if this structure will be accessed by fortran.
  int for_c; //!< Flag that is 1 if the structure will be accessed by c.
  bool allow_realloc; //!< If true, variables can be reallocated during assignment.
  bool is_empty; //!< Set to true for empty list used for count.

  //! Finalize the variable argument list.
  bool end() {
    if (!ptrs)
      va_end(va);
    return (get_nargs() == 0);
  }

  std::va_list* get_va() {
    return &va;
  }

  //! @brief Set the argument count to 0.
  void clear() {
    if (nargs)
      nargs[0] = 0;
    nargs_ = 0;
  }

  //! @brief Get the number of arguments.
  //! @returns Number of arguments.
  size_t get_nargs() const {
    if (nargs)
      return nargs[0];
    return nargs_;
  }

  //! @brief Set the number of arguments.
  //! @param[in] new_nargs New number of arguments.
  void set_nargs(const size_t new_nargs) {
    if (nargs)
      nargs[0] = new_nargs;
    else
      nargs_ = new_nargs;
  }

  //! @brief Increment the number of arguments.
  void inc_nargs() {
    if (nargs)
      nargs[0]++;
    else
      nargs_++;
  }

  /*! @brief Method for skipping a number of bytes in the argument list.
    @param[in] nbytes Number of bytes that should be skipped.
    @returns true if successful, false otherwise.
  */
  bool skip_nbytes(const size_t nbytes) {
    if (!nargs)
      return false;
    YGGDRASIL_RAPIDJSON_ASSERT(nargs && nargs[0] > 0);
    if (!nargs || nargs[0] == 0) {
      // ygglog_error("skip_nbytes: No more arguments");
      return false;
    }
    if (ptrs) {
      iptr++;
    } else {
      if (nbytes == sizeof(void*)) {
	va_arg(va, void*);
      } else if (nbytes == sizeof(size_t)) {
	va_arg(va, size_t);
      } else if (nbytes == sizeof(char*)) {
	va_arg(va, char*);
      } else {
	// printf("WARNING: Cannot get argument of size %ld.\n", nbytes);
	va_arg(va, void*);
	// va_arg(va, char[nbytes]);
      }
    }
    if (nargs[0] > 0)
      nargs[0]--;
    return true;
  }

  /*! 
    @brief Get a pointer from the variable argument list and advance the
      position.
    @param[in] allow_null If 0, an error will be raised if the selected
      pointer is null, otherwise the null pointer will be returned.
    @returns Popped pointer.
  */
  void* pop_ptr(int allow_null = 0) {
    void *out = NULL;
    YGGDRASIL_RAPIDJSON_ASSERT(nargs && nargs[0] > 0 && ptrs != NULL);
    if (!nargs || nargs[0] == 0) {
      // ygglog_throw_error("pop_ptr_cpp: No more arguments");
      return NULL;
    }
    if (ptrs == NULL) {
      // ygglog_throw_error("pop_ptr_cpp: Variable argument list is not stored in pointers.");
      return NULL;
    }
    out = ptrs[iptr];
    iptr++;
    if (nargs[0] > 0)
      nargs[0]--;
    YGGDRASIL_RAPIDJSON_ASSERT((out != NULL) || (allow_null != 0));
    if ((out == NULL) && (allow_null == 0)) {
      std::cerr << "pop_ptr_cpp: Argument " << iptr - 1 << " is NULL" << std::endl;
      // ygglog_throw_error("pop_ptr_cpp: Argument %d is NULL.", iptr - 1);
    }
    return out;
  }
  
  /*!
    @brief C++ wrapper to get a pointer to a pointer from the variable
      argument list and advance the position.
    @param[in] allow_null If 0, an error will be raised if the
      selected pointer is null, otherwise the null pointer will be
      returned.
    @returns Popped pointer.
  */
  void** pop_ptr_ref(int allow_null = 0) {
    void **out = NULL;
    YGGDRASIL_RAPIDJSON_ASSERT(nargs && nargs[0] > 0 && ptrs != NULL);
    if (!nargs || nargs[0] == 0) {
      // ygglog_throw_error("pop_ptr_ref_cpp: No more arguments");
      return NULL;
    }
    if (ptrs == NULL) {
      // ygglog_throw_error("pop_ptr_ref_cpp: Variable argument list is not stored in pointers.");
      return NULL;
    }
    out = ptrs + iptr;
    iptr++;
    if (nargs[0] > 0)
      nargs[0]--;
    YGGDRASIL_RAPIDJSON_ASSERT(((out != NULL) && (*out != NULL)) || (allow_null != 0));
    if ((out == NULL) || ((*out == NULL) && (allow_null == 0))) {
      std::cerr << "pop_ptr_ref_cpp: Argument is NULL." << std::endl;
      // ygglog_throw_error("pop_ptr_ref_cpp: Argument is NULL.");
    }
    return out;
  }

  /*! 
    @brief Pop a value from the variables argument list.
    @tparam T Type of value to pop.
    @param[out] dst Variable to assign the popped value to.
    @param[in] allow_null If 0, an error will be raised if the popped value's
      pointer is null. Otherwise the null pointer will be returned.
    @returns true if successful, false otherwise.
  */
  template<typename T>
  bool pop(T*& dst, int allow_null = 0) {
    if (!nargs || nargs[0] == 0) {
      // ygglog_throw_error("pop: No more arguments");
      return false;
    }
    if (ptrs) {
      dst = ((T*)pop_ptr(allow_null));
    } else {
      dst = va_arg(va, T*);
      if (nargs[0] > 0)
	nargs[0]--;
    }
    return true;
  }
  template<typename T>
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<internal::IsPointer<T>,
			      internal::OrExpr<internal::IsSame<std::complex<float>, T>,
			      internal::OrExpr<internal::IsSame<std::complex<double>, T>,
			      internal::OrExpr<internal::IsSame<std::complex<long double>, T>,
			      internal::OrExpr<internal::IsSame<bool, T>,
			      internal::OrExpr<internal::IsSame<char, T>,
			      internal::OrExpr<internal::IsSame<int8_t, T>,
			      internal::OrExpr<internal::IsSame<int16_t, T>,
			      internal::OrExpr<internal::IsSame<uint8_t, T>,
			      internal::OrExpr<internal::IsSame<uint16_t, T>,
			      internal::IsSame<float, T> > > > > > > > > > >), (bool))
#else // YGGDRASIL_LONG_DOUBLE_AVAILABLE
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<internal::IsPointer<T>,
			      internal::OrExpr<internal::IsSame<std::complex<float>, T>,
			      internal::OrExpr<internal::IsSame<std::complex<double>, T>,
			      internal::OrExpr<internal::IsSame<bool, T>,
			      internal::OrExpr<internal::IsSame<char, T>,
			      internal::OrExpr<internal::IsSame<int8_t, T>,
			      internal::OrExpr<internal::IsSame<int16_t, T>,
			      internal::OrExpr<internal::IsSame<uint8_t, T>,
			      internal::OrExpr<internal::IsSame<uint16_t, T>,
			      internal::IsSame<float, T> > > > > > > > > >), (bool))
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE
  pop(T& dst, int allow_null = 0) {
    if (!nargs || nargs[0] == 0) {
      // ygglog_throw_error("pop: No more arguments");
      return false;
    }
    if (ptrs) {
      dst = ((T*)pop_ptr(allow_null))[0];
    } else {
      dst = va_arg(va, T);
      if (nargs[0] > 0)
	nargs[0]--;
    }
    return true;
  }
#define POP_SPECIAL_(type, type_cast)					\
  template<typename T>							\
  bool pop(T& dst, int allow_null=false,    				\
	   YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<type, T>))) {		\
    if (!nargs || nargs[0] == 0) {					\
      return false;							\
    }									\
    if (ptrs) {								\
      dst = ((type*)pop_ptr(allow_null))[0];				\
    } else {								\
      type_cast tmp;							\
      if (!pop(tmp, allow_null))					\
	return false;							\
      dst = (type)tmp;							\
    }									\
    return true;							\
  }
#define POP_COMPLEX_(type, type_cast)					\
  template<typename T>							\
  bool pop(T& dst, int allow_null=false,				\
	   YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<std::complex<type>, T>))) { \
    if (!nargs || nargs[0] == 0) {					\
      return false;							\
    }									\
    if (ptrs) {								\
      dst = ((std::complex<type>*)pop_ptr(allow_null))[0];		\
    } else {								\
      complex_ ## type_cast ## _pod_t tmp;				\
      if (!pop(tmp, allow_null))					\
	return false;							\
      dst = std::complex<type>(tmp.re, tmp.im);				\
    }									\
    return true;							\
  }
  POP_SPECIAL_(bool, int)
  POP_SPECIAL_(char, int)
  POP_SPECIAL_(int8_t, int)
  POP_SPECIAL_(int16_t, int)
  POP_SPECIAL_(uint8_t, int)
  POP_SPECIAL_(uint16_t, int)
  POP_SPECIAL_(float, double)
  POP_COMPLEX_(float, float)
  POP_COMPLEX_(double, double)
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
  POP_COMPLEX_(long double, long_double)
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE
  
#undef POP_SPECIAL_

  /*! 
    @brief Skip a value from the variables argument list.
    @tparam T Type of value to skip.
    @param[in] pointers If True, a pointer value will be skipped.
    @returns true if successful, false otherwise.
  */
  template<typename T>
  bool skip(bool pointers=false) {
    if (pointers) {
      T* tmp = NULL;
      T** tmp_ref = NULL;
      return pop_mem(tmp, tmp_ref);
    } else {
      T tmp;
      return pop(tmp);
    }
  }

  /*!
    @brief Skip arguments based on the provided schema.
    @tparam ValueType Schema type.
    @param[in] schema Schema containing type information for variables
      to skip.
    @param[in] set If true, arguments will be skipped under the assumption
      that they are variables that would have been set if they were not
      skipped.
    @returns true if successful, false otherwise.
   */
  template<typename ValueType>
  bool skip(ValueType& schema, bool set);

  /*! 
    @brief Get a value from the variables argument list without removing
      any values.
    @tparam T Type of value to get.
    @param[out] dst Variable to assign the value to.
    @param[in] allow_null If 0, an error will be raised if the value's
      pointer is null. Otherwise the null pointer will be returned.
    @returns true if successful, false otherwise.
  */
  template<typename T>
  bool get(T& dst, int allow_null = 0) {
    VarArgList ap_copy(*this);
    return ap_copy.pop(dst, allow_null);
  }

  /*!
    @brief Assign to memory for a pointer retrieved from a variable
      argument list via pop_mem or get_mem without adding a terminating
      character, even if the type is a string.
    @tparam T Type of value to assign.
    @param[in,out] dst Pointer to memory that should be assigned.
    @param[in,out] dst_ref Pointer to dst that can be updated if dst is 
      reallocated.
    @param[in,out] dst_len Current number of elements allocated for in
      dst. This will be updated to the new number of elements in dst
      after assigment.
    @param[in] src Value(s) to assign to dst.
    @param[in] src_len Number of values in src.
    @return true if successful, false otherwise.
  */
  template<typename T>
  bool set_mem(T*& dst, T**& dst_ref, size_t& dst_len,
	       const T* src, const size_t src_len) const {
    if (src_len > dst_len || dst == NULL) {
      if (!allow_realloc) {
	// ygglog_throw_error("set_mem: Buffer is not large enough (dst_len = %zu, src_len = %zu)", dst_len, src_len);
	return false;
      }
      // if (!for_fortran)
      dst = (T*)realloc(dst, src_len * sizeof(T));
      dst_ref[0] = dst;
    }
    memcpy(dst, src, src_len * sizeof(T));
    dst_len = src_len;
    return true;
  }
  
  /*!
    @brief Assign to memory for a pointer retrieved from a variable
      argument list via pop_mem or get_mem and add a null terminating
      character at the end.
    @tparam T Type of value to assign.
    @param[in,out] dst Pointer to memory that should be assigned.
    @param[in,out] dst_ref Pointer to dst that can be updated if dst is 
      reallocated.
    @param[in,out] dst_len Current number of elements allocated for in
      dst. This will be updated to the new number of elements in dst
      after assigment.
    @param[in] src Value(s) to assign to dst.
    @param[in] src_len Number of values in src.
    @return true if successful, false otherwise.
  */
  bool set_mem_term(char*& dst, char**& dst_ref, size_t& dst_len,
		    const char* src, const size_t src_len) const {
    size_t src_len_alloc = src_len;
    if (!for_fortran)
      src_len_alloc++;
    if (src_len_alloc > dst_len || dst == NULL) {
      if (!allow_realloc) {
	// ygglog_throw_error("set_mem_term: Buffer is not large enough (dst_len = %zu, src_len = %zu)", dst_len, src_len);
	return false;
      }
      dst = (char*)realloc(dst, src_len_alloc * sizeof(char));
      dst_ref[0] = dst;
    }
    memcpy(dst, src, src_len * sizeof(char));
    if (!for_fortran) {
      dst[src_len * sizeof(char)] = '\0';
    }
    dst_len = src_len;
    return true;
  }
  
  /*!
    @brief Assign to memory for a pointer retrieved from a variable
      argument list via pop_mem or get_mem that contains an array of
      strings.
    @tparam T Type of value to assign.
    @param[in,out] dst Pointer to memory that should be assigned.
    @param[in,out] dst_ref Pointer to dst that can be updated if dst is 
      reallocated.
    @param[in,out] dst_len Current number of elements allocated for in
      dst. This will be updated to the new number of elements in dst
      after assigment.
    @param[in,out] dst_prec Current size of each string element in the
      array. This will be updated to the new size of each element after
      assignment.
    @param[in] src Value(s) to assign to dst.
    @param[in] src_len Number of values in src.
    @param[in] src_prec Size of each string element.
    @return true if successful, false otherwise.
  */
  bool set_mem_strided(char*& dst, char**& dst_ref,
		       size_t& dst_len, size_t& dst_prec,
		       const char* src, const size_t src_len,
		       const size_t src_prec) const {
    if (src_len > dst_len || src_prec > dst_prec || dst == NULL) {
      if (!allow_realloc) {
	// ygglog_throw_error("set_mem_strided: Buffer is not large enough (dst_nbytes = %zu, src_nbytes = %zu)", dst_nbytes, src_nbytes);
	return false;
      }
      dst = (char*)realloc(dst, src_len * src_prec * sizeof(char));
      dst_ref[0] = dst;
      dst_prec = src_prec;
    }
    dst_len = src_len;
    for (size_t i = 0; i < src_len; i++) {
      memcpy(dst + (i * dst_prec), src + (i * src_prec), src_prec);
      for (size_t j = src_prec; j < dst_prec; j++)
	dst[(i * dst_prec) + j] = '\0';
    }
    return true;
  }
  
  /*! 
    @brief Pop a pointer from the variables argument list.
    @tparam T Type of pointer to pop.
    @param[out] dst Variable that will be assigned the pointer to the
      underlying value.
    @param[out] dst_ref Variable that will be assigned the pointer to the
      address of the underlying value (the pointer to dst) so that the
      pointer may be updated if dst is reallocated.
    @param[in] disable_realloc If true, the memory will be popped without
      assuming it is the address of a pointer for reallocation.
    @returns true if successful, false otherwise.
  */
  template<typename T>
  bool pop_mem(T*& dst, T**& dst_ref, bool disable_realloc=false,
	       bool force_realloc=false) {
    if (!nargs || nargs[0] == 0) {
      // ygglog_throw_error("pop_mem: No more arguments");
      return false;
    }
    if ((allow_realloc || force_realloc) && !disable_realloc) {
      if (ptrs) {
	dst_ref = (T**)pop_ptr_ref(1);
      } else {
	dst_ref = va_arg(va, T**);
	if (nargs[0] > 0)
	  nargs[0]--;
      }
      if (dst_ref == NULL) {
	// ygglog_throw_error("pop_mem: NULL reference returned.");
	return false;
      }
      dst = dst_ref[0];
    } else {
      if (ptrs) {
	dst = (T*)pop_ptr();
      } else {
	dst = va_arg(va, T*);
	if (nargs[0] > 0)
	  nargs[0]--;
      }
      dst_ref = &dst;
      // TODO: Is this always true?
      if (dst == NULL)
	return false;
    }
    return true;
  }

  /*! 
    @brief Get a pointer from the variables argument list without
      removing any values.
    @tparam T Type of pointer to get.
    @param[out] dst Variable that will be assigned the pointer to the
      underlying value.
    @param[out] dst_ref Variable that will be assigned the pointer to the
      address of the underlying value (the pointer to dst) so that the
      pointer may be updated if dst is reallocated.
    @returns true if successful, false otherwise.
  */
  template<typename T>
  bool get_mem(T*& dst, T**& dst_ref) {
    VarArgList ap_copy(*this);
    return ap_copy.pop_mem(dst, dst_ref);
  }

  /*!
    @brief Assign to the next variable in a variable argument list.
    @tparam T Type of value to assign.
    @param[in] src Value to assign to the next variable in ap.
    @param[in] swap If true, src will be updated to the initial value
      contained by the argument.
    @returns true if successful, false otherwise.
  */
  template<typename T>
  bool set(T& src, bool swap=false) {
    T** p = NULL;
    T* arg = NULL;
    if (!nargs || nargs[0] == 0) {
      // ygglog_throw_error("set: No more arguments");
      return false;
    }
    if (!pop_mem(arg, p, swap))
      return false;
    if (allow_realloc && !swap) {
      // if (!allow_realloc)
      // 	return false;
      if (for_fortran) {
	arg = *p;
      } else {
	if (arg == NULL)
	  arg = (T*)malloc(sizeof(T));
	else
	  arg = (T*)realloc(*p, sizeof(T));
      }
      p[0] = arg;
    } else if (arg == NULL) {
      return false;
    }
    if (!arg)
      return false;
    if (swap) {
      T orig = arg[0];
      orig = arg[0];
      arg[0] = src;
      src = orig;
    } else {
      arg[0] = src;
    }
    return true;
  }

  /*
#define SET_SPECIAL_(type, type_cast)		\
  template<>					\
  bool set(type& src, bool swap) {		\
    if (!nargs || nargs[0] == 0) {		\
      return false;				\
    }						\
    type_cast tmp = (type_cast)src;		\
    if (!set(tmp, swap))			\
      return false;				\
    if (swap)					\
      src = (type)tmp;				\
    return true;				\
  }

#undef SET_SPECIAL_
  */

  template<typename T>
  bool apply(T* val, const uint16_t flag) {
    if (flag & kCountVarArgsFlag) {
      inc_nargs();
      return true;
    } else if (flag & kSetVarArgsFlag) {
      if (flag & kSkipVarArgsFlag)
	return skip<T*>(true);
      return set(*val);
    } else if (flag & kGetVarArgsFlag) {
      if (flag & kSkipVarArgsFlag)
	return skip<T>(false);
      return pop(*val);
    }
    return false;
  }

  template<typename T>
  bool apply_ptr(T** val, const uint16_t flag) {
    if (for_fortran && flag == kGetVarArgsFlag) {
      T** val_ref = NULL;
      bool out = pop(val_ref);
      if (out) {
        if (!val_ref)
          return false;
        val[0] = val_ref[0];
      }
      return out;
    }
    return apply(val, flag);
  }

  template<typename T>
  bool apply_mem(T*& dst, T**& dst_ref, const uint16_t flag) {
    if (flag & kCountVarArgsFlag) {
      inc_nargs();
      return true;
    } else if (flag & kSetVarArgsFlag) {
      if (flag & kSkipVarArgsFlag)
	return skip<T*>(true);
      return pop_mem(dst, dst_ref);
    } else if (flag & kGetVarArgsFlag) {
      if (flag & kSkipVarArgsFlag)
	return skip<T*>(false);
      return pop(dst);
    }
    return false;
  }

  template<typename T>
  bool apply_c(T*& dst, T**& dst_ref, const uint16_t flag) {
    if (for_fortran && ((flag == kSetVarArgsFlag) ||
			flag == kGetVarArgsFlag)) {
      // Fortran always passes pointer to pointer
      bool out = pop(dst_ref);
      if (out) {
	if (!dst_ref)
	  return false;
	dst = dst_ref[0];
      }
      return out;
    } else if (for_c && flag == kSetVarArgsFlag) {
      // C always passes pointer to pointer when setting
      return pop_mem(dst, dst_ref, false, true);
    }
    return apply_mem(dst, dst_ref, flag);
  }

  template<typename T>
  bool apply_swap(T* val, const uint16_t flag) {
    if (flag != kSetVarArgsFlag)
      return apply(val, flag);
    return set(*val, true);
  }
  
};

template<typename ValueType>
size_t is_document_format_array(ValueType& d,
				bool get_nelements = false) {
				
  if (!(d.IsArray() && d.Size() > 0))
    return 0;
  size_t nelements = 0;
  size_t i = 0;
  for (typename ValueType::ConstValueIterator it = d.Begin();
       it != d.End(); it++, i++) {
    if (!it->IsNDArray())
      return 0;
    size_t it_nelements = (size_t)(it->GetNElements());
    if (i == 0) {
      nelements = it_nelements;
    } else if (nelements != it_nelements) {
      return 0;
    }
  }
  if (get_nelements)
    return nelements;
  return 1;
}

template<typename ValueType>
size_t is_schema_format_array(ValueType& d,
			      bool get_nelements = false) {
  if (!(d.IsObject() && d.HasMember("type")))
    return 0;
  if (d["type"] != ValueType::GetArrayString())
    return 0;
  if (!d.HasMember("items"))
    return 0;
  if (!d["items"].IsArray())
    return 0;
  if (d["items"].Size() == 0)
    return 0;
  size_t nelements = 0;
  size_t i = 0;
  for (typename ValueType::ConstValueIterator it = d["items"].Begin();
       it != d["items"].End(); it++, i++) {
    if (!(it->HasMember("type") && (*it)["type"].IsString() &&
	  ((*it)["type"] == ValueType::GetNDArrayString() ||
	   (*it)["type"] == ValueType::Get1DArrayString()))) {
      return 0;
    }
    size_t it_nelements = 0;
    if (it->HasMember("length") && (*it)["length"].IsInt())
      it_nelements = (size_t)((*it)["length"].GetInt());
    else if (it->HasMember("shape") && (*it)["shape"].IsArray()) {
      it_nelements = 1;
      for (typename ValueType::ConstValueIterator sit = (*it)["shape"].Begin();
	   sit != (*it)["shape"].End(); sit++) {
	it_nelements *= (size_t)(sit->GetInt());
      }
    }
    if (i == 0) {
      nelements = it_nelements;
    } else if (nelements != it_nelements) {
      return 0;
    }
  }
  if (get_nelements)
    return nelements;
  return 1;
}

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // DISABLE_YGGDRASIL_RAPIDJSON
  
#endif // YGGDRASIL_RAPIDJSON_VALIST_H_
