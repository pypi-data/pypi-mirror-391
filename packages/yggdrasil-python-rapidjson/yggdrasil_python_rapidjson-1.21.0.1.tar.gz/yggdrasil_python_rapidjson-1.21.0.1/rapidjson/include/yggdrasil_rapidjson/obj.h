#ifndef YGGDRASIL_RAPIDJSON_OBJ_H_
#define YGGDRASIL_RAPIDJSON_OBJ_H_

#include "internal/meta.h"
#include <iostream>
#include <set>
#include <iterator>
#include <vector>
#include <map>
#include <algorithm>
#include <cstdlib>
#include <typeinfo>

YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

#if YGGDRASIL_RAPIDJSON_HAS_CXX11
#define OVERRIDE_CXX11 override
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
#define OVERRIDE_CXX11
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
#define SINGLE_ARG(...) (__VA_ARGS__)

//! \brief Convert from an alias for a geometry element to the base.
//! \param alias Name to check.
//! \return Base name associated with the provided alias.
static inline
std::string obj_alias2base(const std::string& alias) {
  if      (alias == "vertices") return std::string("v");
  else if (alias == "vertexes") return std::string("v");
  else if (alias == "vertex"  ) return std::string("v");
  else if (alias == "faces"   ) return std::string("f");
  else if (alias == "face"    ) return std::string("f");
  else if (alias == "edges"   ) return std::string("l");
  else if (alias == "edge"    ) return std::string("l");
  else if (alias == "comment" ) return std::string("#");
  else if (alias == "comments") return std::string("#");
  return std::string(alias);
}

//! \brief Convert from a code string to the long element name.
//! \param code Name to check.
//! \return Long name associated with the provided element.
static inline
std::string obj_code2long(const std::string& code) {
  if      (code == "v" ) return std::string("vertex");
  else if (code == "f" ) return std::string("face");
  else if (code == "l" ) return std::string("edge");
  else if (code == "#" ) return std::string("comment");
  return std::string(code);
}

class ObjRefVertex;
class ObjRefCurve;
class ObjRefSurface;

#define COMPATIBLE_WITH_INT(T)				       \
  internal::OrExpr<internal::IsSame<T,int>,	               \
    internal::OrExpr<internal::IsSame<T,int8_t>,               \
      internal::OrExpr<internal::IsSame<T,uint8_t>,	       \
	internal::OrExpr<internal::IsSame<T,int16_t>,	       \
	  internal::OrExpr<internal::IsSame<T,uint16_t>,       \
	    internal::OrExpr<internal::IsSame<T,int32_t>,      \
	      internal::OrExpr<internal::IsSame<T,uint32_t>,   \
		internal::OrExpr<internal::IsSame<T,int64_t>,  \
		  internal::OrExpr<internal::IsSame<T,ObjRef>, \
		    internal::IsSame<T,uint64_t> > > > > > > > > >
#define COMPATIBLE_WITH_UINT(T)				       \
      internal::OrExpr<internal::IsSame<T,uint8_t>,	       \
	  internal::OrExpr<internal::IsSame<T,uint16_t>,       \
	      internal::OrExpr<internal::IsSame<T,uint32_t>,   \
		  internal::OrExpr<internal::IsSame<T,ObjRef>, \
		      internal::IsSame<T,uint64_t> > > > >
#define COMPATIBLE_WITH_FLOAT(T)			       \
  internal::OrExpr<internal::IsSame<T,int>,	               \
    internal::OrExpr<internal::IsSame<T,int8_t>,               \
      internal::OrExpr<internal::IsSame<T,uint8_t>,	       \
	internal::OrExpr<internal::IsSame<T,int16_t>,	       \
	  internal::OrExpr<internal::IsSame<T,uint16_t>,       \
	    internal::OrExpr<internal::IsSame<T,int32_t>,      \
	      internal::OrExpr<internal::IsSame<T,uint32_t>,   \
		internal::OrExpr<internal::IsSame<T,int64_t>,  \
		  internal::OrExpr<internal::IsSame<T,float>, \
  		    internal::OrExpr<internal::IsSame<T,double>, \
		      internal::IsSame<T,uint64_t> > > > > > > > > > >
#define COMPATIBLE_WITH_STRING(T)					\
  internal::IsSame<T,std::string>
#define COMPATIBLE_WITH_VERT(T)						\
  internal::OrExpr<internal::IsSame<T,ObjRefVertex>, COMPATIBLE_WITH_INT(T)>
#define COMPATIBLE_WITH_CURV(T)					\
  internal::IsSame<T,ObjRefCurve>
#define COMPATIBLE_WITH_SURF(T)					\
  internal::IsSame<T,ObjRefSurface>
#define COMPATIBLE_WITH_TYPE(T1, T2)		 \
  internal::IsSame<T1,T2>
#define COMPATIBLE_WITH_ANY(T)						\
  internal::OrExpr<COMPATIBLE_WITH_INT(T),				\
    internal::OrExpr<COMPATIBLE_WITH_FLOAT(T),				\
      internal::OrExpr<COMPATIBLE_WITH_VERT(T),				\
       	internal::OrExpr<COMPATIBLE_WITH_CURV(T),	                \
       	  internal::OrExpr<COMPATIBLE_WITH_SURF(T),	                \
			   COMPATIBLE_WITH_TYPE(T, std::string)> > > > >
#define ASSERT_COMPATIBLE(T1, T2)					\
  std::cerr << typeid(T1).name() << " and " << typeid(T2).name() << " types are not compatible." << std::endl; \
  YGGDRASIL_RAPIDJSON_ASSERT(!sizeof("T1 and T2 types are not compatible."))

//! Object reference index.
typedef int64_t ObjRef;

enum ObjTypeFlag {
  ObjTypeNull     = 0x0000,
  ObjTypeInt      = 0x0001,
  ObjTypeUint8    = 0x0002,
  ObjTypeUint16   = 0x0004,
  ObjTypeString   = 0x0008,
  ObjTypeFloat    = 0x0010,
  ObjTypeRef      = 0x0020,
  ObjTypeVertex   = 0x0040,
  ObjTypeCurve    = 0x0080,
  ObjTypeSurface  = 0x0100,
  ObjTypeList     = 0x0200,
  ObjTypeIdx      = 0x0400,
  ObjTypeOpt      = 0x0800,
  ObjTypeOff      = 0x1000
};

static inline
bool _types_compatible(const uint16_t a, const uint16_t b) {
  if (a & b) return true;
  uint16_t is_int = (ObjTypeInt | ObjTypeUint8 | ObjTypeUint16 | ObjTypeRef |
		     ObjTypeVertex | ObjTypeCurve | ObjTypeSurface);
  if (((a & is_int) && (b & is_int)) ||
      ((a & ObjTypeFloat) && (b & ObjTypeFloat)) ||
      ((a & ObjTypeString) && (b & ObjTypeString)))
    return true;
  return false;
}
static inline
bool _type_compatible_int(const uint16_t x, bool=false) {
  return _types_compatible(x, ObjTypeInt);
}
static inline
bool _type_compatible_double(const uint16_t x, bool allow_int=false) {
  if (allow_int && _types_compatible(x, ObjTypeInt))
    return true;
  return _types_compatible(x, ObjTypeFloat);
}
static inline
bool _type_compatible_string(const uint16_t x, bool=false) {
  return _types_compatible(x, ObjTypeString);
}
static inline
void _type_inc(std::string&) {}
static inline
void _type_dec(std::string&) {}
template <typename T>
inline void _type_inc(T& x, YGGDRASIL_RAPIDJSON_DISABLEIF((COMPATIBLE_WITH_TYPE(T, std::string)))) {
  x++;
}
template <typename T>
inline void _type_dec(T& x, YGGDRASIL_RAPIDJSON_DISABLEIF((COMPATIBLE_WITH_TYPE(T, std::string)))) {
  x--;
}

//! Test if two vectors are equal element-by-element using is_equal
template <typename T>
inline bool is_equal_vectors(const std::vector<T>& a, const std::vector<T>& b) {
  
  if (a.size() != b.size()) return false;
  for (typename std::vector<T>::const_iterator ait = a.begin(), bit = b.begin(); ait != a.end(); ait++, bit++)
    if (!internal::values_eq(*ait, *bit)) return false;
  return true;
}


#define YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(method)	\
  if (second & ObjTypeVertex) {				\
    method(T, ObjRefVertex);				\
  } else if (second & ObjTypeRef) {			\
    method(T, ObjRef);					\
  } else if (second & ObjTypeUint8) {			\
    method(T, uint8_t);					\
  } else if (second & ObjTypeUint16) {			\
    method(T, uint16_t);				\
  } else if (second & ObjTypeInt) {			\
    method(T, int);					\
  } else if (second & ObjTypeFloat) {			\
    method(T, double);					\
  }
#define YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_(method)	\
  if (second & ObjTypeCurve) {					\
    method(T, ObjRefCurve);					\
  } else if (second & ObjTypeSurface) {				\
    method(T, ObjRefSurface);					\
  } else if (second & ObjTypeString) {				\
    method(T, std::string);					\
  }
#define YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_ALL_(sMethod, vMethod)	\
  if (second & ObjTypeList) {					\
    YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_(vMethod)		\
    else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(vMethod)		\
  }								\
  else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_(sMethod)	\
  else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(sMethod)

struct ObjPropertyType {
public:
  ObjPropertyType(void* mem0, std::string name0, uint16_t flag0, size_t idx0=0) :
    mem(mem0), first(name0), second(flag0), idx(idx0), missing(false), is_index(false), is_color(false) {
    is_index = (first.size() > 6 && (first.substr(first.size() - 6) == "_index"));
    is_color = (first == "red" ||
		first == "green" ||
		first == "blue");
  }
  ObjPropertyType(const ObjPropertyType& other) :
    mem(other.mem), first(other.first), second(other.second), idx(other.idx),
    missing(other.missing), is_index(other.is_index), is_color(other.is_color) {}
  //! \brief Copy assignment.
  ObjPropertyType& operator=(const ObjPropertyType& other) {
    mem = other.mem;
    first = other.first;
    second = other.second;
    idx = other.idx;
    missing = other.missing;
    is_index = other.is_index;
    is_color = other.is_color;
    return *this;
  }
  void* mem;
  std::string first;
  uint16_t second;
  size_t idx;
  bool missing;
  bool is_index;
  bool is_color;

  //! \brief Determine if the property contains a vector of values.
  //! \return true if it contains a vector, false otherwise.
  bool is_vector() const { return (second & ObjTypeList); }

  template<typename T>
  bool _get_scalar_mem(T*& val, bool resize=false) const {
    return const_cast<ObjPropertyType&>(*this)._get_scalar_mem(val, resize);
  }
  template<typename T>
  bool _get_scalar_mem(T*& val, bool resize=false) {
    if (!mem) return false;
    val = NULL;
    if (second & ObjTypeIdx) {
      std::vector<T>* mem_vect = (std::vector<T>*)mem;
      if (idx >= mem_vect->size()) {
	if (resize)
	  mem_vect->resize(idx + 1);
	else
	  return false;
      }
      val = &(mem_vect->begin()[0]) + idx;
    } else {
      val = (T*)mem;
    }
    return true;
  }
  //! \brief Increment the property if an index.
  //! \return true if successful, false otherwise.
  bool inc();

#define PROPERTY_TYPE_(T, flag)						\
  /*! \brief Set the property values by copying from a vector. */	\
  /*! \param val Vector of values to copy from. */			\
  /*! \param inc If true and the property is an index, it will be incremented. */ \
  /*! \return true if successful, false otherwise. */			\
  bool set(const std::vector<T>& val, bool inc=false);			\
  /*! \brief Set the property value. */					\
  /*! \param val Value to copy. */					\
  /*! \param inc If true and the property is an index, it will be incremented. */ \
  /*! \return true if successful, false otherwise. */			\
  bool set(const T& val, bool inc=false);				\
  /*! \brief Copy values into a vector. */				\
  /*! \param[out] out Vector to copy values to. */			\
  /*! \param dec If true and the property is an index, it will be decremented. */ \
  /*! \return true if successful, false otherwise. */			\
  bool get(std::vector<T>& out, bool dec=false) const;			\
  /*! \brief Copy value into a scalar. */				\
  /*! \param[out] out Scalar to copy value to. */			\
  /*! \param dec If true and the property is an index, it will be decremented. */ \
  /*! \return true if successful, false otherwise. */			\
  bool get(T& out, bool dec=false) const;				\
  /*! \brief Append a value to a vector property. */			\
  /*! \param val Value to append. */					\
  /*! \param index Index to append at. Ignored if <0. */		\
  /*! \param inc If true and the property is an index, it will be incremented. */ \
  /*! \return true if successful, false otherwise. */			\
  bool append(const T& val, int index = -1, bool inc=false);		\
  /*! \brief Index into a vector property. */				\
  /*! \param index Index. */						\
  /*! \param[out] out Scalar to copy value into. */			\
  /*! \param dec If true and the property is an index, it will be decremented. */ \
  /*! \return true if successful, false otherwise. */			\
  bool index(const size_t index, T& out, bool dec=false) const
  //! \brief Set a non-integer color
  //! \tparam T Type of source value.
  //! \param val Value to copy.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((COMPATIBLE_WITH_INT(T)), (bool))
    setColor(const T& val, bool inc);
  //! \brief Set an integer color
  //! \tparam T Type of source value.
  //! \param val Value to copy.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_ENABLEIF_RETURN((COMPATIBLE_WITH_INT(T)), (bool))
    setColor(const T& val, bool inc);
  //! \brief Set the property values by copying from a vector.
  //! \tparam T Type in source vector.
  //! \param val Vector of values to copy from.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			      internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			      COMPATIBLE_WITH_SURF(T)> >), (bool))
    set(const std::vector<T>& val, bool inc=false);
  //! \brief Set the property value.
  //! \tparam T Type of source value.
  //! \param val Value to copy.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			      internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			      COMPATIBLE_WITH_SURF(T)> >), (bool))
    set(const T& val, bool inc=false);
  //! \brief Copy values into a vector of a desired type if possible.
  //! \tparam T Desired type.
  //! \param[out] out Vector to copy values to.
  //! \param dec If true and the property is an index, it will be decremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			      internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			      COMPATIBLE_WITH_SURF(T)> >), (bool))
    get(std::vector<T>& out, bool dec=false) const;
  //! \brief Copy value into a scalar of a desired type.
  //! \tparam T Desired type.
  //! \param[out] out Scalar to copy value to.
  //! \param dec If true and the property is an index, it will be decremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			      internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			      COMPATIBLE_WITH_SURF(T)> >), (bool))
    get(T& out, bool dec=false) const;
  //! \brief Append a value to a vector property.
  //! \param val Value to append.
  //! \param index Index to append at. Ignored if <0.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			      internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			      COMPATIBLE_WITH_SURF(T)> >), (bool))
    append(const T& val, int index, bool inc=false);
  //! \brief Index into a vector property.
  //! \param index Index
  //! \param[out] out Scalar to copy value into.
  //! \param dec If true and the property is an index, it will be decremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			      internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			      COMPATIBLE_WITH_SURF(T)> >), (bool))
    index(const size_t index, T& out, bool dec=false) const;
  PROPERTY_TYPE_(std::string, ObjTypeString);
  PROPERTY_TYPE_(ObjRefCurve, ObjTypeCurve);
  PROPERTY_TYPE_(ObjRefSurface, ObjTypeSurface);
#undef PROPERTY_TYPE_
  //! \brief Copy a property from another.
  bool copy(const ObjPropertyType& rhs);
  //! \brief Read a property into memory from a stream.
  //! \param in Input stream.
  //! \return true if successful, false otherwise.
  bool read(std::istream& in);
  //! \brief Count the number of decimal places in a double.
  //! \param x Value to count decimals in.
  //! \return Number of decimal places in x.
  static int count_decimals(double x) {
    int count = 0;
    while (!internal::values_eq((int)x, x)) {
      x *= 10;
      count++;
    }
    return count;
  }
  //! \brief Write the property to an output stream.
  //! \param out Output stream.
  //! \param pad If true, the value will be proceeded by a space.
  //! \return true if successful, false otherwise.
  bool write(std::ostream& out, bool pad) const;
  //! \brief Check for equality with another property. Values in memory
  //!   will be checked, not the pointer addresses.
  //! \param rhs Property to compare against.
  //! \return true if equal, false otherwise.
  bool is_equal(const ObjPropertyType& rhs) const;
  //! \brief Equality operator.
  friend bool operator == (const ObjPropertyType& lhs, const ObjPropertyType& rhs);
  //! \brief Inequality operator.
  friend bool operator != (const ObjPropertyType& lhs, const ObjPropertyType& rhs);
};

inline
bool operator == (const ObjPropertyType& lhs, const ObjPropertyType& rhs)
{ return lhs.is_equal(rhs); }
inline
bool operator != (const ObjPropertyType& lhs, const ObjPropertyType& rhs)
{ return (!lhs.is_equal(rhs)); }

typedef std::vector<ObjPropertyType> ObjPropertiesMap;

class ObjBase {
public:
  ObjBase() : properties() {}
  //! \brief Destructor.
  virtual ~ObjBase() {}
  //! \brief Initialize properties for the class.
  virtual void _init_properties() {}
  //! Properties contained by the element.
  ObjPropertiesMap properties;
  //! \brief Determine if a structure is valid and contains the correct
  //!   properties.
  //! \return true if the structure is valid, false otherwise.
  virtual bool is_valid() const
  { return true; }
  //! \brief Determine if a property refers to an index.
  //! \param name Property name.
  //! \return true if index, false otherwise.
  virtual bool is_index(const std::string name) const
  { return (name.size() > 6 && (name.substr(name.size() - 6) == "_index")); }
  //! \brief Determine if a property refers to an index.
  //! \param i Index of the property to check.
  //! \return true if index, false otherwise.
  virtual bool is_index(size_t i) const {
    if (i >= properties.size()) return false;
    ObjPropertiesMap::const_iterator it = properties.begin() + (int)i;
    return is_index(it->first);
  }
  //! \brief Determine if a property is set.
  //! \param name Property name.
  //! \param dontCheckOrder If true, it is assumed that the property is in
  //!    the list of possible properties for this element.
  //! \param skipColors If true, color data will not be included.
  //! \param[out] idx Pointer to memory that should be set to the property
  //!   index.
  //! \return true if property set, false otherwise.
  virtual bool has_property(const std::string name,
			    bool dontCheckOrder=false,
			    bool skipColors=false,
			    size_t* idx = NULL) const {
    if (dontCheckOrder)
      return true;
    if (skipColors && (name == "red" ||
		       name == "green" ||
		       name == "blue"))
      return false;
    ObjPropertiesMap::const_iterator it = properties.begin();
    size_t i = 0;
    for (; it != properties.end(); it++, i++) {
      if (it->first == name) break;
    }
    if (idx && it != properties.end())
      idx[0] = i;
    return (it != properties.end());
  }
  //! \brief Get the properties associated with this element.
  //! \param skipColors If true, color data will not be included.
  //! \return Property names.
  std::vector<std::string> property_order(bool skipColors=false) const {
    std::vector<std::string> out;
    for (ObjPropertiesMap::const_iterator it = properties.begin();
	 it != properties.end(); it++) {
      if (this->has_property(it->first, true, skipColors, NULL))
	out.push_back(it->first);
    }
    return out;
  }
  //! \brief Get the number of properties in the element.
  //! \param skipColors If true, the size will not include colors.
  //! \return Number of properties in the element.
  virtual size_t size(bool skipColors=false) const
  { return property_order(skipColors).size(); }
  //! \brief Get the minimum number of values allowed for this element to be valid.
  //! \param valuesOnly If true, the minimum for the values vector is returned.
  virtual int min_values(bool valuesOnly=false) const {
    (void)valuesOnly;
    int out = 0;
    for (ObjPropertiesMap::const_iterator it = properties.begin();
	 it != properties.end(); it++) {
      if (it->second & ObjTypeList) return 1;
      if (!(it->second & ObjTypeOpt)) out++;
    }
    return out;
  }
  //! \brief Get the maximum number of values allowed for this element to be valid.
  //! \param valuesOnly If true, the maximum for the values vector is returned.
  virtual int max_values(bool valuesOnly=false) const {
    (void)valuesOnly;
    int out = 0;
    for (ObjPropertiesMap::const_iterator it = properties.begin();
	 it != properties.end(); it++) {
      if (it->second & ObjTypeList) return -1;
      out++;
    }
    return out;
  }
  //! \brief Set an element property.
  //! \tparam T Type of new value.
  //! \tparam i Index of the property to set.
  //! \param new_value Value to assign to the property.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool set_property(size_t i, const T new_value, bool inc=false) {
    if (i >= properties.size()) {
      if (properties.size() > 0) {
	ObjPropertiesMap::iterator last = properties.end() - 1;
	if (last->second & ObjTypeList) {
	  return last->append(new_value, static_cast<int>(i - properties.size() + 1), inc);
	}
      }
      return false;
    }
    ObjPropertiesMap::iterator it = properties.begin() + (int)i;
    if (((i + 1) == properties.size()) && (it->second & ObjTypeList)) {
      return it->append(new_value, 0, inc);
    }
    return it->set(new_value, inc);
  }
  //! \brief Set an element property.
  //! \tparam T Type of new value.
  //! \tparam i Index of the property to set.
  //! \param new_value Values to assign to the property.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool set_property(size_t i, const std::vector<T> new_value, bool inc=false) {
    if (i >= properties.size()) return false;
    ObjPropertiesMap::iterator it = properties.begin() + (int)i;
    return it->set(new_value, inc);
  }
  //! \brief Set an element property.
  //! \tparam T Type of new value.
  //! \param name Name of the property to set.
  //! \param new_value Value to assign to the property.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool set_property(const std::string name, const T new_value, bool inc=false) {
    size_t i = 0;
    if (!this->has_property(name, false, false, &i)) return false;
    return this->set_property(i, new_value, inc);
  }
  //! \brief Get an element property.
  //! \tparam Type of output.
  //! \param i index of the property to get.
  //! \param out Existing memory to copy property to.
  //! \param dec If true and the property is an index, it will be decremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool get_property(size_t i, T& out, bool dec=false) const {
    if (i >= properties.size()) {
      if (properties.size() > 0) {
	ObjPropertiesMap::const_iterator last = properties.end() - 1;
	if (last->second & ObjTypeList)
	  return last->index(i, out, dec);
      }
      return false;
    }
    ObjPropertiesMap::const_iterator it = properties.begin() + (int)i;
    return it->get(out, dec);
  }
  //! \brief Get an element property.
  //! \tparam Type of output.
  //! \param i index of the property to get.
  //! \param out Existing vector to add property values to.
  //! \param dec If true and the property is an index, it will be decremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool get_property(size_t i, std::vector<T>& out, bool dec=false) const {
    if (i >= properties.size()) return false;
    ObjPropertiesMap::const_iterator it = properties.begin() + (int)i;
    return it->get(out, dec);
  }
  //! \brief Get an element property.
  //! \tparam Type of output.
  //! \param name Name of the property to get.
  //! \param out Existing memory to copy property to.
  //! \param dec If true and the property is an index, it will be decremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool get_property(const std::string name, T& out, bool dec=false) const {
    size_t i = 0;
    if (!this->has_property(name, false, false, &i)) return false;
    return this->get_property(i, out, dec);
  }
  bool _inc_properties() {
    for (ObjPropertiesMap::iterator it = properties.begin();
	 it != properties.end(); it++) {
      if (!it->inc()) return false;
    }
    return true;
  }
};

//! Base class for property subelements.
class ObjPropertyElement : public ObjBase {
public:
  ObjPropertyElement() : ObjBase() {}
  template<typename T>
  ObjPropertyElement(T* mem, const std::string name, uint16_t flag) : ObjBase() {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    const ObjPropertiesMap pairs = {
      ObjPropertyType(mem, name, flag)
    };
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    ObjPropertiesMap pairs;
    pairs.push_back(ObjPropertyType(mem, name, flag));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    this->properties = pairs;
  }
};

#define OPERATOR_(type, op, ip, ic)			\
  template <typename T>					\
  friend type operator op(type lhs, const T& rhs) {	\
    lhs ip rhs;						\
    return lhs;						\
  }							\
  type& operator ic() {					\
    (*this) ip 1;					\
    return *this;					\
  }							\
  type operator ic(int) {				\
    type old = *this;					\
    operator ic();					\
    return old;						\
  }
#define ARITHMETIC_OPERATORS_(type)			\
  OPERATOR_(type, +, +=, ++)				\
  OPERATOR_(type, -, -=, --)
  

//! ObjWavefront vertex reference
class ObjRefVertex : public ObjPropertyElement {
public:
  //! \brief Constructor
  //! \param v0 Index of the vertex's coordinates
  //! \param vt0 Index of the vertex's texcoord
  //! \param vn0 Index of the vertex's normal
  //! \param Nparam0 The number of parameters specified by the vertex. If
  //!    not provided, it will be determined by chcking the values of v0, vt0,
  //!    and vn0. (1: (v), 2: (v, vt), 3: (v, vt, vn)).
  ObjRefVertex(ObjRef v0=0, ObjRef vt0=0, ObjRef vn0=0,
	       int8_t Nparam0=-1) :
    ObjPropertyElement(), v(v0), vt(vt0), vn(vn0), Nparam(Nparam0) {
    this->_init_properties();
  }
  //! \brief Constructor
  //! \tparam T Vertex index type
  //! \param v0 Index of the vertex's coordinates
  template <typename T>
  ObjRefVertex(const T& v0,
	       YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_INT(T)))) :
    ObjPropertyElement(), v(v0), vt(0), vn(0), Nparam(1) {
    this->_init_properties();
  }
  //! \brief Constructor
  //! \param v0 Index of the vertex's coordinates
  ObjRefVertex(const double& v0) :
    ObjPropertyElement(), v(static_cast<ObjRef>(v0)), vt(0), vn(0), Nparam(1) {
    this->_init_properties();
  }
  void _init_properties() OVERRIDE_CXX11 {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    this->properties = {
      ObjPropertyType(&v, "vertex_index", ObjTypeRef),
      ObjPropertyType(&vt, "texture_index", (ObjTypeRef | ObjTypeOpt)),
      ObjPropertyType(&vn, "normal_index", (ObjTypeRef | ObjTypeOpt))
    };
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    this->properties.push_back(ObjPropertyType(&v, "vertex_index", ObjTypeRef));
    this->properties.push_back(ObjPropertyType(&vt, "texture_index", (ObjTypeRef | ObjTypeOpt)));
    this->properties.push_back(ObjPropertyType(&vn, "normal_index", (ObjTypeRef | ObjTypeOpt)));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  int8_t get_Nparam() const {
    int8_t Nparam0 = Nparam;
    if (Nparam0 < 0) {
      if (vn != 0)
	Nparam0 = 3;
      else if (vt != 0)
	Nparam0 = 2;
      else
	Nparam0 = 1;
    }
    return Nparam0;
  }
  //! \brief Write the vertex to an output stream.
  //! \param out Output stream.
  //! \return Output stream.
  std::ostream & write(std::ostream &out) const {
    int8_t Nparam0 = get_Nparam();
    out << v;
    if (Nparam0 > 1) {
      out << "/";
      if (vt != 0)
	out << vt;
    }
    if (Nparam0 > 2) {
      out << "/";
      if (vn != 0)
	out << vn;
    }
    return out;
  }
  //! \brief Read the vertex from an input stream.
  //! \param in Input stream.
  //! \return Input stream.
  std::istream & read(std::istream &in) {
    std::string word;
    in >> word;
    std::istringstream ss_word(word);
    std::string token;
    // std::istringstream ss_token;
    v = 0;
    vt = 0;
    vn = 0;
    Nparam = 1;
    for (size_t i = 0; i < word.size(); i++) {
      if (word[i] == '/')
	Nparam++;
    }
    // v
    if (!std::getline(ss_word, token, '/')) {
      Nparam = 0;
      return in;
    }
    {
      std::istringstream ss_token(token);
      ss_token >> v;
    }
    // vt
    if (!std::getline(ss_word, token, '/')) {
      return in;
    }
    {
      std::istringstream ss_token(token);
      ss_token >> vt;
    }
    // vn
    if (!std::getline(ss_word, token, '/')) {
      return in;
    }
    {
      std::istringstream ss_token(token);
      ss_token >> vn;
    }
    return in;
  }
  //! Allow casting to integer.
  operator int() const { return (int)v; }
  //! Index of vertex coordinates.
  ObjRef v;
  //! Index of vertex texcoords.
  ObjRef vt;
  //! Index of vertex normals.
  ObjRef vn;
  //! Number of parameters used in the vertex definition.
  int8_t Nparam;
  //! \brief Check if another vertex is equivalent.
  //! \param rhs Vertex to compare.
  //! \return true if rhs is equivalent.
  bool is_equal(const ObjRefVertex& rhs) const {
    const ObjRefVertex& lhs = *this;
    if (lhs.v != rhs.v) return false;
    if (lhs.vt != rhs.vt) return false;
    if (lhs.vn != rhs.vn) return false;
    return true;
  }
  //! \brief In-place addition.
  //! \param i Integer to increment indexes by.
  template <typename T>
  ObjRefVertex& operator +=(T i) {
    int8_t Nparam0 = get_Nparam();
    v += static_cast<ObjRef>(i);
    if (Nparam0 > 1 && vt != 0)
      vt += static_cast<ObjRef>(i);
    if (Nparam0 > 2 && vn != 0)
      vn += static_cast<ObjRef>(i); 
    return *this;
  }
  //! \brief In-place subtraction.
  //! \param i Integer to decrement indexes by.
  template <typename T>
  ObjRefVertex& operator -=(T i) {
    int8_t Nparam0 = get_Nparam();
    v -= static_cast<ObjRef>(i);
    if (Nparam0 > 1 && vt != 0)
      vt -= static_cast<ObjRef>(i);
    if (Nparam0 > 2 && vn != 0)
      vn -= static_cast<ObjRef>(i); 
    return *this;
  }
  ARITHMETIC_OPERATORS_(ObjRefVertex)
  friend bool operator == (const ObjRefVertex& lhs, const ObjRefVertex& rhs);
  friend std::ostream & operator << (std::ostream &out, const ObjRefVertex &p);
  friend std::istream & operator >> (std::istream &in, ObjRefVertex &p);
};

//! \brief Check if two ObjRefVertex instances are equivalent.
//! \param lhs First instance for comparison.
//! \param rhs Second instance for comparison.
//! \return true if the two instances are equivalent.
inline
bool operator == (const ObjRefVertex& lhs, const ObjRefVertex& rhs)
{ return lhs.is_equal(rhs); }

//! Write an ObjRefVertex element to an output stream.
//! \param out Output stream.
//! \param p Element to write.
//! \return Output stream.
inline
std::ostream & operator << (std::ostream &out, const ObjRefVertex &p)
{ return p.write(out); }

//! Read an ObjRefVertex element from an input stream.
//! \param in Input stream.
//! \param p Element to read into.
//! \return Input stream.
inline
std::istream & operator >> (std::istream &in, ObjRefVertex &p)
{ return p.read(in); }


//! ObjWavefront curve reference.
class ObjRefCurve : public ObjPropertyElement {
public:
  //! \brief Empty constructor.
  ObjRefCurve() :
    ObjPropertyElement(), u0(0.0), u1(0.0), curv2d(-1) {
    this->_init_properties();
  }
  //! \brief Constructor.
  //! \param u00 Curve parameter starting value.
  //! \param u10 Curve parameter ending value.
  //! \param curv2d0 Index of a 2D curve.
  ObjRefCurve(double u00, double u10=0.0, ObjRef curv2d0=-1) :
    ObjPropertyElement(), u0(u00), u1(u10), curv2d(curv2d0) {
    this->_init_properties();
  }
  void _init_properties() OVERRIDE_CXX11 {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    this->properties = {
      ObjPropertyType(&u0, "u0", ObjTypeFloat),
      ObjPropertyType(&u1, "u1", ObjTypeFloat),
      ObjPropertyType(&curv2d, "curve_index", ObjTypeRef)
    };
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    this->properties.push_back(ObjPropertyType(&u0, "u0", ObjTypeFloat));
    this->properties.push_back(ObjPropertyType(&u1, "u1", ObjTypeFloat));
    this->properties.push_back(ObjPropertyType(&curv2d, "curve_index", ObjTypeRef));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  //! \brief Write the curve to an output stream.
  //! \param out Output stream.
  //! \return Output stream.
  std::ostream & write(std::ostream &out) const {
    out << u0 << " " << u1 << " " << curv2d;
    return out;
  }
  //! \brief Read the curve from an input stream.
  //! \param in Input stream.
  //! \return Input stream.
  std::istream & read(std::istream &in) {
    in >> u0;
    in >> u1;
    in >> curv2d;
    return in;
  }
  //! Allow casting to integer.
  operator int() const { return (int)curv2d; }
  //! Curve parameter starting value.
  double u0;
  //! Curve parameter ending value.
  double u1;
  //! Index of a 2D curve definition.
  ObjRef curv2d;
  //! \brief Check if another curve is equivalent.
  //! \param rhs Curve to compare.
  //! \return true if rhs is equivalent.
  bool is_equal(const ObjRefCurve& rhs) const {
    const ObjRefCurve& lhs = *this;
    if (!internal::values_eq(lhs.u0, rhs.u0)) return false;
    if (!internal::values_eq(lhs.u1, rhs.u1)) return false;
    if (lhs.curv2d != rhs.curv2d) return false;
    return true;
  }
  //! \brief In-place addition.
  //! \param i Integer to increment indexes by.
  template <typename T>
  ObjRefCurve& operator +=(T i) {
    curv2d += static_cast<ObjRef>(i);
    return *this;
  }
  //! \brief In-place subtraction.
  //! \param i Integer to decrement indexes by.
  template <typename T>
  ObjRefCurve& operator -=(T i) {
    curv2d -= static_cast<ObjRef>(i);
    return *this;
  }
  ARITHMETIC_OPERATORS_(ObjRefCurve)
  friend bool operator == (const ObjRefCurve& lhs, const ObjRefCurve& rhs);
  friend std::ostream & operator << (std::ostream &out, const ObjRefCurve &p);
  friend std::istream & operator >> (std::istream &in, ObjRefCurve &p);
};

//! Check if two ObjRefCurve instances are equivalent.
//! \param lhs First element for comparison.
//! \param rhs Second element for comparison.
//! \return true if the two elements are equivalent.
inline
bool operator == (const ObjRefCurve& lhs, const ObjRefCurve& rhs)
{ return lhs.is_equal(rhs); }

//! Write an ObjRefCurve element to an output stream.
//! \param out Output stream.
//! \param p Element.
//! \return Output stream.
inline
std::ostream & operator << (std::ostream &out, const ObjRefCurve &p)
{ return p.write(out); }

//! Read an ObjRefCurve element from an input stream.
//! \param in Input stream.
//! \param p Element to read into.
//! \return Input stream.
inline
std::istream & operator >> (std::istream &in, ObjRefCurve &p)
{ return p.read(in); }


//! ObjWavefront surface reference.
class ObjRefSurface : public ObjPropertyElement {
public:
  //! \brief Constructor.
  //! \brief surf0 Index of surface definition.
  //! \brief q00 Starting parameter value.
  //! \brief q10 Ending parameter value.
  //! \brief curv2d0 Index of curve definition.
  ObjRefSurface(ObjRef surf0=-1, double q00=0.0, double q10=0.0, ObjRef curv2d0=-1) :
    ObjPropertyElement(), surf(surf0), q0(q00), q1(q10), curv2d(curv2d0) {
    this->_init_properties();
  }
  //! \brief Constructor.
  //! \tparam T Surface index type.
  //! \brief surf0 Index of surface definition.
  template <typename T>
  ObjRefSurface(const T& surf0,
		YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_INT(T)))) :
    ObjPropertyElement(), surf(surf0), q0(0), q1(0), curv2d(-1) {
    this->_init_properties();
  }
  //! \brief Constructor.
  //! \brief surf0 Index of surface definition.
  ObjRefSurface(const double& surf0) :
    ObjPropertyElement(), surf(static_cast<ObjRef>(surf0)), q0(0), q1(0), curv2d(-1) {
    this->_init_properties();
  }
  void _init_properties() OVERRIDE_CXX11 {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    this->properties = {
      ObjPropertyType(&surf, "surface_index", ObjTypeFloat),
      ObjPropertyType(&q0, "q0", ObjTypeFloat),
      ObjPropertyType(&q1, "q1", ObjTypeFloat),
      ObjPropertyType(&curv2d, "curve_index", ObjTypeRef)
    };
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    this->properties.push_back(ObjPropertyType(&surf, "surface_index", ObjTypeFloat));
    this->properties.push_back(ObjPropertyType(&q0, "q0", ObjTypeFloat));
    this->properties.push_back(ObjPropertyType(&q1, "q1", ObjTypeFloat));
    this->properties.push_back(ObjPropertyType(&curv2d, "curve_index", ObjTypeRef));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  //! \brief Write the surface to an output stream.
  //! \param out Output stream.
  //! \return Output stream.
  std::ostream & write(std::ostream &out) const {
    out << surf << " " << q0 << " " << q1 << " " << curv2d;
    return out;
  }
  //! \brief Read the surface from an input stream.
  //! \param in Input stream.
  //! \return Input stream.
  std::istream & read(std::istream &in) {
    in >> surf;
    in >> q0;
    in >> q1;
    in >> curv2d;
    return in;
  }
  //! Allow casting to integer.
  operator int() const { return (int)surf; }
  //! Index of surface definition.
  ObjRef surf;
  //! Starting parameter value.
  double q0;
  //! Ending parameter value.
  double q1;
  //! Index of surface definition.
  ObjRef curv2d;
  //! \brief Check if another surface is equivalent.
  //! \param rhs Surface to compare.
  //! \return true if rhs is equivalent.
  bool is_equal(const ObjRefSurface& rhs) const {
    const ObjRefSurface& lhs = *this;
    if (lhs.surf != rhs.surf) return false;
    if (!internal::values_eq(lhs.q0, rhs.q0)) return false;
    if (!internal::values_eq(lhs.q1, rhs.q1)) return false;
    if (lhs.curv2d != rhs.curv2d) return false;
    return true;
  }
  //! \brief In-place addition.
  //! \param i Integer to increment indexes by.
  template <typename T>
  ObjRefSurface& operator +=(T i) {
    surf += static_cast<ObjRef>(i);
    curv2d += static_cast<ObjRef>(i);
    return *this;
  }
  //! \brief In-place subtraction.
  //! \param i Integer to decrement indexes by.
  template <typename T>
  ObjRefSurface& operator -=(T i) {
    surf -= static_cast<ObjRef>(i);
    curv2d -= static_cast<ObjRef>(i);
    return *this;
  }
  ARITHMETIC_OPERATORS_(ObjRefSurface)
  friend bool operator == (const ObjRefSurface& lhs, const ObjRefSurface& rhs);
  friend std::ostream & operator << (std::ostream &out, const ObjRefSurface &p);
  friend std::istream & operator >> (std::istream &in, ObjRefSurface &p);
};

#undef ARITHMETIC_OPERATORS_
#undef OPERATOR_

//! Check if two ObjRefSurface instances are equivalent.
//! \param lhs First element for comparison.
//! \param rhs Second element for comparison.
//! \return true if the two elements are equivalent.
inline
bool operator == (const ObjRefSurface& lhs, const ObjRefSurface& rhs)
{ return lhs.is_equal(rhs); }

//! Write an ObjRefSurface element to an output stream.
//! \param out Output stream.
//! \param p Element to write.
//! \return Output stream.
inline
std::ostream & operator << (std::ostream &out, const ObjRefSurface &p)
{ return p.write(out); }

//! Read an ObjRefSurface element from an input stream.
//! \param in Input stream.
//! \param p Element to read into.
//! \return Input stream.
inline
std::istream & operator >> (std::istream &in, ObjRefSurface &p)
{ return p.read(in); }

#define HANDLE_VECTOR_SET_(T, type, TN)					\
    std::vector<type>* mem_cast = (std::vector<type>*)mem;		\
    if (inc && is_index) {						\
      for (TN std::vector<T>::const_iterator v = val.begin();		\
	   v != val.end(); v++) {					\
	type vv = static_cast<type>(*v);				\
	_type_inc(vv);							\
	mem_cast->push_back(vv);					\
      }									\
    } else {								\
      for (TN std::vector<T>::const_iterator v = val.begin();		\
	   v != val.end(); v++) {					\
	mem_cast->push_back(static_cast<type>(*v));			\
      }									\
    }									\
    return true
#define HANDLE_VECTOR_SET_TEMPLATE_(T, type)				\
    HANDLE_VECTOR_SET_(T, type, typename)
#define HANDLE_SCALAR_SET_(T, type)					\
    type* mem_cast = NULL;						\
    if (!_get_scalar_mem(mem_cast, true)) return false;			\
    if (inc && is_index) {						\
      type vv = static_cast<type>(val);					\
      _type_inc(vv);							\
      mem_cast[0] = vv;							\
    } else {								\
      mem_cast[0] = static_cast<type>(val);				\
    }									\
    return true
#define HANDLE_VECTOR_GET_(T, type)					\
    const std::vector<type>* mem_cast = (std::vector<type>*)mem;	\
    if (dec && is_index) {						\
      for (std::vector<type>::const_iterator v = mem_cast->begin();	\
	   v != mem_cast->end(); v++) {					\
	T vv = static_cast<T>(*v);					\
	_type_dec(vv);							\
	out.push_back(vv);						\
      }									\
    } else {								\
      for (std::vector<type>::const_iterator v = mem_cast->begin();	\
	   v != mem_cast->end(); v++) {					\
	out.push_back(static_cast<T>(*v));				\
      }									\
    }									\
    return true
#define HANDLE_SCALAR_GET_(T, type)					\
    type* mem_cast = NULL;						\
    if (!_get_scalar_mem(mem_cast)) return false;			\
    out = static_cast<T>(*mem_cast);					\
    if (dec && is_index) {						\
      _type_dec(out);							\
    }									\
    return true
#define HANDLE_VECTOR_APPEND_(T, type)					\
    std::vector<type>* mem_cast = (std::vector<type>*)mem;		\
    if (index >= 0 && static_cast<size_t>(index) != mem_cast->size()) return false; \
    if (inc && is_index) {						\
      type vv = static_cast<type>(val);					\
      _type_inc(vv);							\
      mem_cast->push_back(vv);						\
    } else {								\
      mem_cast->push_back(static_cast<type>(val));			\
    }									\
    return true
#define HANDLE_VECTOR_INDEX_(T, type)					\
    const std::vector<type>* mem_cast = (std::vector<type>*)mem;	\
    if (index >= mem_cast->size()) return false;			\
    out = static_cast<T>(*(mem_cast->begin() + (int)(index)));		\
    if (dec && is_index) {						\
      _type_dec(out);							\
    }									\
    return true

#define PROPERTY_TYPE_(T, flag)						\
  inline								\
  bool ObjPropertyType::set(const std::vector<T>& val, bool inc) {	\
    if ((!mem) || !(second & ObjTypeList) || (second & ObjTypeIdx)) return false; \
    if (second & flag) {						\
      HANDLE_VECTOR_SET_(T, T, );					\
    }									\
    return false;							\
  }									\
  inline								\
  bool ObjPropertyType::set(const T& val, bool inc) {			\
    if ((!mem) || second & ObjTypeList) return false;			\
    if (second & flag) {						\
      HANDLE_SCALAR_SET_(T, T);						\
    }									\
    return false;							\
  }									\
  inline								\
  bool ObjPropertyType::get(std::vector<T>& out, bool dec) const {	\
    if ((!mem) || (!(second & ObjTypeList)) || (second & ObjTypeIdx)) return false; \
    if (second & flag) {						\
      HANDLE_VECTOR_GET_(T, T);						\
    }									\
    return false;							\
  }									\
  inline								\
  bool ObjPropertyType::get(T& out, bool dec) const {			\
    if ((!mem) || second & ObjTypeList) return false;			\
    if (second & flag) {						\
      HANDLE_SCALAR_GET_(T, T);						\
    }									\
    return false;							\
  }									\
  inline								\
  bool ObjPropertyType::append(const T& val, int index, bool inc) {	\
    if ((!mem) || (!(second & ObjTypeList)) || (second & ObjTypeIdx)) return false; \
    if (second & flag) {						\
      HANDLE_VECTOR_APPEND_(T, T);					\
    }									\
    return false;							\
  }									\
  inline								\
  bool ObjPropertyType::index(const size_t index, T& out, bool dec) const { \
    if ((!mem) || (!(second & ObjTypeList)) || (second & ObjTypeIdx)) return false; \
    if (second & flag) {						\
      HANDLE_VECTOR_INDEX_(T, T);					\
    }									\
    return false;							\
  }
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((COMPATIBLE_WITH_INT(T)), (bool))
ObjPropertyType::setColor(const T& val, bool inc) {
  if ((!mem) || second & ObjTypeList) return false;
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_SCALAR_SET_)
  return true;
}
template<typename T>
YGGDRASIL_RAPIDJSON_ENABLEIF_RETURN((COMPATIBLE_WITH_INT(T)), (bool))
ObjPropertyType::setColor(const T& val, bool inc) {
  double valF = static_cast<double>(val) / 255.0;
  return setColor(valF, inc);
}
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			    internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			    COMPATIBLE_WITH_SURF(T)> >), (bool))
ObjPropertyType::set(const std::vector<T>& val, bool inc) {
  if ((!mem) || !(second & ObjTypeList)) return false;
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_VECTOR_SET_TEMPLATE_)
    return true;
}
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			    internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			    COMPATIBLE_WITH_SURF(T)> >), (bool))
ObjPropertyType::set(const T& val, bool inc) {
  if (is_color) {
    return setColor(val, inc);
  }
  if ((!mem) || second & ObjTypeList) return false;
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_SCALAR_SET_)
  return true;
}
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			    internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			    COMPATIBLE_WITH_SURF(T)> >), (bool))
ObjPropertyType::get(std::vector<T>& out, bool dec) const {
  if ((!mem) || !(second & ObjTypeList) || (second & ObjTypeIdx)) return false;
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_VECTOR_GET_)
  return false;
}
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			    internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			    COMPATIBLE_WITH_SURF(T)> >), (bool))
ObjPropertyType::get(T& out, bool dec) const {
  if ((!mem) || second & ObjTypeList) return false;
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_SCALAR_GET_)
  return true;
}
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			    internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			    COMPATIBLE_WITH_SURF(T)> >), (bool))
ObjPropertyType::append(const T& val, int index, bool inc) {
  if ((!mem) || !(second & ObjTypeList) || (second & ObjTypeIdx)) return false;
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_VECTOR_APPEND_)
  return false;
}
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<COMPATIBLE_WITH_STRING(T),
			    internal::OrExpr<COMPATIBLE_WITH_CURV(T),
			    COMPATIBLE_WITH_SURF(T)> >), (bool))
ObjPropertyType::index(const size_t index, T& out, bool dec) const {
  if ((!mem) || !(second & ObjTypeList) || (second & ObjTypeIdx)) return false;
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_VECTOR_INDEX_)
  return false;
}
PROPERTY_TYPE_(std::string, ObjTypeString)
PROPERTY_TYPE_(ObjRefCurve, ObjTypeCurve)
PROPERTY_TYPE_(ObjRefSurface, ObjTypeSurface)
inline
bool ObjPropertyType::inc() {
  if (!is_index) return true;
  void* T = NULL;
#define INC_SCALAR_(T, type)				\
  {							\
    type v;						\
    if (!get(v)) return false;				\
    if (!set(v, true)) return false;			\
  }
#define INC_VECTOR_(T, type)					\
  {								\
    std::vector<type> v;					\
    if (!get(v)) return false;					\
    std::vector<type>* mem_cast = (std::vector<type>*)mem;	\
    mem_cast->clear();						\
    if (!set(v, true)) return false;				\
  }
  if (second & ObjTypeList) {
    YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(INC_VECTOR_);
  } else {
    YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(INC_SCALAR_);
  }
#undef INC_SCALAR_
#undef INC_VECTOR_
  return (T == NULL);
}
#undef HANDLE_VECTOR_SET_TEMPLATE_
#undef HANDLE_VECTOR_SET_
#undef HANDLE_SCALAR_SET_
#undef HANDLE_VECTOR_GET_
#undef HANDLE_SCALAR_GET_
#undef HANDLE_VECTOR_APPEND_
#undef HANDLE_VECTOR_INDEX_
#undef PROPERTY_TYPE_
inline
bool ObjPropertyType::copy(const ObjPropertyType& rhs) {
  if (first != rhs.first || second != rhs.second || idx != rhs.idx)
    return false;
#define HANDLE_SCALAR_CPY_(T0, T)		\
  T val;					\
  if (!rhs.get(val)) return false;		\
  return set(val)
#define HANDLE_VECTOR_CPY_(T0, T)		\
  std::vector<T> val;				\
  if (!rhs.get(val)) return false;		\
  return set(val)
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_ALL_(HANDLE_SCALAR_CPY_, HANDLE_VECTOR_CPY_)
#undef HANDLE_SCALAR_CPY_
#undef HANDLE_VECTOR_CPY_
    return false;
}
inline
bool ObjPropertyType::read(std::istream& in) {
#define HANDLE_SCALAR_READ_(T0, T)					\
  if (in.peek() == '\n') {						\
    if (second & ObjTypeIdx && second & ObjTypeString)			\
      in >> std::ws;							\
    missing = true;							\
    return (second & ObjTypeOpt);					\
  }									\
  T* val = NULL;							\
  if (!_get_scalar_mem(val, true)) return false;			\
  if (!(in >> *val)) {							\
    if (second & ObjTypeIdx) {						\
      std::vector<T>* mem_vect = (std::vector<T>*)mem;			\
      mem_vect->resize(mem_vect->size() - 1);				\
    }									\
    missing = true;							\
    return (second & ObjTypeOpt);					\
  }									\
  return true
#define HANDLE_VECTOR_READ_(T0, T)		\
  std::vector<T>* val = (std::vector<T>*)mem;	\
  T x = 0;					\
  while ((in.peek() != '\n') && (in >> x))	\
    val->push_back(x);				\
  return true
  if (!mem) return false;
  if (second & ObjTypeOff) {
    if (!(second & ObjTypeInt) || (second & ObjTypeList)) return false;
    std::string valS;
    in >> valS;
    ((int*)mem)[0] = (valS == "off") ? 0 : std::atoi(valS.c_str());
    return true;
  } else if (second & ObjTypeList) {
    if (second & ObjTypeString) {
      std::string x = "";
      std::vector<std::string>* val = (std::vector<std::string>*)mem;
      while ((in.peek() != '\n') && (in >> x))
	val->push_back(x);
      in >> std::skipws;
      return true;
    }
    // Do this explicitly because string can't be initialized with 0
    // else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_(HANDLE_VECTOR_READ_)
    else if (second & ObjTypeCurve) {
      HANDLE_VECTOR_READ_(T, ObjRefCurve);
    } else if (second & ObjTypeSurface) {
      HANDLE_VECTOR_READ_(T, ObjRefSurface);
    } else if (second & ObjTypeString) {
      std::vector<std::string>* val = (std::vector<std::string>*)mem;
      std::string x;
      while ((in.peek() != '\n') && (in >> x))
	val->push_back(x);
      return true;
    }
    else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_VECTOR_READ_)
  }
  else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_(HANDLE_SCALAR_READ_)
  else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_SCALAR_READ_)
#undef HANDLE_SCALAR_READ_
#undef HANDLE_VECTOR_READ_
  return false;
}
inline
bool ObjPropertyType::write(std::ostream& out, bool pad) const {
#define RECORD_FORMAT_(prec)				\
  out_flags = out.flags();				\
  out_prec = out.precision();				\
  out.precision(prec);					\
  out << std::fixed
#define RESTORE_FORMAT_				\
  out.precision(out_prec);			\
  out.flags(out_flags)
#define HANDLE_SCALAR_WRITE_(T0, T)					\
  T* val = NULL;							\
  if (!_get_scalar_mem(val)) return (second & ObjTypeOpt);		\
  if (second & ObjTypeFloat) {						\
    RECORD_FORMAT_(prec);						\
  }									\
  if (pad) out << " ";							\
  out << *val;								\
  if (second & ObjTypeFloat) {						\
    RESTORE_FORMAT_;							\
  }									\
  return true
#define HANDLE_VECTOR_WRITE_(T0, T)					\
  std::vector<T>* val = (std::vector<T>*)mem;				\
  if (second & ObjTypeFloat) {						\
    RECORD_FORMAT_(prec);						\
  }									\
  if (pad) out << " ";							\
  for (std::vector<T>::iterator v = val->begin(); v != val->end(); v++) { \
    if (v != val->begin())						\
      out << " ";							\
    out << *v;								\
  }									\
  if (second & ObjTypeFloat) {						\
    RESTORE_FORMAT_;							\
  }									\
  return true
  int prec = 1;
  std::streamsize out_prec = 0;
  std::ios_base::fmtflags out_flags = out.flags();
  if (!mem) return false;
  if (second & ObjTypeOff) {
    if (!(second & ObjTypeInt) || (second & ObjTypeList)) return false;
    int* val = (int*)mem;
    if (*val == 0)
      out << "off";
    else
      out << *val;
    return true;
  } else if (second & ObjTypeList) {
    if (second & ObjTypeFloat) {
      {
	std::vector<double>* val = (std::vector<double>*)mem;
	for (std::vector<double>::iterator v = val->begin(); v != val->end(); v++)
	  prec = (std::max)(prec, count_decimals(*v));
      }
      HANDLE_VECTOR_WRITE_(double, double);
    }
    else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_(HANDLE_VECTOR_WRITE_)
    else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_VECTOR_WRITE_)
  } else if (second & ObjTypeFloat) {
    prec = (std::max)(1, count_decimals(*((double*)mem)));
    HANDLE_SCALAR_WRITE_(double, double);
  }
  else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_(HANDLE_SCALAR_WRITE_)
  else YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_(HANDLE_SCALAR_WRITE_)
#undef HANDLE_SCALAR_WRITE_
#undef HANDLE_VECTOR_WRITE_
#undef RECORD_FORMAT_
#undef RESTORE_FORMAT_
  return false;
}
inline
bool ObjPropertyType::is_equal(const ObjPropertyType& rhs) const {
  if (first != rhs.first || second != rhs.second) return false;
  if ((!mem) || (!rhs.mem)) return false;
#define HANDLE_SCALAR_(T0, T)					\
  T* val_lhs = NULL;						\
  T* val_rhs = NULL;						\
  bool mem_lhs = _get_scalar_mem(val_lhs);			\
  bool mem_rhs = rhs._get_scalar_mem(val_rhs);			\
  if (!mem_lhs || !mem_rhs)					\
    return ((second & ObjTypeOpt) && (mem_lhs == mem_rhs));	\
  return internal::values_eq(*val_lhs, *val_rhs)
#define HANDLE_VECTOR_ISEQ_(T0, T)					\
  const std::vector<T>* val_lhs = (std::vector<T>*)mem;			\
  const std::vector<T>* val_rhs = (std::vector<T>*)(rhs.mem);		\
  return is_equal_vectors(*val_lhs, *val_rhs)
  YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_ALL_(HANDLE_SCALAR_, HANDLE_VECTOR_ISEQ_)
#undef HANDLE_SCALAR_
#undef HANDLE_VECTOR_ISEQ_
  return false;
}
#undef YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_ALL_
#undef YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_
#undef YGGDRASIL_RAPIDJSON_HANDLE_PROPERTY_TYPES_SPECIAL_


#define REPORT_UNSUPPORTED_ELEMENT(src, name)	\
  {									\
    std::cerr << "Unsupported element signifier for " #src ": " << name << std::endl; \
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof("Unsupported element signifier"));		\
  }
#define OBJ_ELEMENT_INIT(word, lhs, args) {				\
    bool first = true;							\
    while (true) {							\
      if      (word == "#"         ) lhs = new ObjComment args;		\
      else if (word == "v"         ) lhs = new ObjVertex args;		\
      else if (word == "vp"        ) lhs = new ObjVParameter args;	\
      else if (word == "vn"        ) lhs = new ObjVNormal args;		\
      else if (word == "vt"        ) lhs = new ObjVTexture args;	\
      else if (word == "p"         ) lhs = new ObjPoint args;		\
      else if (word == "l"         ) lhs = new ObjLine args;		\
      else if (word == "f"         ) lhs = new ObjFace args;		\
      else if (word == "curv"      ) lhs = new ObjCurve args;		\
      else if (word == "curv2"     ) lhs = new ObjCurve2D args;		\
      else if (word == "surf"      ) lhs = new ObjSurface args;		\
      else if (word == "cstype"    ) lhs = new ObjFreeFormType args;	\
      else if (word == "deg"       ) lhs = new ObjDegree args;		\
      else if (word == "bmat"      ) lhs = new ObjBasisMatrix args;	\
      else if (word == "step"      ) lhs = new ObjStep args;		\
      else if (word == "parm"      ) lhs = new ObjParameter args;	\
      else if (word == "trim"      ) lhs = new ObjTrim args;		\
      else if (word == "hole"      ) lhs = new ObjHole args;		\
      else if (word == "scrv"      ) lhs = new ObjScrv args;		\
      else if (word == "sp"        ) lhs = new ObjSpecialPoints args;	\
      else if (word == "con"       ) lhs = new ObjConnect args;		\
      else if (word == "g"         ) lhs = new ObjGroup args;		\
      else if (word == "s"         ) lhs = new ObjSmoothingGroup args;	\
      else if (word == "mg"        ) lhs = new ObjMergingGroup args;	\
      else if (word == "o"         ) lhs = new ObjObjectName args;	\
      else if (word == "bevel"     ) lhs = new ObjBevel args;		\
      else if (word == "c_interp"  ) lhs = new ObjCInterp args;		\
      else if (word == "d_interp"  ) lhs = new ObjDInterp args;		\
      else if (word == "lod"       ) lhs = new ObjLOD args;		\
      else if (word == "maplib"    ) lhs = new ObjTextureMapLib args;	\
      else if (word == "usemap"    ) lhs = new ObjTextureMap args;	\
      else if (word == "usemtl"    ) lhs = new ObjMaterial args;	\
      else if (word == "mtllib"    ) lhs = new ObjMaterialLib args;	\
      else if (word == "shadow_obj") lhs = new ObjShadowFile args;	\
      else if (word == "trace_obj" ) lhs = new ObjTraceFile args;	\
      else if (word == "ctech"     ) lhs = new ObjCTech args;		\
      else if (word == "stech"     ) lhs = new ObjSTech args;		\
      else if (word == "end"       ) lhs = NULL;			\
      else if (first) {							\
	first = false;							\
	word = obj_alias2base(word);					\
	continue;							\
      } else {								\
	REPORT_UNSUPPORTED_ELEMENT(init, word);				\
      }									\
      break;								\
    }									\
    }

#define OBJ_P_(...) ObjPropertyType(__VA_ARGS__)
#define COMPARE_IDX(x, nprev)						\
  (((int)x >= 0 && (size_t)x <= nprev) ||				\
   ((int)x < 0 && (int)x < -(int)nprev))
#define GENERIC_CONSTRUCTOR_COPY(cls, base, init, props)		\
  /*! \copydoc ObjElement::ObjElement(const ObjElement&) */		\
  cls(const cls& rhs) :							\
    base(rhs.code, rhs.parent) UNPACK_MACRO init {			\
    this->_init_properties();						\
    base::copy_members(dynamic_cast<const base*>(&rhs));		\
    this->copy_members(&rhs);						\
  }									\
  /*! \copydoc ObjElement::ObjElement(const ObjElement*) */		\
  cls(const ObjElement* rhs) :						\
    base(rhs->code, rhs->parent) UNPACK_MACRO init {			\
    this->_init_properties();						\
    base::copy_members(dynamic_cast<const base*>(rhs));			\
    this->copy_members(dynamic_cast<const cls*>(rhs));			\
  }									\
  /*! \copydoc ObjElement::copy() */					\
  cls* copy() const OVERRIDE_CXX11 { return new cls(*this); }
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
#define GENERIC_ELEMENT_CONSTRUCTOR(cls, base, codeS, init, props)	\
  /*! \brief Empty constructor. */					\
  /*! \param parent0 The element's parent group. */			\
  cls(const ObjGroupBase* parent0 = NULL) :				\
    base(#codeS, parent0) UNPACK_MACRO init {				\
    this->_init_properties();						\
  }									\
  GENERIC_CONSTRUCTOR_COPY(cls, base, init, props);			\
  void _init_properties() OVERRIDE_CXX11 {				\
    this->properties = {						\
      UNPACK_MACRO props						\
    };									\
  }
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
#define GENERIC_ELEMENT_CONSTRUCTOR(cls, base, codeS, init, props)	\
  /*! \brief Empty constructor. */					\
  /*! \param parent0 The element's parent group. */			\
  cls(const ObjGroupBase* parent0 = NULL) :				\
    base(#codeS, parent0) UNPACK_MACRO init {				\
    this->_init_properties();						\
  }									\
  GENERIC_CONSTRUCTOR_COPY(cls, base, init, props);			\
  void _init_properties() OVERRIDE_CXX11 {				\
    ObjPropertyType tmp[] = {						\
      UNPACK_MACRO props						\
    };									\
    this->properties.assign(&tmp[0], &tmp[(sizeof(tmp) / sizeof(ObjPropertyType)) - 1] + 1); \
  }
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11

#define GENERIC_COPY_MEMBERS(cls)					\
  /*! \brief Copy element specific members from another instance. */	\
  /*! \param[in] rhs Element to copy members from. */			\
  /*! \return true if successful, false otherwise. */			\
  bool copy_members(const cls* rhs) {					\
    if (!set_meta_properties(rhs->size())) return false;		\
    if (rhs->properties.size() != properties.size()) return false;	\
    ObjPropertiesMap::const_iterator rit = rhs->properties.begin();	\
    for (ObjPropertiesMap::iterator lit = properties.begin();		\
	 lit != properties.end(); lit++, rit++) {			\
      if (!this->has_property(lit->first, true, false, NULL)) continue;	\
      if (!lit->copy(*rit)) return false;				\
    }									\
    return true;							\
  }
#define DUMMY_ARRAY_CONSTRUCTOR(cls, base, code, init)			\
  /*! \brief Raise an error. */						\
  template <typename T>							\
  cls(const std::vector<T> &,						\
      const ObjGroupBase* parent0 = NULL,				\
      bool = false) : base(#code, parent0) UNPACK_MACRO init {		\
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(#cls " elements cannot be initialized from a vector")); \
  }									\
  /*! \brief Raise an error. */						\
  template <typename T, size_t N>					\
  cls(const T (&)[N],							\
      const ObjGroupBase* parent0 = NULL,				\
      bool = false) : base(#code, parent0) UNPACK_MACRO init {		\
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(#cls " elements cannot be initialized from an array")); \
  }

#define GENERIC_SCALAR_CONSTRUCTOR(cls, base, code, type, def, props)	\
  GENERIC_ELEMENT_CONSTRUCTOR(cls, base, code, SINGLE_ARG(, value(def)), props); \
  DUMMY_ARRAY_CONSTRUCTOR(cls, base, code, SINGLE_ARG(, value(def)))	\
  /*! \brief Initialize an element from a scalar. */			\
  /*! \param value0 Scalar value. */					\
  /*! \param parent0 Parent group. */					\
  template <typename T>							\
  cls(const T& value0,							\
      const ObjGroupBase* parent0 = NULL,				\
      YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_TYPE(T, type)))) :		\
  base(#code, parent0), value(value0) {					\
    this->_init_properties();						\
  }									\
  /*! \brief Initialize an element from a scalar. */			\
  /*! \param value0 Scalar value. */					\
  /*! \param parent0 Parent group. */					\
  template <typename T>							\
  cls(const T&,								\
      const ObjGroupBase* parent0 = NULL,				\
      YGGDRASIL_RAPIDJSON_DISABLEIF((internal::OrExpr<COMPATIBLE_WITH_TYPE(T, type),\
			   internal::IsPointer<T> >))) :			\
    base(#code, parent0), value(def) {					\
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(#cls " must be initialized from" #type ".")); \
  }

#define GENERIC_SCALAR_BODY_BASE(cls, type)				\
  GENERIC_COPY_MEMBERS(cls)						\
  type value;
#define GENERIC_SCALAR_BODY(cls, base, codeS, def, props, valType, outType, outTypeName) \
  GENERIC_SCALAR_CONSTRUCTOR(cls, base, codeS, valType, def, props)	\
  GENERIC_SCALAR_BODY_BASE(cls, valType)

#define GENERIC_VECTOR_CONSTRUCTOR(cls, base, code, init, props, compat, T2) \
  GENERIC_ELEMENT_CONSTRUCTOR(cls, base, code, init, props)		\
  /*! \brief Initialize and element from a C++ vector of values. */	\
  /*! \tparam T Vector element type. Must be castable to the type. */	\
  /*! \param values0 Vector of values. */				\
  /*! \param parent0 The element's parent group. */			\
  template <typename T>							\
  cls(const std::vector<T> &values0,					\
      const ObjGroupBase* parent0 = NULL,				\
      YGGDRASIL_RAPIDJSON_ENABLEIF((compat))) :					\
  base(#code, parent0) UNPACK_MACRO init {				\
    this->_init_properties();						\
    assign_values(values, values0);					\
    from_values();							\
  }									\
  /*! \brief Raise an error if non-compatible vector is provided. */	\
  /*! \tparam T Type of vector elements. */				\
  template <typename T>							\
  cls(const std::vector<T>&,						\
      const ObjGroupBase* parent0 = NULL,				\
      YGGDRASIL_RAPIDJSON_DISABLEIF((compat))) :					\
    base(#code, parent0) UNPACK_MACRO init {				\
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(#cls " must be initialized from " #T2 "s.")); \
  }									\
  /*! \brief Initialize an element from a C array of values. */		\
  /*! \tparam T Array element type. */					\
  /*! \tparam N Array size. */						\
  /*! \param src Array of values. */					\
  template <typename T, size_t N>					\
  cls(const T (&values0)[N],						\
      const ObjGroupBase* parent0 = NULL,				\
      YGGDRASIL_RAPIDJSON_ENABLEIF((compat))) :					\
    base(#code, parent0) UNPACK_MACRO init {				\
    this->_init_properties();						\
    assign_values(values, std::vector<T>(values0, values0+N));		\
    from_values();							\
  }									\
  /*! \brief Raise an error if non-compatible vector is provided. */	\
  /*! \tparam T Type of vector elements. */				\
  /*! \tparam N Array size. */						\
  template <typename T, size_t N>					\
  cls(const T (&)[N],							\
      const ObjGroupBase* parent0 = NULL,				\
      YGGDRASIL_RAPIDJSON_DISABLEIF((compat))) :					\
    base(#code, parent0) UNPACK_MACRO init {				\
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(#cls " must be initialized from " #T2 "s.")); \
  }
#define GENERIC_VECTOR_BODY_BASE(cls, type)				\
  GENERIC_COPY_MEMBERS(cls)						\
  /*! \copydoc ObjElement::size */					\
  size_t size(bool skipColors=false) const OVERRIDE_CXX11 {		\
    size_t out = 0;							\
    for (ObjPropertiesMap::const_iterator it = properties.begin();	\
	 it != properties.end(); it++) {				\
      if (!this->has_property(it->first, true, skipColors, NULL)) continue; \
      if (it->second & ObjTypeList)					\
	out += values.size();						\
      else								\
	out++;								\
    }									\
    return out;								\
  }									\
  std::vector<type> values;
#define GENERIC_VECTOR_BODY_STORED(cls, base, code, props, compat, valType, outType, outTypeName) \
  GENERIC_VECTOR_CONSTRUCTOR(cls, base, code, SINGLE_ARG(, values()), props, UNPACK_MACRO compat, valType) \
  GENERIC_VECTOR_BODY_BASE(cls, valType)				\
  /*! \copydoc ObjElement::from_values() */				\
  bool from_values() OVERRIDE_CXX11 {					\
    int min = min_values(true);						\
    int max = max_values(true);						\
    YGGDRASIL_RAPIDJSON_ASSERT((min < 0 || values.size() >= (size_t)min) &&	\
		     (max < 0 || values.size() <= (size_t)max));	\
    return ((min < 0 || values.size() >= (size_t)min) &&		\
	    (max < 0 || values.size() <= (size_t)max));			\
  }
#define GENERIC_VECTOR_BODY_STRICT(cls, base, code, props, compat, valType, outType, outTypeName, min, max) \
  GENERIC_VECTOR_BODY_STORED(cls, base, code, props, compat, valType, outType, outTypeName); \
  /*! \brief Get the minimum number of values required for this element to be valid. */	\
  int min_values(bool=false) const OVERRIDE_CXX11 { return min; }	\
  /*! \brief Get the maximum number of values allowed for this element to be valid. */	\
  int max_values(bool=false) const OVERRIDE_CXX11 { return max; }	\
  /*! \copydoc ObjElement::add_subelement */				\
  bool add_subelement() OVERRIDE_CXX11 {				\
    values.resize(values.size() + 1);					\
    return true;							\
  }
#define GENERIC_VECTOR_BODY_MIXED(cls, base, code, init, props, valType, minB, maxB) \
  GENERIC_ELEMENT_CONSTRUCTOR(cls, base, code, init, props)		\
  DUMMY_ARRAY_CONSTRUCTOR(cls, base, code, init)			\
  /*! \brief Get the minimum number of values required for this element to be valid. */	\
  /*! \param valuesOnly If true, the minimum for the values vector is returned. */ \
  int min_values(bool valuesOnly=false) const OVERRIDE_CXX11 {		\
    int minV = minB;							\
    if (valuesOnly) return minV;					\
    int out = (std::max)(minV, 0);					\
    for (ObjPropertiesMap::const_iterator it = properties.begin();	\
	 it != properties.end(); it++) {				\
      if (it->second & ObjTypeList) continue;				\
      if (!(it->second & ObjTypeOpt)) out++;				\
    }									\
    return out;								\
  }									\
  /*! \brief Get the maximum number of values allowed for this element to be valid. */	\
  /*! \param valuesOnly If true, the maximum for the values vector is returned. */ \
  int max_values(bool valuesOnly=false) const OVERRIDE_CXX11 {		\
    int maxV = maxB;							\
    if (valuesOnly || maxV < 0) return maxV;				\
    int out = (std::max)(maxV, 0);					\
    for (ObjPropertiesMap::const_iterator it = properties.begin();	\
	 it != properties.end(); it++) {				\
      if (it->second & ObjTypeList) continue;				\
      out++;								\
    }									\
    return out;								\
  }									\
  GENERIC_VECTOR_BODY_BASE(cls, valType)
#define GENERIC_VECTOR_BODY_TEMP(cls, base, code, init, props, compat, valType) \
  GENERIC_VECTOR_CONSTRUCTOR(cls, base, code, init, props, UNPACK_MACRO compat, valType) \
  /*! \copydoc ObjElement::from_values() */				\
  bool from_values() OVERRIDE_CXX11 {					\
    return this->set_properties(values);				\
  }									\
  /*! \copydoc ObjElement::read_values */				\
  bool read_values(std::istream &in, const bool& dont_descend=false) OVERRIDE_CXX11 { \
    (void)dont_descend;							\
    if (!ObjElement::read_values(in, values)) return false;		\
    return this->set_properties(values);				\
  }									\
  GENERIC_VECTOR_BODY_BASE(cls, valType)

// SCALAR CLASS MACROS
#define GENERIC_SCALAR_STRING(cls, code, def, props)			\
  class cls : public ObjElement {					\
  public:								\
  GENERIC_SCALAR_BODY(cls, ObjElement, code, def, props, std::string, std::string, string) \
  }

// VECTOR CLASS MACROS
#define GENERIC_VECTOR_STRING(cls, code, type, props)			\
  class cls : public ObjElement {					\
  public:								\
  GENERIC_VECTOR_BODY_STRICT(cls, ObjElement, code, props,		\
			     SINGLE_ARG(COMPATIBLE_WITH_TYPE(T, std::string)), \
			     std::string, std::string, string,		\
			     -1, -1)					\
  }
#define GENERIC_VECTOR_OBJREFVERTEX(cls, code, min)			\
  class cls : public ObjElement {					\
  public:								\
  GENERIC_VECTOR_BODY_STRICT(cls, ObjElement, code,			\
			     SINGLE_ARG(OBJ_P_(&values, "vertex_index", ObjTypeVertex | ObjTypeList)), \
			     SINGLE_ARG(COMPATIBLE_WITH_VERT(T)),	\
			     ObjRefVertex, int, int,			\
			     min, -1)					\
  GENERIC_CLASS_VECTOR_TYPE_IS_VALID_VERTREF(min)			\
  }
#define GENERIC_VECTOR_OBJREFCURVE(cls, code)				\
  class cls : public ObjElement {					\
  public:								\
  GENERIC_VECTOR_BODY_STRICT(cls, ObjElement, code,			\
			     SINGLE_ARG(OBJ_P_(&values, "curve_index", ObjTypeCurve | ObjTypeList)), \
			     SINGLE_ARG(COMPATIBLE_WITH_TYPE(T, ObjRefCurve)), \
			     ObjRefCurve, int, int,			\
			     -1, -1)					\
  /*! \copydoc ObjElement::is_valid_idx */				\
  bool is_valid_idx(std::map<std::string,size_t>& idx) const OVERRIDE_CXX11 { \
    if (!ObjElement::is_valid_idx(idx)) return false;			\
    std::map<std::string,size_t>::iterator x = idx.find("curv2");	\
    size_t ncurv = 0;							\
    if (x != idx.end()) ncurv = x->second;				\
    for (std::vector<ObjRefCurve>::const_iterator it = values.begin();	\
	 it != values.end(); it++) {					\
      if (!COMPARE_IDX((it->curv2d), ncurv)) return false;		\
    }									\
    return true;							\
  }									\
  /* \copydoc ObjElement::append_indexes */				\
  void append_indexes(const std::map<std::string,size_t> idx) OVERRIDE_CXX11 { \
    std::map<std::string,size_t>::const_iterator x = idx.find("curv2"); \
    size_t ncurv = 0;							\
    if (x != idx.end()) ncurv = x->second;				\
    for (std::vector<ObjRefCurve>::iterator it = values.begin();	\
	 it != values.end(); it++) {					\
      it->curv2d += static_cast<ObjRef>(ncurv);				\
    }									\
  }									\
  /*! \copydoc ObjElement::last_subelement */				\
  ObjPropertyElement* last_subelement(bool* temp = NULL) OVERRIDE_CXX11 { \
    if (values.size() == 0) return NULL;				\
    if (temp) temp[0] = false;						\
    return &(values[values.size() - 1]);				\
  }									\
  }
    
#define GENERIC_VECTOR_OBJREFSURFACE(cls, code)				\
  class cls : public ObjElement {					\
  public:								\
  GENERIC_VECTOR_BODY_STRICT(cls, ObjElement, code,			\
			     SINGLE_ARG(OBJ_P_(&values, "surface_index", ObjTypeSurface | ObjTypeList)), \
			     SINGLE_ARG(COMPATIBLE_WITH_TYPE(T, ObjRefSurface)), \
			     ObjRefSurface, int, int,			\
    1, -1)								\
  /*! \copydoc ObjElement::is_valid_idx */				\
  bool is_valid_idx(std::map<std::string,size_t>& idx) const OVERRIDE_CXX11 { \
    if (!ObjElement::is_valid_idx(idx)) return false;			\
    std::map<std::string,size_t>::iterator curv = idx.find("curv2");	\
    std::map<std::string,size_t>::iterator surf = idx.find("surf");	\
    size_t ncurv = 0, nsurf = 0;					\
    if (curv != idx.end()) ncurv = curv->second;			\
    if (surf != idx.end()) nsurf = surf->second;			\
    for (std::vector<ObjRefSurface>::const_iterator it = values.begin(); \
	 it != values.end(); it++) {					\
      if (!COMPARE_IDX((it->curv2d), ncurv)) return false;		\
      if (!COMPARE_IDX((it->surf), nsurf)) return false;		\
    }									\
    return true;							\
  }									\
  /* \copydoc ObjElement::append_indexes */				\
  void append_indexes(const std::map<std::string,size_t> idx) OVERRIDE_CXX11 { \
    std::map<std::string,size_t>::const_iterator curv = idx.find("curv2"); \
    std::map<std::string,size_t>::const_iterator surf = idx.find("surf"); \
    size_t ncurv = 0, nsurf = 0;					\
    if (curv != idx.end()) ncurv = curv->second;			\
    if (surf != idx.end()) nsurf = surf->second;			\
    for (std::vector<ObjRefSurface>::iterator it = values.begin();	\
	 it != values.end(); it++) {					\
      it->curv2d += static_cast<ObjRef>(ncurv);				\
      it->surf += static_cast<ObjRef>(nsurf);				\
    }									\
  }									\
  /*! \copydoc ObjElement::last_subelement */				\
  ObjPropertyElement* last_subelement(bool* temp = NULL) OVERRIDE_CXX11 { \
    if (values.size() == 0) return NULL;				\
    if (temp) temp[0] = false;						\
    return &(values[values.size() - 1]);				\
  }									\
  }
#define GENERIC_CLASS_VECTOR_TYPE_IS_VALID(code, type)			\
  /*! \copydoc ObjElement::is_valid_idx */				\
  bool is_valid_idx(std::map<std::string,size_t>& idx) const OVERRIDE_CXX11 { \
    if (!ObjElement::is_valid_idx(idx)) return false;			\
    std::map<std::string,size_t>::iterator x = idx.find(code);		\
    size_t nprev = 0;							\
    if (x != idx.end()) nprev = x->second;				\
    for (std::vector<type>::const_iterator it = values.begin();		\
	 it != values.end(); it++) {					\
      if (!COMPARE_IDX((*it), nprev)) return false;			\
    }									\
    return true;							\
  }									\
  /* \copydoc ObjElement::append_indexes */				\
  void append_indexes(const std::map<std::string,size_t> idx) OVERRIDE_CXX11 { \
    std::map<std::string,size_t>::const_iterator x = idx.find(code);	\
    size_t nprev = 0;							\
    if (x != idx.end()) nprev = x->second;				\
    for (std::vector<type>::iterator it = values.begin();		\
	 it != values.end(); it++) {					\
      *it += static_cast<type>(nprev);					\
    }									\
  }									\
  /*! \copydoc ObjElement::last_subelement */				\
  ObjPropertyElement* last_subelement(bool* temp = NULL) OVERRIDE_CXX11 { \
    if (values.size() == 0 || (!temp) || this->properties.size() > 1) return NULL; \
    *temp = true;							\
    return new ObjPropertyElement(&(*(values.end() - 1)),		\
				  this->properties.begin()->first,	\
				  this->properties.begin()->second);	\
  }
#define GENERIC_CLASS_VECTOR_TYPE_IS_VALID_VERTREF(min)			\
  /*! \copydoc ObjElement::is_valid_idx */				\
  bool is_valid_idx(std::map<std::string,size_t>& idx) const OVERRIDE_CXX11 { \
    if (!ObjElement::is_valid_idx(idx)) return false;			\
    if (values.size() < min) return false;				\
    std::map<std::string,size_t>::iterator v = idx.find("v");		\
    std::map<std::string,size_t>::iterator vt = idx.find("vt");		\
    std::map<std::string,size_t>::iterator vn = idx.find("vn");		\
    size_t nv = 0, nvt = 0, nvn = 0;					\
    if (v != idx.end()) nv = v->second;					\
    if (vt != idx.end()) nvt = vt->second;				\
    if (vn != idx.end()) nvn = vn->second;				\
    for (std::vector<ObjRefVertex>::const_iterator it = values.begin();	\
	 it != values.end(); it++) {					\
      if (!COMPARE_IDX((it->v), nv)) return false;			\
      if (!COMPARE_IDX((it->vt), nvt)) return false;			\
      if (!COMPARE_IDX((it->vn), nvn)) return false;			\
    }									\
    return true;							\
  }									\
  /* \copydoc ObjElement::append_indexes */				\
  void append_indexes(const std::map<std::string,size_t> idx) OVERRIDE_CXX11 { \
    std::map<std::string,size_t>::const_iterator v = idx.find("v");	\
    std::map<std::string,size_t>::const_iterator vt = idx.find("vt");	\
    std::map<std::string,size_t>::const_iterator vn = idx.find("vn");	\
    size_t nv = 0, nvt = 0, nvn = 0;					\
    if (v != idx.end()) nv = v->second;					\
    if (vt != idx.end()) nvt = vt->second;				\
    if (vn != idx.end()) nvn = vn->second;				\
    for (std::vector<ObjRefVertex>::iterator it = values.begin();	\
	 it != values.end(); it++) {					\
      it->v += static_cast<ObjRef>(nv);					\
      it->vt += static_cast<ObjRef>(nvt);				\
      it->vn += static_cast<ObjRef>(nvn);				\
    }									\
  }									\
  /*! \copydoc ObjElement::last_subelement */				\
  ObjPropertyElement* last_subelement(bool* temp = NULL) OVERRIDE_CXX11 { \
    if (values.size() == 0) return NULL;				\
    if (temp) temp[0] = false;						\
    return &(values[values.size() - 1]);				\
  }
  
  
// Forward declaration
class ObjElement;
class ObjVParameter;
class ObjVNormal;
class ObjVTexture;
class ObjPoint;
class ObjLine;
class ObjFace;
class ObjCurve;
class ObjCurve2D;
class ObjSurface;
class ObjFreeFormType;
class ObjDegree;
class ObjBasisMatrix;
class ObjStep;
class ObjParameter;
class ObjTrim;
class ObjHole;
class ObjScrv;
class ObjSpecialPoints;
class ObjConnect;
class ObjGroupBase;
class ObjGroup;
class ObjSmoothingGroup;
class ObjMergingGroup;
class ObjObjectName;
inline bool read_obj_element(std::istream &in,
			     ObjGroupBase* parent,
			     const bool& dont_descend,
			     ObjElement*& out);

//! ObjWavefront color.
class ObjColor {
public:
  //! Empty initializer with (r,g,b) = (0,0,0)
  ObjColor() :
    r(0), g(0), b(0), is_set(false) {}
  //! \brief Create a RGB color element.
  //! \param red Color index in red.
  //! \param green Color index in green.
  //! \param blue Color index in blue.
  ObjColor(double red, double green, double blue) :
    r(red), g(green), b(blue), is_set(true) {}
  //! \brief Create a RGB color element.
  //! \param red Color index in red.
  //! \param green Color index in green.
  //! \param blue Color index in blue.
  ObjColor(int red, int green, int blue) :
    r(((double)red)/255.0),
    g(((double)green)/255.0),
    b(((double)blue)/255.0), is_set(true) {}
  //! Red color value.
  double r;
  //! Blue color value.
  double g;
  //! Green color value.
  double b;
  //! true if the color was set.
  bool is_set;
  //! \brief Check if another ObjColor object is equivalent.
  //! \param rhs Object for comparison.
  bool is_equal(const ObjColor& rhs) const {
    const ObjColor& lhs = *this;
    if (lhs.is_set != rhs.is_set) return false;
    if (!internal::values_eq(lhs.r, rhs.r)) return false;
    if (!internal::values_eq(lhs.g, rhs.g)) return false;
    if (!internal::values_eq(lhs.b, rhs.b)) return false;
    return true;
  }
  friend bool operator == (const ObjColor& lhs, const ObjColor& rhs);
};

//! \brief Check if two ObjColor instances are equivalent.
//! \param lhs First instance for comparison.
//! \param rhs Second instance for comparison.
//! \return true if the two instances are equivalent.
inline
bool operator == (const ObjColor& lhs, const ObjColor& rhs)
{ return lhs.is_equal(rhs); }

//! ObjWavefront element base class.
class ObjElement : public ObjBase {
public:
  //! \brief Empty constructor.
  //! \param parent0 The element's parent group.
  ObjElement(const ObjGroupBase* parent0 = NULL) :
    ObjBase(), code(""), parent(parent0) {}
  //! \brief Initialize an element from an element code.
  //! \tparam Number of properties/
  //! \param code0 Element code.
  //! \param parent0 The element's parent group.
  ObjElement(const std::string& code0,
	     const ObjGroupBase* parent0 = NULL) :
    ObjBase(), code(code0), parent(parent0) {}
  //! \brief Copy constructor.
  //! \param rhs Element to copy.
  ObjElement(const ObjElement& rhs) :
    ObjBase(), code(rhs.code), parent(rhs.parent) {}
  //! \brief Initialize and element from a C++ vector of values.
  //! \tparam T Vector element type. Must be an integer or floating point.
  //! \param parent0 The element's parent group.
  template <typename T, size_t N>
  ObjElement(const std::string& code0, const T (&)[N],
	     const ObjGroupBase* parent0 = NULL) :
    ObjBase(), code(code0), parent(parent0) {
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(code + " element cannot be constructed from a vector of the provided type."));
  }
  //! \brief Initialize and element from a C++ vector of values.
  //! \tparam T Vector element type. Must be an integer or floating point.
  //! \param parent0 The element's parent group.
  template <typename T>
  ObjElement(const std::string& code0, const std::vector<T> &,
	     const ObjGroupBase* parent0 = NULL) :
    ObjBase(), code(code0), parent(parent0) {
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(code + " element cannot be constructed from a vector of the provided type."));
  }
  
  //! \brief Copy element specific members from another instance.
  //! \param[in] rhs Element to copy members from.
  //! \return true if successful, false otherwise.
  bool copy_members(const ObjElement* rhs) {
    YGGDRASIL_RAPIDJSON_ASSERT(code == rhs->code);
    YGGDRASIL_RAPIDJSON_ASSERT(parent == rhs->parent);
    return (code == rhs->code && parent == rhs->parent);
  }
  //! \brief Create a copy of the element.
  //! \return Copied element.
  virtual ObjElement* copy() const = 0;
  //! \brief Check if the element is a group of elements.
  //! \return true if the element is a group.
  virtual bool is_group() const { return false; }
  //! \brief Assign values to a vector from a pointer to an array.
  //! \tparam T1 Type of elements in the destination vector.
  //! \tparam T2 Type of elements in the source array.
  //! \param[in, out] dst Vector to assign values to.
  //! \param src Pointer to the source array.
  //! \param N Number of elements in the source array.
  template <typename T1, typename T2>
  void assign_values(std::vector<T1>& dst, const T2* src, const size_t &N)
  { assign_values(dst, std::vector<T2>(src, src+N)); }
  //! \brief Assign values to a vector from stack array.
  //! \tparam T1 Type of elements in the destination vector.
  //! \tparam T2 Type of elements in the source array.
  //! \param[in, out] dst Vector to assign values to.
  //! \param src Source array.
  template <typename T1, typename T2, size_t N>
  void assign_values(std::vector<T1>& dst, const T2 (&src)[N])
  { assign_values(dst, std::vector<T2>(src, src+N)); }
  //! \brief Assign values to a vector from a vector.
  //! \tparam T1 Type of elements in the destination vector.
  //! \tparam T2 Type of elements in the source vector.
  //! \param[in, out] dst Vector to assign values to.
  //! \param src Source vector.
  template <typename T1, typename T2>
  void assign_values(std::vector<T1>& dst, const std::vector<T2> &src,
		     YGGDRASIL_RAPIDJSON_ENABLEIF((
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,ObjRef>,
       COMPATIBLE_WITH_INT(T2)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,double>,
       COMPATIBLE_WITH_FLOAT(T2)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,ObjRefVertex>,
       COMPATIBLE_WITH_VERT(T2)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,std::string>,
       COMPATIBLE_WITH_TYPE(T2, std::string)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,uint16_t>,
       COMPATIBLE_WITH_UINT(T2)>,
       COMPATIBLE_WITH_TYPE(T1, T2)> > > > >))) {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    for (auto it = src.begin(); it != src.end(); it++)
      dst.emplace_back((T1)(*it));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    for (typename std::vector<T2>::const_iterator it = src.begin(); it != src.end(); it++)
      dst.push_back((T1)(*it));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  //! \brief Raise an error if the types are not compatible.
  template <typename T1, typename T2>
  void assign_values(std::vector<T1>&, const std::vector<T2> &,
		     YGGDRASIL_RAPIDJSON_DISABLEIF((
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,ObjRef>,
       COMPATIBLE_WITH_INT(T2)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,double>,
       COMPATIBLE_WITH_FLOAT(T2)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,ObjRefVertex>,
       COMPATIBLE_WITH_VERT(T2)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,std::string>,
       COMPATIBLE_WITH_TYPE(T2, std::string)>,
       internal::OrExpr<internal::AndExpr<internal::IsSame<T1,uint16_t>,
       COMPATIBLE_WITH_UINT(T2)>,
       COMPATIBLE_WITH_TYPE(T1, T2)> > > > >))) {
    ASSERT_COMPATIBLE(T1, T2);
  }
  //! \brief Assign element members from an array of values stored in another
  //!   class member during a previous call to assign_values.
  //! return true if successful, false otherwise.
  virtual bool from_values() { return true; } // Do nothing, keep values in vector
  //! \brief Read element members from an input stream.
  //! \param in Input stream.
  //! \param dont_descend If true, subelements will not be read from the
  //!   input stream.
  //! \return true if successful, false otherwise.
  virtual bool read_values(std::istream& in, const bool& dont_descend=false) {
    (void)dont_descend;
    size_t i = 0;
    for (ObjPropertiesMap::iterator it = this->properties.begin();
	 it != this->properties.end(); it++, i++) {
      if (!it->mem) return false;
      if (!this->has_property(it->first, true, false, NULL)) continue;
      if (!it->read(in)) return false;
      if (it->missing) break;
    }
    // TOOD: Set meta?
    return true;
  };
  //! \brief Write element member to an output stream.
  //! \param out Output stream.
  //! \return true if successful, false otherwise.
  virtual bool write_values(std::ostream& out) const {
    size_t i = 0;
    bool first = true;
    for (ObjPropertiesMap::const_iterator it = this->properties.begin();
	 it != this->properties.end(); it++, i++) {
      if (!this->has_property(it->first, true, false, NULL)) continue;
      if (!it->mem) return false;
      if (!it->write(out, !first)) return false;
      first = false;
    }
    return true;
  }
  //! \brief Check if another element is equivalent.
  //! \param rhs0 Element to compare.
  //! \return true if rhs is equivalent.
  virtual bool is_equal(const ObjElement* rhs0) const {
    if (rhs0->code != this->code) return false;
    if (properties.size() != rhs0->properties.size()) return false;
    ObjPropertiesMap::const_iterator rit = rhs0->properties.begin();
    for (ObjPropertiesMap::const_iterator lit = this->properties.begin();
	 lit != this->properties.end(); lit++, rit++) {
      bool present = this->has_property(lit->first, true, false, NULL);
      if (present != rhs0->has_property(lit->first, true, false, NULL))
	return false;
      if (!present) continue;
      if (*lit != *rit) return false;
    }
    return true;
}
  //! \brief Set meta properties that control which properties are defined.
  //! \param N Number of properties provided.
  //! \return true if successful, false otherwise.
  virtual bool set_meta_properties(const size_t) { return true; }
  //! \brief Set properties from an array of values.
  //! \param arr Property values.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool set_properties(const std::vector<T>& arr) {
    if (!set_meta_properties(arr.size())) return false;
    int minV = min_values();
    int maxV = max_values();
    if ((minV >= 0 && arr.size() < (size_t)minV) ||
	(maxV >= 0 && arr.size() > (size_t)maxV)) return false;
    typename std::vector<T>::const_iterator v = arr.begin();
    size_t i = 0;
    for (ObjPropertiesMap::const_iterator it = this->properties.begin();
	 it != this->properties.end(); it++, i++) {
      if (!this->has_property(it->first, true, false, NULL)) continue;
      if (v == arr.end())
	return (it->second & ObjTypeOpt);
      if (it->second & ObjTypeList) {
	std::vector<T> sub_arr(v, arr.end());
	if (!set_property(i, sub_arr)) return false;
      } else {
	if (!set_property(i, *v)) return false;
      }
      v++;
    }
    return is_valid();
  }
#define DUMMY_MANAGE_PROPERTY_(type, typeName)				\
  /*! \brief Set an element property. */				\
  /*! \param i index of the property to set. */				\
  /*! \param new_value Value to assign to the property. */		\
  /*! \return true if successful, false otherwise. */			\
  bool set_property_ ## typeName(size_t i, const type new_value) {	\
    if (i >= this->properties.size()) return false;				\
    ObjPropertiesMap::iterator it = this->properties.begin() + (int)i;	\
    if (_type_compatible_ ## typeName(it->second, true) &&		\
	it->set(new_value)) return true;				\
    std::cerr << "set_property for " << #typeName << "s not defined for " << it->first << " property of " << code << "elements." << std::endl; \
    return false;							\
  }									\
  /*! \brief Set an element property array. */				\
  /*! \param i index of the property to set. */				\
  /*! \param new_values Array of values to assign to the property. */	\
  /*! \return true if successful, false otherwise. */			\
  bool set_property_array_ ## typeName(size_t i, const std::vector<type> new_values) { \
    if (i >= this->properties.size()) return false;				\
    ObjPropertiesMap::iterator it = this->properties.begin() + (int)i;	\
    if (_type_compatible_ ## typeName(it->second, true) &&		\
	it->set(new_values)) return true;				\
    std::cerr << "set_property for array of " << #typeName << "s not defined for " << it->first << " property of " << code << "elements." << std::endl; \
    return false;							\
  }									\
  /*! \brief Get an element property. */				\
  /*! \param i index of the property to get. */				\
  /*! \param out Existing memory to copy property to. */		\
  /*! \return true if successful, false otherwise. */			\
  bool get_property_ ## typeName(size_t i, type& out) const {		\
    if (i >= this->properties.size()) return false;				\
    ObjPropertiesMap::const_iterator it = this->properties.begin() + (int)i;	\
    if (_type_compatible_ ## typeName(it->second, true) &&		\
	it->get(out)) return true;					\
    std::cerr << "get_property for " << #typeName << "s not defined for " << it->first << " property of " << code << "elements." << std::endl; \
    return false;							\
  }									\
  /*! \brief Get an element property array. */				\
  /*! \param i index of the property to get. */				\
  /*! \param out Existing array to add property values to. */		\
  /*! \return true if successful, false otherwise. */			\
  bool get_property_array_ ## typeName(size_t i, std::vector<type>& out) const { \
    if (i >= this->properties.size()) return false;				\
    ObjPropertiesMap::const_iterator it = this->properties.begin() + (int)i;	\
    if (_type_compatible_ ## typeName(it->second, true) &&		\
	it->get(out)) return true;					\
    std::cerr << "get_property for array of " << #typeName << "s not defined for " << it->first << " property of " << code << "elements." << std::endl; \
    return false;							\
  }
  
  DUMMY_MANAGE_PROPERTY_(double, double)
  DUMMY_MANAGE_PROPERTY_(int, int)
  DUMMY_MANAGE_PROPERTY_(std::string, string)
  
#undef DUMMY_MANAGE_PROPERTY_
  
  //! \brief Get properties into an array of values.
  //! \param[out] arr Vector to add properties to.
  //! \param skipColors If true, color properties will not be included.
  //! \param dec If true and a property is an index, it will be decremented.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool get_properties(std::vector<T>& arr, bool skipColors=false, bool dec=false) const {
    size_t i = 0, count = arr.size();
    arr.resize(count + this->size(skipColors));
    ObjPropertiesMap::const_iterator last = this->properties.begin() + (int)(this->properties.size() - 1);
    for (ObjPropertiesMap::const_iterator it = this->properties.begin();
	 it != this->properties.end(); it++, i++) {
      if (!this->has_property(it->first, true, skipColors, NULL))
	continue;
      // TODO: Automatically cast ints to double when T is double and property
      //   has integer type
      if (it->second & ObjTypeList) {
	if (it != last) return false;
	arr.resize(count);  // Trim extra values so that get_property appends
	if (!get_property(i, arr, dec)) return false;
      } else {
	if (count >= arr.size()) return false;
	if (!get_property(i, arr[count], dec)) return false;
      }
      count++;
    }
    return true;
  }
  
  //! \brief Get element values as an array of strings.
  //! \return Array of string values.
  std::vector<std::string> get_string_array(bool=false) const {
    std::vector<std::string> out;
    get_string_array(out);
    return out;
  }
  //! \brief Get element values as an array of strings.
  //! \param[out] out Array to put values in.
  void get_string_array(std::vector<std::string>& out, bool=false) const {
    YGGDRASIL_RAPIDJSON_ASSERT(!requires_double());
    if (requires_double()) return;
    get_properties(out);
  }
  //! \brief Get element values as an array of ints.
  //! \param nvert Number of vertices previously added to a Ply
  //!   object being constructed from this geometry.
  //! \param dec If true and a property is an index, it will be decremented.
  //! \return Array of int values.
  std::vector<int> get_int_array(const size_t nvert=0, bool dec=false) const {
    std::vector<int> out;
    get_int_array(out, nvert, dec);
    return out;
  }
  //! \brief Get element values as an array of ints.
  //! \param nvert Number of vertices previously added to a Ply
  //!   object being constructed from this geometry.
  //! \param dec If true and a property is an index, it will be decremented.
  //! \param[out] out Array to put values in.
  void get_int_array(std::vector<int>& out,
		     const size_t nvert=0, bool dec=false) const {
    YGGDRASIL_RAPIDJSON_ASSERT(!requires_double());
    if (requires_double()) return;
    get_properties(out, dec);
    if (nvert > 0) {
      for (size_t i = 0; i < out.size(); i++) {
	if (out[i] < 0)
	  out[i] = (int)(nvert) + out[i] + 1;
	out[i]--;
      }
    }
  }
  //! \brief Get element values as an array of doubles.
  //! \param skipColors If true, color data will not be included.
  //! \param dec If true and a property is an index, it will be decremented.
  //! \return Array of double values.
  std::vector<double> get_double_array(bool skipColors=false, bool dec=false) const {
    std::vector<double> out;
    get_double_array(out, skipColors, dec);
    return out;
  }
  //! \brief Get element values as an array of doubles.
  //! \param skipColors If true, color data will not be included.
  //! \param dec If true and a property is an index, it will be decremented.
  //! \param[out] out Array to put values in.
  void get_double_array(std::vector<double>& out,
			bool skipColors=false, bool dec=false) const {
    YGGDRASIL_RAPIDJSON_ASSERT(requires_double());
    get_properties(out, skipColors, dec);
  }
  //! \brief Add a property sub-element to this element. This is only valid
  //!   for element types that can contain a variable number of sub-elements.
  //! \return true if successfull, false otherwise.
  //! \return Newly added property element.
  virtual bool add_subelement() {
    std::cerr << "add_subelement not implemented for this type (code = " << code << ")" << std::endl;
    return false;
  }
  //! \brief Get the most recently added sub-element. This is only valid for
  //!   element types that can contain a variable number of sub-elements.
  //! \return Newly added property element.
  //! \param[out] temp Pointer to boolean that signals if the returned
  //!   pointer is a temporary wrapper. If true, the returned pointer
  //!   should be cleaned up by the user.
  virtual const ObjPropertyElement* last_subelement(bool* temp = NULL) const {
    return const_cast<ObjElement&>(*this).last_subelement(temp);
  }
  //! \brief Get the most recently added sub-element. This is only valid for
  //!   element types that can contain a variable number of sub-elements.
  //! \return Newly added property element.
  //! \param[out] temp Pointer to boolean that signals if the returned
  //!   pointer is a temporary wrapper. If true, the returned pointer
  //!   should be cleaned up by the user.
  virtual ObjPropertyElement* last_subelement(bool* = NULL) {
    std::cerr << "last_subelement not implemented for this type (code = " << code << ")" << std::endl;
    return NULL;
  }
  //! \brief Set a subelement property for the most recently added sub-element.
  //!   This is only valid for element types that contain a variable number of
  //!   subelements.
  //! \param name Name of the property to set.
  //! \param value Value to set the property to.
  //! \param inc If true and the property is an index, it will be incremented.
  //! \return true if succesful, false otherwise.
  template<typename T>
  bool set_subelement_property(const std::string name, const T& value, bool inc=false) {
    bool temp = false;
    ObjPropertyElement* last = this->last_subelement(&temp);
    if (!last) return false;
    bool flag = last->set_property(name, value, inc);
    // if (temp) delete last;
    return flag;
  }
  //! \brief Get a subelement property for the most recently added sub-element.
  //!   This is only valid for element types that contain a variable number of
  //!   subelements.
  //! \param name Name of the property to get.
  //! \param value Reference to memory where the value should be stored.
  //! \param dec If true and the property is an index, it will be decremented.
  //! \return true if succesful, false otherwise.
  template<typename T>
  bool get_subelement_property(const std::string name, T& value, bool dec=false) const {
    bool temp = false;
    const ObjPropertyElement* last = this->last_subelement(&temp);
    if (!last) return false;
    bool flag = last->get_property(name, value, dec);
    // if (temp) delete last;
    return flag;
  }
  //! \brief Determine if the specified property is a vector.
  //! \param name Property name.
  //! \return true if it is a vector, false otherwise.
  bool is_vector(const std::string name) const {
    ObjPropertiesMap::const_iterator it = this->properties.begin();
    for (; it != this->properties.end(); it++) {
      if (it->first == name) break;
    }
    return (it != this->properties.end() && it->second & ObjTypeList);
  }
  //! \brief Determine if any of the elements properties require doubles.
  //! \return true if it requires doubles, false otherwise.
  bool requires_double() const {
    for (ObjPropertiesMap::const_iterator it = this->properties.begin();
	 it != this->properties.end(); it++)
      if ((it->second & (ObjTypeFloat | ObjTypeCurve | ObjTypeSurface))
	  && this->has_property(it->first, true, false, NULL))
	return true;
    return false;
  }
  //! \brief Determine if the specified property requires doubles.
  //! \param name Property to check.
  //! \return true if it requires doubles, false otherwise.
  bool requires_double(const std::string name) const {
    ObjPropertiesMap::const_iterator it = this->properties.begin();
    for (; it != this->properties.end(); it++) {
      if (it->first == name) break;
    }
    return (it != this->properties.end() &&
	    it->second & (ObjTypeFloat | ObjTypeCurve | ObjTypeSurface));
  }
  //! \brief Determine if a structure is valid and there are vertexes for
  //!   all those referenced in faces and edges.
  //! \param idx Map containing the number of preceeding elements of each
  //!   type.
  //! \return true if the structure is valid, false otherwise.
  virtual bool is_valid_idx(std::map<std::string,size_t>& idx) const
  { (void)idx; return this->is_valid(); }
  //! \brief Read elements from an input stream.
  //! \param in Input stream.
  //! \param dont_descend If true, groups will not read elements.
  //! \return true if successful, false otherwise.
  virtual bool read(std::istream &in, const bool& dont_descend=false) {
    return this->read_values(in, dont_descend);
  }
  //! \brief Read element members from an input stream into a vector.
  //! \param in Input stream.
  //! \param values Vector to store read values in.
  //! \return true if successful, false otherwise.
  template <typename T>
  bool read_values(std::istream &in, std::vector<T> &values,
		   YGGDRASIL_RAPIDJSON_DISABLEIF((COMPATIBLE_WITH_TYPE(T, std::string)))) {
    T x = 0;
    while ((in.peek() != '\n') && (in >> x))
      values.push_back(x);
    return true;
  }
  //! \brief Read element members from an input stream into a vector.
  //! \param in Input stream.
  //! \param values Vector to store read values in.
  //! \return true if successful, false otherwise.
  bool read_values(std::istream &in, std::vector<std::string> &values) {
    std::string x = "";
    while ((in.peek() != '\n') && (in >> x))
      values.push_back(x);
    in >> std::skipws;
    return true;
  }
  //! \brief Write the element to an output stream.
  //! \param out Output stream.
  //! \return true if successful, false otherwise.
  bool write(std::ostream &out) const {
    if (!this->write_prefix(out)) return false;
    if (!this->write_values(out)) return false;
    return this->write_suffix(out);
  }
  //! \brief Write prefix before values.
  //! \param out Output stream.
  //! \return true if successful, false otherwise.
  virtual bool write_prefix(std::ostream &out) const {
    if (code != "")
      out << code << " ";
    return true;
  }
  //! \brief Write element member to an output stream from a vector.
  //! \param out Output stream.
  //! \param values Values to write.
  //! \return true if successful, false otherwise.
  template <typename T>
  bool write_values(std::ostream &out, const std::vector<T> &values) const {
    for (typename std::vector<T>::const_iterator it = values.begin(); it != values.end(); it++) {
      if (it != values.begin())
	out << " ";
      out << *it;
    }
    return true;
  }
  //! \brief Write suffix after values.
  //! \param out Output stream.
  //! \return true if successful, false otherwise.
  virtual bool write_suffix(std::ostream &out) const {
    out << std::endl;
    return true;
  }
  //! \brief Get a string representation of the element.
  //! \param[in] indent Indentation to use on each line.
  //! \return String representation.
  std::string as_string(std::string indent = "") const {
    std::string out;
    std::stringstream ss(out);
    write(ss);
    if (!indent.empty()) {
      size_t idx = 0;
      while (true) {
	idx = out.find("\n", idx);
	if (idx == std::string::npos)
	  break;
	idx++;
	out.insert(idx, indent);
	idx += indent.size();
      }
    }
    return out;
  }
  //! \brief Get the colors for an element set in array form.
  //! \param defaultValue Value to add if colors are missing.
  //! \returns The colors for the requirested type in array form.
  template<typename CT>
  std::vector<CT> get_colors_array(CT defaultValue=0) const {
    std::vector<CT> out;
    get_colors_array(out, defaultValue);
    return out;
  }
  //! \brief Get the colors for an element set in array form.
  //! \param out Array to add values to.
  //! \param defaultValue Value to add if colors are missing.
  virtual void get_colors_array(std::vector<double>&,
				double=0) const {}
  //! \brief Get the colors for an element set in array form.
  //! \param out Array to add values to.
  //! \param defaultValue Value to add if colors are missing.
  virtual void get_colors_array(std::vector<uint8_t>&,
				uint8_t=0) const {}
  //! \brief Determine if the element contains color information.
  //! \return true if there are colors, false otherwise.
  virtual bool has_colors() const { return false; }
  //! \brief Add element colors to this element.
  //! \param arr Color property values for this element.
  //! \param N Number of color properties.
  //! \return true if successful, false otherwise.
  virtual bool add_colors(const double*, SizeType) {
    return false;
  }
  //! \brief Add element colors to this element.
  //! \param arr Color property values for this element.
  //! \param N Number of color properties.
  //! \return true if successful, false otherwise.
  virtual bool add_colors(const uint8_t*, SizeType) {
    return false;
  }
  //! \brief Increase indexes to account for previous elements when appending
  //!   and element to another group.
  //! \param idx Mapping of element types and counts for those types.
  virtual void append_indexes(const std::map<std::string,size_t> idx)
  { (void)idx; }
  //! Disable copy assignment for elements.
  ObjElement& operator=(const ObjElement& other);
  //! Code indicating the type of element.
  std::string code;
  //! Pointer to the parent element class.
  const ObjGroupBase* parent;
  
  friend std::ostream & operator << (std::ostream &out, const ObjElement &p);
};

//! Write an element to an output stream.
//! \param out Output stream.
//! \param p Element.
//! \return Output stream.
inline
std::ostream & operator << (std::ostream &out, const ObjElement &p)
{ p.write(out); return out; }

//! Element grouping base class.
class ObjGroupBase : public ObjElement {
public:
  //! \brief Empty constructor.
  //! \param parent0 The element's parent group.
  ObjGroupBase(const ObjGroupBase* parent0 = NULL) :
    ObjElement(parent0), elements(), finalized(false) {}
  //! \brief Initialize an element group from an element code.
  //! \param code The element code string.
  //! \param parent0 The element's parent group.
  ObjGroupBase(const std::string& code,
	       const ObjGroupBase* parent0 = NULL) :
    ObjElement(code, parent0), elements(), finalized(false) {}
  //! \brief Initialize an element group from an element code.
  //! \param code The element code string.
  //! \param elements0 Group elements.
  //! \param parent0 The element's parent group.
  ObjGroupBase(const std::string& code,
	       const std::vector<ObjElement*> &elements0,
	       const ObjGroupBase* parent0 = NULL) :
    ObjElement(code, parent0), elements(), finalized(false) {
    assign_values(elements, elements0);
  }
  GENERIC_CONSTRUCTOR_COPY(ObjGroupBase, ObjElement, SINGLE_ARG(, elements(), finalized(false)), SINGLE_ARG());
  ~ObjGroupBase() {
    for (std::vector<ObjElement*>::iterator it = elements.begin(); it != elements.end(); it++)
      delete *it;
    elements.resize(0);
  }
  //! \brief Copy element specific members from another instance.
  //! \param[in] rhs Element to copy members from.
  //! \return true if successful, false otherwise.
  bool copy_members(const ObjGroupBase* rhs) {
    finalized = rhs->finalized;
    for (std::vector<ObjElement*>::const_iterator it = rhs->elements.begin(); it != rhs->elements.end(); it++)
      elements.push_back((*it)->copy());
    return true;
  }
  //! \brief Check if the element is a group of elements.
  //! \return true if the element is a group.
  bool is_group() const OVERRIDE_CXX11 { return true; }
  //! \brief Finalize the group.
  void finalize() { finalized = true; }
  //! \copydoc ObjElement::read_values
  bool read_values(std::istream &in, const bool& dont_descend=false) OVERRIDE_CXX11 {
    if (!this->read_group_header(in))  return false;
    if (!dont_descend) {
      while (!finalized) {
	ObjElement* x = NULL;
	if (!read_obj_element(in, this, true, x)) return false;
	if (!x) return false;
	if (x != this)
	  add_element(x);
      }
    }
    return true;
  }
  //! \brief Read group header information.
  //! \param in Input stream.
  virtual bool read_group_header(std::istream &) { return true; }
  //! \brief Write group header information.
  //! \param out Output stream.
  virtual bool write_group_header(std::ostream & out) const {
    out << std::endl;
    return true;
  }
  //! \copydoc ObjElement::write_values
  bool write_values(std::ostream &out) const OVERRIDE_CXX11 {
    if (!this->write_group_header(out)) return false;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if (!(*it)->write(out)) return false;
    }
    return this->write_group_footer(out);
  }
  //! \brief Write group footer information.
  //! \param out Output stream.
  virtual bool write_group_footer(std::ostream &) const { return true; }
  //! \copydoc ObjElement::is_equal
  bool is_equal(const ObjElement* rhs0) const OVERRIDE_CXX11 {
    if (rhs0->code != this->code)
      return false;
    const ObjGroupBase* lhs = this;
    const ObjGroupBase* rhs = dynamic_cast<const ObjGroupBase*>(rhs0);
    if (lhs->elements.size() != rhs->elements.size()) return false;
    for (std::vector<ObjElement*>::const_iterator lit = lhs->elements.begin(), rit = rhs->elements.begin();
	 lit != lhs->elements.end(); lit++, rit++)
      if (!((*lit)->is_equal(*rit))) return false;
    return true;
  }
  //! \brief Get the number of elements of a certain type.
  //! \param[in] Name of the element type to count.
  //! \return Number of elements of the requested type.
  size_t count_elements(const std::string name) const {
    std::string name2 = obj_alias2base(name);
    size_t out = 0;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code == name2)
	out++;
    }
    return out;
  }
  //! \brief Get a list of unique element types in the group.
  //! \return Unique element types.
  std::vector<std::string> element_types() const {
    std::set<std::string> unique_names;
    std::vector<std::string> out;
    size_t prev_size = 0;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin();
	 it != elements.end(); it++) {
      unique_names.insert((*it)->code);
      if (unique_names.size() > prev_size) {
	out.push_back((*it)->code);
	prev_size++;
      }
    }
    return out;
  }
  //! \brief Get a mapping of element types in the group and counts of that
  //!   type of element.
  //! \return Map between element type and count.
  std::map<std::string,size_t> element_counts() const {
    std::map<std::string,size_t> idx;
    element_counts(idx, NULL);
    return idx;
  }
  void element_counts(std::map<std::string,size_t>& idx,
		      const ObjGroupBase* stop=NULL) const {
    if (this->parent && stop != this->parent)
      this->parent->element_counts(idx, this);
    for (std::vector<ObjElement*>::const_iterator it = elements.begin();
	 it != elements.end(); it++) {
      if (stop && stop == *it) break;
      if (idx.find((*it)->code) == idx.end())
	idx[(*it)->code] = 0;
      idx[(*it)->code]++;
      if ((*it)->is_group())
	(dynamic_cast<ObjGroupBase*>(*it))->element_counts(idx, this);
    }
  }
  //! \copydoc ObjElement::is_valid_idx
  bool is_valid_idx(std::map<std::string,size_t>& idx) const OVERRIDE_CXX11 {
    for (std::vector<ObjElement*>::const_iterator it = elements.begin();
	 it != elements.end(); it++) {
      if (!(*it)->is_valid_idx(idx)) return false;
      std::map<std::string,size_t>::iterator x = idx.find((*it)->code);
      if (x == idx.end()) {
	idx[(*it)->code] = 0;
	x = idx.find((*it)->code);
      }
      x->second++;
    }
    return true;
  }
  //! \brief Append elements from another group to this one.
  //! \param rhs Group to append elements from.
  void append(const ObjGroupBase* rhs) {
    std::map<std::string,size_t> idx = element_counts();
    for (std::vector<ObjElement*>::const_iterator rit = rhs->elements.begin();
	 rit != rhs->elements.end(); rit++) {
      ObjElement* cpy = copy_element(*rit);
      cpy->append_indexes(idx);
    }
  }
  //! \copydoc ObjElement::append_indexes
  void append_indexes(const std::map<std::string,size_t> idx) OVERRIDE_CXX11 {
    for (std::vector<ObjElement*>::iterator it = elements.begin(); it != elements.end(); it++)
      (*it)->append_indexes(idx);
  }
  //! \brief Determine if the specified element type requires doubles.
  //! \param name Element type to check.
  //! \return true if it requires doubles, false otherwise.
  bool requires_double(const std::string name) const {
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code != name) continue;
      if ((*it)->is_group()) {
	if ((dynamic_cast<ObjGroupBase*>(*it))->requires_double(name))
	  return true;
      } else {
	if ((*it)->requires_double()) return true;
      }
    }
    return false;
  }
  //! \brief Determine the maximum size of elements of a certain type.
  //! \param name Name of the element set to get the size of.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \return Maximum element size.
  size_t max_size(const std::string& name, bool skipColors=false) const {
    std::string name2 = obj_alias2base(name);
    size_t maxSize = 0;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code != name2) continue;
      if ((*it)->is_group())
	maxSize = (std::max)(maxSize, (dynamic_cast<ObjGroupBase*>(*it))->max_size(name2, skipColors));
      else
	maxSize = (std::max)(maxSize, (*it)->size(skipColors));
    }
    return maxSize;
  }
  //! \brief Get an element set in an array form.
  //! \param name Name of the element set to get.
  //! \param[out] out The element set of the requested type in array form.
  //! \param minSize Minimum number of values to add for each element.
  //! \param defaultValue Value to pad with for elements with fewer than
  //!   minSize values.
  //! \param dec If true and a property is an index, it will be decremented.
  void get_int_array(const std::string& name,
		     std::vector<int>& out,
		     const size_t minSize,
		     int defaultValue=-1,
		     bool dec=false) const {
    std::string name2 = obj_alias2base(name);
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code != name2) continue;
      if ((*it)->is_group()) {
	dynamic_cast<ObjGroupBase*>(*it)->get_int_array(name2, out, minSize,
							defaultValue, dec);
      } else {
	size_t before = out.size();
	(*it)->get_int_array(out, 0, dec);
	for (size_t i = 0; i < (minSize - (out.size() - before)); i++)
	  out.push_back(defaultValue);
      }
    }
  }
  //! \brief Get an element set in an array form.
  //! \param name Name of the element set to get.
  //! \param[out] out The element set of the requested type in array form.
  //! \param minSize Minimum number of values to add for each element.
  //! \param defaultValue Value to pad with for elements with fewer than
  //!   minSize values.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \param dec If true and a property is an index, it will be decremented.
  void get_double_array(const std::string& name,
			std::vector<double>& out,
			const size_t minSize,
			double defaultValue=NAN,
			bool skipColors=false,
			bool dec=false) const {
    std::string name2 = obj_alias2base(name);
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code != name2) continue;
      if ((*it)->is_group()) {
	dynamic_cast<ObjGroupBase*>(*it)->get_double_array(name2, out, minSize,
							   defaultValue,
							   skipColors, dec);
      } else {
	size_t before = out.size();
	(*it)->get_double_array(out, skipColors, dec);
	for (size_t i = 0; i < (minSize - (out.size() - before)); i++)
	  out.push_back(defaultValue);
      }
    }
  }
  //! Vector of elements in the group.
  std::vector<ObjElement*> elements;
  //! True if the group has been finalized.
  bool finalized;

  // ELEMENT METHODS
  
  //! \brief Find the last element of a given type.
  //! \param code Code of element to find.
  const ObjElement* last_element(const std::string& code0) const {
    for (std::vector<ObjElement*>::const_reverse_iterator it = elements.rbegin(); it != elements.rend(); it++)
      if ((*it)->code == code0)
	return *it;
    return NULL;
  }
  //! \brief End a group.
  //! \return true if successful, false otherwise.
  virtual bool end_group() {
    if (this->finalized) return false;
    ObjElement* last = elements.back();
    if (last->is_group()) {
      ObjGroupBase* last_grp = dynamic_cast<ObjGroupBase*>(last);
      if (!(last_grp->finalized)) {
	return last_grp->end_group();
      }
    }
    return false;
  }
  //! \brief Add an element to the geometry.
  //! \param x New element.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  ObjElement* add_element(ObjElement* x, bool inc = false) {
    YGGDRASIL_RAPIDJSON_ASSERT(!finalized);
    if (elements.size() > 0) {
      ObjElement* last = elements.back();
      if (last->is_group()) {
	ObjGroupBase* last_grp = dynamic_cast<ObjGroupBase*>(last);
	if (!(last_grp->finalized)) {
	  if ((x != NULL) && (last_grp->code == "g") && (x->code == "g"))
	    last_grp->finalize();
	  else
	    return last_grp->add_element(x, inc);
	}
      }
    }
    if (x == NULL) {
      finalize();
    } else if (this->code == "g" && x->code == "g") {
      finalize();
      const_cast<ObjGroupBase*>(this->parent)->add_element(x, inc);
    } else {
      x->parent = this;
      if (inc)
	x->_inc_properties();
      elements.push_back(x);
    }
    return x;
  }
  //! \brief Add an element to the geometry by copying an existing element.
  //! \param x New element.
  //! \return New element.
  ObjElement* copy_element(const ObjElement* x);
  //! \brief Add an empty element to the geometry.
  //! \param name Name of the type of element being added.
  //! \return New element.
  ObjElement* add_element(std::string name);
  //! \brief Add an element to the geometry from a C++ vector of values.
  //! \tparam T Type of value in the values vector.
  //! \param name Name of the type of element being added.
  //! \param values Vector of values defining the element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  template <typename T>
  ObjElement* add_element(std::string name, const std::vector<T> &values,
			  const T* ignore = 0, bool inc = false);
  //! \brief Add an element to the geometry from a C array of values.
  //! \tparam T Type of value in the values array.
  //! \tparam N Number of elements in the values array.
  //! \param name Name of the type of element being added.
  //! \param values Array of values defining the element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  template <typename T, size_t N>
  ObjElement* add_element(std::string name, const T (&values)[N],
			  const T* ignore = 0, bool inc = false,
			  YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_ANY(T)))) {
    return add_element(name, std::vector<T>(values, values+N), ignore, inc);
  }
  //! \brief Add an element to the geometry from a C array of values.
  //! \tparam T Type of value in the values array.
  //! \param name Name of the type of element being added.
  //! \param values Array of values defining the element.
  //! \param N Number of elements in the values array.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  template <typename T>
  ObjElement* add_element(std::string name, const T* values, size_t N,
			  const T* ignore = 0, bool inc = false,
			  YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_ANY(T)))) {
    return add_element(name, std::vector<T>(values, values+N), ignore, inc);
  }
  // template <size_t N>
  // ObjElement* ObjGroupBase::add_element(std::string name, const char* values[N]) {
  // std::vector<std::string> values_v;
  // for (size_t i = 0; i < N; i++)
  // values_v.push_back(std::string(values[i]));
  // return add_element(name, values_v);
  // };

  // Curve element methods
  //! \brief Add an element to the geometry.
  //! \tparam T Type of value in the values vector.
  //! \param u0 1st element parameter.
  //! \param u1 2nd element parameter.
  //! \param values Vector of additional values defining the element.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  template <typename T>
  ObjElement* add_element(const std::string name,
			  const double& u0, const double& u1,
			  const std::vector<T> &values, bool inc = false);
  //! \brief Add an element to the geometry from a C array of values.
  //! \tparam T Type of value in the values array.
  //! \tparam N Number of elements in the values array.
  //! \param name Name of the type of element being added.
  //! \param u0 1st element parameter.
  //! \param u1 2nd element parameter.
  //! \param values Array of values defining the element.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  template <typename T, size_t N>
  ObjElement* add_element(std::string name,
			  const double& u0, const double& u1,
			  const T (&values)[N], bool inc = false) {
    return add_element(name, u0, u1, std::vector<T>(values, values+N), inc);
  }

  // Surface element methods
  //! \brief Add an element to the geometry.
  //! \tparam T Type of value in the values vector.
  //! \param u0 1st element parameter.
  //! \param u1 2nd element parameter.
  //! \param u2 3rd element parameter.
  //! \param u3 4th element parameter.
  //! \param values Vector of additional values defining the element.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  template <typename T>
  ObjElement* add_element(const std::string name,
			  const double& u0, const double& u1,
			  const double& u2, const double& u3,
			  const std::vector<T> &values, bool inc = false);
  //! \brief Add an element to the geometry from a C array of values.
  //! \tparam T Type of value in the values array.
  //! \tparam N Number of elements in the values array.
  //! \param name Name of the type of element being added.
  //! \param u0 1st element parameter.
  //! \param u1 2nd element parameter.
  //! \param u2 3rd element parameter.
  //! \param u3 4th element parameter.
  //! \param values Array of values defining the element.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  template <typename T, size_t N>
  ObjElement* add_element(std::string name,
			  const double& u0, const double& u1,
			  const double& u2, const double& u3,
			  const T (&values)[N], bool inc = false) {
    return add_element(name, u0, u1, u2, u3, std::vector<T>(values, values+N), inc);
  }

  // Parameter element methods
  //! \brief Add a parameter element to the geometry.
  //! \tparam T Type of value in the values vector.
  //! \param name Name of the type of element being added.
  //! \param direction Name of the parameter direction.
  //! \param values Vector of additional values defining the element.
  //! \return New element.
  template <typename T>
  ObjElement* add_element(std::string name, std::string direction,
			  const std::vector<T> &values);
  //! \brief Add a parameter element to the geometry.
  //! \tparam T Type of value in the values array.
  //! \tparam N Number of elements in the values array.
  //! \param name Name of the type of element being added.
  //! \param direction Name of the parameter direction.
  //! \param values Array of values defining the element. 
  //! \return New element.
  template <typename T, size_t N>
  ObjElement* add_element(std::string name, std::string direction,
			  const T (&values)[N]) {
    return add_element(name, direction, std::vector<T>(values, values+N));
  }

  //! \brief Add a scalar group element.
  //! \param name Name of the type of element being added.
  //! \param value Scalar value.
  //! \return New element.
  ObjElement* add_element(std::string name, const char* value) {
    std::string s(value);
    return add_element(name, s);
  }

  //! \brief Add a scalar group element.
  //! \tparam T Type of value.
  //! \param name Name of the type of element being added.
  //! \param value Scalar value.
  //! \return New element.
  template<typename T>
  YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<internal::IsPointer<T>,
			      internal::IsSame<T,std::string> >), (ObjElement*))
    add_element(std::string name, const T& value);
  
  //! \brief Add a scalar string group element.
  //! \param name Name of the type of element being added.
  //! \param value Scalar value.
  //! \return New element.
  ObjElement* add_element(std::string name, const std::string& value);

  //! \brief Add a merging group element.
  //! \tparam T Type of value.
  //! \param name Name of the type of element being added.
  //! \param value Scalar value.
  //! \param resolution Merge resolution.
  //! \param inc If true and a property is an index, it will be incremented.
  //! \return New element.
  ObjElement* add_element(std::string name, const int& value, const double& resolution, bool inc = false);
  //! \brief Add a merging group element.
  //! \param name Name of the type of element being added.
  //! \param value Scalar value.
  //! \param resolution Merge resolution.
  //! \return New element.
  ObjElement* add_element(std::string name, const std::string& value, const double& resolution);

};

//! Comment data
GENERIC_VECTOR_STRING(ObjComment, #, std::string, SINGLE_ARG(OBJ_P_(&values, "words", ObjTypeString | ObjTypeList)));

//! Vertex data
class ObjVertex : public ObjElement {
public:
  GENERIC_VECTOR_BODY_TEMP(ObjVertex, ObjElement, v,
			   SINGLE_ARG(, values(), x(0), y(0), z(0), w(-1), color()),
			   SINGLE_ARG(OBJ_P_(&x, "x", ObjTypeFloat),
				      OBJ_P_(&y, "y", ObjTypeFloat),
				      OBJ_P_(&z, "z", ObjTypeFloat),
				      OBJ_P_(&(color.r), "red", ObjTypeFloat | ObjTypeOpt),
				      OBJ_P_(&(color.g), "green", ObjTypeFloat | ObjTypeOpt),
				      OBJ_P_(&(color.b), "blue", ObjTypeFloat | ObjTypeOpt),
				      OBJ_P_(&w, "w", ObjTypeFloat | ObjTypeOpt)),
			   SINGLE_ARG(COMPATIBLE_WITH_FLOAT(T)),
			   double)
  //! Vertex coordinate in the x direction.
  double x;
  //! Vertex coordinate in the y direction.
  double y;
  //! Vertex coordinate in the z direction.
  double z;
  //! Vertex weight, negative values indicate a default weight of 1.
  double w;
  //! Vertex color.
  ObjColor color;
  
  //! \copydoc ObjElement::get_colors_array
  void get_colors_array(std::vector<double>& out,
			double defaultValue=0) const OVERRIDE_CXX11 {
    if (color.is_set) {
      out.push_back(static_cast<double>(color.r));
      out.push_back(static_cast<double>(color.g));
      out.push_back(static_cast<double>(color.b));
    } else {
      out.push_back(defaultValue);
      out.push_back(defaultValue);
      out.push_back(defaultValue);
    }
  }
  //! \copydoc ObjElement::get_colors_array
  void get_colors_array(std::vector<uint8_t>& out,
			uint8_t defaultValue=0) const OVERRIDE_CXX11 {
    if (color.is_set) {
      out.push_back(static_cast<uint8_t>(color.r * 255.0));
      out.push_back(static_cast<uint8_t>(color.g * 255.0));
      out.push_back(static_cast<uint8_t>(color.b * 255.0));
    } else {
      out.push_back(defaultValue);
      out.push_back(defaultValue);
      out.push_back(defaultValue);
    }
  }
  //! \copydoc ObjElement::has_property
  bool has_property(const std::string name, bool dontCheckOrder=false, bool skipColors=false, size_t* idx=NULL) const  OVERRIDE_CXX11 {
    return (ObjElement::has_property(name, dontCheckOrder, skipColors, idx) &&
	    !(((skipColors || !color.is_set)
	       && (name == "red" || name == "green" || name == "blue")) ||
	      (w < 0 && name == "w")));
  }
  //! \copydoc ObjElement::set_meta_properties
  bool set_meta_properties(const size_t N) OVERRIDE_CXX11 {
    if (N == 3) {
      w = -1;
      color.is_set = false;
    } else if (N == 4) {
      w = 0;
      color.is_set = false;
    } else if (N == 6) {
      w = -1;
      color.is_set = true;
    } else if (N == 7) {
      w = 0;
      color.is_set = true;
    } else {
      return false;
    }
    return true;
  }
  //! \copydoc ObjElement::has_colors
  bool has_colors() const OVERRIDE_CXX11 {
    return color.is_set;
  }
  //! \brief Add element colors to this element.
  //! \param arr Color property values for this element.
  //! \param N Number of color properties.
  //! \return true if successful, false otherwise.
  bool add_colors(const double* arr, SizeType N) OVERRIDE_CXX11 {
    if (N == 3) {
      color.is_set = true;
      color.r = arr[0];
      color.g = arr[1];
      color.b = arr[2];
      return true;
    }
    return false;
  }
  //! \brief Add element colors to this element.
  //! \param arr Color property values for this element.
  //! \param N Number of color properties.
  //! \return true if successful, false otherwise.
  bool add_colors(const uint8_t* arr, SizeType N) OVERRIDE_CXX11 {
    if (N == 3) {
      color.is_set = true;
      color.r = ((double)(arr[0]))/255.0;
      color.g = ((double)(arr[1]))/255.0;
      color.b = ((double)(arr[2]))/255.0;
      return true;
    }
    return false;
  }
};

//! Object vertex parameter
class ObjVParameter : public ObjElement {
public:
  GENERIC_VECTOR_BODY_TEMP(ObjVParameter, ObjElement, vp,
			   SINGLE_ARG(, values(), u(0), v(0), w(-1)),
			   SINGLE_ARG(OBJ_P_(&u, "u", ObjTypeFloat),
				      OBJ_P_(&v, "v", ObjTypeFloat),
				      OBJ_P_(&w, "w", ObjTypeFloat | ObjTypeOpt)),
			   SINGLE_ARG(COMPATIBLE_WITH_FLOAT(T)),
			   double)
  //! Parameter value in first dimension.
  double u;
  //! Parameter value in second dimension.
  double v;
  //! Parameter weight, negative values indicate a default weight of 1.
  double w;
  
  //! \copydoc ObjElement::has_property
  bool has_property(const std::string name, bool dontCheckOrder=false, bool skipColors=false, size_t* idx=NULL) const  OVERRIDE_CXX11 {
    return (ObjElement::has_property(name, dontCheckOrder, skipColors, idx) &&
	    (w >= 0 || name != "w"));
  }
  //! \copydoc ObjElement::set_meta_properties
  bool set_meta_properties(const size_t N) OVERRIDE_CXX11 {
    if (N == 2)
      w = -1;
    else if (N == 3)
      w = 0;
    else
      return false;
    return true;
  }
};

//! Vertex normal element.
class ObjVNormal : public ObjElement {
public:
  GENERIC_VECTOR_BODY_TEMP(ObjVNormal, ObjElement, vn,
			   SINGLE_ARG(, values(), i(0), j(0), k(0)),
			   SINGLE_ARG(OBJ_P_(&i, "i", ObjTypeFloat),
				      OBJ_P_(&j, "j", ObjTypeFloat),
				      OBJ_P_(&k, "k", ObjTypeFloat)),
			   SINGLE_ARG(COMPATIBLE_WITH_FLOAT(T)),
			   double)
  //! Normal vector in the x direction.
  double i;
  //! Normal vector in the y direction.
  double j;
  //! Normal vector in the z direction.
  double k;
  
  //! \copydoc ObjElement::set_meta_properties
  bool set_meta_properties(const size_t N) OVERRIDE_CXX11 {
    return (N == 3);
  }
};

//! Texture vertex element.
class ObjVTexture : public ObjElement {
public:
  GENERIC_VECTOR_BODY_TEMP(ObjVTexture, ObjElement, vt,
			   SINGLE_ARG(, values(), u(0), v(0), w(0)),
			   SINGLE_ARG(OBJ_P_(&u, "u", ObjTypeFloat),
				      OBJ_P_(&v, "v", ObjTypeFloat | ObjTypeOpt),
				      OBJ_P_(&w, "w", ObjTypeFloat | ObjTypeOpt)),
			   SINGLE_ARG(COMPATIBLE_WITH_FLOAT(T)),
			   double)
  //! Texture coordinate in the horizontal direction.
  double u;
  //! Texture coordinate in the vertical direction; a negative value indicates a default of 0.
  double v;
  //! Texture coordinate in the depth direction; a negative value indicates a default of 0.
  double w;
  
  //! \copydoc ObjElement::has_property
  bool has_property(const std::string name, bool dontCheckOrder=false, bool skipColors=false, size_t* idx=NULL) const  OVERRIDE_CXX11 {
    return (ObjElement::has_property(name, dontCheckOrder, skipColors, idx) &&
	    !((v < 0 && name == "v") || (w < 0 && name == "w")));
  }
  //! \copydoc ObjElement::set_meta_properties
  bool set_meta_properties(const size_t N) OVERRIDE_CXX11 {
    if (N == 1) {
      v = -1.0;
      w = -1.0;
    } else if (N == 2) {
      v = 0.0;
      w = -1.0;
    } else if (N == 3) {
      v = 0.0;
      w = 0.0;
    } else {
      return false;
    }
    return true;
  }
};

// Elements

//! Point element.
class ObjPoint : public ObjElement {
public:
  GENERIC_VECTOR_BODY_STORED(ObjPoint, ObjElement, p,
			     SINGLE_ARG(OBJ_P_(&values, "vertex_index", ObjTypeRef | ObjTypeList)),
			     SINGLE_ARG(COMPATIBLE_WITH_INT(T)),
			     ObjRef, int, int)
  GENERIC_CLASS_VECTOR_TYPE_IS_VALID("v", ObjRef)
};

//! Line element.
GENERIC_VECTOR_OBJREFVERTEX(ObjLine, l, 2);

//! Face element.
GENERIC_VECTOR_OBJREFVERTEX(ObjFace, f, 3);

//! Free-form element group.
class ObjFreeFormElement : public ObjGroupBase {
public:
  //! \brief Empty constructor.
  //! \param parent0 The element's parent group.
  ObjFreeFormElement(const ObjGroupBase* parent0 = NULL) :
    ObjGroupBase(parent0) { YGGDRASIL_RAPIDJSON_ASSERT(parent0); }
  //! \brief Initialize an element from an element code.
  //! \param code0 Element code.
  //! \param parent0 The element's parent group.
  ObjFreeFormElement(const std::string& code0,
		     const ObjGroupBase* parent0 = NULL) :
    ObjGroupBase(code0, parent0) { YGGDRASIL_RAPIDJSON_ASSERT(parent0); }
  //! \copydoc ObjElement::ObjElement(const ObjElement&)
  ObjFreeFormElement(const ObjFreeFormElement& rhs) : ObjGroupBase(rhs) {}
  //! \copydoc ObjGroupBase::read_group_header
  bool read_group_header(std::istream &in) OVERRIDE_CXX11 {
    return ObjElement::read_values(in);
  }
  //! \copydoc ObjGroupBase::write_group_header
  bool write_group_header(std::ostream &out) const OVERRIDE_CXX11 {
    if (!ObjElement::write_values(out)) return false;
    return ObjGroupBase::write_group_header(out);
  }
  //! \copydoc ObjGroupBase::write_group_footer
  bool write_group_footer(std::ostream &out) const OVERRIDE_CXX11 {
    out << "end";
    return true;
  }
  //! \copydoc ObjElement::is_equal
  bool is_equal(const ObjElement* rhs0) const OVERRIDE_CXX11 {
    if (!(ObjGroupBase::is_equal(rhs0))) return false;
    return ObjElement::is_equal(rhs0);
  }
  //! \copydoc ObjGroupBase::end_group
  bool end_group() OVERRIDE_CXX11 {
    if (this->finalized) return false;
    this->finalize();
    return true;
  }
};

//! Curve element.
class ObjCurve : public ObjFreeFormElement {
public:
  GENERIC_VECTOR_BODY_MIXED(ObjCurve, ObjFreeFormElement, curv,
			    SINGLE_ARG(, values(), u0(0), u1(0)),
			    SINGLE_ARG(OBJ_P_(&u0, "u0", ObjTypeFloat),
				       OBJ_P_(&u1, "u1", ObjTypeFloat),
				       OBJ_P_(&values, "vertex_index", ObjTypeRef | ObjTypeList)),
			    ObjRef, 2, -1)
  GENERIC_CLASS_VECTOR_TYPE_IS_VALID("v", ObjRef)
  //! Curve value in first parameter direction.
  double u0;
  //! Curve value in second parameter direction.
  double u1;
  
  //! \brief Initialize and element from a C++ vector of values.
  //! \param u00 Starting curve parameter value.
  //! \param u10 Ending curve parameter value.
  //! \param values0 Vector of values.
  //! \param parent0 The element's parent group.
  //! \tparam T Vector element type. Must be an integer or floating point.
  //!   Only integer values are allowed for ObjPoint elements.
  template <typename T>
  ObjCurve(const double& u00, const double& u10,
	   const std::vector<T> &values0,
	   const ObjGroupBase* parent0 = NULL,
	   YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_INT(T)))) :
    ObjFreeFormElement("curv", parent0), values(), u0(u00), u1(u10) {
    this->_init_properties();
    assign_values(values, values0);
    from_values();
  }
};

//! 2D curve element.
class ObjCurve2D : public ObjFreeFormElement {
public:
  GENERIC_VECTOR_BODY_STRICT(ObjCurve2D, ObjFreeFormElement, curv2,
			     SINGLE_ARG(OBJ_P_(&values, "parameter_index", ObjTypeRef | ObjTypeList)),
			     SINGLE_ARG(COMPATIBLE_WITH_INT(T)),
			     ObjRef, int, int,
			     2, -1)
  GENERIC_CLASS_VECTOR_TYPE_IS_VALID("vp", ObjRef)
};

//! Surface element.
class ObjSurface : public ObjFreeFormElement {
public:
  GENERIC_VECTOR_BODY_MIXED(ObjSurface, ObjFreeFormElement, surf,
			    SINGLE_ARG(, values(), s0(0), s1(0), t0(0), t1(0)),
			    SINGLE_ARG(OBJ_P_(&s0, "s0", ObjTypeFloat),
				       OBJ_P_(&s1, "s1", ObjTypeFloat),
				       OBJ_P_(&t0, "t0", ObjTypeFloat),
				       OBJ_P_(&t1, "t1", ObjTypeFloat),
				       OBJ_P_(&values, "vertex_index", (ObjTypeRef | ObjTypeVertex | ObjTypeList))),
			    ObjRefVertex, 1, -1)
  GENERIC_CLASS_VECTOR_TYPE_IS_VALID_VERTREF(1);
  //! Surface starting parameter in first dimension.
  double s0;
  //! Surface ending parameter in first dimension.
  double s1;
  //! Surface starting parameter in second dimension.
  double t0;
  //! Surface ending parameter in second dimension.
  double t1;
  //! \brief Initialize and element from a C++ vector of values.
  //! \tparam T Vector element type. Must be an integer.
  //! \param s00 Starting curve parameter value in 1st dimension.
  //! \param s10 Ending curve parameter value in 1st dimension.
  //! \param t00 Starting curve parameter value in 2nd dimension.
  //! \param t10 Ending curve parameter value in 2nd dimension.
  //! \param values0 Vector of values.
  //! \param parent0 The element's parent group.
  template <typename T>
  ObjSurface(const double& s00, const double& s10,
	     const double& t00, const double& t10,
	     const std::vector<T> &values0,
	     const ObjGroupBase* parent0 = NULL,
	     YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_VERT(T)))) :
    ObjFreeFormElement("surf", parent0), values(), s0(s00), s1(s10), t0(t00), t1(t10) {
    this->_init_properties();
    assign_values(values, values0);
    from_values();
  }
};

#undef FREEFORM_CONSTRUCTOR_EMPTY
#undef FREEFORM_CONSTRUCTOR_COPY

//! Free-form element group.
class ObjFreeFormType : public ObjElement {
public:
  GENERIC_VECTOR_BODY_STORED(ObjFreeFormType, ObjElement, cstype,
			     SINGLE_ARG(OBJ_P_(&values, "rat", ObjTypeString | ObjTypeIdx, 0),
					OBJ_P_(&values, "type", ObjTypeString | ObjTypeIdx | ObjTypeOpt, 1)),
			     SINGLE_ARG(COMPATIBLE_WITH_TYPE(T, std::string)),
			     std::string, std::string, string)
  //! \copydoc ObjElement::is_valid
  bool is_valid() const OVERRIDE_CXX11 {
    if (!(values.size() == 1 || values.size() == 2)) return false;
    std::string ival = values[0];
    if (ival == "rat" && values.size() == 2)
      ival = values[1];
    return (ival == "bmatrix"  || // basis matrix
	    ival == "bezier"   || // Bezier
	    ival == "bspline"  || // B-spline
	    ival == "cardinal" || // Cardinal
	    ival == "taylor"   ); // Taylor    
  }
};

//! Degree element.
class ObjDegree : public ObjElement {
public:
  GENERIC_VECTOR_BODY_STORED(ObjDegree, ObjElement, deg,
			     SINGLE_ARG(OBJ_P_(&values, "degu", ObjTypeUint16 | ObjTypeIdx, 0),
					OBJ_P_(&values, "degv", ObjTypeUint16 | ObjTypeIdx | ObjTypeOpt, 1)),
			     SINGLE_ARG(COMPATIBLE_WITH_UINT(T)),
			     uint16_t, int, int)
};


//! Basis matrix element.
class ObjBasisMatrix : public ObjElement {
public:
  GENERIC_VECTOR_BODY_MIXED(ObjBasisMatrix, ObjElement, bmat,
			    SINGLE_ARG(, values(), direction("")),
			    SINGLE_ARG(OBJ_P_(&direction, "direction", ObjTypeString),
				       OBJ_P_(&values, "matrix", ObjTypeFloat | ObjTypeList)),
			    double, 1, -1)
  //! Basis matrix direction.
  std::string direction;
  
  //! \brief Initialize an element from a C array of values.
  //! \tparam T Array element type.
  //! \tparam N Array size.
  //! \param direction0 Basis direction.
  //! \param src Array of values.
  //! \param parent0 The element's parent group.
  template <typename T, size_t N>
  ObjBasisMatrix(const std::string& direction0, const T (&src)[N],
		 const ObjGroupBase* parent0 = NULL) :
    ObjElement("bmat", parent0), values(), direction(direction0) {
    this->_init_properties();
    std::vector<T> values0(src, src+N);
    assign_values(values, values0);
    from_values();
  }
  //! \brief Initialize and element from a C++ vector of values.
  //! \param direction0 Basis direction.
  //! \param values0 Vector of values.
  //! \param parent0 The element's parent group.
  ObjBasisMatrix(const std::string& direction0, const std::vector<double> &values0,
		 const ObjGroupBase* parent0 = NULL) :
    ObjElement("bmat", parent0), values(), direction(direction0) {
    this->_init_properties();
    assign_values(values, values0);
    from_values();
  }
  //! \copydoc ObjElement::is_valid
  bool is_valid() const OVERRIDE_CXX11 {
    if (!this->parent) return false;
    const ObjElement* deg0 = this->parent->last_element("deg");
    if (!deg0) return false;
    const ObjDegree* deg = dynamic_cast<const ObjDegree*>(deg0);
    int n = 0;
    if (direction == "u")
      n = deg->values[0];
    else if (direction == "v") {
      if (deg->values.size() != 2) return false;
      n = deg->values[1];
    } else {
      return false;
    }
    return (values.size() == (size_t)((n + 1)*(n + 1)));
  }
};

//! Step element.
class ObjStep : public ObjElement {
public:
  GENERIC_VECTOR_BODY_STORED(ObjStep, ObjElement, step,
			     SINGLE_ARG(OBJ_P_(&values, "stepu", ObjTypeFloat | ObjTypeIdx, 0),
					OBJ_P_(&values, "stepv", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 1)),
			     SINGLE_ARG(COMPATIBLE_WITH_FLOAT(T)),
			     double, double, double)
};

//! Parameter element.
class ObjParameter : public ObjElement {
public:
  GENERIC_VECTOR_BODY_MIXED(ObjParameter, ObjElement, parm,
			    SINGLE_ARG(, values(), direction("")),
			    SINGLE_ARG(OBJ_P_(&direction, "direction", ObjTypeString),
				       OBJ_P_(&values, "parameter", ObjTypeFloat | ObjTypeList)),
			    double, 2, -1)
  //! Parameter direction.
  std::string direction;
  
  //! \brief Initialize and element from a C++ vector of values.
  //! \tparam T Vector element type. Must be catable to double.
  //! \param direction0 Parameter direction.
  //! \param values0 Vector of values.
  //! \param parent0 The element's parent group.
  template<typename T>
  ObjParameter(const std::string& direction0, const std::vector<T> &values0,
	       const ObjGroupBase* parent0 = NULL,
	       YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_FLOAT(T)))) :
    ObjElement("parm", parent0), values(), direction(direction0) {
    this->_init_properties();
    assign_values(values, values0);
    from_values();
  }
  //! \brief Initialize and element from a C++ vector of values.
  //! \tparam T Vector element type. Must be an integer or floating point.
  //! \param direction0 Parameter direction.
  //! \param parent0 The element's parent group.
  template <typename T>
  ObjParameter(const std::string&, const std::vector<T> &,
	       const ObjGroupBase* parent0 = NULL,
	       YGGDRASIL_RAPIDJSON_DISABLEIF((COMPATIBLE_WITH_FLOAT(T)))) :
    ObjElement("parm", parent0), values(), direction("") {
    YGGDRASIL_RAPIDJSON_ASSERT(sizeof("ObjParameter type is double"));
  }
  //! \copydoc ObjElement::is_valid
  bool is_valid() const OVERRIDE_CXX11 {
    return ((direction == "u") || (direction == "v"));
  }
};

//! Trim element.
GENERIC_VECTOR_OBJREFCURVE(ObjTrim, trim);

//! Hole element.
GENERIC_VECTOR_OBJREFCURVE(ObjHole, hole);

//! Special curve element.
GENERIC_VECTOR_OBJREFCURVE(ObjScrv, scrv);

//! Special points element.
class ObjSpecialPoints : public ObjElement {
public:
  GENERIC_VECTOR_BODY_STRICT(ObjSpecialPoints, ObjElement, sp,
			     SINGLE_ARG(OBJ_P_(&values, "param_index", ObjTypeRef | ObjTypeList)),
			     SINGLE_ARG(COMPATIBLE_WITH_INT(T)),
			     ObjRef, int, int,
			     1, -1);
  GENERIC_CLASS_VECTOR_TYPE_IS_VALID("vp", ObjRef)
};

//! Connection element.
GENERIC_VECTOR_OBJREFSURFACE(ObjConnect, con);

//! Group of elements.
class ObjGroup : public ObjGroupBase {
public:
  GENERIC_VECTOR_CONSTRUCTOR(ObjGroup, ObjGroupBase, g,
			     SINGLE_ARG(, values()),
			     SINGLE_ARG(OBJ_P_(&values, "labels", ObjTypeString | ObjTypeList)),
			     COMPATIBLE_WITH_TYPE(T, std::string),
			     std::string)
  GENERIC_COPY_MEMBERS(ObjGroup)
  //! \brief Initialize and element from a scalar.
  //! \tparam T Type of value.
  //! \param value Scalar value.
  //! \param parent0 The element's parent group.
  template<typename T>
  ObjGroup(const T &value,
	   const ObjGroupBase* parent0 = NULL,
	   YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_TYPE(T, std::string)))) :
    ObjGroupBase("g", parent0), values() {
    this->_init_properties();
    std::vector<T> values0;
    values0.push_back(value);
    assign_values(values, values0);
    from_values();
  }
  //! \brief Raise an error for incompatible types.
  //! \tparam T Type of value.
  //! \param parent0 The element's parent group.
  template<typename T>
  ObjGroup(const T &,
	   const ObjGroupBase* parent0 = NULL,
	   YGGDRASIL_RAPIDJSON_DISABLEIF((internal::OrExpr<COMPATIBLE_WITH_TYPE(T, std::string),
				internal::IsPointer<T> >))) :
    ObjGroupBase("g", parent0), values() {
    ASSERT_COMPATIBLE(T, std::string);
  }
  //! \copydoc ObjGroupBase::read_group_header
  bool read_group_header(std::istream &in) OVERRIDE_CXX11 {
    return ObjElement::read_values(in, values);
  }
  //! \copydoc ObjGroupBase::write_group_header
  bool write_group_header(std::ostream &out) const OVERRIDE_CXX11 {
    if (!ObjElement::write_values(out, values)) return false;
    return ObjGroupBase::write_group_header(out);
  }
  //! \copydoc ObjElement::write_suffix
  bool write_suffix(std::ostream &) const OVERRIDE_CXX11 {
    // No new line as last group element will be terminated
    return true;
  }
  //! \copydoc ObjElement::is_equal
  bool is_equal(const ObjElement* rhs0) const OVERRIDE_CXX11 {
    if (!ObjGroupBase::is_equal(rhs0))
      return false;
    const ObjGroup* lhs = this;
    const ObjGroup* rhs = dynamic_cast<const ObjGroup*>(rhs0);
    std::string lhs_str = "";
    std::string rhs_str = "";
    for (std::vector<std::string>::const_iterator it = lhs->values.begin(); it != lhs->values.end(); it++) {
      if (it != lhs->values.begin())
	lhs_str.append(" ");
      lhs_str.append(*it);
    }
    for (std::vector<std::string>::const_iterator it = rhs->values.begin(); it != rhs->values.end(); it++) {
      if (it != rhs->values.begin())
	rhs_str.append(" ");
      rhs_str.append(*it);
    }
    if (lhs_str != rhs_str)
      return false;
    return true;
  }
  //! Vector of element values in the group.
  std::vector<std::string> values;
};

//! Smoothing group element.
class ObjSmoothingGroup : public ObjElement {
public:
  GENERIC_SCALAR_BODY(ObjSmoothingGroup, ObjElement, s, 0,
		      SINGLE_ARG(OBJ_P_(&value, "state", ObjTypeInt | ObjTypeOff)),
		      int, int, int)
  //! \copydoc ObjElement::is_valid
  bool is_valid() const OVERRIDE_CXX11 {
    return value >= 0;
  }
};

//! Merging group.
class ObjMergingGroup : public ObjElement {
public:
  GENERIC_ELEMENT_CONSTRUCTOR(ObjMergingGroup, ObjElement, mg,
			      SINGLE_ARG(, value(0), resolution(0)),
			      SINGLE_ARG(OBJ_P_(&value, "state", ObjTypeInt | ObjTypeOff),
					 OBJ_P_(&resolution, "resolution", ObjTypeFloat)));
  DUMMY_ARRAY_CONSTRUCTOR(ObjMergingGroup, ObjElement, mg, SINGLE_ARG(, value(0), resolution(0)))
  GENERIC_SCALAR_BODY_BASE(ObjMergingGroup, int)
  //! Group resolution.
  double resolution;
  //! \brief Initialize the smoothing group from a string.
  //! \param value0 Scalar value.
  //! \param parent0 Parent group.
  template <typename T>
  ObjMergingGroup(const T& value0, const double& resolution0,
		  const ObjGroupBase* parent0 = NULL,
		  YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_TYPE(T, std::string)))) :
    ObjElement("mg", parent0), value((value0 == "off") ? 0 : std::atoi(value0.c_str())), resolution(resolution0) {
    this->_init_properties();
  }
  //! \brief Initialize the smoothing group from an integer.
  //! \param value0 Scalar value.
  //! \param parent0 Parent group.
  template <typename T>
  ObjMergingGroup(const T& value0, const double& resolution0,
		  const ObjGroupBase* parent0 = NULL,
		  YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_INT(T)))) :
    ObjElement("mg", parent0), value(value0), resolution(resolution0) {
    this->_init_properties();
  }
  //! \brief Raise an error for non string or integer types.
  template <typename T>
  ObjMergingGroup(const T&, const double&,
		  const ObjGroupBase* parent0 = NULL,
		  YGGDRASIL_RAPIDJSON_DISABLEIF((internal::OrExpr<
				       COMPATIBLE_WITH_INT(T),
				       COMPATIBLE_WITH_TYPE(T, std::string)>))) :
    ObjElement("mg", parent0), value(0), resolution(0) {
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof("ObjMergingGroup must be initialized from a string or integer."));
  }
  //! \copydoc ObjElement::is_valid
  bool is_valid() const OVERRIDE_CXX11 {
    return value >= 0;
  }
};

//! Object name element.
GENERIC_SCALAR_STRING(ObjObjectName, o, "", SINGLE_ARG(OBJ_P_(&value, "value", ObjTypeString)));

// Display/render attributes

#define BOOL_ELEMENT_CLASS(cls, code)					\
  class cls : public ObjElement {					\
  public:								\
  GENERIC_SCALAR_BODY(cls, ObjElement, code, "off", SINGLE_ARG(OBJ_P_(&value, "state", ObjTypeString)), std::string, std::string, string) \
  /*! \copydoc ObjElement::is_valid */					\
  bool is_valid() const OVERRIDE_CXX11 {				\
    return ((value == "on") || (value == "off"));			\
  }									\
  }

//! Bevel interpolation.
BOOL_ELEMENT_CLASS(ObjBevel, bevel);

//! Color interpolation.
BOOL_ELEMENT_CLASS(ObjCInterp, c_interp);

//! Dissolve interpolation.
BOOL_ELEMENT_CLASS(ObjDInterp, d_interp);

#undef BOOL_ELEMENT_CLASS

//! Level of detail.
class ObjLOD : public ObjElement {
public:
  GENERIC_SCALAR_BODY(ObjLOD, ObjElement, lod, 0, SINGLE_ARG(OBJ_P_(&value, "value", ObjTypeInt)), int, int, int)
};

//! Map library file.
GENERIC_VECTOR_STRING(ObjTextureMapLib, maplib, std::string, SINGLE_ARG(OBJ_P_(&values, "value", ObjTypeString | ObjTypeList)));

//! Texture map.
GENERIC_SCALAR_STRING(ObjTextureMap, usemap, "off", SINGLE_ARG(OBJ_P_(&value, "value", ObjTypeString)));

//! Material name.
GENERIC_SCALAR_STRING(ObjMaterial, usemtl, "", SINGLE_ARG(OBJ_P_(&value, "value", ObjTypeString)));

//! Matrial library file.
GENERIC_VECTOR_STRING(ObjMaterialLib, mtllib, std::string, SINGLE_ARG(OBJ_P_(&values, "value", ObjTypeString | ObjTypeList)));

//! Shadow object file.
GENERIC_SCALAR_STRING(ObjShadowFile, shadow_obj, "", SINGLE_ARG(OBJ_P_(&value, "value", ObjTypeString)));

//! Ray tracing object file.
GENERIC_SCALAR_STRING(ObjTraceFile, trace_obj, "", SINGLE_ARG(OBJ_P_(&value, "value", ObjTypeString)));

//! Curve technique resolution.
class ObjCTech : public ObjElement {
public:
  GENERIC_VECTOR_BODY_MIXED(ObjCTech, ObjElement, ctech,
			    SINGLE_ARG(, values(), technique("")),
			    SINGLE_ARG(OBJ_P_(&technique, "technique", ObjTypeString),
				       OBJ_P_(&values, "resolution", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 0),
				       OBJ_P_(&values, "maxlength", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 0),
				       OBJ_P_(&values, "maxdist", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 0),
				       OBJ_P_(&values, "maxangle", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 1)),
			    double, 1, 2)
  //! Technique used for the resolution.
  std::string technique;
  
  template<typename T>
  ObjCTech(const std::string& technique0,
	   const std::vector<T> &values0,
	   const ObjGroupBase* parent0 = NULL,
	   YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_FLOAT(T)))) :
    ObjElement("ctech", parent0), values(), technique(technique0) {
    this->_init_properties();
    assign_values(values, values0);
    from_values();
  }
  template<typename T>
  ObjCTech(const std::string& technique0,
	   const std::vector<T> &,
	   const ObjGroupBase* parent0 = NULL,
	   YGGDRASIL_RAPIDJSON_DISABLEIF((COMPATIBLE_WITH_FLOAT(T)))) :
    ObjElement("ctech", parent0), values(), technique(technique0) {
    YGGDRASIL_RAPIDJSON_ASSERT(sizeof("ObjCTech type is double"));
  }
  //! \copydoc ObjElement::has_property
  bool has_property(const std::string name, bool dontCheckOrder=false, bool skipColors=false, size_t* idx=NULL) const  OVERRIDE_CXX11 {
    return (ObjElement::has_property(name, dontCheckOrder, skipColors, idx) &&
	    ((name == "technique") ||
	     (technique == "cparm" && name == "resolution") ||
	     (technique == "cspace" && name == "maxlength") ||
	     (technique == "curv" && (name == "maxdist" ||
				      name == "maxangle"))));
  }
  //! \copydoc ObjElement::is_valid
  bool is_valid() const OVERRIDE_CXX11 {
    return (((technique == "cparm" ||
	      technique == "cspace") && values.size() == 1) ||
	    (technique == "curv" && values.size() == 2));
  }
};

//! Surface technique resolution.
class ObjSTech : public ObjElement {
public:
  GENERIC_VECTOR_BODY_MIXED(ObjSTech, ObjElement, stech,
			    SINGLE_ARG(, values(), technique("")),
			    SINGLE_ARG(OBJ_P_(&technique, "technique", ObjTypeString),
				       OBJ_P_(&values, "ures", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 0),
				       OBJ_P_(&values, "vres", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 1),
				       OBJ_P_(&values, "uvres", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 0),
				       OBJ_P_(&values, "maxlength", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 0),
				       OBJ_P_(&values, "maxdist", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 0),
				       OBJ_P_(&values, "maxangle", ObjTypeFloat | ObjTypeIdx | ObjTypeOpt, 1)),
			    double, 1, 2)
  //! Technique used for the resolution.
  std::string technique;
    
  template<typename T>
  ObjSTech(const std::string& technique0,
	   const std::vector<T> &values0,
	   const ObjGroupBase* parent0 = NULL,
	   YGGDRASIL_RAPIDJSON_ENABLEIF((COMPATIBLE_WITH_FLOAT(T)))) :
    ObjElement("stech", parent0), values(), technique(technique0) {
    this->_init_properties();
    assign_values(values, values0);
    from_values();
  }
  template<typename T>
  ObjSTech(const std::string& technique0,
	   const std::vector<T> &,
	   const ObjGroupBase* parent0 = NULL,
	   YGGDRASIL_RAPIDJSON_DISABLEIF((COMPATIBLE_WITH_FLOAT(T)))) :
    ObjElement("stech", parent0), values(), technique(technique0) {
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof("ObjSTech type is double"));
  }
  //! \copydoc ObjElement::has_property
  bool has_property(const std::string name, bool dontCheckOrder=false, bool skipColors=false, size_t* idx=NULL) const  OVERRIDE_CXX11 {
    return (ObjElement::has_property(name, dontCheckOrder, skipColors, idx) &&
	    ((name == "technique") ||
	     (technique == "cparma" && (name == "ures" ||
					name == "vres")) ||
	     (technique == "cparmb" && name == "uvres") ||
	     (technique == "cspace" && name == "maxlength") ||
	     (technique == "curv" && (name == "maxdist" ||
				      name == "maxangle"))));
  }
  //! \copydoc ObjElement::is_valid
  bool is_valid() const OVERRIDE_CXX11 {
    return (((technique == "cparmb" || technique == "cspace") &&
	     values.size() == 1) ||
	    ((technique == "cparma" || technique == "curv") &&
	     values.size() == 2));
  }
};

//! \brief Read an element from an input stream.
//! \param in Input stream.
//! \param parent Optional element group that will contain the read elements.
//! \param dont_descend If true, subelements will not be read from the
//!   input stream.
//! \param[out] out New element. This will be null in the case of an error or
//!   then end of the input stream.
//! \return true if successful, false otherwise.
inline bool read_obj_element(std::istream &in,
			     ObjGroupBase* parent,
			     const bool& dont_descend,
			     ObjElement*& out) {
  std::string word = "";
  out = NULL;
  if (in >> word) {
    if (word == "end") {
      out = parent;
      return parent->end_group();
    } else {
      OBJ_ELEMENT_INIT(word, out, (parent));
      if (!out)  return false;
      if (!out->read_values(in, dont_descend)) return false;
    }
  } else {
    out = parent;
    parent->finalize();
  }
  return true;
}

//! Forward declare ply
class Ply;

//! Obj wavefront 3D geometry container class.
class ObjWavefront : public ObjGroupBase {
public:
  ObjWavefront() : ObjGroupBase("") {}
  //! \brief Copy constructor.
  //! \param rhs Instance to copy.
  ObjWavefront(const ObjWavefront& rhs) : ObjGroupBase(rhs) {}
  //! \brief Copy from ply.
  //! \param rhs Instance to copy.
  ObjWavefront(const Ply& rhs) : ObjGroupBase("") {
    fromPly(rhs);
  }
  //! \brief Create an ObjWavefront instance from C arrays of vertices.
  //! \tparam Tv Type of value in vertex value arrays.
  //! \tparam Mv Number of vertex elements.
  //! \tparam Nv Number of values in the array for each vertex element.
  //! \param vertices Array of vertex element value arrays.
  template<typename Tv, size_t Mv, size_t Nv>
  ObjWavefront(const Tv (&vertices)[Mv][Nv]) : ObjGroupBase("") {
    add_element_set("v", vertices);
  }
  //! \brief Create an ObjWavefront instance from C arrays of vertices and
  //!   faces.
  //! \tparam Tv Type of value in vertex value arrays.
  //! \tparam Mv Number of vertex elements.
  //! \tparam Nv Number of values in the array for each vertex element.
  //! \tparam Tf Type of value in face value arrays.
  //! \tparam Mf Number of face elements.
  //! \tparam Nf Number of values in the array for each face element.
  //! \param vertices Array of vertex element value arrays.
  //! \param faces Array of face element value arrays.
  template<typename Tv, size_t Mv, size_t Nv,
	   typename Tf, size_t Mf, size_t Nf>
  ObjWavefront(const Tv (&vertices)[Mv][Nv], const Tf (&faces)[Mf][Nf]) :
    ObjGroupBase("") {
    add_element_set("v", vertices);
    add_element_set("f", faces);
  }
  //! \brief Create an ObjWavefront instance from C arrays of vertices,
  //!   faces, and edges.
  //! \tparam Tv Type of value in vertex value arrays.
  //! \tparam Mv Number of vertex elements.
  //! \tparam Nv Number of values in the array for each vertex element.
  //! \tparam Tf Type of value in face value arrays.
  //! \tparam Mf Number of face elements.
  //! \tparam Nf Number of values in the array for each face element.
  //! \tparam Te Type of value in edge value arrays.
  //! \tparam Me Number of edge elements.
  //! \tparam Ne Number of values in the array for each edge element.
  //! \param vertices Array of vertex element value arrays.
  //! \param faces Array of face element value arrays.
  //! \param edges Array of edge element value arrays.
  template<typename Tv, size_t Mv, size_t Nv,
	   typename Tf, size_t Mf, size_t Nf,
	   typename Te, size_t Me, size_t Ne>
  ObjWavefront(const Tv (&vertices)[Mv][Nv], const Tf (&faces)[Mf][Nf],
	       const Te (&edges)[Me][Ne]) :
    ObjGroupBase("") {
    add_element_set("v", vertices);
    add_element_set("f", faces);
    add_element_set("l", edges);
  }
  //! \brief Create an ObjWavefront instance from a 3D mesh.
  //! \param xyz Vector of vertex information for faces in the structure.
  //! \param prune_duplicates If true, existing vertices will be checked
  //!   before adding new ones.
  ObjWavefront(const std::vector<std::vector<double> > xyz,
	       bool prune_duplicates=false) :
    ObjGroupBase("") {
    add_mesh(xyz, prune_duplicates);
  }
  //! \brief Copy assignment
  //! \param[in] rhs Instance to copy.
  ObjWavefront& operator=(const ObjWavefront& rhs) {
    this->~ObjWavefront();
    new (this) ObjWavefront(rhs);
    return *this;
  }
  //! \brief Copy from ply.
  //! \param rhs Instance to copy.
  void fromPly(const Ply& p);
  //! \copydoc ObjGroupBase::write_group_header
  bool write_group_header(std::ostream &) const OVERRIDE_CXX11 {
    return true; // Don't write a header for the start of the file
  }
  //! \copydoc ObjElement::write_suffix
  bool write_suffix(std::ostream &) const OVERRIDE_CXX11 {
    // No new line as last group element will be terminated
    return true;
  }
  //! \brief Determine if a structure is valid and there are vertexes for
  //!   all those referenced in faces and edges.
  //! \return true if the structure is valid, false otherwise.
  bool is_valid() const OVERRIDE_CXX11 {
    std::map<std::string,size_t> idx;
    return ObjGroupBase::is_valid_idx(idx);
  }
  //! \brief Add a set of elements to the geometry from a C array of value
  //!   arrays.
  //! \tparam T Type of value in the values array.
  //! \tparam M Number of elements being added.
  //! \tparam N Number of entries in each element's values array.
  //! \param name Name of the type of elements being added.
  //! \param values Array of value arrays defining the elements.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \param inc If true and a property is an index, it will be incremented.
  template <typename T, size_t M, size_t N>
  void add_element_set(std::string name, const T (&values)[M][N],
		       const T* ignore = 0, bool inc = false) {
    std::string name2 = obj_alias2base(name);
    for (SizeType i = 0; i < M; i++)
      this->add_element(name2, values[i], ignore, inc);
  }
  //! \brief Add a new element set to the geometry.
  //! \tparam T Type of property values.
  //! \param name Name of the type of element in the set.
  //! \param arr Property values for each of the elements in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of properties for each element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \param inc If true and a property is an index, it will be incremented.
  template <typename T>
  void add_element_set(const std::string& name,
		       const T* arr, SizeType M, SizeType N,
		       const T* ignore = 0, bool inc = false) {
    std::string name2 = obj_alias2base(name);
    const T* p = arr;
    for (SizeType i = 0; i < M; i++, p += N)
      this->add_element(name2, p, N, ignore, inc);
  }
  //! \brief Get the minimum bounds of the structure in 3D.
  //! \return Minimum extend of structure in x, y, z.
  std::vector<double> minimums() const {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    std::vector<double> out = {NAN, NAN, NAN};
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    std::vector<double> out(3);
    for (size_t i = 0; i < 3; i++)
      out[i] = NAN;
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    bool first = true;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code == "v") {
	if (first) {
	  out = (*it)->get_double_array(true);
	  first = false;
	} else {
	  std::vector<double> iarr = (*it)->get_double_array(true);
	  out[0] = (std::min)(out[0], iarr[0]);
	  out[1] = (std::min)(out[1], iarr[1]);
	  out[2] = (std::min)(out[2], iarr[2]);
	}
      }
    }
    return out;
  }
  //! \brief Get the maximum bounds of the structure in 3D.
  //! \return Maximum extend of structure in x, y, z.
  std::vector<double> maximums() const {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    std::vector<double> out = {NAN, NAN, NAN};
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    std::vector<double> out(3);
    for (size_t i = 0; i < 3; i++)
      out[i] = NAN;
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    bool first = true;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code == "v") {
	if (first) {
	  out = (*it)->get_double_array(true);
	  first = false;
	} else {
	  std::vector<double> iarr = (*it)->get_double_array(true);
	  out[0] = (std::max)(out[0], iarr[0]);
	  out[1] = (std::max)(out[1], iarr[1]);
	  out[2] = (std::max)(out[2], iarr[2]);
	}
      }
    }
    return out;
  }
  //! \brief Locate existing vertex that matches the provided vertex.
  //! \param v Vertex to search for.
  //! \returns Index of existing vertex that matches v, -1 if a match
  //!   cannot be found.
  int find_vertex(const std::vector<double> v) const {
    int idx = 0;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code == "v") {
	const ObjVertex* iv = dynamic_cast<const ObjVertex*>(*it);
	if (internal::values_eq(v[0], iv->x) &&
	    internal::values_eq(v[1], iv->y) &&
	    internal::values_eq(v[2], iv->z))
	  return idx;
	idx++;
      }
    }
    return -1;
  }
  //! \brief Add elements from a mesh.
  //! \param xyz Vector of vectors containing vertices for each point
  //!   in the faces.
  //! \param prune_duplicates If true, existing vertices will be checked
  //!   before adding new ones.
  void add_mesh(const std::vector<std::vector<double> > xyz,
		bool prune_duplicates=false) {
    size_t nVerts = count_elements("vertex");
    std::vector<std::vector<ObjRef> > faces;
    for (std::vector<std::vector<double> >::const_iterator it = xyz.begin();
	 it != xyz.end(); it++) {
      size_t verts_per_face = it->size() / 3;
      std::vector<ObjRef> iface;
      for (size_t i = 0; i < verts_per_face; i++) {
	std::vector<double> ivert(it->begin() + static_cast<long>(i * 3),
				  it->begin() + static_cast<long>((i + 1) * 3));
	int idxVert = -1;
	if (prune_duplicates)
	  idxVert = find_vertex(ivert);
	if (idxVert < 0) {
	  idxVert = static_cast<int>(nVerts);
	  add_element("vertex", ivert);
	  nVerts++;
	}
	iface.push_back(static_cast<ObjRef>(idxVert + 1));
      }
      faces.push_back(iface);
    }
    for (std::vector<std::vector<ObjRef> >::const_iterator it = faces.begin();
	 it != faces.end(); it++)
      add_element("face", *it);
  }
  //! \brief Get the mesh for the structure.
  //! \return Structure mesh with each row representing a face with vertex
  //!    information provided in sequence for each face.
  std::vector<std::vector<double> > mesh() const {
    std::vector<std::vector<double> > out;
    std::vector<size_t> vert_idx;
    size_t i = 0, iFace = 0;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++, i++) {
      if ((*it)->code == "v")
	vert_idx.push_back(i);
      else if ((*it)->code == "f") {
	const std::vector<int> idx = (*it)->get_int_array();
	out.push_back(std::vector<double>());
	for (std::vector<int>::const_iterator f = idx.begin(); f != idx.end(); f++) {
	  int iv = 0;
	  if (*f > 0)
	    iv = *f - 1;
	  else
	    iv = (int)(vert_idx.size()) + *f;
	  YGGDRASIL_RAPIDJSON_ASSERT(iv >= 0 && iv < (int)(vert_idx.size()));
	  if (iv < 0 || iv >= (int)(vert_idx.size())) {
	    out.clear();
	    return out;
	  }
	  size_t nPrev = out[iFace].size();
	  elements[vert_idx[(size_t)(iv)]]->get_double_array(out[iFace], true);
	  while (out[iFace].size() > (nPrev + 3))
	    out[iFace].pop_back();
	}
	iFace++;
      }
    }
    return out;
  }
  //! \brief Get the areas for each face in the structure.
  //! \return Vector of areas for each face.
  std::vector<double> areas() const {
    return mesh2areas(mesh());
  }
  //! \copydoc ObjElement::has_colors
  bool has_colors() const OVERRIDE_CXX11 {
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->has_colors()) return true;
    }
    return false;
  }
  //! \brief Determine if any elements of a given type contain color
  //!   information.
  //! \param name Name of the element set to check.
  //! \return true if there are colors, false otherwise.
  bool has_colors(const std::string& name) const {
    std::string name2 = obj_alias2base(name);
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code != name2) continue;
      if ((*it)->has_colors()) return true;
    }
    return false;
  }
  //! \brief Get an element set in an array form.
  //! \param name0 Name of the element set to get.
  //! \param[out] N Number of elements in the returned array.
  //! \param[out[ M Number of values for each element in the returned array.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \param dec If true and a property is an index, it will be decremented.
  //! \returns The element set of the requested type in array form.
  std::vector<int> get_int_array(const std::string& name0,
				 size_t &N, size_t &M,
				 bool=false, bool dec=false) const {
    std::string name = obj_alias2base(name0);
    std::vector<int> out;
    size_t minSize = this->max_size(name);
    int defaultValue = 0;
    if (dec) defaultValue--;
    ObjGroupBase::get_int_array(name, out, minSize, defaultValue, dec);
    M = minSize;
    N = out.size() / M;
    return out;
  }
  //! \brief Get an element set in an array form.
  //! \param name0 Name of the element set to get.
  //! \param[out] N Number of elements in the returned array.
  //! \param[out[ M Number of values for each element in the returned array.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \param dec If true and a property is an index, it will be decremented.
  //! \returns The element set of the requested type in array form.
  std::vector<double> get_double_array(const std::string& name0,
				       size_t &N, size_t &M,
				       bool skipColors=false,
				       bool dec=false) const {
    std::string name = obj_alias2base(name0);
    std::vector<double> out;
    size_t minSize = this->max_size(name, skipColors);
    ObjGroupBase::get_double_array(name, out, minSize, NAN, skipColors, dec);
    M = minSize;
    N = out.size() / M;
    return out;
  }
  //! \copydoc ObjElement::get_colors_array
  void get_colors_array(std::vector<double>& out,
			double defaultValue=0) const OVERRIDE_CXX11 {
    if (!has_colors()) return;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++)
      (*it)->get_colors_array(out, defaultValue);
  }
  //! \copydoc ObjElement::get_colors_array
  void get_colors_array(std::vector<uint8_t>& out,
			uint8_t defaultValue=0) const OVERRIDE_CXX11 {
    if (!has_colors()) return;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++)
      (*it)->get_colors_array(out, defaultValue);
  }
  //! \brief Get the colors for an element set in arrayform.
  //! \param name Name of the element set to get.
  //! \param[out] N Number of elements in the returned array.
  //! \param[out] M Number of values for each element in the returned array.
  //! \param defaultValue Value to add if colors are missing.
  //! \returns The colors for the requirested type in array form.
  template<typename CT>
  std::vector<CT> get_colors_array(const std::string& name,
				   size_t &N, size_t &M,
				   CT defaultValue=0) const {
    std::string name2 = obj_alias2base(name);
    std::vector<CT> out;
    if (!has_colors(name2)) return out;
    N = 0;
    for (std::vector<ObjElement*>::const_iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code != name2) continue;
      (*it)->get_colors_array(out, defaultValue);
      N++;
    }
    M = out.size() / N;
    YGGDRASIL_RAPIDJSON_ASSERT(M == 3);
    return out;
  }
  //! \brief Add element colors to a set.
  //! \param name Name of the type of element in the set.
  //! \param arr Colors for each of the elements in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of color properties for each element.
  //! \return true if successful, false otherwise.
  template<typename CT>
  bool add_element_set_colors(const std::string& name,
			      const CT* arr, SizeType M, SizeType N) {
    std::string name2 = obj_alias2base(name);
    if (N != 3 || M != count_elements(name2)) return false;
    size_t i = 0;
    for (std::vector<ObjElement*>::iterator it = elements.begin(); it != elements.end(); it++) {
      if ((*it)->code != name2) continue;
      if (!(*it)->add_colors(arr + (N * i), N)) return false;
      i++;
    }
    return true;
  }
  //! \copydoc ObjElement::read
  bool read(std::istream &in, const bool& dont_descend=false) OVERRIDE_CXX11 {
    in >> std::ws;
    return ObjGroupBase::read(in, dont_descend);
  }

  friend bool operator == (const ObjWavefront& lhs, const ObjWavefront& rhs);
  friend bool operator != (const ObjWavefront& lhs, const ObjWavefront& rhs);
  friend std::ostream & operator << (std::ostream &out, const ObjWavefront &p);
  friend std::istream & operator >> (std::istream &in,  ObjWavefront &p);
};
//! \brief Check the equivalent of two ObjWavefront instances by comparing
//!   elements (calls ObjWavefront::is_equal method).
//! \param lhs First instance for comparison.
//! \param rhs Second instance for comparison.
//! \return true if the two instances are equivalent.
inline
bool operator == (const ObjWavefront& lhs, const ObjWavefront& rhs)
{ return lhs.is_equal(&rhs); }

//! \brief Check the inequivalance of two ObjWavefront instances by comparing
//!   elements (calls ObjWavefront::is_equal method).
//! \param lhs First instance for comparison.
//! \param rhs Second instance for comparison.
//! \return true if the two instances are not equivalent.
inline
bool operator != (const ObjWavefront& lhs, const ObjWavefront& rhs)
{ return !lhs.is_equal(&rhs); }

//! \brief Write an ObjWavefront object to an output stream.
//! \param out Output stream.
//! \param p ObjWavefront object.
//! \return Output stream.
inline
std::ostream & operator << (std::ostream &out, const ObjWavefront &p)
{ p.write(out); return out; }

//! \brief Read an ObjWavefront object from an input stream.
//! \param in Input stream.
//! \param p ObjWavefrotn object.
//! \return Input stream.
inline
std::istream & operator >> (std::istream &in, ObjWavefront &p)
{ p.read(in); return in; }

inline
ObjElement* ObjGroupBase::copy_element(const ObjElement* x) {
  ObjElement* x_cpy = NULL;
  std::string name_copy = x->code;
  OBJ_ELEMENT_INIT(name_copy, x_cpy, (x));
  return ObjGroupBase::add_element(x_cpy);
}
inline
ObjElement* ObjGroupBase::add_element(std::string name) {
  ObjElement* x = NULL;
  OBJ_ELEMENT_INIT(name, x, (this));
  return ObjGroupBase::add_element(x);
}
template <typename T>
ObjElement* ObjGroupBase::add_element(std::string name,
				      const std::vector<T> &values,
				      const T* ignore, bool inc) {
  ObjElement* x = NULL;
  if (ignore) {
    std::vector<T> values2;
    for (typename std::vector<T>::const_iterator it = values.begin(); it != values.end(); it++) {
      if (internal::values_eq(*it, *ignore)) break;
      values2.push_back(*it);
    }
    OBJ_ELEMENT_INIT(name, x, (values2, this));
  } else {
    OBJ_ELEMENT_INIT(name, x, (values, this));
  }
  return ObjGroupBase::add_element(x, inc);
}
template <typename T>
ObjElement* ObjGroupBase::add_element(const std::string name,
				      const double& u0, const double& u1,
				      const std::vector<T> &values,
				      bool inc) {
  ObjElement* x = NULL;
  if (name == "curv") x = new ObjCurve(u0, u1, values, this);
  else REPORT_UNSUPPORTED_ELEMENT(ObjCurve, name);
  return ObjGroupBase::add_element(x, inc);
}
template <typename T>
ObjElement* ObjGroupBase::add_element(const std::string name,
				      const double& u0, const double& u1,
				      const double& u2, const double& u3,
				      const std::vector<T> &values,
				      bool inc) {
  ObjElement* x = NULL;
  if (name == "surf") x = new ObjSurface(u0, u1, u2, u3, values, this);
  else REPORT_UNSUPPORTED_ELEMENT(ObjSurface, name);
  return ObjGroupBase::add_element(x, inc);
}
template <typename T>
ObjElement* ObjGroupBase::add_element(std::string name, std::string direction,
				      const std::vector<T> &values) {
  ObjElement* x = NULL;
  if      (name == "parm" ) x = new ObjParameter(direction, values, this);
  else if (name == "ctech") x = new ObjCTech(direction, values, this);
  else if (name == "stech") x = new ObjSTech(direction, values, this);
  else REPORT_UNSUPPORTED_ELEMENT(direction, name);
  return ObjGroupBase::add_element(x);
}
template<typename T>
YGGDRASIL_RAPIDJSON_DISABLEIF_RETURN((internal::OrExpr<internal::IsPointer<T>,
			    internal::IsSame<T,std::string> >), (ObjElement*))
  ObjGroupBase::add_element(std::string name, const T& value) {
  ObjElement* x = NULL;
  if      (name == "s"         ) x = new ObjSmoothingGroup(value, this);
  else if (name == "lod"       ) x = new ObjLOD(value, this);
  else if ((name == "trim") || (name == "scrv") || (name == "hole")) {
    std::vector<T> values;
    values.push_back(value);
    return ObjGroupBase::add_element(name, values);
  }
  else REPORT_UNSUPPORTED_ELEMENT(scalar, name);
  return ObjGroupBase::add_element(x);
}
inline
ObjElement* ObjGroupBase::add_element(std::string name, const std::string& value) {
  ObjElement* x = NULL;
  if      (name == "g"         ) x = new ObjGroup(value, this);
  else if (name == "s"         ) x = new ObjSmoothingGroup(value, this);
  else if (name == "bevel"     ) x = new ObjBevel(value, this);
  else if (name == "c_interp"  ) x = new ObjCInterp(value, this);
  else if (name == "d_interp"  ) x = new ObjDInterp(value, this);
  else if (name == "usemap"    ) x = new ObjTextureMap(value, this);
  else if (name == "usemtl"    ) x = new ObjMaterial(value, this);
  else if (name == "shadow_obj") x = new ObjShadowFile(value, this);
  else if (name == "trace_obj" ) x = new ObjTraceFile(value, this);
  else if (name == "maplib"    ) {
    std::vector<std::string> values;
    values.push_back(value);
    x = new ObjTextureMapLib(values, this);
  } else if (name == "mtllib"  ) {
    std::vector<std::string> values;
    values.push_back(value);
    x = new ObjMaterialLib(values, this);
  }
  else if (name == "#") {
    std::vector<std::string> values;
    size_t prev = 0, i = 0;
    while (i < value.size()) {
      if (value[i] == ' ') {
	if (i > 0)
	  values.push_back(value.substr(prev, i));
	while (i < value.size() && value[i] == ' ')
	  i++;
	prev = i;
      } else {
	i++;
      }
    }
    x = new ObjComment(values, this);
  }
  else REPORT_UNSUPPORTED_ELEMENT(scalar, name);
  return ObjGroupBase::add_element(x);
}

inline
ObjElement* ObjGroupBase::add_element(std::string name, const int& value,
				      const double& resolution,
				      bool inc) {
  ObjElement* x = NULL;
  if      (name == "mg"   ) x = new ObjMergingGroup(value, resolution, this);
  else REPORT_UNSUPPORTED_ELEMENT(ObjMergingGroup, name);
  return ObjGroupBase::add_element(x, inc);
}
inline
ObjElement* ObjGroupBase::add_element(std::string name,
				      const std::string& value,
				      const double& resolution) {
  ObjElement* x = NULL;
  if      (name == "mg"   ) x = new ObjMergingGroup(value, resolution, this);
  else if (name == "parm" ) {
    std::vector<double> vres;
    vres.push_back(resolution);
    x = new ObjParameter(value, vres, this);
  }
  else if (name == "ctech") {
    std::vector<double> vres;
    vres.push_back(resolution);
    x = new ObjCTech(value, vres, this);
  }
  else if (name == "stech") {
    std::vector<double> vres;
    vres.push_back(resolution);
    x = new ObjSTech(value, vres, this);
  }
  else REPORT_UNSUPPORTED_ELEMENT(ObjMergingGroupString, name);
  return ObjGroupBase::add_element(x);
}

#undef GENERIC_CLASS_VECTOR_TYPE_IS_VALID_VERTREF
#undef GENERIC_CLASS_VECTOR_TYPE_IS_VALID
#undef GENERIC_VECTOR_OBJREFSURFACE
#undef GENERIC_VECTOR_OBJREFCURVE
#undef GENERIC_VECTOR_OBJREFVERTEX
#undef GENERIC_VECTOR_STRING
#undef GENERIC_SCALAR_STRING
#undef GENERIC_CLASS_SCALAR_TYPE
#undef GENERIC_SCALAR_BODY
#undef GENERIC_SCALAR_BODY_BASE
#undef DUMMY_ARRAY_CONSTRUCTOR
#undef GENERIC_VECTOR_CONSTRUCTOR
#undef ASSERT_COMPATIBLE
#undef COMPATIBLE_WITH_ANY
#undef COMPATIBLE_WITH_TYPE
#undef COMPATIBLE_WITH_SURF
#undef COMPATIBLE_WITH_CURV
#undef COMPATIBLE_WITH_VERT
#undef COMPATIBLE_WITH_FLOAT
#undef COMPATIBLE_WITH_UINT
#undef COMPATIBLE_WITH_INT
#undef GENERIC_ELEMENT_CONSTRUCTOR
#undef GENERIC_CONSTRUCTOR_COPY
#undef COMPARE_IDX
#undef OBJ_P_
#undef OVERRIDE_CXX11
#undef OBJ_ELEMENT_INIT
#undef REPORT_UNSUPPORTED_ELEMENT

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // YGGDRASIL_RAPIDJSON_OBJ_H_
