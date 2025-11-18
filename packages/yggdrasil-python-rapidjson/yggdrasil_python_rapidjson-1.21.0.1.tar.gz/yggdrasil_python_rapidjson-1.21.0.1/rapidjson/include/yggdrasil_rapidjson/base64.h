/*
 * Base64 encoding/decoding (RFC1341)
 * Copyright (c) 2005-2011, Jouni Malinen <j@w1.fi>
 *
 * This software may be distributed under the terms of the BSD license.
 * See README for more details.
 */

#include "yggdrasil_rapidjson.h"

#ifndef BASE64_H_
#define BASE64_H_

#include <vector>
#include "encodings.h"
#include "stream.h"
#include "precision.h"

YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

#ifdef __cplusplus /* If this is a C++ compiler, use C linkage */
extern "C" {
#endif

static const unsigned char base64_table[65] =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
static const unsigned char base64_table_last = '=';

/**
 * base64_encode - Base64 encode
 * @src: Data to be encoded
 * @len: Length of the data to be encoded
 * @out_len: Pointer to output length variable, or %NULL if not used
 * Returns: Allocated buffer of out_len bytes of encoded data,
 * or %NULL on failure
 *
 * Caller is responsible for freeing the returned buffer. Returned buffer is
 * nul terminated to make it easier to use as a C string. The nul terminator is
 * not included in out_len.
 */
static inline unsigned char * base64_encode(const unsigned char *src, size_t len,
					    size_t *out_len)
{
  unsigned char *out, *pos;
  const unsigned char *end, *in;
  size_t olen;
  int line_len;

  olen = len * 4 / 3 + 4; /* 3-byte blocks to 4-byte */
  olen += olen / 72; /* line feeds */
  olen++; /* nul termination */
  if (olen < len)
    return NULL; /* integer overflow */
  out = (unsigned char *)malloc(olen);
  if (out == NULL)
    return NULL;

  end = src + len;
  in = src;
  pos = out;
  line_len = 0;
  while (end - in >= 3) {
    *pos++ = base64_table[in[0] >> 2];
    *pos++ = base64_table[((in[0] & 0x03) << 4) | (in[1] >> 4)];
    *pos++ = base64_table[((in[1] & 0x0f) << 2) | (in[2] >> 6)];
    *pos++ = base64_table[in[2] & 0x3f];
    in += 3;
    line_len += 4;
    if (line_len >= 72) {
      *pos++ = '\n';
      line_len = 0;
    }
  }

  if (end - in) {
    *pos++ = base64_table[in[0] >> 2];
    if (end - in == 1) {
      *pos++ = base64_table[(in[0] & 0x03) << 4];
      *pos++ = base64_table_last;
    } else {
      *pos++ = base64_table[((in[0] & 0x03) << 4) |
			    (in[1] >> 4)];
      *pos++ = base64_table[(in[1] & 0x0f) << 2];
    }
    *pos++ = base64_table_last;
    line_len += 4;
  }

  if (line_len)
    *pos++ = '\n';

  *pos = '\0';
  if (out_len)
    *out_len = (size_t)(pos - out);
  return out;
}


/**
 * base64_decode - Base64 decode
 * @src: Data to be decoded
 * @len: Length of the data to be decoded
 * @out_len: Pointer to output length variable
 * Returns: Allocated buffer of out_len bytes of decoded data,
 * or %NULL on failure
 *
 * Caller is responsible for freeing the returned buffer.
 */
static inline unsigned char * base64_decode(const unsigned char *src, size_t len,
					    size_t *out_len)
{
  unsigned char dtable[256], *out, *pos, block[4], tmp;
  size_t i, count, olen;
  int pad = 0;

  
  memset(dtable, 0x80, 256);
  for (i = 0; i < sizeof(base64_table) - 1; i++)
    dtable[base64_table[i]] = (unsigned char) i;
  dtable[base64_table_last] = 0;

  count = 0;
  for (i = 0; i < len; i++) {
    if (dtable[src[i]] != 0x80)
      count++;
  }

  if (count == 0 || count % 4)
    return NULL;

  olen = count / 4 * 3;
  pos = out = (unsigned char *)malloc(olen);
  if (out == NULL)
    return NULL;

  count = 0;
  for (i = 0; i < len; i++) {
    tmp = dtable[src[i]];
    if (tmp == 0x80)
      continue;

    if (src[i] == base64_table_last)
      pad++;
    block[count] = tmp;
    count++;
    if (count == 4) {
      *pos++ = (unsigned char)((block[0] << 2) | (block[1] >> 4));
      *pos++ = (unsigned char)((block[1] << 4) | (block[2] >> 2));
      *pos++ = (unsigned char)((block[2] << 6) | block[3]);
      count = 0;
      if (pad) {
	if (pad == 1)
	  pos--;
	else if (pad == 2)
	  pos -= 2;
	else {
	  /* Invalid padding */
	  free(out);
	  return NULL;
	}
	break;
      }
    }
  }

  *out_len = (size_t)(pos - out);
  return out;
}

#ifdef __cplusplus /* If this is a C++ compiler, end C linkage */
}
#endif

// template <typename StreamType>
// class Base64StreamWrapper  {
// public:
//   typedef typename StreamType::Ch Ch;
//   Base64StreamWrapper(StreamType &stream) :
//     stream_(stream), buffer_(),
//     dtable_(), // buffer_empty_(),
//     pos_(0), buffer_pos_(0) {
//     buffer_[0] = '\0';
//     buffer_[1] = '\0';
//     buffer_[2] = '\0';
//     buffer_empty_[0] = true;
//     buffer_empty_[1] = true;
//     buffer_empty_[2] = true;
//     memset(dtable_, 0x80, 256);
//     for (size_t i = 0; i < sizeof(base64_table) - 1; i++)
//       dtable_[base64_table[i]] = (unsigned char) i;
//     dtable_[base64_table_last] = 0;
//   }
// private:
//   StreamType &stream_;
//   unsigned char buffer_[3];
//   unsigned char dtable_[256];
//   bool buffer_empty_[3];
//   size_t pos_;
//   size_t buffer_pos_;
// };


//! Input stream wrapper for decoding base64.
template <typename StreamType>
class Base64InputStreamWrapper {
public:
  //! Character type read from the stream.
  typedef typename StreamType::Ch Ch;
  //! \brief Wrap a stream in a base64 decoder.
  //! \param stream Stream.
  Base64InputStreamWrapper(StreamType &stream) :
    stream_(stream), buffer_(),
    dtable_(), // buffer_empty_(),
    pos_(0), buffer_pos_(0) {
    buffer_[0] = '\0';
    buffer_[1] = '\0';
    buffer_[2] = '\0';
    buffer_empty_[0] = true;
    buffer_empty_[1] = true;
    buffer_empty_[2] = true;
    memset(dtable_, 0x80, 256);
    for (size_t i = 0; i < sizeof(base64_table) - 1; i++)
      dtable_[base64_table[i]] = (unsigned char) i;
    dtable_[base64_table_last] = 0;
    ReadNext();
  }
  //! \brief Peek at the nth byte.
  //! \param n Offset to check for byte at.
  //! \return Byte.
  unsigned char PeekByte(size_t n = 0) {
    if ((buffer_pos_ + n) < 3)
      return buffer_[buffer_pos_ + n];
    YGGDRASIL_RAPIDJSON_ASSERT(buffer_pos_ == 3);  // Don't overwrite buffer
    YGGDRASIL_RAPIDJSON_ASSERT(n < 3);
    ReadNext();
    return buffer_[buffer_pos_ + n];
  }
  //! \brief Peek at the next character.
  //! \return Character.
  Ch Peek() {
    Ch out = '\0';
    unsigned char *bytes = reinterpret_cast<unsigned char*>(&out);
    for (size_t i = 0; i < sizeof(Ch); i++)
      bytes[i] = PeekByte(i);
    return out;
  }
  //! \brief Peek at the next set of bytes and check if there are enough to
  //!   read a character from.
  //! \return true if there are enough bytes for a character.
  bool PeekEmpty() {
    for (size_t i = 0; i < sizeof(Ch); i++) {
      PeekByte(i);
      if (!(buffer_empty_[buffer_pos_ + i])) return false;
    }
    return true;
  }
  //! \brief Take one byte from the stream.
  //! \return Byte.
  unsigned char TakeByte() {
    if (buffer_pos_ >= 3)
      ReadNext();
    buffer_empty_[buffer_pos_] = true;
    return buffer_[buffer_pos_++];
  }
  //! \brief Take a character from the stream.
  //! \return Character.
  Ch Take() {
    Ch out = '\0';
    unsigned char *bytes = reinterpret_cast<unsigned char*>(&out);
    for (size_t i = 0; i < sizeof(Ch); i++)
      bytes[i] = TakeByte();
    pos_++;
    return out;
  }
  //! \brief Report the position in the buffer.
  //! \return Buffer position.
  size_t Tell() { return pos_; } // When is this used?
  
  // unsigned char* PeekNext() {
  //   // std::cerr << "PeekNext" << std::endl;
  //   // YGGDRASIL_RAPIDJSON_ASSERT(false);
  //   // return NULL;
  //   unsigned char *out = (unsigned char*)malloc(3 * sizeof(unsigned char));
  //   unsigned char *pos = out;
  //   unsigned char encoded[4] = {0x80, 0x80, 0x80, 0x80};
  //   unsigned char src = '\0';
  //   size_t pad = 0;
  //   const Ch* next = stream_.Peek4();
  //   for (size_t i = 0; i < 4; i++) {
  //     src = (unsigned char)(next[i]);
  //     encoded[i] = dtable_[src];
  //     if (encoded[i] == 0x80)
  // 	continue;
  //     if (src == base64_table_last)
  // 	pad++;
  //   }
  //   unsigned char *block = encoded;
  //   *pos++ = (unsigned char)((block[0] << 2) | (block[1] >> 4));
  //   *pos++ = (unsigned char)((block[1] << 4) | (block[2] >> 2));
  //   *pos++ = (unsigned char)((block[2] << 6) | block[3]);
  //   for (size_t i = 0; i < pad; i++)
  //     out[2 - i] = '\0';
  //   return out;
  // }

  //! \brief Read the next set of bytes from the stream.
  void ReadNext() {
    // Decode
    unsigned char *pos = &(buffer_[0]);
    unsigned char encoded[4] = {0x80, 0x80, 0x80, 0x80};
    unsigned char src = '\0';
    size_t pad = 0;
    buffer_pos_ = 0;
    buffer_[0] = '\0';
    buffer_[1] = '\0';
    buffer_[2] = '\0';
    buffer_empty_[0] = false;
    buffer_empty_[1] = false;
    buffer_empty_[2] = false;
    if (stream_.Peek() == '\0') {
      buffer_empty_[0] = true;
      buffer_empty_[1] = true;
      buffer_empty_[2] = true;
      return;
    }
    // std::cerr << "Reading from " << stream_.Tell() << std::endl;
    // std::cerr << "  encoded: ";
    for (size_t i = 0; i < 4; i++) {
      while (encoded[i] == 0x80) {
	YGGDRASIL_RAPIDJSON_ASSERT(stream_.Peek() != '\0');
	// std::cerr << stream_.Peek();
	src = (unsigned char)(stream_.Take());
	encoded[i] = dtable_[src];
      }
      if (src == base64_table_last)
	pad++;
    }
    // std::cerr << std::endl;
    unsigned char *block = encoded;
    *pos++ = (unsigned char)((block[0] << 2) | (block[1] >> 4));
    *pos++ = (unsigned char)((block[1] << 4) | (block[2] >> 2));
    *pos++ = (unsigned char)((block[2] << 6) | block[3]);
    for (size_t i = 0; i < pad; i++) {
      buffer_[2 - i] = '\0';
      buffer_empty_[2 - i] = true;
    }
    // std::cerr << "  decoded: ";
    // for (size_t i = 0; i < 3; i++)
    //   std::cerr << buffer_[i];
    // std::cerr << std::endl;
  }
  
  //! \brief Wrapper for stream
  UTFType GetType() const { return stream_.GetType(); }
  
private:
  StreamType &stream_;
  unsigned char buffer_[3];
  unsigned char dtable_[256];
  bool buffer_empty_[3];
  size_t pos_;
  size_t buffer_pos_;
  
};

template <typename HandlerType>
class JSONCoreWrapper {
public:
  typedef typename HandlerType::Ch Ch;
  JSONCoreWrapper(HandlerType& handler) :
    handler_(&handler) {}
#define WRAP_CORE_(method, arg)			\
  return handler_->method arg
  bool Null()                 { WRAP_CORE_(Null, ()); }
  bool Bool(bool b)           { WRAP_CORE_(Bool, (b)); }
  bool Int(int i)             { WRAP_CORE_(Int, (i)); }
  bool Uint(unsigned u)       { WRAP_CORE_(Uint, (u)); }
  bool Int64(int64_t i64)     { WRAP_CORE_(Int64, (i64)); }
  bool Uint64(uint64_t u64)   { WRAP_CORE_(Uint64, (u64)); }
  bool Double(double d)       { WRAP_CORE_(Double, (d)); }
  bool StartObject()
  { WRAP_CORE_(StartObject, ()); }
  bool EndObject(SizeType memberCount = 0)
  { WRAP_CORE_(EndObject, (memberCount)); }
  bool StartArray()
  { WRAP_CORE_(StartArray, ()); }
  bool EndArray(SizeType elementCount = 0)
  { WRAP_CORE_(EndArray, (elementCount)); }
  bool Key(const Ch* str, SizeType length, bool copy = false)
  { WRAP_CORE_(Key, (str, length, copy)); }
  bool String(const Ch* str, SizeType length, bool copy = false, bool addNull = false) {
    if (!addNull)
      return handler_->String(str, length, copy);
    CrtAllocator allocator;
    Ch* tmp = (Ch*)allocator.Malloc(length + 1);
    memcpy(tmp, str, length * sizeof(Ch));
    tmp[length] = '\0';
    bool out = handler_->String(tmp, length, true);
    allocator.Free(tmp);
    return out;
  }
#undef WRAP_CORE_ 
  template <typename SchemaValueType>
  bool YggdrasilString(const Ch* str, SizeType length, bool copy, SchemaValueType& schema) {
    typename SchemaValueType::MemberIterator type = schema.FindMember(SchemaValueType::GetTypeString());
    if (type == schema.MemberEnd())
      return false;
    bool isScalar = (type->value == SchemaValueType::GetScalarString());
    if (isScalar ||
	type->value == SchemaValueType::Get1DArrayString() ||
	type->value == SchemaValueType::GetNDArrayString()) {
      typename SchemaValueType::MemberIterator subtype = schema.FindMember(SchemaValueType::GetSubTypeString());
      if (subtype == schema.MemberEnd())
	return false;
      YggSubType src_subtype;
      SizeType src_precision = schema[SchemaValueType::GetPrecisionString()].GetUint();
      size_t nelements = 1, i = 0;
#define CALL_COMPLEX_							\
      if (!StartArray()) return false; if (!Double(tmp[i].real())) return false; if (!Double(tmp[i].imag())) return false; if (!EndArray(2)) return false
#define CASE_BASE_(name, mkTmp, call, freeTmp)	\
      if (subtype->value == SchemaValueType::Get ## name ## SubTypeString()) { \
	src_subtype = kYgg ## name ## SubType;				\
	mkTmp;								\
	call								\
	freeTmp;							\
	return true;							\
      }
#define CALL_BASE_(call)			\
	if (!call(tmp[i])) return false
#define CASES_(mkTmpBase, callWrap, freeTmpBase, callStr)		\
      CASE_BASE_(Int, mkTmpBase(int64_t), callWrap(CALL_BASE_(Int64)), freeTmpBase) \
      else CASE_BASE_(Uint, mkTmpBase(uint64_t), callWrap(CALL_BASE_(Uint64)), freeTmpBase) \
      else CASE_BASE_(Float, mkTmpBase(double), callWrap(CALL_BASE_(Double)), freeTmpBase) \
      else CASE_BASE_(Complex, mkTmpBase(std::complex<double>), callWrap(CALL_COMPLEX_), freeTmpBase) \
      else CASE_BASE_(String, const Ch* tmp = str, callWrap(callStr), tmp = NULL) \
      else return false
      
      if (isScalar) {
#define MKTMP_SCALAR_(type)						\
	type tmp0;							\
	type* tmp = &tmp0;						\
	changePrecision(src_subtype, src_precision, (const unsigned char*)str, tmp, 1)
#define CALL_SCALAR_WRAP_(call) call;

	CASES_(MKTMP_SCALAR_, CALL_SCALAR_WRAP_, tmp = NULL,
	       if (!String(tmp, length, true, true)) return false);

#undef CALL_SCALAR_WRAP_
#undef MKTMP_SCALAR_

      } else {
	std::vector<size_t> shape;
	if (schema.HasMember(SchemaValueType::GetShapeString())) {
	  for (typename SchemaValueType::ValueIterator it = schema[SchemaValueType::GetShapeString()].Begin();
	       it != schema[SchemaValueType::GetShapeString()].End(); it++) {
	    nelements *= it->GetUint();
	    shape.push_back(it->GetUint());
	  }
	} else if (schema.HasMember(SchemaValueType::GetLengthString())) {
	  nelements = schema[SchemaValueType::GetLengthString()].GetUint();
	  shape.push_back(nelements);
	}
	typename SchemaValueType::AllocatorType allocator;
#define MKTMP_ARRAY_(type)						\
	type* tmp = (type*)(allocator.Malloc(nelements * sizeof(type))); \
	changePrecision(src_subtype, src_precision, (const unsigned char*)str, tmp, (SizeType)nelements)
#define CALL_ARRAY_WRAP_(call)						\
	  size_t total_prod = 1;					\
	  for (size_t j = 0; j < shape.size(); j++) {			\
	    total_prod *= shape[j];					\
	  }								\
	  for (i = 0; i < nelements; i++) {				\
	    size_t rem = i;						\
	    size_t prod = total_prod;					\
	    size_t do_begin = 0, do_end = 0;				\
	    for (size_t j = 0; j < shape.size(); j++) {			\
	      if (rem == 0)						\
		do_begin++;						\
	      else if (rem == prod - 1)					\
		do_end++;						\
	      prod /= shape[j];						\
	      rem -= (static_cast<size_t>(std::floor(rem / prod)) * prod); \
	    }								\
	    for (size_t j = 0; j < do_begin; j++) {			\
	      if (!StartArray()) return false;				\
	    }								\
	    call;							\
	    for (size_t j = 0; j < do_end; j++) {			\
	      if (!EndArray()) return false;				\
	    }								\
	  }

	CASES_(MKTMP_ARRAY_, CALL_ARRAY_WRAP_, allocator.Free(tmp),
	       if (!String(tmp + (i * src_precision / sizeof(Ch)), (SizeType)(src_precision / sizeof(Ch)), true, true)) return false);

#undef CALL_ARRAY_WRAP_
#undef MKTMP_ARRAY_
      }
#undef CASES_
#undef CASE_BASE_
#undef CALL_BASE_
#undef CALL_COMPLEX_
    } else {
      return String(str, length, copy, true);
    }
  }
  template <typename SchemaValueType>
  bool YggdrasilStartObject(SchemaValueType&) {
    return StartObject();
  }
  bool YggdrasilEndObject(SizeType memberCount = 0) {
    return EndObject(memberCount);
  }
private:
  HandlerType* handler_;
};

//! Output stream wrapper that will encode character bytes as base64.
template <typename StreamType>
class Base64OutputStreamWrapper {
public:
  //! Character type writen to the stream.
  typedef typename StreamType::Ch Ch;
  //! Wrap a stream in base64 encoding.
  Base64OutputStreamWrapper(StreamType &stream) :
    stream_(stream), buffer_(),
    dtable_(), // buffer_empty_(),
    pos_(0), buffer_pos_(0) {
    buffer_[0] = '\0';
    buffer_[1] = '\0';
    buffer_[2] = '\0';
    buffer_empty_[0] = true;
    buffer_empty_[1] = true;
    buffer_empty_[2] = true;
    memset(dtable_, 0x80, 256);
    for (size_t i = 0; i < sizeof(base64_table) - 1; i++)
      dtable_[base64_table[i]] = (unsigned char) i;
    dtable_[base64_table_last] = 0;
  }
  //! \brief Reserve enough space in the stream for a certain number of characters.
  //! \tparam Ch2 Type of character to reserve space for.
  //! \param count Number of characters to reserve space for.
  template<typename Ch2>
  void Reserve(size_t count) {
    stream_.Reserve(count * sizeof(Ch2) * 4 / 3);
  }
  //! \brief Begin a stream.
  //! \returns Character inserted.
  Ch* PutBegin() { return stream_.PutBegin(); }
  //! \brief Insert a byte.
  //! \param ch Byte.
  void PutByte(unsigned char ch) {
    YGGDRASIL_RAPIDJSON_ASSERT(buffer_pos_ < 3);
    buffer_empty_[buffer_pos_] = false;
    buffer_[buffer_pos_++] = ch;
    if (buffer_pos_ == 3)
      WriteNext();
  }
  //! \brief Insert a character.
  //! \tparam Ch2 Character type.
  //! \param ch Character.
  template<typename Ch2>
  void Put(Ch2 ch) {
    unsigned char* bytes = reinterpret_cast<unsigned char*>(&ch);
    for (size_t i = 0; i < sizeof(Ch2); i++) {
      PutByte(bytes[i]);
    }
  }
  //! \brief Flush the stream.
  void Flush() { stream_.Flush(); }
  //! \brief Finalize an partial byte sets and insert a character.
  //! \tparam Ch2 Character type.
  //! \param ch Character to insert at the end.
  //! \return Stream size.
  template<typename Ch2>
  size_t PutEnd(Ch2* ch) {
    if (buffer_pos_ > 0)
      WriteNext();
    return stream_.PutEnd(ch);
  }

  //! \brief Write the bytes in the buffer to the stream as base64 encoded characters.
  void WriteNext() {
    if (buffer_pos_ == 0) return;
    // Encode
    unsigned char encoded[4] = {'\0', '\0', '\0', '\0'};
    unsigned char *in = &(buffer_[0]);
    unsigned char *pos = &(encoded[0]);
    if ((!buffer_empty_[0]) && (!buffer_empty_[1]) && (!buffer_empty_[2])) {
      *pos++ = base64_table[in[0] >> 2];
      *pos++ = base64_table[((in[0] & 0x03) << 4) | (in[1] >> 4)];
      *pos++ = base64_table[((in[1] & 0x0f) << 2) | (in[2] >> 6)];
      *pos++ = base64_table[in[2] & 0x3f];
    } else {
      *pos++ = base64_table[in[0] >> 2];
      if (buffer_empty_[1]) {
	*pos++ = base64_table[(in[0] & 0x03) << 4];
	*pos++ = base64_table_last;
      } else {
	*pos++ = base64_table[((in[0] & 0x03) << 4) |
			      (in[1] >> 4)];
	*pos++ = base64_table[(in[1] & 0x0f) << 2];
      }
      *pos++ = base64_table_last;
    }
    // Output
    for (size_t i = 0; i < 4; i++) {
      if (encoded[i] == '\0')
	break;
      stream_.Put((Ch)(encoded[i]));
    }
    // Reset
    buffer_pos_ = 0;
    buffer_[0] = '\0';
    buffer_[1] = '\0';
    buffer_[2] = '\0';
    buffer_empty_[0] = true;
    buffer_empty_[1] = true;
    buffer_empty_[2] = true;
  }
  //! \brief Dummy yggdrasil method used by HasYggdrasil.
  template <typename SchemaValueType>
  bool YggdrasilString(const Ch*, SizeType, bool, SchemaValueType&)
  { return false; }

  //! \brief Wrapper for stream
  UTFType GetType() const { return stream_.GetType(); }
  
private:
  StreamType &stream_;
  unsigned char buffer_[3];
  unsigned char dtable_[256];
  bool buffer_empty_[3];
  size_t pos_;
  size_t buffer_pos_;
  
};

template<typename Ch>
bool isYggdrasilString(const Ch* str, SizeType length, bool) {
    const Ch ygg[5] = {'-', 'Y', 'G', 'G', '-'};
    SizeType len_ygg = 5;
    if (length < (2 * len_ygg))
      return false;
    return ((memcmp(ygg, str, sizeof(ygg)) == 0) &&
	    (memcmp(ygg, str + (length - len_ygg), sizeof(ygg)) == 0));
}


template<typename Encoding, typename BufferType>
bool parseYggdrasilString(const typename Encoding::Ch* str, SizeType length, bool copy,
			  BufferType& os_body, BufferType& os_schema) {
    if (!isYggdrasilString(str, length, copy))
      return false;
    const typename Encoding::Ch ygg[5] = {'-', 'Y', 'G', 'G', '-'};
    SizeType len_ygg = 5;
    // Locate -ygg- markers
    SizeType i = len_ygg, beg_schema = len_ygg, end_schema, len_schema, elen_schema, beg_body, end_body, len_body, elen_body;
    beg_schema = len_ygg;
    while ((i < length) && (memcmp(ygg, str + i, sizeof(ygg)) != 0)) i++;
    end_schema = i;
    len_schema = end_schema - beg_schema;
    elen_schema = len_schema * 3 / 4;
    beg_body = end_schema + len_ygg;
    end_body = length - len_ygg;
    len_body = end_body - beg_body;
    elen_body = len_body * 3 / 4;
    YGGDRASIL_RAPIDJSON_ASSERT((end_body + len_ygg) == length);
    // Add stream
    GenericStringStream<Encoding> is(str);
    is.src_ += len_ygg;
    Base64InputStreamWrapper<GenericStringStream<Encoding> > is64(is);
    // Extract the schema
    // std::cerr << "Reading schema (encoded_len = " << len_schema
    // 	  << ", decoded_len = " << elen_schema
    // 	  << ")" << std::endl;
    for (SizeType j = 0; j < elen_schema; j++) {
      // std::cerr << "    char " << j << " " << is64.Peek() << std::endl;
      if (is64.Peek() != '\0') {
	os_schema.Put(is64.Take());
      } else { 
	is64.Take();
      }
    }
    is.src_ += len_ygg;
    // Extract the body
    // std::cerr << "Reading body (encoded_len = " << len_body
    // 	  <<", decoded_len = " << elen_body
    // 	  << ")" << std::endl;
    SizeType nempty_body = 0;
    for (SizeType j = 0; j < elen_body; j++) {
      // std::cerr << "    char " << j << " " << is64.Peek() << std::endl;
      if (!(is64.PeekEmpty())) {
	os_body.Put(is64.Take());
      } else {
	is64.Take();
	nempty_body++;
      }
    }
    elen_body = elen_body - nempty_body;
    is.src_ += len_ygg;
    YGGDRASIL_RAPIDJSON_ASSERT(is.Tell() == (size_t)length);
    // std::cerr << "schema: \"" << os_schema.GetString() << "\"" << std::endl;
    // std::cerr << "body: \"" << os_body.GetString() << "\"" << std::endl;
    return true;
}

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // BASE64_H_
