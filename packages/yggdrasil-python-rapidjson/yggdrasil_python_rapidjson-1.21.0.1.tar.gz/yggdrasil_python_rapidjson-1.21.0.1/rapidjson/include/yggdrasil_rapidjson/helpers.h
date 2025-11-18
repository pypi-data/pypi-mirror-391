#ifndef YGGDRASIL_RAPIDJSON_DOC_HELPERS_H_
#define YGGDRASIL_RAPIDJSON_DOC_HELPERS_H_

#include "ply.h"
#include "obj.h"
#include "va_list.h"

YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

// Forward declaration.
template <typename Encoding, typename Allocator>
class GenericValue;

template <typename Encoding, typename Allocator, typename StackAllocator>
class GenericDocument;

#ifndef YGGDRASIL_RAPIDJSON_DEFAULT_STACK_ALLOCATOR
#define YGGDRASIL_RAPIDJSON_DEFAULT_STACK_ALLOCATOR ::YGGDRASIL_RAPIDJSON_NAMESPACE::CrtAllocator
#endif

// Geometry helpers
inline
void ObjWavefront::fromPly(const Ply& p) {
  size_t nvert = 0;
  for (std::vector<std::string>::const_iterator name = p.element_order.begin(); name != p.element_order.end(); name++) {
    if ((*name) == "vertex") {
      for (std::vector<PlyElement>::const_iterator it = p.elements.find(*name)->second.elements.begin();
	   it != p.elements.find(*name)->second.elements.end(); it++) {
	ObjElement* ito = this->add_element("v", it->get_double_array(true));
	if (it->colors.size() > 0) {
	  std::vector<uint8_t> icolors = it->get_colors_array();
	  ito->add_colors(icolors.data(), static_cast<SizeType>(icolors.size()));
	}
	nvert++;
      }
    } else if ((*name) == "face") {
      for (std::vector<PlyElement>::const_iterator it = p.elements.find(*name)->second.elements.begin();
	   it != p.elements.find(*name)->second.elements.end(); it++) {
	this->add_element("f", it->get_int_array(nvert, true));
	// Face colors not supported
	// if (it->colors.size() > 0) {
	//   std::vector<uint8_t> icolors = it->get_colors_array();
	//   ito->add_colors(icolors.data(), static_cast<SizeType>(icolors.size()));
	// }
      }
    } else if ((*name) == "edge") {
      for (std::vector<PlyElement>::const_iterator it = p.elements.find(*name)->second.elements.begin();
	   it != p.elements.find(*name)->second.elements.end(); it++) {
	this->add_element("l", it->get_int_array(nvert));
	// Edge colors not supported
	// if (it->colors.size() > 0) {
	//   std::vector<uint8_t> icolors = it->get_colors_array();
	//   ito->add_colors(icolors.data(), static_cast<SizeType>(icolors.size()));
	// }
      }
    } else
      YGGDRASIL_RAPIDJSON_ASSERT(((*name) == "vertex") ||
		       ((*name) == "face") ||
		       ((*name) == "edge"));
  }
}
inline
void Ply::fromObjWavefront(const ObjWavefront& o) {
  size_t nvert = 0;
  for (std::vector<ObjElement*>::const_iterator it = o.elements.begin(); it != o.elements.end(); it++) {
    if ((*it)->code == "v") {
      this->add_element("vertex", (*it)->get_double_array());
      nvert++;
    } else if ((*it)->code == "f") {
      this->add_element("face", (*it)->get_int_array(nvert));
    } else if ((*it)->code == "l") {
      this->add_element("edge", (*it)->get_int_array(nvert));
    }
    else
      YGGDRASIL_RAPIDJSON_ASSERT(((*it)->code == "v") ||
		       ((*it)->code == "f") ||
		       ((*it)->code == "l"));
  }
}

// VarArgs helpers
/*!
  @brief Count the number of variable arguments that would be returned or
    set for the type described by the schema.
  @param[in] schema Schema containing type information about the
    variables.
  @param[in] set If true, the arguments are counted for the case where
    the schema would be used to set variables.
  @returns Number of variables associated with the schema.
 */
template<typename ValueType>
size_t countVarArgs(ValueType& schema, bool set) {
  GenericDocument<typename ValueType::EncodingType,
		  typename ValueType::AllocatorType,
		  YGGDRASIL_RAPIDJSON_DEFAULT_STACK_ALLOCATOR> tmp;
  return tmp.CountVarArgs(schema, set);
}

template<typename ValueType>
bool VarArgList::skip(ValueType& schema, bool set) {
  GenericDocument<typename ValueType::EncodingType,
		  typename ValueType::AllocatorType,
		  YGGDRASIL_RAPIDJSON_DEFAULT_STACK_ALLOCATOR> tmp;
  return tmp.SkipVarArgs(schema, *this, set);
}

#define ENCODING_STRING_(name, ...)			\
  const Ch name ## String[] = { __VA_ARGS__, '\0' }
#define COMPARE_(x, dec)						\
  (std::basic_string<Ch>(x) == std::basic_string<Ch>(dec ## String))
#define SWITCH_(x, CASE_)						\
  CASE_(x, ASCII, ASCII)						\
  else CASE_(x, ASCII, Null)						\
  else CASE_(x, UTF8, UTF8)						\
  else CASE_(x, UTF16, UTF16)						\
  else CASE_(x, UTF32, UTF32)						\
  else CASE_(x, UTF32, UCS4)						\
  else {								\
    return false;							\
  }
template <typename SourceEncoding, typename DestEncoding, typename AllocatorType>
inline bool TranslateEncoding_inner(const void* src, SizeType srcNbytes,
				    void*& dst, SizeType& dstNbytes,
				    AllocatorType& allocator,
				    bool requireFixedWidth = false) {
  if (requireFixedWidth && (!DestEncoding::fixedWidth || !SourceEncoding::fixedWidth))
    return false;
  SizeType srcLength = srcNbytes / ((SizeType)sizeof(typename SourceEncoding::Ch));
  GenericStringStream<SourceEncoding> is((const typename SourceEncoding::Ch*)src);
  GenericStringBuffer<DestEncoding> os;
  while (YGGDRASIL_RAPIDJSON_LIKELY(is.Tell() < srcLength)) {
    Transcoder<SourceEncoding, DestEncoding>::Transcode(is, os);
  }
  if (dst == NULL) {
    dstNbytes = (SizeType)os.GetLength() * (SizeType)sizeof(typename DestEncoding::Ch);
    dst = allocator.Malloc(dstNbytes);
    if (!dst) return false;
  } else {
    if (dstNbytes != (SizeType)os.GetLength() * (SizeType)sizeof(typename DestEncoding::Ch))
      return false;
  }
  memcpy(dst, os.GetString(), dstNbytes);
  return true;
}
template <typename SourceEncoding, typename Ch, typename AllocatorType>
inline bool TranslateEncoding_outer(const void* src, SizeType srcNbytes,
				    void*& dst, SizeType& dstNbytes, const Ch* dstEncoding,
				    AllocatorType& allocator,
				    bool requireFixedWidth = false) {
  ENCODING_STRING_(ASCII, 'A', 'S', 'C', 'I', 'I');
  ENCODING_STRING_(UTF8, 'U', 'T', 'F', '8');
  ENCODING_STRING_(UTF16, 'U', 'T', 'F', '1', '6');
  ENCODING_STRING_(UTF32, 'U', 'T', 'F', '3', '2');
  ENCODING_STRING_(UCS4, 'U', 'C', 'S', '4');
  ENCODING_STRING_(Null, 'n', 'u', 'l', 'l');
#define INNER_CASE_(x, dec, decS)					\
  if (COMPARE_(x, decS)) {						\
    return TranslateEncoding_inner<SourceEncoding, dec<> >(src, srcNbytes, dst, dstNbytes, allocator, requireFixedWidth); \
  }
  SWITCH_(dstEncoding, INNER_CASE_)
}
template <typename Ch, typename AllocatorType>
inline bool TranslateEncoding(const void* src, SizeType srcNbytes, const Ch* srcEncoding,
			      void*& dst, SizeType& dstNbytes, const Ch* dstEncoding,
			      AllocatorType& allocator,
			      bool requireFixedWidth = false) {
  ENCODING_STRING_(ASCII, 'A', 'S', 'C', 'I', 'I');
  ENCODING_STRING_(UTF8, 'U', 'T', 'F', '8');
  ENCODING_STRING_(UTF16, 'U', 'T', 'F', '1', '6');
  ENCODING_STRING_(UTF32, 'U', 'T', 'F', '3', '2');
  ENCODING_STRING_(UCS4, 'U', 'C', 'S', '4');
  ENCODING_STRING_(Null, 'n', 'u', 'l', 'l');
#define OUTER_CASE_(x, dec, decS)					\
  if (COMPARE_(x, decS)) {						\
    return TranslateEncoding_outer<dec<> >(src, srcNbytes, dst, dstNbytes, dstEncoding, allocator, requireFixedWidth); \
  }
  SWITCH_(srcEncoding, OUTER_CASE_)
}
#undef SWITCH_
#undef OUTER_CASE_
#undef INNER_CASE_
#undef COMPARE_
#undef ENCODING_STRING_

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // YGGDRASIL_RAPIDJSON_DOC_HELPERS_H_
