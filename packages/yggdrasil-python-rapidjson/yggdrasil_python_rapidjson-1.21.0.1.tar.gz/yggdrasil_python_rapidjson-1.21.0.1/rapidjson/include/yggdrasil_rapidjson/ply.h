#ifndef YGGDRASIL_RAPIDJSON_PLY_H_
#define YGGDRASIL_RAPIDJSON_PLY_H_

#include "internal/meta.h"
#include <iostream>
#include <map>
#include <vector>
#include <algorithm>

YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

#if YGGDRASIL_RAPIDJSON_ENDIAN == YGGDRASIL_RAPIDJSON_LITTLEENDIAN
#define NUMBER_MEMBER_BASE_(name, type, ptype1, ptype2, ptype3)		\
    name(const type x) : v(x), pad1(0), pad2(0), pad3(0) {}		\
    name() : v(0), pad1(0), pad2(0), pad3(0) {}				\
    name(std::istream &in) : v(0), pad1(0), pad2(0), pad3(0) { read(in); } \
    bool is_equal(const name &y) const {				\
      return internal::values_eq(v, y.v); }				\
    type v;								\
    ptype1 pad1;							\
    ptype2 pad2;							\
    ptype3 pad3
#define NUMBER_MEMBER_(name, member, type, ptype1, ptype2, ptype3)	\
  struct name {								\
    NUMBER_MEMBER_BASE_(name, type, ptype1, ptype2, ptype3);		\
    std::istream & read(std::istream &in) {				\
      in >> v;								\
      return in;							\
    }									\
    std::ostream & write(std::ostream &out) const {			\
      out << v;								\
      return out;							\
    }									\
  } member
#define NUMBER_MEMBER_CHAR_(name, member, type, ptype1, ptype2, ptype3)	\
  struct name {								\
    NUMBER_MEMBER_BASE_(name, type, ptype1, ptype2, ptype3);		\
    std::istream & read(std::istream &in) {				\
      int tmp = 0;							\
      in >> tmp;							\
      YGGDRASIL_RAPIDJSON_ASSERT(tmp >= 0 && tmp < 256);				\
      v = (type)tmp;							\
      return in;							\
    }									\
    std::ostream & write(std::ostream &out) const {			\
      out << (int)v;							\
      return out;							\
    }									\
  } member
  
#else
// TODO
#endif

#define NUMBER_DATA_SWITCH_(x, flag, before, after)			\
  switch (flag) {							\
  case (kInt8Flag) : before x.i8.v after; break;			\
  case (kUint8Flag) : before x.u8.v after; break;			\
  case (kInt16Flag) : before x.i16.v after; break;			\
  case (kUint16Flag) : before x.u16.v after; break;			\
  case (kInt32Flag) : before x.i32.v after; break;			\
  case (kUint32Flag) : before x.u32.v after; break;			\
  case (kFloatFlag) : before x.f.v after; break;			\
  case (kDoubleFlag) : before x.d after; break;				\
  default: YGGDRASIL_RAPIDJSON_ASSERT(false);					\
  }
#define NUMBER_DATA_COMPARE_(x, y, flag, var)				\
  switch (flag) {							\
  case (kInt8Flag) : var = (x.i8.v == y.i8.v); break;			\
  case (kUint8Flag) : var = (x.u8.v == y.u8.v); break;			\
  case (kInt16Flag) : var = (x.i16.v == y.i16.v); break;		\
  case (kUint16Flag) : var = (x.u16.v == y.u16.v); break;		\
  case (kInt32Flag) : var = (x.i32.v == y.i32.v); break;		\
  case (kUint32Flag) : var = (x.u32.v == y.u32.v); break;		\
  case (kFloatFlag) : var = (fabs(x.f.v - y.f.v) < 0.01f); break;	\
  case (kDoubleFlag) : var = (abs(x.d - y.d) < 0.01); break;		\
  default: YGGDRASIL_RAPIDJSON_ASSERT(false);					\
  }
// Forward declarations
class PlyElement;
class PlyElementSet;
template<typename T>
inline uint16_t type2flag();
template<>
inline uint16_t type2flag<int8_t>();
template<>
inline uint16_t type2flag<uint8_t>();
template<>
inline uint16_t type2flag<int16_t>();
template<>
inline uint16_t type2flag<uint16_t>();
template<>
inline uint16_t type2flag<int32_t>();
template<>
inline uint16_t type2flag<uint32_t>();
template<>
inline uint16_t type2flag<float>();
template<>
inline uint16_t type2flag<double>();

//! \brief Convert from an alias for a geometry element to the base.
//! \param alias Name to check.
//! \return Base name associated with the provided alias.
static inline
std::string ply_alias2base(const std::string& alias) {
  if      (alias == "vertices") return std::string("vertex");
  else if (alias == "vertexes") return std::string("vertex");
  else if (alias == "faces"   ) return std::string("face");
  else if (alias == "edges"   ) return std::string("edge");
  else if (alias == "comments") return std::string("comment");
  return std::string(alias);
}

static inline
std::vector<double> cross_product_3d(std::vector<double>& a,
				     std::vector<double>& b) {
  std::vector<double> out(3);
  out[0] = (a[1] * b[2]) - (a[2] * b[1]);
  out[1] = (a[2] * b[0]) - (a[0] * b[2]);
  out[2] = (a[0] * b[1]) - (a[1] * b[0]);
  return out;
}

//! \brief Get the areas for each face in the structure.
//! \param mesh Mesh describine structure.
//! \return Vector of areas for each face.
static inline
std::vector<double> mesh2areas(const std::vector<std::vector<double> > mesh) {
  std::vector<double> out;
  for (std::vector<std::vector<double> >::const_iterator it = mesh.begin();
       it != mesh.end(); it++) {
    long nvert = static_cast<long>(it->size()) / 3;
    std::vector<double> sum(3, 0.0);
    std::vector<double> vi(3);
    std::vector<double> vin1(3);
    std::vector<double> cross(3);
    for (long i = 0; i < nvert; i++) {
      vi.assign(it->begin() + (3 * i), it->begin() + (3 * (i + 1)));
      if (i == 0)
	vin1.assign(it->begin() + (3 * (nvert - 1)),
		    it->begin() + (3 * nvert));
      else
	vin1.assign(it->begin() + (3 * (i - 1)),
		    it->begin() + (3 * i));
      cross = cross_product_3d(vi, vin1);
      for (size_t j = 0; j < 3; j++)
	sum[j] = sum[j] + cross[j];
    }
    double total = 0.0;
    for (size_t j = 0; j < 3; j++) {
      sum[j] /= 2;
      total += std::pow(sum[j], 2);
    }
    out.push_back(std::sqrt(total));
  }
  return out;
}


//! Generic ply geometry element
class PlyElement {
public:
  //! Empty constructor.
  //! \param parent0 Element set containing this element.
  PlyElement(PlyElementSet* parent0=NULL) : parent(parent0), property_order(), colors(), properties() {
    if (parent0 != NULL)
      init_from_parent_();
  }
  //! \brief Copy constructor.
  //! \param rhs Element to copy.
  PlyElement(const PlyElement &rhs) : parent(rhs.parent), property_order(rhs.property_order), colors(rhs.colors), properties(rhs.properties) {}
  //! \brief Copy constructor.
  //! \param parent0 Parent to set for copy.
  //! \param rhs Element to copy.
  PlyElement(PlyElementSet* parent0, const PlyElement &rhs) : parent(parent0), property_order(rhs.property_order), colors(rhs.colors), properties(rhs.properties) {}
  //! \brief Create an element by reading from an input stream.
  //! \param parent0 Element set containing this element.
  //! \param in Input stream.
  PlyElement(PlyElementSet* parent0, std::istream &in) :
    parent(parent0), property_order(), colors(), properties() {
    init_from_parent_();
    read(in);
  }
  //! \brief Create an element from a vector of property values.
  //! \tparam Type of property values.
  //! \param parent0 Element set containing this element.
  //! \param arr Property values.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  template<typename T>
  PlyElement(PlyElementSet* parent0,
	     const std::vector<T> &arr, const T* ignore = 0) :
    parent(parent0), property_order(), colors(), properties() {
    init_from_parent_();
    size_t i = 0;
    for (std::vector<std::string>::const_iterator name = property_order.begin(); name != property_order.end(); name++, i++) {
      std::map<std::string, Data>::iterator it = properties.find(*name);
      YGGDRASIL_RAPIDJSON_ASSERT(it != properties.end());
      YGGDRASIL_RAPIDJSON_ASSERT(i < arr.size());
      if ((it != properties.end()) && (i < arr.size())) {
        if (it->second.f & kListFlag) {
          it->second.assign(arr, ignore);
        } else {
          if (ignore && internal::values_eq(arr[i], *ignore)) return;
          it->second.assign(arr[i]);
        }
      }
    }
  }

  enum ElementType {
    kNullFlag       = 0x0000,
    kInt8Flag       = 0x0008,
    kUint8Flag      = 0x0010,
    kInt16Flag      = 0x0020,
    kUint16Flag     = 0x0040,
    kInt32Flag      = 0x0080,
    kUint32Flag     = 0x0100,
    kFloatFlag      = 0x0200,
    kDoubleFlag     = 0x0400,
    kListFlag       = 0x0800
  };
#if !YGGDRASIL_RAPIDJSON_HAS_CXX11
  PlyElement& operator=(const PlyElement& other) {
    new (this) PlyElement(other);
    return *this;
  }
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
private:
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
  //! Disable copy assignment for elements.
  PlyElement& operator=(const PlyElement& other);
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  void init_from_parent_();
  struct Number {
    int64_t i64;
    NUMBER_MEMBER_(F, f, float, int16_t, int8_t, int8_t);
    NUMBER_MEMBER_CHAR_(I8, i8, int8_t, int8_t, int16_t, int32_t);
    NUMBER_MEMBER_CHAR_(U8, u8, uint8_t, int8_t, int16_t, int32_t);
    NUMBER_MEMBER_(I16, i16, int16_t, int16_t, int16_t, int16_t);
    NUMBER_MEMBER_(U16, u16, uint16_t, int16_t, int16_t, int16_t);
    NUMBER_MEMBER_(I32, i32, int32_t, int16_t, int8_t, int8_t);
    NUMBER_MEMBER_(U32, u32, uint32_t, int16_t, int8_t, int8_t);
    double d;
    Number() :
      i64(0), f(0.0), i8(0), u8(0), i16(0), u16(0), i32(0), u32(0), d(0.0) {}
    // Number() : Number(0) { memset(this, 0, sizeof(Number)); }
    //! \brief Create a zeroed number instance.
    //! \param flag Flag indicating what type to store 0 as.
    Number(const uint16_t &flag) :
      i64(0), f(0.0), i8(0), u8(0), i16(0), u16(0), i32(0), u32(0), d(0.0)
    { this->assign(flag, 0); }
    //! \brief Read number data from an input stream.
    //! \param flag Flag indicating what type of data to read.
    //! \param in Input stream.
    Number(const uint16_t &flag, std::istream &in) :
      i64(0), f(0.0), i8(0), u8(0), i16(0), u16(0), i32(0), u32(0), d(0.0) {
      this->assign(flag, 0);
      this->read(flag, in);
    }
    //! \brief Create an number instance from a scalar.
    //! \tparam T Type of scalar.
    //! \param flag Flag indicating what type to store x as.
    //! \param x Scalar data to store.
    template <typename T>
    Number(const uint16_t &flag, const T &x) :
      i64(0), f(0.0), i8(0), u8(0), i16(0), u16(0), i32(0), u32(0), d(0.0) {
      this->assign(flag, x);
    }
    //! \brief Determine if the value is the default.
    //! \param flag Flag indicating what type is stored.
    //! \return true if the value is default, false otherwise.
    bool is_default(const uint16_t &flag) const {
      switch (flag) {
      case (kInt8Flag) :
      case (kUint8Flag) :
      case (kInt16Flag) :
      case (kUint16Flag) :
      case (kInt32Flag) :
      case (kUint32Flag) :
	return (get_value_as<int>(flag) == default_value<int>(flag));
      case (kFloatFlag) :
      case (kDoubleFlag) :
	return internal::values_eq(get_value_as<double>(flag),
				default_value<double>(flag));
      default: return false;
      }
    }
    //! \brief Determine if the number has a default value.
    //! \param flag Flag indicating type of stored data.
    //! \return true if there is a default, false otherwise.
    static bool has_default(const uint16_t &flag) {
      switch (flag & ~kListFlag) {
      case (kUint8Flag) :
      case (kUint16Flag) :
      case (kUint32Flag) :
	return false;
      default:
	return true;
      }
    }
    //! \brief Get default value.
    //! \param flag Flag indicating type of stored data.
    //! \return The default value for a value of the specified type.
    template<typename T>
    static T default_value(const uint16_t &flag) {
      switch (flag & ~kListFlag) {
      case (kUint8Flag) :
      case (kUint16Flag) :
      case (kUint32Flag) :
	return 0;
      case (kInt8Flag) :
      case (kInt16Flag) :
      case (kInt32Flag) :
	return -1;
      default:
	if (internal::IsSame<T, double>::Value)
	  return (T)NAN;
	return -1;
      }
    }
    //! \brief Assign a scalar value to this instance.
    //! \tparam T Type of scalar.
    //! \param flag Flag indicating what type to store x as.
    //! \param x Scalar data to store.
    template <typename T>
    void assign(const uint16_t &flag, const T &x) {
      switch (flag) {
      case (kInt8Flag) : i8 = I8((int8_t)(x)); break;
      case (kUint8Flag) : u8 = U8((uint8_t)(x)); break;
      case (kInt16Flag) : i16 = I16((int16_t)(x)); break;
      case (kUint16Flag) : u16 = U16((uint16_t)(x)); break;
      case (kInt32Flag) : i32 = I32((int32_t)(x)); break;
      case (kUint32Flag) : u32 = U32((uint32_t)(x)); break;
      case (kFloatFlag) : f = F((float)(x)); break;
      case (kDoubleFlag) : d = (double)(x); break;
      default: i64 = (int64_t)(x); break;
      }
    }
    //! \brief Read number data from an input stream.
    //! \param flag Flag indicating the type of data to read.
    //! \param in Input stream.
    //! \return Input stream.
    std::istream & read(const uint16_t &flag, std::istream &in) {
      switch (flag) {
      case (kInt8Flag) : return i8.read(in);
      case (kUint8Flag) : return u8.read(in);
      case (kInt16Flag) : return i16.read(in);
      case (kUint16Flag) : return u16.read(in);
      case (kInt32Flag) : return i32.read(in);
      case (kUint32Flag) : return u32.read(in);
      case (kFloatFlag) : return f.read(in);
      case (kDoubleFlag) : in >> d; return in;
      default: YGGDRASIL_RAPIDJSON_ASSERT(false);
      }
      return in;
    }
    //! \brief Write number data to an output stream.
    //! \param flag Flag indicating the type of data in the instance.
    //! \param out Output stream.
    //! \return Output stream.
    std::ostream & write(const uint16_t &flag, std::ostream &out) const {
      switch (flag) {
      case (kInt8Flag) : return i8.write(out);
      case (kUint8Flag) : return u8.write(out);
      case (kInt16Flag) : return i16.write(out);
      case (kUint16Flag) : return u16.write(out);
      case (kInt32Flag) : return i32.write(out);
      case (kUint32Flag) : return u32.write(out);
      case (kFloatFlag) : return f.write(out);
      case (kDoubleFlag) : out << d; return out;
      default: YGGDRASIL_RAPIDJSON_ASSERT(false);
      }
      return out;
    }
    //! \brief Check if this number is equivalent to another.
    //! \param flag Flag indicating the type of data in both numbers.
    //! \param y Instance for comparison.
    //! \return true if this instances is equivalent to y.
    bool is_equal(const uint16_t &flag, const Number& y) const {
      switch (flag) {
      case (kInt8Flag) : return i8.is_equal(y.i8);
      case (kUint8Flag) : return u8.is_equal(y.u8);
      case (kInt16Flag) : return i16.is_equal(y.i16);
      case (kUint16Flag) : return u16.is_equal(y.u16);
      case (kInt32Flag) : return i32.is_equal(y.i32);
      case (kUint32Flag) : return u32.is_equal(y.u32);
      case (kFloatFlag) : return f.is_equal(y.f);
      case (kDoubleFlag) : return internal::values_eq(d, y.d);
      default: YGGDRASIL_RAPIDJSON_ASSERT(false);
      }
      return false;
    }
    //! \brief Get a value as cast to a new type.
    //! \tparam Type to return.
    //! \param flag Type flag indicating the type of data stored.
    //! \returns Cast value.
    template <typename T>
    T get_value_as(const uint16_t &flag) const {
      switch (flag) {
      case (kInt8Flag) : return (T)(i8.v);
      case (kUint8Flag) : return (T)(u8.v);
      case (kInt16Flag) : return (T)(i16.v);
      case (kUint16Flag) : return (T)(u16.v);
      case (kInt32Flag) : return (T)(i32.v);
      case (kUint32Flag) : return (T)(u32.v);
      case (kFloatFlag) : return (T)(f.v);
      case (kDoubleFlag) : return (T)(d);
      default: YGGDRASIL_RAPIDJSON_ASSERT(false);
      }
      return 0;
    }
    //! \brief Increment the data inplace.
    //! \param x Scalar to increment by.
    //! \param flag Type flag indicating the type of data stored.
    template <typename T>
    void add_inplace(const uint16_t &flag, const T& x) {
      T new_value = get_value_as<T>(flag) + x;
      assign<T>(flag, new_value);
    }
  }; // 8 bytes
  struct Data {
    Data() : f(0), n(0), elements() {}  //  memset(this, 0, sizeof(Data)); }
    //! \brief Create an empty data instance with type information.
    //! \param flag Flag indicating the type that should be used to store the
    //!    data.
    Data(const uint16_t flag) : f(flag), n(flag), elements() {}
    //! \brief Read data value(s) from an input stream.
    //! \param flag Flag indicating the type that should be used to store the
    //!    data.
    //! \param in Input stream.
    Data(const uint16_t flag, std::istream &in) :
      f(flag), n(flag), elements() {
      read(in);
    }
    //! \brief Create a data instance from a scalar value.
    //! \tparam T Type of scalar data.
    //! \param flag Flag indicating the type that should be used to store the
    //!    data.
    //! \param x Scalar data.
    template<typename T>
    Data(const uint16_t flag, const T &x) :
      f(flag), n(flag), elements() {
      assign(x);
    }
    //! \brief Create a data instance from a vector of values.
    //! \tparam T Type of data in the vector.
    //! \param flag Flag indicating the type that should be used to store the
    //!    data.
    //! \param x Vector of values.
    //! \param ignore Value to ignore. After this value is encountered for an
    //!   element will be added.
    template<typename T>
    Data(const uint16_t flag, const std::vector<T> &x, const T* ignore = 0) :
      f(flag), n(flag), elements() {
      YGGDRASIL_RAPIDJSON_ASSERT(flag & kListFlag);
      uint16_t element_flags = (uint16_t)(flag & ~kListFlag);
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
      for (typename std::vector<T>::const_iterator it = x.begin(); it != x.end(); it++) {
	if (ignore && internal::values_eq(*ignore, *it)) return;
	elements.emplace_back(element_flags, *it);
      }
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
      for (typename std::vector<T>::const_iterator it = x.begin(); it != x.end(); it++) {
	if (ignore && internal::values_eq(*ignore, *it)) return;
	elements.push_back(Number(element_flags, *it));
      }
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    }
    //! \brief Read data value(s) from an input stream.
    //! \param in Input stream.
    void read(std::istream &in) {
      if (f & kListFlag) {
	uint16_t element_flags = (uint16_t)(f & ~kListFlag);
	size_t size = 0;
	in >> size;
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
	for (size_t i = 0; i < size; i++)
	  elements.emplace_back(element_flags, in);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
	for (size_t i = 0; i < size; i++)
	  elements.push_back(Number(element_flags, in));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
      } else {
	n.read(f, in);
      }
    }
    //! \brief Assign a vector of values.
    //! \tparam Scalar type.
    //! \param x Scalar.
    template<typename T>
    void assign(const std::vector<T>& x, const T* ignore = 0) {
      YGGDRASIL_RAPIDJSON_ASSERT(f & kListFlag);
      uint16_t element_flags = (uint16_t)(f & ~kListFlag);
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
      for (typename std::vector<T>::const_iterator it = x.begin(); it != x.end(); it++) {
	if (ignore && internal::values_eq(*ignore, *it)) return;
	elements.emplace_back(element_flags, *it);
      }
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
      for (typename std::vector<T>::const_iterator it = x.begin(); it != x.end(); it++) {
	if (ignore && internal::values_eq(*ignore, *it)) return;
	elements.push_back(Number(element_flags, *it));
      }
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    }
    //! \brief Assign a scalar value.
    //! \tparam Scalar type.
    //! \param x Scalar.
    template<typename T>
    void assign(const T& x) {
      YGGDRASIL_RAPIDJSON_ASSERT(!(f & kListFlag));
      n.assign(f, x);
    }
    //! \brief Increment the data inplace.
    //! \param x Scalar to increment by.
    //! \return Result of addition.
    template<typename T>
    Data& operator+=(const T& x) {
      uint16_t element_flags = (uint16_t)(f & ~kListFlag);
      if (f & kListFlag) {
	for (std::vector<Number>::iterator it = elements.begin();
	     it != elements.end(); it++) {
	  it->add_inplace(element_flags, x);
	}
      } else {
	n.add_inplace(element_flags, x);
      }
      return *this;
    }
    //! \brief Write data to an output stream.
    //! \param out Output stream.
    void write(std::ostream &out) const {
      if (f & kListFlag) {
	uint16_t element_flags = (uint16_t)(f & ~kListFlag);
	out << elements.size();
	for (std::vector<Number>::const_iterator it = elements.begin(); it != elements.end(); it++) {
	  out << " ";
	  it->write(element_flags, out);
	}
      } else {
	n.write(f, out);
      }
    }
    //! \brief Check if this data is equivalent to another Data instance.
    //! \param y Instance for comparison.
    //! \return true if this instance is equivalent to y.
    bool is_equal(const Data& y) const {
      if (f != y.f) return false;
      if (f & kListFlag) {
	if (elements.size() != y.elements.size()) return false;
	uint16_t element_flags = (uint16_t)(f & ~kListFlag);
	for (std::vector<Number>::const_iterator it1 = elements.begin(), it2 = y.elements.begin();
	     it1 != elements.end(); it1++, it2++) {
	  if (!(it1->is_equal(element_flags, *it2))) return false;
	}
	return true;
      } else {
	return n.is_equal(f, y.n);
      }
    }
    //! \brief Get the number of elements in the data object.
    //! \return Number of elements.
    size_t size() const {
      if (f & kListFlag) return elements.size();
      return 1;
    }
    //! \brief Determine if the data contains multiple elements.
    //! \return true if there are multiple elements, false otherwise.
    bool is_vector() const {
      return (f & kListFlag);
    }
    //! \brief Get the type flag associated with the data.
    //! \return flags
    uint16_t flags() const {
      return f;
    }
    //! \brief Determine if the data has a default value.
    //! \return true if there is a default, false otherwise.
    bool has_default() const {
      return n.has_default(f);
    }
    //! \brief Determine if the value is the default.
    //! \return true if the value is default, false otherwise.
    bool is_default() const {
      if (is_vector()) return false;
      return n.is_default(f);
    }
    //! \brief Get default value.
    //! \return The default value for a value of the specified type.
    template<typename T>
    T default_value() const {
      return Number::default_value<T>(f);
    }
    //! \brief Remove defaults from list
    void prune_defaults() {
      if (!(f & kListFlag)) return;
      for (std::vector<Number>::iterator it = elements.begin();
	   it != elements.end(); it++) {
	if (it->is_default((uint16_t)(f & ~kListFlag))) {
	  elements.erase(it, elements.end());
	  return;
	}
      }
    }
    //! \brief Determine if the data contains floating point values.
    //! \return true if there are floating point values, false otherwise.
    bool requires_double() const {
      return f & (kFloatFlag | kDoubleFlag);
    }
    //! \brief Get a value as cast to a new type.
    //! \tparam Type to return.
    //! \returns Cast value.
    template <typename T>
    T get_value_as() const {
      return n.get_value_as<T>(f);
    }
    //! \brief Get a list element as cast to a new type.
    //! \tparam Type to return.
    //! \param i Index of element to return.
    //! \returns Cast value.
    template <typename T>
    T get_value_as(size_t i) const {
      return elements[i].get_value_as<T>((uint16_t)(f & ~kListFlag));
    }
    //! Flag indicating the data type.
    uint16_t f;
    // union {
    //! Numeric data component.
    Number n;
    //! Vector of numeric data components.
    std::vector<Number> elements;
    // };
  };

  //! \brief Add a property value from a Number instance to a vector.
  //! \param x Number instance.
  //! \param flag Type flag indicating the type of data stored in x.
  //! \param[in,out] out Vector to add property value to.
  template <typename T>
  void extend_aray_data_number(const Number &x, const uint16_t &flag,
			       std::vector<T> &out) const {
    switch (flag) {
    case (kInt8Flag) : out.push_back((T)(x.i8.v)); break;
    case (kUint8Flag) : out.push_back((T)(x.u8.v)); break;
    case (kInt16Flag) : out.push_back((T)(x.i16.v)); break;
    case (kUint16Flag) : out.push_back((T)(x.u16.v)); break;
    case (kInt32Flag) : out.push_back((T)(x.i32.v)); break;
    case (kUint32Flag) : out.push_back((T)(x.u32.v)); break;
    case (kFloatFlag) : out.push_back((T)(x.f.v)); break;
    case (kDoubleFlag) : out.push_back((T)(x.d)); break;
    default: YGGDRASIL_RAPIDJSON_ASSERT(false);
    }
  }

  //! \brief Add property values from a Data instance to a vector.
  //! \param d Data instance.
  //! \param[in,out] out Vector to add property values to.
  template <typename T>
  void extend_aray_data(const Data &d, std::vector<T> &out) const {
    if (d.f & kListFlag) {
      uint16_t element_flags = (uint16_t)(d.f & ~kListFlag);
      for (std::vector<Number>::const_iterator it = d.elements.begin(); it != d.elements.end(); it++)
	extend_aray_data_number(*it, element_flags, out);
    } else {
      extend_aray_data_number(d.n, d.f, out);
    }
  }

  friend class PlyElementSet;
  template<typename T>
  friend inline uint16_t type2flag();
  
public:
  //! Element set containing this element.
  PlyElementSet* parent;
  //! Names of properties defining the element in the order they are read/
  //!   written when serialized.
  std::vector<std::string> property_order;
  //! Names of colors properties for the element.
  std::vector<std::string> colors;
  //! Mapping between property names and the property values.
  std::map<std::string, Data> properties;

  //! \brief Set a vector property by name.
  //! \tparam Value type.
  //! \param name Name of property to set.
  //! \param values Property values.
  //! \param isColor If true, the property is treated as a color.
  //! \return true if successful, false otherwise.
  template <typename T>
  bool set_property(const std::string name, const std::vector<T>& values, bool isColor = false);
  //! \brief Set a scalar property by name.
  //! \tparam Value type.
  //! \param name Name of property to set.
  //! \param value Property value.
  //! \param isColor If true, the property is treated as a color.
  //! \return true if successful, false otherwise.
  template <typename T>
  bool set_property(const std::string name, const T& value, bool isColor = false);
  //! \brief Determine if the data contains multiple elements.
  //! \param name Property to check.
  //! \return true if there are multiple elements, false otherwise.
  bool is_vector(const std::string name) const {
    std::map<std::string, Data>::const_iterator it = properties.find(name);
    bool out = false;
    if (it != properties.end())
      out = it->second.is_vector();
    return out;
  }
  //! \brief Get the type flag associated with the data ina property.
  //! \param name Property to check.
  //! \return flags
  uint16_t flags(const std::string name) const {
    std::map<std::string, Data>::const_iterator it = properties.find(name);
    if (it != properties.end())
      return it->second.flags();
    return 0;
  }
  //! \brief Determine if a property contains floating point values.
  //! \param name Property to check.
  //! \return true if there are floating point values, false otherwise.
  bool requires_double(const std::string name) const {
    std::map<std::string, Data>::const_iterator it = properties.find(name);
    bool out = false;
    if (it != properties.end())
      out = it->second.requires_double();
    return out;
  }
  //! \brief Get a property value as cast to a new type.
  //! \tparam Type to return.
  //! \param name Property to return.
  //! \returns Cast value.
  template <typename T>
  T get_value_as(const std::string name) const {
    std::map<std::string, Data>::const_iterator it = properties.find(name);
    T out = 0;
    if (it != properties.end())
      out = it->second.get_value_as<T>();
    return out;
  }
  //! \brief Get a list property element as cast to a new type.
  //! \tparam Type to return.
  //! \param name Property to return.
  //! \param i Index of element to return.
  //! \returns Cast value.
  template <typename T>
  T get_value_as(const std::string name, size_t i) const {
    std::map<std::string, Data>::const_iterator it = properties.find(name);
    T out = 0;
    if (it != properties.end())
      out = it->second.get_value_as<T>(i);
    return out;
  }
  //! \brief Convert a ply serialized type name to a type flag.
  //! \param type Ply serialized type name.
  //! \return Type flag.
  static uint16_t typename2flag(const std::string& type) {
    if (type == "list")
      return kListFlag;
    else if (type == "char")
      return kInt8Flag;
    else if (type == "uchar")
      return kUint8Flag;
    else if (type == "short")
      return kInt16Flag;
    else if (type == "ushort")
      return kUint16Flag;
    else if (type == "int")
      return kInt32Flag;
    else if (type == "uint")
      return kUint32Flag;
    else if (type == "float")
      return kFloatFlag;
    else if (type == "double")
      return kDoubleFlag;
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(std::string("Unsupported type: ") + type));
    return 0;
  }
  //! \brief Convert a type flag into the ply serialized type name.
  //! \param type Type flag.
  //! \return Ply serialized type name.
  static std::string flag2typename(const uint16_t& type) {
    if (type & kListFlag) {
      return "list";
    }
    switch (type) {
    case kInt8Flag:
      return "char";
    case kUint8Flag:
      return "uchar";
    case kInt16Flag:
      return "short";
    case kUint16Flag:
      return "ushort";
    case kInt32Flag:
      return "int";
    case kUint32Flag:
      return "uint";
    case kFloatFlag:
      return "float";
    case kDoubleFlag:
      return "double";
    default:
      YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(std::string("Unsupported type: ") + std::to_string(type)));
    }
    return "";
  }
  //! \brief Check if this element is equivalent to another.
  //! \param rhs Element for comparison.
  //! \return true if this element is equivalent to rhs.
  bool is_equal(const PlyElement& rhs) const {
    if (this->property_order.size() != rhs.property_order.size())
      return false;
    if (this->properties.size() != rhs.properties.size())
      return false;
    for (size_t i = 0; i < this->property_order.size(); i++) {
      if (this->property_order[i] != rhs.property_order[i])
	return false;
    }
    for (std::map<std::string, Data>::const_iterator lit = this->properties.begin(); lit != this->properties.end(); lit++) {
      std::map<std::string, Data>::const_iterator rit = rhs.properties.find(lit->first);
      YGGDRASIL_RAPIDJSON_ASSERT(rit != rhs.properties.end());
      if (rit == rhs.properties.end())
	return false;
      if (!(lit->second.is_equal(rit->second)))
	return false;
    }
    return true;
  }
  //! \brief Write element properties to an output stream.
  //! \param out Output stream.
  //! \return Output stream.
  std::ostream & write(std::ostream &out,
		       std::map<std::string, uint16_t> property_flags) const {
    for (std::vector<std::string>::const_iterator name = property_order.begin(); name != property_order.end(); name++) {
      std::map<std::string, Data>::const_iterator it = properties.find(*name);
      if (name != property_order.begin())
	out << " ";
      if (it == properties.end()) {
	std::map<std::string, uint16_t>::const_iterator it_flag = property_flags.find(*name);
	if (it_flag == property_flags.end())
	  out << Number::default_value<int>(kFloatFlag);
	else if (it_flag->second & (kFloatFlag | kDoubleFlag))
	  out << Number::default_value<double>(it_flag->second);
	else
	  out << Number::default_value<int>(it_flag->second);
      } else {
	it->second.write(out);
      }
    }
    out << std::endl;
    return out;
  }
  //! \brief Read in element properties from an input stream.
  //! \param in Input stream.
  //! \return Input stream.
  std::istream & read(std::istream &in) {
    std::vector<std::string> to_erase;
    for (std::vector<std::string>::const_iterator name = property_order.begin(); name != property_order.end(); name++) {
      std::map<std::string, Data>::iterator it = properties.find(*name);
      YGGDRASIL_RAPIDJSON_ASSERT(it != properties.end());
      if (it == properties.end()) continue;
      it->second.read(in);
      if (it->second.has_default()) {
	if (it->second.is_vector())
	  it->second.prune_defaults();
	else if (it->second.is_default())
	  to_erase.push_back(it->first);
      }
    }
    for (std::vector<std::string>::const_iterator name = to_erase.begin();
	 name != to_erase.end(); name++)
      properties.erase(*name);
    return in;
  }
  //! \brief Retrieve a value of a specific type from a Data instance.
  //! \tparam T Type of values to retrieve.
  //! \param x Data instance.
  //! \return Data value.
  template <typename T>
  static T get_scalar(const Data &x) {
    YGGDRASIL_RAPIDJSON_ASSERT(!(x.f & kListFlag));
    if (x.f & kInt8Flag)
      return (T)(x.n.i8.v);
    else if (x.f & kUint8Flag)
      return (T)(x.n.u8.v);
    else if (x.f & kInt16Flag)
      return (T)(x.n.i16.v);
    else if (x.f & kUint16Flag)
      return (T)(x.n.u16.v);
    else if (x.f & kInt32Flag)
      return (T)(x.n.i32.v);
    else if (x.f & kUint32Flag)
      return (T)(x.n.u32.v);
    else if (x.f & kFloatFlag)
      return (T)(x.n.f.v);
    else if (x.f & kDoubleFlag)
      return (T)(x.n.d);
    YGGDRASIL_RAPIDJSON_ASSERT(!sizeof("Cannot get scalar for type"));
    return T(0);
  }
  //! \brief Get the number of values in the element.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \return Number of values.
  size_t size(bool skipColors=false) const {
    size_t out = 0;
    for (std::vector<std::string>::const_iterator name = property_order.begin(); name != property_order.end(); name++) {
      std::map<std::string, Data>::const_iterator it = properties.find(*name);
      if (skipColors && !colors.empty() && *name == colors[0]) break;
      if (it != properties.end())
	out += it->second.size();
    }
    return out;
  }
  //! \brief Get element values as an array of ints.
  //! \param nvert Number of vertices previously added to an ObjWavefront
  //!   object being constructed from this geometry.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \param minSize Minimum number of values that should be added for the
  //!   element. If the number of values is smaller, the vector will be
  //!   padded with defaultValue.
  //! \param defaultValue Value to pad vector with if there are fewer values
  //!   than minSize.
  //! \return Array of int values.
  std::vector<int> get_int_array(const size_t nvert=0,
				 bool skipColors=false,
				 const size_t minSize=0,
				 const int defaultValue=-1) const {
    std::vector<int> out;
    get_int_array(out, nvert, skipColors, minSize, defaultValue);
    return out;
  }
  //! \brief Get element values as an array of ints.
  //! \param out Vector to add values to.
  //! \param nvert Number of vertices previously added to an ObjWavefront
  //!   object being constructed from this geometry.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \param minSize Minimum number of values that should be added for the
  //!   element. If the number of values is smaller, the vector will be
  //!   padded with defaultValue.
  //! \param defaultValue Value to pad vector with if there are fewer values
  //!   than minSize.
  void get_int_array(std::vector<int>& out,
		     const size_t nvert=0,
		     bool skipColors=false,
		     const size_t minSize = 0,
		     const int defaultValue = -1) const {
    size_t nPrev = out.size();
    for (std::vector<std::string>::const_iterator name = property_order.begin(); name != property_order.end(); name++) {
      if (skipColors && !colors.empty() && colors[0] == *name) break;
      std::map<std::string, Data>::const_iterator it = properties.find(*name);
      YGGDRASIL_RAPIDJSON_ASSERT(it != properties.end());
      if (it != properties.end())
	extend_aray_data(it->second, out);
    }
    if (nvert > 0) {
      for (size_t i = nPrev; i < out.size(); i++)
	out[i] = out[i] + 1;
    }
    size_t nValue = out.size() - nPrev;
    if (nValue < minSize) {
      for (size_t i = nValue; i < minSize; i++)
	out.push_back(defaultValue);
    }
  }
  //! \brief Get element values as an array of doubles.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \param minSize Minimum number of values that should be added for the
  //!   element. If the number of values is smaller, the vector will be
  //!   padded with defaultValue.
  //! \param defaultValue Value to pad vector with if there are fewer values
  //!   than minSize.
  //! \return Array of double values.
  std::vector<double> get_double_array(bool skipColors=false,
				       const size_t minSize=0,
				       const double defaultValue=NAN) const {
    std::vector<double> out;
    get_double_array(out, skipColors, minSize, defaultValue);
    return out;
  }
  //! \brief Get element values as an array of doubles.
  //! \param out Array to add values to.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \param minSize Minimum number of values that should be added for the
  //!   element. If the number of values is smaller, the vector will be
  //!   padded with defaultValue.
  //! \param defaultValue Value to pad vector with if there are fewer values
  //!   than minSize.
  void get_double_array(std::vector<double>& out,
			bool skipColors=false,
			const size_t minSize=0,
			const double defaultValue=NAN) const {
    size_t nPrev = out.size();
    for (std::vector<std::string>::const_iterator name = property_order.begin(); name != property_order.end(); name++) {
      if (skipColors && !colors.empty() && colors[0] == *name) break;
      std::map<std::string, Data>::const_iterator it = properties.find(*name);
      YGGDRASIL_RAPIDJSON_ASSERT(it != properties.end());
      if (it != properties.end())
	extend_aray_data(it->second, out);
    }
    size_t nValue = out.size() - nPrev;
    if (nValue < minSize) {
      for (size_t i = nValue; i < minSize; i++)
	out.push_back(defaultValue);
    }
  }
  //! \brief Get the colors for an element set in arrayform.
  //! \param defaultValue Value to add if colors are missing.
  //! \returns The colors for the requirested type in array form.
  std::vector<uint8_t> get_colors_array(uint8_t defaultValue=0) const {
    std::vector<uint8_t> out;
    get_colors_array(out, defaultValue);
    return out;
  }
  //! \brief Get the colors for an element set in arrayform.
  //! \param out Array to add values to.
  //! \param defaultValue Value to add if colors are missing.
  void get_colors_array(std::vector<uint8_t>& out,
			uint8_t defaultValue=0) const {
    for (std::vector<std::string>::const_iterator name = colors.begin(); name != colors.end(); name++) {
      std::map<std::string, Data>::const_iterator it = properties.find(*name);
      if (it != properties.end())
	extend_aray_data(it->second, out);
      else
	out.push_back(defaultValue);
    }
  }
  //! \brief Add element colors to this element.
  //! \param arr Colors for this element.
  //! \param properties0 Map between property names and a flag indicating
  //!   the data type for the property values.
  //! \param property_colors The names of color properties defined in arr.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool add_colors(const T* arr,
		  const std::map<std::string, uint16_t> &properties0,
		  const std::vector<std::string>& property_colors) {
    if (colors.empty()) {
      colors = property_colors;
      size_t i = 0;
      for (std::vector<std::string>::const_iterator name = colors.begin();
	   name != colors.end(); name++, i++) {
	property_order.push_back(*name);
	std::map<std::string, uint16_t>::const_iterator it = properties0.find(*name);
	YGGDRASIL_RAPIDJSON_ASSERT(it != properties0.end());
	if (it == properties0.end()) return false;
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
	properties.emplace(std::piecewise_construct,
			   std::forward_as_tuple(*name),
			   std::forward_as_tuple(it->second, arr[i]));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
	properties[*name] = Data(it->second, arr[i]);
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
      }
    } else {
      if (colors != property_colors)
	return false;
      size_t i = 0;
      for (std::vector<std::string>::const_iterator name = colors.begin();
	   name != colors.end(); name++, i++) {
	std::map<std::string, uint16_t>::const_iterator it = properties0.find(*name);
	YGGDRASIL_RAPIDJSON_ASSERT(it != properties0.end());
	if (it == properties0.end()) return false;
	properties[*name].n.assign(it->second, arr[i]);
      }
    }
    return true;
  }
  //! \brief Increase indexes.
  //! \param N Amount to increment indexes by.
  //! \param maxProp Maximum number of properties to increase the index of.
  //!   Ignored if 0.
  void increase_index(const size_t N, size_t maxProp = 0) {
    size_t iProp = 0;
    for (std::vector<std::string>::iterator name = property_order.begin(); name != property_order.end(); name++, iProp++) {
      if (maxProp > 0 && iProp >= maxProp) break;
      std::map<std::string, Data>::iterator it = properties.find(*name);
      if (it != properties.end()) {
	it->second += N;
      }
    }
  }
  
  friend bool operator == (const PlyElement& lhs, const PlyElement& rhs);
};

//! \brief Check if two PlyElement instances are equivalent.
//! \param lhs First element for comparison.
//! \param rhs Second element for comparison.
//! \return true if the two elements are equivalent.
inline
bool operator == (const PlyElement& lhs, const PlyElement& rhs)
{ return lhs.is_equal(rhs); }

//! \brief Get the flag indicating a type.
//! \tparam T Type to get flag for.
template<typename T>
inline uint16_t type2flag() { return PlyElement::kNullFlag; }
//! \brief Get the flag indicating the int8_t type.
template<>
inline uint16_t type2flag<int8_t>() { return PlyElement::kInt8Flag; }
//! \brief Get the flag indicating the uint8_t type.
template<>
inline uint16_t type2flag<uint8_t>() { return PlyElement::kUint8Flag; }
//! \brief Get the flag indicating the int16_t type.
template<>
inline uint16_t type2flag<int16_t>() { return PlyElement::kInt16Flag; }
//! \brief Get the flag indicating the uint16_t type.
template<>
inline uint16_t type2flag<uint16_t>() { return PlyElement::kUint16Flag; }
//! \brief Get the flag indicating the int32_t type.
template<>
inline uint16_t type2flag<int32_t>() { return PlyElement::kInt32Flag; }
//! \brief Get the flag indicating the uint32_t type.
template<>
inline uint16_t type2flag<uint32_t>() { return PlyElement::kUint32Flag; }
//! \brief Get the flag indicating the float type.
template<>
inline uint16_t type2flag<float>() { return PlyElement::kFloatFlag; }
//! \brief Get the flag indicating the double type.
template<>
inline uint16_t type2flag<double>() { return PlyElement::kDoubleFlag; }

//! Container for a set of ply elements.
class PlyElementSet {
public:
  //! \brief Create an empty element set.
  //! \param name0 Name of the element type in the set.
  PlyElementSet(const std::string& name0="") :
    name(name0), elements(), property_order(), colors(), property_flags(), property_size_flags() {}
  //! \brief Create an empty element set with property information.
  //! \tparam T Data type that will be expected for element property values.
  //!   This is determined by the unused third parameter.
  //! \param name0 Name of the element type in the set.
  //! \param property_names Names of properties defining each element in the
  //!   order they were read or will be written.
  //! \param is_array If true, the provided property is recorded as an array.
  template <typename T>
  PlyElementSet(const std::string& name0,
		const std::vector<std::string> &property_names,
		const std::vector<std::string> &property_colors,
		const T&,
		const bool is_array = false) :
    name(name0), elements(), property_order(),
    colors(property_colors), property_flags(), property_size_flags() {
    set_flags<T>(property_names, is_array);
  }
  //! \brief Create an element set from an array of property values.
  //! \tparam T Type of property values.
  //! \tparam M Number of elements in the set.
  //! \tparam N Number of property values for each element.
  //! \param name0 Name of the element type in the set.
  //! \param arr Array of property values for each element in the set.
  //! \param property_colors Names of properties defining colors for each
  //!   element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  template <typename T, size_t M, size_t N>
  PlyElementSet(const std::string& name0,
		const T (&arr)[M][N],
		const std::vector<std::string> &property_names,
		const std::vector<std::string> &property_colors,
		const T* ignore = 0) :
    name(name0), elements(), property_order(),
    colors(property_colors), property_flags(), property_size_flags() {
    set_flags<T>(property_names, bool(N != (property_names.size())));
    YGGDRASIL_RAPIDJSON_ASSERT((N == property_names.size())
		     || (property_names.size() == 1));
    for (size_t i = 0; i < M; i++)
      add_element(std::vector<T>(arr[i], arr[i] + N), ignore);
  }
  //! \brief Create an element set from an array of property values.
  //! \tparam T Type of property values.
  //! \param name0 Name of the element type in the set.
  //! \param arr Array of property values for each element in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of property values for each element.
  //! \param property_names Names of properties defining each element in the
  //!   order they were read or will be written.
  //! \param property_colors Names of properties defining colors for each
  //!   element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  template <typename T>
  PlyElementSet(const std::string& name0,
		const T* arr, size_t M, size_t N,
		const std::vector<std::string> &property_names,
		const std::vector<std::string> &property_colors,
		const T* ignore = 0) :
    name(name0), elements(), property_order(),
    colors(property_colors), property_flags(), property_size_flags() {
    set_flags<T>(property_names, bool(N != (property_names.size())));
    YGGDRASIL_RAPIDJSON_ASSERT((N == property_names.size())
		     || (property_names.size() == 1));
    for (size_t i = 0; i < M; i++)
      add_element(std::vector<T>(arr + (i * N), arr + (i * N) + N), ignore);
  }
  //! \brief Copy constructor.
  //! \param other Set to copy.
  PlyElementSet(const PlyElementSet& other) :
    name(other.name), elements(),
    property_order(other.property_order), colors(other.colors),
    property_flags(other.property_flags),
    property_size_flags(other.property_size_flags) {
    for (size_t i = 0; i < other.elements.size(); i++)
      add_element(other.elements[i]);
  }
    
  //! Name of the type of element in the set.
  std::string name;
  //! Elements in the set.
  std::vector<PlyElement> elements;
  //! The names of properties defining each element in the order that they
  //!   were read or will be written.
  std::vector<std::string> property_order;
  //! Names of colors properties for the element.
  std::vector<std::string> colors;
  //! Mapping between properties and flags defining the types used for the
  //!   property values.
  std::map<std::string, uint16_t> property_flags;
  //! Mapping between properties and the sizes of the properties if they are
  //!   stored/serialized as arrays.
  std::map<std::string, uint16_t> property_size_flags;

  //! \brief Set the type flags for the element set.
  //! \tparam T Data type that will be used to store element properties.
  //! \param property_names Names of properties defining each element.
  //! \param property_colors Names of properties defining colors for each
  //!   element.
  //! \param is_array If true, the provided property is recorded as an array.
  template<typename T>
  void set_flags(const std::vector<std::string> &property_names,
		 const bool is_array) {
    uint16_t flags = type2flag<T>();
    uint16_t size_flags = 0;
    if (is_array) {
      YGGDRASIL_RAPIDJSON_ASSERT(property_names.size() == 1);
      flags = (flags | PlyElement::kListFlag);
      size_flags = PlyElement::kUint8Flag;
    }
    for (typename std::vector<std::string>::const_iterator it = property_names.begin(); it != property_names.end(); it++) {
      property_order.push_back(*it);
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
      property_flags.emplace(std::piecewise_construct,
			     std::forward_as_tuple(*it),
			     std::forward_as_tuple(flags));
      property_size_flags.emplace(std::piecewise_construct,
				  std::forward_as_tuple(*it),
				  std::forward_as_tuple(size_flags));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
      property_flags[*it] = flags;
      property_size_flags[*it] = size_flags;
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    }
  }
  //! \brief Add a single empty element to the geometry.
  //! \returns New element.
  PlyElement* add_element() {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.emplace_back(this);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.push_back(PlyElement(this));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    return &(elements[elements.size() - 1]);
  }
  //! \brief Add an element to the set.
  //! \tparam Type of property values.
  //! \param arr Property values for the new element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \returns New element.
  template<typename T>
  PlyElement* add_element(const std::vector<T> &arr, const T* ignore = 0)
  {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.emplace_back(this, arr, ignore);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.push_back(PlyElement(this, arr, ignore));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    return &(elements[elements.size() - 1]);
  }
  //! \brief Add an element to the set by copying an existing element.
  //! \param other Element to copy.
  //! \returns New element.
  PlyElement* add_element(const PlyElement& other) {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.emplace_back(other);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.push_back(PlyElement(this, other));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    return &(elements[elements.size() - 1]);
  }
  //! \brief Determine if an element set requires doubles to be represented
  //!   as an array.
  //! \return True if the set requires doubles, false otherwise.
  bool requires_double() const {
    for (std::vector<std::string>::const_iterator iname = property_order.begin(); iname != property_order.end(); iname++) {
      std::map<std::string, uint16_t>::const_iterator it = property_flags.find(*iname);
      YGGDRASIL_RAPIDJSON_ASSERT(it != property_flags.end());
      if (it->second & (PlyElement::kFloatFlag | PlyElement::kDoubleFlag))
	return true;
    }
    return false;
  }
  //! \brief Get element values as an array of ints.
  //! \param nvert Number of vertices previously added to an ObjWavefront
  //!   object being constructed from this geometry.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \return Array of int values.
  std::vector<int> get_int_array(const size_t nvert=0,
				 bool skipColors=false) const {
    std::vector<int> out;
    get_int_array(out, nvert, skipColors);
    return out;
  }
  //! \brief Get element values as an array of ints.
  //! \param out Vector to add values to.
  //! \param nvert Number of vertices previously added to an ObjWavefront
  //!   object being constructed from this geometry.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  void get_int_array(std::vector<int>& out,
		     const size_t nvert=0,
		     bool skipColors=false) const {
    size_t minSize = 0;
    if (minSize == 0) {
      for (std::vector<PlyElement>::const_iterator it = elements.begin(); it != elements.end(); it++)
	minSize = (std::max)(minSize, it->size(skipColors));
    }
    for (std::vector<PlyElement>::const_iterator it = elements.begin(); it != elements.end(); it++)
      it->get_int_array(out, nvert, skipColors, minSize, -1);
  }
  //! \brief Get element values as an array of doubles.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \return Array of double values.
  std::vector<double> get_double_array(bool skipColors=false) const {
    std::vector<double> out;
    get_double_array(out, skipColors);
    return out;
  }
  //! \brief Get element values as an array of doubles.
  //! \param out Array to add values to.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  void get_double_array(std::vector<double>& out,
			bool skipColors=false) const {
    double defaultValue = NAN;
    size_t minSize = 0;
    for (std::vector<PlyElement>::const_iterator it = elements.begin(); it != elements.end(); it++)
      minSize = (std::max)(minSize, it->size(skipColors));
    for (std::vector<PlyElement>::const_iterator it = elements.begin(); it != elements.end(); it++)
      it->get_double_array(out, skipColors, minSize, defaultValue);
  }
  //! \brief Get the colors for an element set in arrayform.
  //! \param defaultValue Value to add if colors are missing.
  //! \return The colors for the requirested type in array form.
  std::vector<uint8_t> get_colors_array(uint8_t defaultValue=0) const {
    std::vector<uint8_t> out;
    get_colors_array(out, defaultValue);
    return out;
  }
  //! \brief Get the colors for an element set in arrayform.
  //! \param out Array to add values to.
  //! \param defaultValue Value to add if colors are missing.
  void get_colors_array(std::vector<uint8_t>& out,
			uint8_t defaultValue=0) const {
    if (colors.empty()) return;
    for (std::vector<PlyElement>::const_iterator it = elements.begin(); it != elements.end(); it++)
      it->get_colors_array(out, defaultValue);
  }
  //! \brief Add element colors to a set.
  //! \param arr Colors for each of the elements in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of color properties for each element.
  //! \param property_colors The names of color properties defined in arr.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool add_colors(const T* arr, SizeType M, SizeType N,
		  const std::vector<std::string>& property_colors) {
    if (elements.size() != M || property_colors.size() != N) return false;
    if (colors.size() == 0) {
      colors = property_colors;
      set_flags<T>(property_colors, false);
    } else if (colors != property_colors) {
      return false;
    }
    const T* p = arr;
    for (std::vector<PlyElement>::iterator it = elements.begin();
	 it != elements.end(); it++, p += N) {
      if (!it->add_colors(p, property_flags, colors)) return false;
    }
    return true;
  }
  //! \brief Add colors to an existing element.
  //! \param idx Index of the element to add colors to.
  //! \param arr Colors.
  //! \param property_colors Names of the colors.
  //! \return true if successful, false otherwise.
  template <typename T>
  bool add_element_colors(const size_t idx,
			  const std::vector<T>& arr) {
    std::vector<std::string> property_colors = colors;
    if (property_colors.empty()) {
      property_colors.push_back("red");
      property_colors.push_back("green");
      property_colors.push_back("blue");
    }
    return add_element_colors(idx, arr, property_colors);
  }
  //! \brief Add colors to an existing element.
  //! \param idx Index of the element to add colors to.
  //! \param arr Colors.
  //! \param property_colors Names of the colors.
  //! \return true if successful, false otherwise.
  template <typename T>
  bool add_element_colors(const size_t idx,
			  const std::vector<T>& arr,
			  const std::vector<std::string>& property_colors) {
    if (idx >= elements.size()) return false;
    if (colors.size() == 0) {
      colors = property_colors;
      set_flags<T>(property_colors, false);
    } else if (colors != property_colors) {
      return false;
    }
    if (colors.size() != arr.size())
      return false;
    return elements[idx].add_colors(arr.data(), property_flags, colors);
  }
  //! \brief Check if this element set is equivalent to another.
  //! \param rhs Element set to compare against.
  //! \return true if this element set is equivalent to rhs.
  bool is_equal(const PlyElementSet& rhs) const {
    if (this->name != rhs.name)
      return false;
    if (this->property_flags != rhs.property_flags)
      return false;
    if (this->elements != rhs.elements)
      return false;
    return true;
  }
  //! \brief Write all elements in the set to an output stream.
  //! \param out Output stream.
  //! \return Output stream.
  std::ostream & write(std::ostream &out) const {
    int i = 0;
    for (std::vector<PlyElement>::const_iterator it = elements.begin(); it != elements.end(); it++, i++)
      it->write(out, property_flags);
    return out;
  }
  //! \brief Write the header entry defining an element set to an output
  //!   stream.
  //! \param out Output stream.
  void write_header(std::ostream &out) const {
    out << "element " << name << " " << elements.size() << std::endl;
    for (std::vector<std::string>::const_iterator iname = property_order.begin(); iname != property_order.end(); iname++) {
      std::map<std::string, uint16_t>::const_iterator it = property_flags.find(*iname);
      YGGDRASIL_RAPIDJSON_ASSERT(it != property_flags.end());
      
      out << "property " << PlyElement::flag2typename(it->second) << " ";
      if (it->second & PlyElement::kListFlag) {
	uint16_t element_flag = PlyElement::kUint8Flag;
	std::map<std::string, uint16_t>::const_iterator it_size = property_size_flags.find(*iname);
	if (it_size != property_size_flags.end())
	  element_flag = it_size->second;
	out << PlyElement::flag2typename(element_flag) << " "
	    << PlyElement::flag2typename((uint16_t)(it->second & ~PlyElement::kListFlag)) << " ";
      }
      out << it->first << std::endl;
    }
  }
  //! \brief Read all expected elements from an input stream.
  //! \param in Input stream.
  //! \param count Number of elements to read.
  //! \return Input stream.
  std::istream & read(std::istream &in, uint32_t count) {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    for (size_t i = 0; i < count; i++)
      elements.emplace_back(this, in);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    for (size_t i = 0; i < count; i++)
      elements.push_back(PlyElement(this, in));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    return in;
  }
  //! \brief Read the next property from an input stream.
  //! \param in Input stream.
  //! \param[in,out] inColors If true, the property is a colors. If false,
  //!   the read property will be checked against known colors parameters
  //!   and inColors will be set to the result.
  void read_property(std::istream &in, bool &inColors) {
    std::string property_name;
    std::string property_type;
    in >> property_type;
    uint16_t flags = PlyElement::typename2flag(property_type);
    uint16_t size_flags = 0;
    if (flags & PlyElement::kListFlag) {
      std::string word;
      in >> word;
      size_flags = PlyElement::typename2flag(word);
      in >> word;
      flags = flags | PlyElement::typename2flag(word);
    }
    in >> property_name;
    if (!inColors) {
      inColors = (property_name == "red" || property_name == "r");
    }
    if (inColors)
      colors.push_back(property_name);
    property_order.push_back(property_name);
    property_flags[property_name] = flags;
    property_size_flags[property_name] = size_flags;
  }
};

//! \brief Check for equivalence between two PlyElementSet instances.
//! \param lhs First element set for comparison.
//! \param rhs Second element set for comparison.
//! \return true if the two instances are equivalent.
inline
bool operator == (const PlyElementSet& lhs, const PlyElementSet& rhs)
{ return lhs.is_equal(rhs); }

//! Forward declaration.
class ObjWavefront;

//! Ply 3D geometry container class.
class Ply {
public:
  Ply() : comments(), format("ascii 1.0"), elements(), element_order() {}
  //! \brief Copy constructor.
  //! \param rhs Instance to copy.
  Ply(const Ply& rhs) : comments(rhs.comments), format(rhs.format), elements(rhs.elements), element_order(rhs.element_order) {}
  //! \brief Copy from an ObjWavefront instance.
  //! \param rhs Instance to copy.
  Ply(const ObjWavefront& rhs) :
    comments(), format("ascii 1.0"), elements(), element_order() {
    fromObjWavefront(rhs);
  }
  //! \brief Create an Ply instance from a C array of vertices.
  //! \tparam Tv Type of value in vertex value arrays.
  //! \tparam Mv Number of vertex elements.
  //! \tparam Nv Number of values in the array for each vertex element.
  //! \param vertices Array of vertex element value arrays.
  template<typename Tv, SizeType Mv, SizeType Nv>
  Ply(const Tv (&vertices)[Mv][Nv]) :
    comments(), format("ascii 1.0"), elements(), element_order() {
    add_element_set("vertex", vertices);
  }
  //! \brief Create an Ply instance from C arrays of vertices and faces.
  //! \tparam Tv Type of value in vertex value arrays.
  //! \tparam Mv Number of vertex elements.
  //! \tparam Nv Number of values in the array for each vertex element.
  //! \tparam Tf Type of value in face value arrays.
  //! \tparam Mf Number of face elements.
  //! \tparam Nf Number of values in the array for each face element.
  //! \param vertices Array of vertex element value arrays.
  //! \param faces Array of face element value arrays.
  template<typename Tv, SizeType Mv, SizeType Nv,
	   typename Tf, SizeType Mf, SizeType Nf>
  Ply(const Tv (&vertices)[Mv][Nv], const Tf (&faces)[Mf][Nf]) :
    comments(), format("ascii 1.0"), elements(), element_order() {
    add_element_set("vertex", vertices);
    add_element_set("face", faces);
  }
  //! \brief Create an Ply instance from C arrays of vertices, faces, and
  //!   edges.
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
  template<typename Tv, SizeType Mv, SizeType Nv,
	   typename Tf, SizeType Mf, SizeType Nf,
	   typename Te, SizeType Me, SizeType Ne>
  Ply(const Tv (&vertices)[Mv][Nv], const Tf (&faces)[Mf][Nf],
      const Te (&edges)[Me][Ne]) :
    comments(), format("ascii 1.0"), elements(), element_order() {
    add_element_set("vertex", vertices);
    add_element_set("face", faces);
    add_element_set("edge", edges);
  }
  //! \brief Create a Ply instance from a 3D mesh.
  //! \param xyz Vector of vertex information for faces in the structure.
  //! \param prune_duplicates If true, existing vertices will be checked
  //!   before adding new ones.
  Ply(const std::vector<std::vector<double> > xyz,
      bool prune_duplicates=false) :
    comments(), format("ascii 1.0"), elements(), element_order() {
    add_mesh(xyz, prune_duplicates);
  }
  //! \brief Copy assignment
  //! \param[in] rhs Instance to copy.
  Ply& operator=(const Ply& rhs) {
    this->~Ply();
    new (this) Ply(rhs);
    return *this;
  }
  //! \brief Copy from an ObjWavefront instance.
  //! \param rhs Instance to copy.
  void fromObjWavefront(const ObjWavefront& rhs);
    
  //! \brief Add a set of vertex elements.
  //! \tparam Tv Type of element properties.
  //! \tparam Mv Number of elements.
  //! \tparam Nv Number of properties defining each element.
  //! \param vertices Property values for each element in the set.
  template<typename Tv, SizeType Mv, SizeType Nv>
  void add_element_set_vertex(const Tv (&vertices)[Mv][Nv]) {
    add_element_set("vertex", vertices);
  }

  //! \brief Add a set of edge elements.
  //! \tparam Te Type of element properties.
  //! \tparam Me Number of elements.
  //! \tparam Ne Number of properties defining each element.
  //! \param edges Property values for each element in the set.
  template<typename Te, SizeType Me, SizeType Ne>
  void add_element_set_edge(const Te (&edges)[Me][Ne]) {
    add_element_set("edge", edges);
  }

  //! Comments at the beginning of the serialized geometry.
  std::vector<std::string> comments;
  //! Version string specifying the format of the serialized geometry.
  std::string format;
  //! Map between element type names and sets of elements.
  std::map<std::string,PlyElementSet> elements;
  //! Element type names in the order that they were read or should be written.
  std::vector<std::string> element_order;

  //! \brief Get the property names associated with an element set.
  //! \param name0 Type of elements in the set.
  //! \param N Number of properties in each element.
  //! \param[out] colors Array to put color property names in.
  //! \returns Array of properties associated with the element set.
  std::vector<std::string> get_property_names(const std::string& name0,
					      SizeType N,
					      std::vector<std::string>& colors) const {
    std::string name = ply_alias2base(name0);
    std::vector<std::string> property_names;
    if (name == "vertex") {
      YGGDRASIL_RAPIDJSON_ASSERT((N == 3) || (N == 6));
      property_names.push_back("x");
      property_names.push_back("y");
      property_names.push_back("z");
      if (N == 6) {
	property_names.push_back("red");
	property_names.push_back("green");
	property_names.push_back("blue");
	colors.push_back("red");
	colors.push_back("green");
	colors.push_back("blue");
      }
    } else if (name == "face") {
      property_names.push_back("vertex_index");
    } else if (name == "edge") {
      YGGDRASIL_RAPIDJSON_ASSERT((N == 2) || (N == 5));
      property_names.push_back("vertex1");
      property_names.push_back("vertex2");
      if (N == 5) {
	property_names.push_back("red");
	property_names.push_back("green");
	property_names.push_back("blue");
	colors.push_back("red");
	colors.push_back("green");
	colors.push_back("blue");
      }
    }
    return property_names;
  }
  //! \brief Add a single element to the geometry.
  //! \param name0 Name of the type of element being added.
  //! \param arr Vector of element properties.
  //! \param property_names Vector of element property names.
  //! \param property_colors Names of properties defining colors for each
  //!   element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \returns New element.
  template <typename T>
  PlyElement* add_element(const std::string& name0,
			  const std::vector<T> &arr,
			  const std::vector<std::string> &property_names,
			  const std::vector<std::string> &property_colors,
			  const T* ignore = 0) {
    std::string name = ply_alias2base(name0);
    bool is_array = bool(arr.size() != property_names.size());
    YGGDRASIL_RAPIDJSON_ASSERT((!is_array) || (property_names.size() == 1));
    if (elements.find(name) == elements.end()) {
      add_element_set(name);
      elements[name].set_flags<T>(property_names, is_array);
      elements[name].colors = property_colors;
    }
    return elements[name].add_element(arr, ignore);
  }
  //! \brief Add a single element to the geometry.
  //! \param name Name of the type of element being added.
  //! \param arr Vector of element properties.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  //! \returns New element.
  template <typename T>
  PlyElement* add_element(const std::string& name,
			  const std::vector<T> &arr,
			  const T* ignore = 0) {
    std::vector<std::string> property_colors;
    std::vector<std::string> property_names = get_property_names(name,
								 (SizeType)arr.size(),
								 property_colors);
    return add_element(name, arr, property_names, property_colors, ignore);
  }
  //! \brief Add a single empty element to the geometry.
  //! \param name Name of the type of element being added.
  //! \returns New element.
  PlyElement* add_element(const std::string& name) {
    std::string name2 = ply_alias2base(name);
    if (elements.find(name2) == elements.end()) {
      add_element_set(name2);
    }
    return elements[name2].add_element();
  }
  //! \brief Add a new element set to the geometry.
  //! \tparam T Type of property values.
  //! \tparam M Number of elements in the set.
  //! \tparam N Number of properties for each element.
  //! \param name0 Name of the type of element in the set.
  //! \param arr Property values for each of the elements in the set.
  //! \param property_names The names of properties defining each element in
  //!   the set in the order they were read or will be written.
  //! \param property_colors Names of properties defining colors for each
  //!   element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  template <typename T, SizeType M, SizeType N>
  void add_element_set(const std::string& name0,
		       const T (&arr)[M][N],
		       const std::vector<std::string>& property_names,
		       const std::vector<std::string>& property_colors,
		       const T* ignore = 0) {
    std::string name = ply_alias2base(name0);
    YGGDRASIL_RAPIDJSON_ASSERT(elements.find(name) == elements.end());
    element_order.push_back(name);
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.emplace(std::piecewise_construct,
		     std::forward_as_tuple(name),
		     std::forward_as_tuple(name, arr, property_names,
					   property_colors, ignore));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements[name] = PlyElementSet(name, arr, property_names,
				   property_colors, ignore);
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  //! \brief Add a new element set to the geometry.
  //! \tparam T Type of property values.
  //! \tparam M Number of elements in the set.
  //! \tparam N Number of properties for each element.
  //! \param name Name of the type of element in the set.
  //! \param arr Property values for each of the elements in the set.
  //! \param property_names The names of properties defining each element in
  //!   the set in the order they were read or will be written.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  template <typename T, SizeType M, SizeType N>
  void add_element_set(const std::string& name,
		       const T (&arr)[M][N], const T* ignore = 0) {
    std::vector<std::string> colors;
    std::vector<std::string> property_names = get_property_names(name, N,
								 colors);
    add_element_set(name, arr, property_names, colors, ignore);
  }
  //! \brief Add a new element set to the geometry.
  //! \tparam T Type of property values.
  //! \param name0 Name of the type of element in the set.
  //! \param arr Property values for each of the elements in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of properties for each element.
  //! \param property_names Vector of element property names.
  //! \param property_colors Names of properties defining colors for each
  //!   element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  template <typename T>
  void add_element_set(const std::string& name0,
		       const T* arr, SizeType M, SizeType N,
		       const std::vector<std::string>& property_names,
		       const std::vector<std::string>& property_colors,
		       const T* ignore = 0) {
    std::string name = ply_alias2base(name0);
    YGGDRASIL_RAPIDJSON_ASSERT(elements.find(name) == elements.end());
    element_order.push_back(name);
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.emplace(std::piecewise_construct,
		     std::forward_as_tuple(name),
		     std::forward_as_tuple(name, arr, (size_t)M, (size_t)N,
					   property_names, property_colors,
					   ignore));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements[name] = PlyElementSet(name, arr, (size_t)M, (size_t)N,
				   property_names, property_colors, ignore);
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  //! \brief Add a new element set to the geometry.
  //! \tparam T Type of property values.
  //! \param name Name of the type of element in the set.
  //! \param arr Property values for each of the elements in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of properties for each element.
  //! \param ignore Value to ignore. After this value is encountered for an
  //!   element will be added.
  template <typename T>
  void add_element_set(const std::string& name,
		       const T* arr, SizeType M, SizeType N,
		       const T* ignore = 0) {
    std::vector<std::string> colors;
    std::vector<std::string> property_names = get_property_names(name, N,
								 colors);
    add_element_set(name, arr, M, N, property_names, colors, ignore);
  }
  //! \brief Add a new element set to the geometry and allocates for elements.
  //! \param name0 Name of the type of element in the set.
  void add_element_set(const std::string& name0) {
    std::string name = ply_alias2base(name0);
    element_order.push_back(name);
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.emplace(std::piecewise_construct,
		     std::forward_as_tuple(name),
		     std::forward_as_tuple(name));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements[name] = PlyElementSet(name);
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  //! \brief Add a new element set to the geometry by copying an existing set.
  //! \param name0 Name of the type of element in the set.
  //! \param other Element set to copy.
  void add_element_set(const std::string& name0,
		       const PlyElementSet& other) {
    std::string name = ply_alias2base(name0);
    element_order.push_back(name);
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements.emplace(std::piecewise_construct,
		     std::forward_as_tuple(name),
		     std::forward_as_tuple(other));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    elements[name] = PlyElementSet(other);
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
  //! \brief Add element colors to a set.
  //! \param name Name of the type of element in the set.
  //! \param arr Colors for each of the elements in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of color properties for each element.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool add_element_set_colors(const std::string& name,
			      const T* arr, SizeType M, SizeType N) {
    if (N == 3) {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
      std::vector<std::string> property_colors({"red", "green", "blue"});
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
      std::vector<std::string> property_colors(3);
      property_colors[0].assign("red");
      property_colors[1].assign("green");
      property_colors[2].assign("blue");
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
      return add_element_set_colors(name, arr, M, N, property_colors);
    }
    return false;
  }
  //! \brief Add element colors to a set.
  //! \param name Name of the type of element in the set.
  //! \param arr Colors for each of the elements in the set.
  //! \param M Number of elements in the set.
  //! \param N Number of color properties for each element.
  //! \param property_colors The names of color properties defined in arr.
  //! \return true if successful, false otherwise.
  template<typename T>
  bool add_element_set_colors(const std::string& name,
			      const T* arr, SizeType M, SizeType N,
			      const std::vector<std::string>& property_colors) {
    if (property_colors.empty() || property_colors.size() != N) return false;
    PlyElementSet* elementSet = get_element_set(name);
    if (elementSet)
      return elementSet->add_colors(arr, M, N, property_colors);
    return false;
  }
  //! \brief Get the number of elements of a certain type.
  //! \param[in] Name of the element type to count.
  //! \return Number of elements of the requested type.
  size_t count_elements(const std::string name) const {
    const PlyElementSet* element_set = get_element_set(name);
    if (!element_set) return 0;
    return element_set->elements.size();
  }
  //! \brief Get a mapping of element types in the group and counts of that
  //!   type of element.
  //! \return Map between element type and count.
  std::map<std::string,size_t> element_counts() const {
    std::map<std::string,size_t> idx;
    for (std::map<std::string,PlyElementSet>::const_iterator it = elements.begin();
	 it != elements.end(); it++) {
      idx[it->first] = it->second.elements.size();
    }
    return idx;
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
  //! \brief Get an element set.
  //! \param name0 Name of the element set to get.
  //! \returns The element set of the requested type if it exists and NULL
  //!   otherwise.
  const PlyElementSet* get_element_set(const std::string& name0) const {
    return const_cast<Ply&>(*this).get_element_set(name0);
  }
  //! \brief Get an element set.
  //! \param name0 Name of the element set to get.
  //! \returns The element set of the requested type if it exists and NULL
  //!   otherwise.
  PlyElementSet* get_element_set(const std::string& name0) {
    std::string name = ply_alias2base(name0);
    std::map<std::string,PlyElementSet>::iterator eit = elements.find(name);
    if (eit == elements.end())
      return NULL;
    return &(eit->second);
  }
  //! \brief Get an element set in an array form.
  //! \param name0 Name of the element set to get.
  //! \param[out] N Number of elements in the returned array.
  //! \param[out[ M Number of values for each element in the returned array.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \returns The element set of the requested type in array form.
  std::vector<int> get_int_array(const std::string& name0,
				 size_t &N, size_t &M,
				 bool skipColors=false) const {
    std::string name = ply_alias2base(name0);
    std::vector<int> out;
    const PlyElementSet* s = get_element_set(name);
    if (s == NULL) return out;
    out = s->get_int_array(0, skipColors);
    N = s->elements.size();
    M = out.size() / N;
    return out;
  }
  //! \brief Get an element set in an array form.
  //! \param name0 Name of the element set to get.
  //! \param[out] N Number of elements in the returned array.
  //! \param[out[ M Number of values for each element in the returned array.
  //! \param skipColors If true, the parameters containing colors will not be
  //!   included.
  //! \returns The element set of the requested type in array form.
  std::vector<double> get_double_array(const std::string& name0,
				       size_t &N, size_t &M,
				       bool skipColors=false) const {
    std::string name = ply_alias2base(name0);
    std::vector<double> out;
    const PlyElementSet* s = get_element_set(name);
    if (s == NULL) return out;
    out = s->get_double_array(skipColors);
    N = s->elements.size();
    M = out.size() / N;
    return out;
  }
  //! \brief Get the colors for an element set in arrayform.
  //! \param name0 Name of the element set to get.
  //! \param[out] N Number of elements in the returned array.
  //! \param[out[ M Number of values for each element in the returned array.
  //! \param defaultValue Value to add if colors are missing.
  //! \returns The colors for the requirested type in array form.
  std::vector<uint8_t> get_colors_array(const std::string& name0,
					size_t &N, size_t &M,
					uint8_t defaultValue=0) const {
    std::string name = ply_alias2base(name0);
    std::vector<uint8_t> out;
    const PlyElementSet* s = get_element_set(name);
    if (s == NULL) return out;
    out = s->get_colors_array(defaultValue);
    N = s->elements.size();
    M = out.size() / N;
    return out;
  }
  //! \brief Check if this geometry is equivalent to another.
  //! \param rhs Geometry to compare against.
  //! \return true If this geometry is equivalent to rhs.
  bool is_equal(const Ply& rhs) const {
    if (this->comments != rhs.comments)
      return false;
    if (this->format != rhs.format)
      return false;
    if (this->elements != rhs.elements)
      return false;
    return true;
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
    const PlyElementSet* elementSet = get_element_set("vertex");
    if (elementSet) {
      std::vector<PlyElement>::const_iterator it = elementSet->elements.begin();
      out = it->get_double_array(true);
      it++;
      for (; it != elementSet->elements.end(); it++) {
	std::vector<double> iarr = it->get_double_array(true);
	out[0] = (std::min)(out[0], iarr[0]);
	out[1] = (std::min)(out[1], iarr[1]);
	out[2] = (std::min)(out[2], iarr[2]);
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
    const PlyElementSet* elementSet = get_element_set("vertex");
    if (elementSet) {
      std::vector<PlyElement>::const_iterator it = elementSet->elements.begin();
      out = it->get_double_array(true);
      it++;
      for (; it != elementSet->elements.end(); it++) {
	std::vector<double> iarr = it->get_double_array(true);
	out[0] = (std::max)(out[0], iarr[0]);
	out[1] = (std::max)(out[1], iarr[1]);
	out[2] = (std::max)(out[2], iarr[2]);
      }
    }
    return out;
  }
  //! \brief Determine if a structure is valid and there are vertexes for
  //!   all those referenced in faces and edges.
  //! \return true if the structure is valid, false otherwise.
  bool is_valid() const {
    int nvert = 0;
    const PlyElementSet* vertices = get_element_set("vertex");
    if (vertices) nvert = (int)vertices->elements.size();
    for (std::map<std::string,PlyElementSet>::const_iterator it = elements.begin();
	 it != elements.end(); it++) {
      if (it->first == "vertex" || it->second.requires_double()) continue;
      const std::vector<int> idx = it->second.get_int_array(0, true);
      for (std::vector<int>::const_iterator f = idx.begin(); f != idx.end(); f++)
	if (*f >= nvert) return false;
    }
    return true;
  }
  //! \brief Locate existing vertex that matches the provided vertex.
  //! \param v Vertex to search for.
  //! \returns Index of existing vertex that matches v, -1 if a match
  //!   cannot be found.
  int find_vertex(const std::vector<double> v) const {
    int idx = 0;
    const PlyElementSet* vertices = get_element_set("vertex");
    if (vertices) {
      for (std::vector<PlyElement>::const_iterator it = vertices->elements.begin();
	   it != vertices->elements.end(); it++) {
	std::vector<double> iv = it->get_double_array(true);
	if (internal::values_eq(v[0], iv[0]) &&
	    internal::values_eq(v[1], iv[1]) &&
	    internal::values_eq(v[2], iv[2]))
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
    for (std::vector<std::vector<double> >::const_iterator it = xyz.begin();
	 it != xyz.end(); it++) {
      size_t verts_per_face = it->size() / 3;
      std::vector<int> iface;
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
	iface.push_back(idxVert);
      }
      add_element("face", iface);
    }
  }
  //! \brief Get the mesh for the structure.
  //! \return Structure mesh with each row representing a face with vertex
  //!    information provided in sequence for each face.
  std::vector<std::vector<double> > mesh() const {
    std::vector<std::vector<double> > out;
    const PlyElementSet* faces = get_element_set("face");
    const PlyElementSet* vertices = get_element_set("vertex");
    if (!(faces && vertices)) return out;
    size_t iFace = 0;
    for (std::vector<PlyElement>::const_iterator it = faces->elements.begin();
	 it != faces->elements.end(); it++, iFace++) {
      const std::vector<int> idx = it->get_int_array();
      out.push_back(std::vector<double>());
      for (std::vector<int>::const_iterator f = idx.begin(); f != idx.end(); f++) {
	YGGDRASIL_RAPIDJSON_ASSERT(*f < (int)vertices->elements.size());
	if (*f >= (int)vertices->elements.size()) {
	  out.clear();
	  return out;
	}
	vertices->elements[(size_t)(*f)].get_double_array(out[iFace], true);
      }
    }
    return out;
  }
  //! \brief Get the areas for each face in the structure.
  //! \return Vector of areas for each face.
  std::vector<double> areas() const {
    return mesh2areas(mesh());
  }
  //! \brief Append elements from another structure to this one.
  //! \param other Structure to append.
  void append(const Ply& other) {
    size_t nvert = 0;
    for (std::vector<std::string>::const_iterator it = other.comments.begin();
	 it != other.comments.end(); it++) {
      bool match = false;
      for (std::vector<std::string>::const_iterator jt = comments.begin();
	   jt != comments.end(); jt++) {
	if (*it == *jt) {
	  match = true;
	  break;
	}
      }
      if (!match)
	comments.push_back(*it);
    }
    const PlyElementSet* vertices = get_element_set("vertex");
    if (vertices) nvert = vertices->elements.size();
    for (std::map<std::string,PlyElementSet>::const_iterator it = other.elements.begin();
	 it != other.elements.end(); it++) {
      size_t nPrev = 0;
      PlyElementSet* elementSet = get_element_set(it->first);
      if (!elementSet) {
	add_element_set(it->first, it->second);
	elementSet = get_element_set(it->first);
      } else {
	nPrev = elementSet->elements.size();
	for (std::vector<PlyElement>::const_iterator iit = it->second.elements.begin();
	     iit != it->second.elements.end(); iit++)
	  elementSet->add_element(*iit);
      }
      if (nvert > 0 && it->first != "vertex") {
	size_t maxProp = 0;
	if (it->first == "edge") maxProp = 2;
	for (std::vector<PlyElement>::iterator iit = elementSet->elements.begin() + (long)nPrev;
	     iit != elementSet->elements.end(); iit++)
	  iit->increase_index(nvert, maxProp);
      }
    }
  }
  //! \brief Combine this structure with another.
  //! \param rhs Structure to be added to this one.
  //! \param Result of addition.
  friend Ply operator+(const Ply& lhs, const Ply& rhs) {
    Ply out(lhs);
    out.append(rhs);
    return out;
  }
  //! \brief Write geometry elements to an output stream.
  //! \param out Output stream.
  //! \return Output stream.
  std::ostream & write(std::ostream &out) const {
    // Write header
    out << "ply" << std::endl
	<< "format " << format << std::endl;
    for (std::vector<std::string>::const_iterator it = comments.begin(); it != comments.end(); it++)
      out << "comment " << *it << std::endl;
    for (std::vector<std::string>::const_iterator it = element_order.begin(); it != element_order.end(); it++) {
      std::map<std::string,PlyElementSet>::const_iterator eit = elements.find(*it);
      YGGDRASIL_RAPIDJSON_ASSERT(eit != elements.end());
      eit->second.write_header(out);
    }
    out << "end_header" << std::endl;
    // Write body
    for (std::vector<std::string>::const_iterator it = element_order.begin(); it != element_order.end(); it++) {
      std::map<std::string,PlyElementSet>::const_iterator eit = elements.find(*it);
      YGGDRASIL_RAPIDJSON_ASSERT(eit != elements.end());
      eit->second.write(out);
    }
    return out;
  }
  //! \brief Read geometry elements from an input stream.
  //! \param in Input stream.
  //! \return Input stream.
  std::istream & read(std::istream &in) {
    std::string word;
    in >> std::ws;
    in >> word;
    if (word != "ply")
      YGGDRASIL_RAPIDJSON_ASSERT(!sizeof("Input does not appear to be in ply format"));
    // Read header
    std::string current_element;
    bool inColors = false;
    std::vector<uint32_t> counts;
    while (in >> word) {
      if (word == "end_header")
	break;
      else if (word == "format") {
	bool first = true;
	format = "";
	while ((in.peek()!='\n') && (in >> word)) {
	  if (!first)
	    format += " ";
	  format += word;
	  first = false;
	}
      } else if (word == "comment") {
	std::string comment;
	bool first = true;
	while ((in.peek()!='\n') && (in >> word)) {
	  if (!first)
	    comment += " ";
	  comment += word;
	  first = false;
	}
	comments.push_back(comment);
      } else if (word == "element") {
	uint32_t count = 0;
	in >> current_element;
	in >> count;
	counts.push_back(count);
	add_element_set(current_element);
	inColors = false;
      } else if (word == "property") {
	elements[current_element].read_property(in, inColors);
      } else {
	YGGDRASIL_RAPIDJSON_ASSERT(!sizeof(std::string("Unrecognized input beginning w/ ") + word));
      }
    }
    // Read body
    size_t i = 0;
    for (std::vector<std::string>::iterator it = element_order.begin(); it != element_order.end(); it++, i++) {
      std::map<std::string,PlyElementSet>::iterator eit = elements.find(*it);
      YGGDRASIL_RAPIDJSON_ASSERT(eit != elements.end());
      eit->second.read(in, counts[i]);
    }
    return in;
  }
  
  friend bool operator == (const Ply& lhs, const Ply& rhs);
  friend bool operator != (const Ply& lhs, const Ply& rhs);
  friend std::ostream & operator << (std::ostream &out, const Ply &p);
  friend std::istream & operator >> (std::istream &in,  Ply &p);
};

//! \brief Check for equality between two ply geometries.
//! \param lhs First geometry for comparison.
//! \param rhs Second geometry for comparison.
//! \return true if the two geometries are equivalent.
inline
bool operator == (const Ply& lhs, const Ply& rhs)
{ return lhs.is_equal(rhs); }

//! \brief Check for inequality between two ply geometries.
//! \param lhs First geometry for comparison.
//! \param rhs Second geometry for comparison.
//! \return true if the two geometries are not equivalent.
inline
bool operator != (const Ply& lhs, const Ply& rhs)
{ return !lhs.is_equal(rhs); }

//! \brief Write a Ply geometry to an output stream.
//! \param out Output stream.
//! \param p Geometry.
//! \return Output stream.
inline
std::ostream & operator << (std::ostream &out, const Ply &p)
{ return p.write(out); }

//! \brief Read a Ply geometry from an input stream.
//! \param in Input stream.
//! \param p Destination geometry.
//! \return Input sream.
inline
std::istream & operator >> (std::istream &in, Ply &p)
{ return p.read(in); }


inline
void PlyElement::init_from_parent_() {
  property_order = parent->property_order;
  colors = parent->colors;
  for (std::map<std::string, uint16_t>::const_iterator it = parent->property_flags.begin();
       it != parent->property_flags.end(); it++) {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    properties.emplace(std::piecewise_construct,
		       std::forward_as_tuple(it->first),
		       std::forward_as_tuple(it->second));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    properties[it->first] = Data(it->second);
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  }
}
template <typename T>
bool PlyElement::set_property(const std::string name, const std::vector<T>& values, bool isColor) {
  std::map<std::string, Data>::const_iterator it = properties.find(name);
  if (it == properties.end()) {
    property_order.push_back(name);
    parent->property_order.push_back(name);
    if (isColor) {
      colors.push_back(name);
      parent->colors.push_back(name);
    }
    uint16_t flags = type2flag<T>() | kListFlag;
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    properties.emplace(std::piecewise_construct,
		       std::forward_as_tuple(name),
		       std::forward_as_tuple(flags, values));
    parent->property_flags.emplace(std::piecewise_construct,
				   std::forward_as_tuple(name),
				   std::forward_as_tuple(flags));
    parent->property_size_flags.emplace(std::piecewise_construct,
					std::forward_as_tuple(name),
					std::forward_as_tuple(kUint8Flag));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    properties[name] = Data(flags, values);
    parent->property_flags[name] = flags;
    parent->property_size_flags[name] = kUint8Flag;
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  } else {
    properties[name].assign(values);
  }
  it = properties.find(name);
  return true;
}
template <typename T>
bool PlyElement::set_property(const std::string name, const T& value, bool isColor) {
  std::map<std::string, Data>::const_iterator it = properties.find(name);
  if (it == properties.end()) {
    property_order.push_back(name);
    parent->property_order.push_back(name);
    if (isColor) {
      colors.push_back(name);
      parent->colors.push_back(name);
    }
    uint16_t flags = type2flag<T>();
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    properties.emplace(std::piecewise_construct,
		       std::forward_as_tuple(name),
		       std::forward_as_tuple(flags, value));
    parent->property_flags.emplace(std::piecewise_construct,
				   std::forward_as_tuple(name),
				   std::forward_as_tuple(flags));
    parent->property_size_flags.emplace(std::piecewise_construct,
					std::forward_as_tuple(name),
					std::forward_as_tuple(0));
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    properties[name] = Data(flags, value);
    parent->property_flags[name] = flags;
    parent->property_size_flags[name] = 0;
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
  } else {
    properties[name].assign(value);
  }
  it = properties.find(name);
  return true;
}

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // YGGDRASIL_RAPIDJSON_PLY_H_
