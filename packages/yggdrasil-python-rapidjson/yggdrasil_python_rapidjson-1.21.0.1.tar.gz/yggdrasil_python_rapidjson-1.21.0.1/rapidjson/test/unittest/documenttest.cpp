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

#include "unittest.h"
#include "yggdrasil_rapidjson/document.h"
#include "yggdrasil_rapidjson/writer.h"
#include "yggdrasil_rapidjson/filereadstream.h"
#include "yggdrasil_rapidjson/encodedstream.h"
#include "yggdrasil_rapidjson/stringbuffer.h"
#include <sstream>
#include <algorithm>

#ifdef __clang__
YGGDRASIL_RAPIDJSON_DIAG_PUSH
YGGDRASIL_RAPIDJSON_DIAG_OFF(c++98-compat)
YGGDRASIL_RAPIDJSON_DIAG_OFF(missing-variable-declarations)
#endif

using namespace yggdrasil_rapidjson;

template <typename DocumentType>
void ParseCheck(DocumentType& doc) {
    typedef typename DocumentType::ValueType ValueType;

    EXPECT_FALSE(doc.HasParseError());
    if (doc.HasParseError())
        printf("Error: %d at %zu\n", static_cast<int>(doc.GetParseError()), doc.GetErrorOffset());
    EXPECT_TRUE(static_cast<ParseResult>(doc));

    EXPECT_TRUE(doc.IsObject());

    EXPECT_TRUE(doc.HasMember("hello"));
    const ValueType& hello = doc["hello"];
    EXPECT_TRUE(hello.IsString());
    EXPECT_STREQ("world", hello.GetString());

    EXPECT_TRUE(doc.HasMember("t"));
    const ValueType& t = doc["t"];
    EXPECT_TRUE(t.IsTrue());

    EXPECT_TRUE(doc.HasMember("f"));
    const ValueType& f = doc["f"];
    EXPECT_TRUE(f.IsFalse());

    EXPECT_TRUE(doc.HasMember("n"));
    const ValueType& n = doc["n"];
    EXPECT_TRUE(n.IsNull());

    EXPECT_TRUE(doc.HasMember("i"));
    const ValueType& i = doc["i"];
    EXPECT_TRUE(i.IsNumber());
    EXPECT_EQ(123, i.GetInt());

    EXPECT_TRUE(doc.HasMember("pi"));
    const ValueType& pi = doc["pi"];
    EXPECT_TRUE(pi.IsNumber());
    EXPECT_DOUBLE_EQ(3.1416, pi.GetDouble());

    EXPECT_TRUE(doc.HasMember("a"));
    const ValueType& a = doc["a"];
    EXPECT_TRUE(a.IsArray());
    EXPECT_EQ(4u, a.Size());
    for (SizeType j = 0; j < 4; j++)
        EXPECT_EQ(j + 1, a[j].GetUint());

#ifndef DISABLE_YGGDRASIL_RAPIDJSON
    EXPECT_TRUE(doc.HasMember("s_int"));
    const ValueType& s_int = doc["s_int"];
    EXPECT_TRUE(s_int.IsYggdrasil());
    EXPECT_TRUE(s_int.IsScalar());
    EXPECT_TRUE(s_int.template IsScalar<int32_t>());
    EXPECT_EQ((int32_t)1, s_int.template GetScalar<int32_t>());
    int32_t s_int_val;
    s_int.GetScalar(s_int_val);
    EXPECT_EQ((int32_t)1, s_int_val);

    // // Ply structure
    // float vertices[8][3] = 
    //   {{0.0, 0.0, 0.0},
    //    {0.0, 0.0, 1.0},
    //    {0.0, 1.0, 1.0},
    //    {0.0, 1.0, 0.0},
    //    {1.0, 0.0, 0.0},
    //    {1.0, 0.0, 1.0},
    //    {1.0, 1.0, 1.0},
    //    {1.0, 1.0, 0.0}};
    // int faces[2][3] = 
    //   {{3, 0, 1},
    //    {3, 0, 2}};
    // int edges[5][2] = 
    //   {{0, 1},
    //    {1, 2},
    //    {2, 3},
    //    {3, 0},
    //    {2, 0}};
    // yggdrasil_rapidjson::Ply ply0(vertices, faces, edges);
    // EXPECT_TRUE(doc.HasMember("ply"));
    // const ValueType& ply = doc["ply"];
    // EXPECT_TRUE(ply.IsYggdrasil());
    // EXPECT_TRUE(ply.IsPly());
    // EXPECT_EQ(ply0, ply.GetPly());
    // yggdrasil_rapidjson::Ply cpy;
    // ply.GetPly(cpy);
    // EXPECT_EQ(ply0, cpy);
    
#endif // DISABLE_YGGDRASIL_RAPIDJSON
    
}

template <typename Allocator, typename StackAllocator>
void ParseTest() {
    typedef GenericDocument<UTF8<>, Allocator, StackAllocator> DocumentType;
    DocumentType doc;

#ifndef DISABLE_YGGDRASIL_RAPIDJSON
    const char* json = " { \"hello\" : \"world\", \"t\" : true , \"f\" : false, \"n\": null, \"i\":123, \"pi\": 3.1416, \"a\":[1, 2, 3, 4], \"s_int\": \"-YGG-eyJ0eXBlIjoic2NhbGFyIiwgInN1YnR5cGUiOiJpbnQiLCAicHJlY2lzaW9uIjo0fQ==-YGG-AQAAAA==-YGG-\", \"ply\": \"-YGG-eyJ0eXBlIjoicGx5In0=-YGG-cGx5CmZvcm1hdCBhc2NpaSAxLjAKZWxlbWVudCB2ZXJ0ZXggOApwcm9wZXJ0eSBmbG9hdCB4CnByb3BlcnR5IGZsb2F0IHkKcHJvcGVydHkgZmxvYXQgegplbGVtZW50IGZhY2UgMgpwcm9wZXJ0eSBsaXN0IHVjaGFyIGludCB2ZXJ0ZXhfaW5kZXgKZWxlbWVudCBlZGdlIDUKcHJvcGVydHkgaW50IHZlcnRleDEKcHJvcGVydHkgaW50IHZlcnRleDIKZW5kX2hlYWRlcgowIDAgMAowIDAgMQowIDEgMQowIDEgMAoxIDAgMAoxIDAgMQoxIDEgMQoxIDEgMAozIDMgMCAxCjMgMyAwIDIKMCAxCjEgMgoyIDMKMyAwCjIgMAo=-YGG-\" } ";
#else
    const char* json = " { \"hello\" : \"world\", \"t\" : true , \"f\" : false, \"n\": null, \"i\":123, \"pi\": 3.1416, \"a\":[1, 2, 3, 4] } ";
#endif // DISABLE_YGGDRASIL_RAPIDJSON

    doc.Parse(json);
    ParseCheck(doc);

    doc.SetNull();
    StringStream s(json);
    doc.template ParseStream<0>(s);
    ParseCheck(doc);

    doc.SetNull();
    char *buffer = strdup(json);
    doc.ParseInsitu(buffer);
    ParseCheck(doc);
    free(buffer);

    // Parse(const Ch*, size_t)
    size_t length = strlen(json);
    buffer = reinterpret_cast<char*>(malloc(length * 2));
    memcpy(buffer, json, length);
    memset(buffer + length, 'X', length);
#if YGGDRASIL_RAPIDJSON_HAS_STDSTRING
    std::string s2(buffer, length); // backup buffer
#endif
    doc.SetNull();
    doc.Parse(buffer, length);
    free(buffer);
    ParseCheck(doc);

#if YGGDRASIL_RAPIDJSON_HAS_STDSTRING
    // Parse(std::string)
    doc.SetNull();
    doc.Parse(s2);
    ParseCheck(doc);
#endif
}

TEST(Document, Parse) {
    ParseTest<MemoryPoolAllocator<>, CrtAllocator>();
    ParseTest<MemoryPoolAllocator<>, MemoryPoolAllocator<> >();
    ParseTest<CrtAllocator, MemoryPoolAllocator<> >();
    ParseTest<CrtAllocator, CrtAllocator>();
}

TEST(Document, UnchangedOnParseError) {
    Document doc;
    doc.SetArray().PushBack(0, doc.GetAllocator());

    ParseResult noError;
    EXPECT_TRUE(noError);

    ParseResult err = doc.Parse("{]");
    EXPECT_TRUE(doc.HasParseError());
    EXPECT_NE(err, noError);
    EXPECT_NE(err.Code(), noError);
    EXPECT_NE(noError, doc.GetParseError());
    EXPECT_EQ(err.Code(), doc.GetParseError());
    EXPECT_EQ(err.Offset(), doc.GetErrorOffset());
    EXPECT_TRUE(doc.IsArray());
    EXPECT_EQ(doc.Size(), 1u);

    err = doc.Parse("{}");
    EXPECT_FALSE(doc.HasParseError());
    EXPECT_FALSE(err.IsError());
    EXPECT_TRUE(err);
    EXPECT_EQ(err, noError);
    EXPECT_EQ(err.Code(), noError);
    EXPECT_EQ(err.Code(), doc.GetParseError());
    EXPECT_EQ(err.Offset(), doc.GetErrorOffset());
    EXPECT_TRUE(doc.IsObject());
    EXPECT_EQ(doc.MemberCount(), 0u);
}

static FILE* OpenEncodedFile(const char* filename) {
    const char *paths[] = {
        "encodings",
        "bin/encodings",
        "../bin/encodings",
        "../../bin/encodings",
        "../../../bin/encodings"
    };
    char buffer[1024];
    for (size_t i = 0; i < sizeof(paths) / sizeof(paths[0]); i++) {
        snprintf(buffer, 1024, "%s/%s", paths[i], filename);
        FILE *fp = fopen(buffer, "rb");
        if (fp)
            return fp;
    }
    return 0;
}

TEST(Document, Parse_Encoding) {
    const char* json = " { \"hello\" : \"world\", \"t\" : true , \"f\" : false, \"n\": null, \"i\":123, \"pi\": 3.1416, \"a\":[1, 2, 3, 4] } ";

    typedef GenericDocument<UTF16<> > DocumentType;
    DocumentType doc;
    
    // Parse<unsigned, SourceEncoding>(const SourceEncoding::Ch*)
    // doc.Parse<kParseDefaultFlags, UTF8<> >(json);
    // EXPECT_FALSE(doc.HasParseError());
    // EXPECT_EQ(0, StrCmp(doc[L"hello"].GetString(), L"world"));

    // Parse<unsigned, SourceEncoding>(const SourceEncoding::Ch*, size_t)
    size_t length = strlen(json);
    char* buffer = reinterpret_cast<char*>(malloc(length * 2));
    memcpy(buffer, json, length);
    memset(buffer + length, 'X', length);
#if YGGDRASIL_RAPIDJSON_HAS_STDSTRING
    std::string s2(buffer, length); // backup buffer
#endif
    doc.SetNull();
    doc.Parse<kParseDefaultFlags, UTF8<> >(buffer, length);
    free(buffer);
    EXPECT_FALSE(doc.HasParseError());
    if (doc.HasParseError())
        printf("Error: %d at %zu\n", static_cast<int>(doc.GetParseError()), doc.GetErrorOffset());
    EXPECT_EQ(0, StrCmp(doc[L"hello"].GetString(), L"world"));

#if YGGDRASIL_RAPIDJSON_HAS_STDSTRING
    // Parse<unsigned, SourceEncoding>(std::string)
    doc.SetNull();

#if defined(_MSC_VER) && _MSC_VER < 1800
    doc.Parse<kParseDefaultFlags, UTF8<> >(s2.c_str()); // VS2010 or below cannot handle templated function overloading. Use const char* instead.
#else
    doc.Parse<kParseDefaultFlags, UTF8<> >(s2);
#endif
    EXPECT_FALSE(doc.HasParseError());
    EXPECT_EQ(0, StrCmp(doc[L"hello"].GetString(), L"world"));
#endif
}

TEST(Document, ParseStream_EncodedInputStream) {
    // UTF8 -> UTF16
    FILE* fp = OpenEncodedFile("utf8.json");
    char buffer[256];
    FileReadStream bis(fp, buffer, sizeof(buffer));
    EncodedInputStream<UTF8<>, FileReadStream> eis(bis);

    GenericDocument<UTF16<> > d;
    d.ParseStream<0, UTF8<> >(eis);
    EXPECT_FALSE(d.HasParseError());

    fclose(fp);

    wchar_t expected[] = L"I can eat glass and it doesn't hurt me.";
    GenericValue<UTF16<> >& v = d[L"en"];
    EXPECT_TRUE(v.IsString());
    EXPECT_EQ(sizeof(expected) / sizeof(wchar_t) - 1, v.GetStringLength());
    EXPECT_EQ(0, StrCmp(expected, v.GetString()));

    // UTF16 -> UTF8 in memory
    StringBuffer bos;
    typedef EncodedOutputStream<UTF8<>, StringBuffer> OutputStream;
    OutputStream eos(bos, false);   // Not writing BOM
    {
        Writer<OutputStream, UTF16<>, UTF8<> > writer(eos);
        d.Accept(writer);
    }

    // Condense the original file and compare.
    fp = OpenEncodedFile("utf8.json");
    FileReadStream is(fp, buffer, sizeof(buffer));
    Reader reader;
    StringBuffer bos2;
    Writer<StringBuffer> writer2(bos2);
    reader.Parse(is, writer2);
    fclose(fp);

    EXPECT_EQ(bos.GetSize(), bos2.GetSize());
    EXPECT_EQ(0, memcmp(bos.GetString(), bos2.GetString(), bos2.GetSize()));
}

TEST(Document, ParseStream_AutoUTFInputStream) {
    // Any -> UTF8
    FILE* fp = OpenEncodedFile("utf32be.json");
    char buffer[256];
    FileReadStream bis(fp, buffer, sizeof(buffer));
    AutoUTFInputStream<unsigned, FileReadStream> eis(bis);

    Document d;
    d.ParseStream<0, AutoUTF<unsigned> >(eis);
    EXPECT_FALSE(d.HasParseError());

    fclose(fp);

    char expected[] = "I can eat glass and it doesn't hurt me.";
    Value& v = d["en"];
    EXPECT_TRUE(v.IsString());
    EXPECT_EQ(sizeof(expected) - 1, v.GetStringLength());
    EXPECT_EQ(0, StrCmp(expected, v.GetString()));

    // UTF8 -> UTF8 in memory
    StringBuffer bos;
    Writer<StringBuffer> writer(bos);
    d.Accept(writer);

    // Condense the original file and compare.
    fp = OpenEncodedFile("utf8.json");
    FileReadStream is(fp, buffer, sizeof(buffer));
    Reader reader;
    StringBuffer bos2;
    Writer<StringBuffer> writer2(bos2);
    reader.Parse(is, writer2);
    fclose(fp);

    EXPECT_EQ(bos.GetSize(), bos2.GetSize());
    EXPECT_EQ(0, memcmp(bos.GetString(), bos2.GetString(), bos2.GetSize()));
}

TEST(Document, Swap) {
    Document d1;
    Document::AllocatorType& a = d1.GetAllocator();

    d1.SetArray().PushBack(1, a).PushBack(2, a);

    Value o;
    o.SetObject().AddMember("a", 1, a);

    // Swap between Document and Value
    d1.Swap(o);
    EXPECT_TRUE(d1.IsObject());
    EXPECT_TRUE(o.IsArray());

    d1.Swap(o);
    EXPECT_TRUE(d1.IsArray());
    EXPECT_TRUE(o.IsObject());

    o.Swap(d1);
    EXPECT_TRUE(d1.IsObject());
    EXPECT_TRUE(o.IsArray());

    // Swap between Document and Document
    Document d2;
    d2.SetArray().PushBack(3, a);
    d1.Swap(d2);
    EXPECT_TRUE(d1.IsArray());
    EXPECT_TRUE(d2.IsObject());
    EXPECT_EQ(&d2.GetAllocator(), &a);

    // reset value
    Value().Swap(d1);
    EXPECT_TRUE(d1.IsNull());

    // reset document, including allocator
    // so clear o before so that it doesnt contain dangling elements
    o.Clear();
    Document().Swap(d2);
    EXPECT_TRUE(d2.IsNull());
    EXPECT_NE(&d2.GetAllocator(), &a);

    // testing std::swap compatibility
    d1.SetBool(true);
    using std::swap;
    swap(d1, d2);
    EXPECT_TRUE(d1.IsNull());
    EXPECT_TRUE(d2.IsTrue());

    swap(o, d2);
    EXPECT_TRUE(o.IsTrue());
    EXPECT_TRUE(d2.IsArray());
}


// This should be slow due to assignment in inner-loop.
struct OutputStringStream : public std::ostringstream {
    typedef char Ch;

    virtual ~OutputStringStream();

    void Put(char c) {
        put(c);
    }
    void Flush() {}
};

OutputStringStream::~OutputStringStream() {}

TEST(Document, AcceptWriter) {
    Document doc;
    doc.Parse(" { \"hello\" : \"world\", \"t\" : true , \"f\" : false, \"n\": null, \"i\":123, \"pi\": 3.1416, \"a\":[1, 2, 3, 4] } ");

    OutputStringStream os;
    Writer<OutputStringStream> writer(os);
    doc.Accept(writer);

    EXPECT_EQ("{\"hello\":\"world\",\"t\":true,\"f\":false,\"n\":null,\"i\":123,\"pi\":3.1416,\"a\":[1,2,3,4]}", os.str());
}

TEST(Document, UserBuffer) {
    typedef GenericDocument<UTF8<>, MemoryPoolAllocator<>, MemoryPoolAllocator<> > DocumentType;
    char valueBuffer[4096];
    char parseBuffer[2048];  // TODO: Determine why the allocator requires more than 1024 on Mac M1
    MemoryPoolAllocator<> valueAllocator(valueBuffer, sizeof(valueBuffer));
    MemoryPoolAllocator<> parseAllocator(parseBuffer, sizeof(parseBuffer));
    DocumentType doc(&valueAllocator, sizeof(parseBuffer) / 2, &parseAllocator);
    doc.Parse(" { \"hello\" : \"world\", \"t\" : true , \"f\" : false, \"n\": null, \"i\":123, \"pi\": 3.1416, \"a\":[1, 2, 3, 4] } ");
    EXPECT_FALSE(doc.HasParseError());
    EXPECT_LE(valueAllocator.Size(), sizeof(valueBuffer));
    EXPECT_LE(parseAllocator.Size(), sizeof(parseBuffer));

    // Cover MemoryPoolAllocator::Capacity()
    EXPECT_LE(valueAllocator.Size(), valueAllocator.Capacity());
    EXPECT_LE(parseAllocator.Size(), parseAllocator.Capacity());
}

// Issue 226: Value of string type should not point to NULL
TEST(Document, AssertAcceptInvalidNameType) {
    Document doc;
    doc.SetObject();
    doc.AddMember("a", 0, doc.GetAllocator());
    doc.FindMember("a")->name.SetNull(); // Change name to non-string type.

    OutputStringStream os;
    Writer<OutputStringStream> writer(os);
    ASSERT_THROW(doc.Accept(writer), AssertException);
}

// Issue 44:    SetStringRaw doesn't work with wchar_t
TEST(Document, UTF16_Document) {
    GenericDocument< UTF16<> > json;
    json.Parse<kParseValidateEncodingFlag>(L"[{\"created_at\":\"Wed Oct 30 17:13:20 +0000 2012\"}]");

    ASSERT_TRUE(json.IsArray());
    GenericValue< UTF16<> >& v = json[0];
    ASSERT_TRUE(v.IsObject());

    GenericValue< UTF16<> >& s = v[L"created_at"];
    ASSERT_TRUE(s.IsString());

    EXPECT_EQ(0, memcmp(L"Wed Oct 30 17:13:20 +0000 2012", s.GetString(), (s.GetStringLength() + 1) * sizeof(wchar_t)));
}

#if YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS

#if 0 // Many old compiler does not support these. Turn it off temporaily.

#include <type_traits>

TEST(Document, Traits) {
    static_assert(std::is_constructible<Document>::value, "");
    static_assert(std::is_default_constructible<Document>::value, "");
#ifndef _MSC_VER
    static_assert(!std::is_copy_constructible<Document>::value, "");
#endif
    static_assert(std::is_move_constructible<Document>::value, "");

    static_assert(!std::is_nothrow_constructible<Document>::value, "");
    static_assert(!std::is_nothrow_default_constructible<Document>::value, "");
#ifndef _MSC_VER
    static_assert(!std::is_nothrow_copy_constructible<Document>::value, "");
    static_assert(std::is_nothrow_move_constructible<Document>::value, "");
#endif

    static_assert(std::is_assignable<Document,Document>::value, "");
#ifndef _MSC_VER
  static_assert(!std::is_copy_assignable<Document>::value, "");
#endif
    static_assert(std::is_move_assignable<Document>::value, "");

#ifndef _MSC_VER
    static_assert(std::is_nothrow_assignable<Document, Document>::value, "");
#endif
    static_assert(!std::is_nothrow_copy_assignable<Document>::value, "");
#ifndef _MSC_VER
    static_assert(std::is_nothrow_move_assignable<Document>::value, "");
#endif

    static_assert( std::is_destructible<Document>::value, "");
#ifndef _MSC_VER
    static_assert(std::is_nothrow_destructible<Document>::value, "");
#endif
}

#endif

template <typename Allocator>
struct DocumentMove: public ::testing::Test {
};

typedef ::testing::Types< CrtAllocator, MemoryPoolAllocator<> > MoveAllocatorTypes;
TYPED_TEST_CASE(DocumentMove, MoveAllocatorTypes);

TYPED_TEST(DocumentMove, MoveConstructor) {
    typedef TypeParam Allocator;
    typedef GenericDocument<UTF8<>, Allocator> D;
    Allocator allocator;

    D a(&allocator);
    a.Parse("[\"one\", \"two\", \"three\"]");
    EXPECT_FALSE(a.HasParseError());
    EXPECT_TRUE(a.IsArray());
    EXPECT_EQ(3u, a.Size());
    EXPECT_EQ(&a.GetAllocator(), &allocator);

    // Document b(a); // does not compile (!is_copy_constructible)
    D b(std::move(a));
    EXPECT_TRUE(a.IsNull());
    EXPECT_TRUE(b.IsArray());
    EXPECT_EQ(3u, b.Size());
    EXPECT_THROW(a.GetAllocator(), AssertException);
    EXPECT_EQ(&b.GetAllocator(), &allocator);

    b.Parse("{\"Foo\": \"Bar\", \"Baz\": 42}");
    EXPECT_FALSE(b.HasParseError());
    EXPECT_TRUE(b.IsObject());
    EXPECT_EQ(2u, b.MemberCount());

    // Document c = a; // does not compile (!is_copy_constructible)
    D c = std::move(b);
    EXPECT_TRUE(b.IsNull());
    EXPECT_TRUE(c.IsObject());
    EXPECT_EQ(2u, c.MemberCount());
    EXPECT_THROW(b.GetAllocator(), AssertException);
    EXPECT_EQ(&c.GetAllocator(), &allocator);
}

TYPED_TEST(DocumentMove, MoveConstructorParseError) {
    typedef TypeParam Allocator;
    typedef GenericDocument<UTF8<>, Allocator> D;

    ParseResult noError;
    D a;
    a.Parse("{ 4 = 4]");
    ParseResult error(a.GetParseError(), a.GetErrorOffset());
    EXPECT_TRUE(a.HasParseError());
    EXPECT_NE(error, noError);
    EXPECT_NE(error.Code(), noError);
    EXPECT_NE(error.Code(), noError.Code());
    EXPECT_NE(error.Offset(), noError.Offset());

    D b(std::move(a));
    EXPECT_FALSE(a.HasParseError());
    EXPECT_TRUE(b.HasParseError());
    EXPECT_EQ(a.GetParseError(), noError);
    EXPECT_EQ(a.GetParseError(), noError.Code());
    EXPECT_EQ(a.GetErrorOffset(), noError.Offset());
    EXPECT_EQ(b.GetParseError(), error);
    EXPECT_EQ(b.GetParseError(), error.Code());
    EXPECT_EQ(b.GetErrorOffset(), error.Offset());

    D c(std::move(b));
    EXPECT_FALSE(b.HasParseError());
    EXPECT_TRUE(c.HasParseError());
    EXPECT_EQ(b.GetParseError(), noError.Code());
    EXPECT_EQ(c.GetParseError(), error.Code());
    EXPECT_EQ(b.GetErrorOffset(), noError.Offset());
    EXPECT_EQ(c.GetErrorOffset(), error.Offset());
}

// This test does not properly use parsing, just for testing.
// It must call ClearStack() explicitly to prevent memory leak.
// But here we cannot as ClearStack() is private.
#if 0
TYPED_TEST(DocumentMove, MoveConstructorStack) {
    typedef TypeParam Allocator;
    typedef UTF8<> Encoding;
    typedef GenericDocument<Encoding, Allocator> Document;

    Document a;
    size_t defaultCapacity = a.GetStackCapacity();

    // Trick Document into getting GetStackCapacity() to return non-zero
    typedef GenericReader<Encoding, Encoding, Allocator> Reader;
    Reader reader(&a.GetAllocator());
    GenericStringStream<Encoding> is("[\"one\", \"two\", \"three\"]");
    reader.template Parse<kParseDefaultFlags>(is, a);
    size_t capacity = a.GetStackCapacity();
    EXPECT_GT(capacity, 0u);

    Document b(std::move(a));
    EXPECT_EQ(a.GetStackCapacity(), defaultCapacity);
    EXPECT_EQ(b.GetStackCapacity(), capacity);

    Document c = std::move(b);
    EXPECT_EQ(b.GetStackCapacity(), defaultCapacity);
    EXPECT_EQ(c.GetStackCapacity(), capacity);
}
#endif

TYPED_TEST(DocumentMove, MoveAssignment) {
    typedef TypeParam Allocator;
    typedef GenericDocument<UTF8<>, Allocator> D;
    Allocator allocator;

    D a(&allocator);
    a.Parse("[\"one\", \"two\", \"three\"]");
    EXPECT_FALSE(a.HasParseError());
    EXPECT_TRUE(a.IsArray());
    EXPECT_EQ(3u, a.Size());
    EXPECT_EQ(&a.GetAllocator(), &allocator);

    // Document b; b = a; // does not compile (!is_copy_assignable)
    D b;
    b = std::move(a);
    EXPECT_TRUE(a.IsNull());
    EXPECT_TRUE(b.IsArray());
    EXPECT_EQ(3u, b.Size());
    EXPECT_THROW(a.GetAllocator(), AssertException);
    EXPECT_EQ(&b.GetAllocator(), &allocator);

    b.Parse("{\"Foo\": \"Bar\", \"Baz\": 42}");
    EXPECT_FALSE(b.HasParseError());
    EXPECT_TRUE(b.IsObject());
    EXPECT_EQ(2u, b.MemberCount());

    // Document c; c = a; // does not compile (see static_assert)
    D c;
    c = std::move(b);
    EXPECT_TRUE(b.IsNull());
    EXPECT_TRUE(c.IsObject());
    EXPECT_EQ(2u, c.MemberCount());
    EXPECT_THROW(b.GetAllocator(), AssertException);
    EXPECT_EQ(&c.GetAllocator(), &allocator);
}

TYPED_TEST(DocumentMove, MoveAssignmentParseError) {
    typedef TypeParam Allocator;
    typedef GenericDocument<UTF8<>, Allocator> D;

    ParseResult noError;
    D a;
    a.Parse("{ 4 = 4]");
    ParseResult error(a.GetParseError(), a.GetErrorOffset());
    EXPECT_TRUE(a.HasParseError());
    EXPECT_NE(error.Code(), noError.Code());
    EXPECT_NE(error.Offset(), noError.Offset());

    D b;
    b = std::move(a);
    EXPECT_FALSE(a.HasParseError());
    EXPECT_TRUE(b.HasParseError());
    EXPECT_EQ(a.GetParseError(), noError.Code());
    EXPECT_EQ(b.GetParseError(), error.Code());
    EXPECT_EQ(a.GetErrorOffset(), noError.Offset());
    EXPECT_EQ(b.GetErrorOffset(), error.Offset());

    D c;
    c = std::move(b);
    EXPECT_FALSE(b.HasParseError());
    EXPECT_TRUE(c.HasParseError());
    EXPECT_EQ(b.GetParseError(), noError.Code());
    EXPECT_EQ(c.GetParseError(), error.Code());
    EXPECT_EQ(b.GetErrorOffset(), noError.Offset());
    EXPECT_EQ(c.GetErrorOffset(), error.Offset());
}

// This test does not properly use parsing, just for testing.
// It must call ClearStack() explicitly to prevent memory leak.
// But here we cannot as ClearStack() is private.
#if 0
TYPED_TEST(DocumentMove, MoveAssignmentStack) {
    typedef TypeParam Allocator;
    typedef UTF8<> Encoding;
    typedef GenericDocument<Encoding, Allocator> D;

    D a;
    size_t defaultCapacity = a.GetStackCapacity();

    // Trick Document into getting GetStackCapacity() to return non-zero
    typedef GenericReader<Encoding, Encoding, Allocator> Reader;
    Reader reader(&a.GetAllocator());
    GenericStringStream<Encoding> is("[\"one\", \"two\", \"three\"]");
    reader.template Parse<kParseDefaultFlags>(is, a);
    size_t capacity = a.GetStackCapacity();
    EXPECT_GT(capacity, 0u);

    D b;
    b = std::move(a);
    EXPECT_EQ(a.GetStackCapacity(), defaultCapacity);
    EXPECT_EQ(b.GetStackCapacity(), capacity);

    D c;
    c = std::move(b);
    EXPECT_EQ(b.GetStackCapacity(), defaultCapacity);
    EXPECT_EQ(c.GetStackCapacity(), capacity);
}
#endif

#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11_RVALUE_REFS

// Issue 22: Memory corruption via operator=
// Fixed by making unimplemented assignment operator private.
//TEST(Document, Assignment) {
//  Document d1;
//  Document d2;
//  d1 = d2;
//}

#ifndef DISABLE_YGGDRASIL_RAPIDJSON
// Tests for getting setting from arguments
#define SET_GET_(get_args, set_args)		\
  Document d;					\
  EXPECT_TRUE(d.GetVarArgs get_args);		\
  EXPECT_TRUE(d.SetVarArgs set_args)
#define SET_GET_REALLOC_(get_args, set_args)	\
  Document d;					\
  EXPECT_TRUE(d.GetVarArgs get_args);		\
  EXPECT_TRUE(d.SetVarArgsRealloc set_args)
#define SET_GET_SIMPLE_(name, type, schema, value)	\
  TEST(VarArgs, name) {					\
    Document s;						\
    s.Parse("{\"type\": \"" #schema "\"}");		\
    const type a = value;				\
    type b;						\
    SET_GET_((&s, a), (&s, &b));			\
    EXPECT_EQ(a, b);					\
  }
#define SET_GET_1DARRAY_(name, type, subtype, precision, len, ...)	\
  TEST(VarArgs, 1DArray_ ## name) {					\
    Document s;								\
    s.Parse("{\"type\": \"1darray\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision "}");				\
    type a[len];							\
    size_t a_len = len;							\
    for (size_t i = 0; i < a_len; i++)					\
      a[i] = type(__VA_ARGS__);						\
    type b[len];							\
    size_t b_len = len;							\
    SET_GET_((&s, &(a[0]), a_len), (&s, &(b[0]), &b_len));		\
    EXPECT_EQ(a_len, b_len);						\
    for (size_t i = 0; i < a_len; i++) {				\
      EXPECT_EQ(a[i], b[i]);						\
    }									\
  }									\
  TEST(VarArgs, 1DArray_ ## name ##_Realloc) {				\
    Document s;								\
    s.Parse("{\"type\": \"1darray\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision "}");				\
    type a[len];							\
    size_t a_len = len;							\
    for (size_t i = 0; i < a_len; i++)					\
      a[i] = type(__VA_ARGS__);						\
    type* b = NULL;							\
    size_t b_len = 0;							\
    SET_GET_REALLOC_((&s, &(a[0]), a_len), (&s, &b, &b_len));		\
    EXPECT_EQ(a_len, b_len);						\
    EXPECT_TRUE(b != NULL);						\
    for (size_t i = 0; i < a_len; i++) {				\
      EXPECT_EQ(a[i], b[i]);						\
    }									\
    free(b);								\
  }									\
  TEST(VarArgs, 1DArray_ ## name ##_Realloc_Defined) {			\
    Document s;								\
    s.Parse("{\"type\": \"1darray\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision ","				\
	    " \"length\": " #len "}");					\
    type a[len];							\
    size_t a_len = len;							\
    for (size_t i = 0; i < a_len; i++)					\
      a[i] = type(__VA_ARGS__);						\
    type b[len];							\
    SET_GET_((&s, &(a[0])), (&s, &(b[0])));				\
    for (size_t i = 0; i < a_len; i++) {				\
      EXPECT_EQ(a[i], b[i]);						\
    }									\
  }
#define BRACES_(...)							\
  {__VA_ARGS__}
#define BRACKETS_(...)							\
  [__VA_ARGS__]
#define STR_(x)								\
  #x
#define SET_GET_NDARRAY_(name, type, subtype, precision, len, ndim, shape, ...) \
  TEST(VarArgs, NDArray_ ## name) {					\
    Document s;								\
    s.Parse("{\"type\": \"ndarray\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision ","				\
	    " \"ndim\": " #ndim "}");					\
    size_t a_shape[ndim] = BRACES_ shape;				\
    type a[len];							\
    size_t a_len = len;							\
    size_t a_ndim = ndim;						\
    for (size_t i = 0; i < a_len; i++)					\
      a[i] = type(__VA_ARGS__);						\
    type b[len];							\
    size_t b_ndim = ndim;						\
    size_t b_shape[ndim] = BRACES_ shape;				\
    SET_GET_((&s, a, a_ndim, &a_shape[0]), (&s, &b, &b_ndim, &b_shape[0])); \
    EXPECT_EQ(a_ndim, b_ndim);						\
    for (size_t i = 0; i < a_ndim; i++) {				\
      EXPECT_EQ(a_shape[i], b_shape[i]);				\
    }									\
    for (size_t i = 0; i < a_len; i++) {				\
      EXPECT_EQ(a[i], b[i]);						\
    }									\
  }									\
  TEST(VarArgs, NDArray_ ## name ## _Realloc) {				\
    Document s;								\
    s.Parse("{\"type\": \"ndarray\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision ","				\
	    " \"ndim\": " #ndim "}");					\
    size_t a_shape[ndim] = BRACES_ shape;				\
    type a[len];							\
    size_t a_len = len;							\
    size_t a_ndim = ndim;						\
    for (size_t i = 0; i < a_len; i++)					\
      a[i] = type(__VA_ARGS__);						\
    type* b = NULL;							\
    size_t b_ndim = 0;							\
    size_t* b_shape = NULL;						\
    SET_GET_REALLOC_((&s, a, a_ndim, &a_shape[0]), (&s, &b, &b_ndim, &b_shape)); \
    EXPECT_EQ(a_ndim, b_ndim);						\
    for (size_t i = 0; i < a_ndim; i++) {				\
      EXPECT_EQ(a_shape[i], b_shape[i]);				\
    }									\
    for (size_t i = 0; i < a_len; i++) {				\
      EXPECT_EQ(a[i], b[i]);						\
    }									\
    free(b);								\
    free(b_shape);							\
  }									\
  TEST(VarArgs, NDArray_ ## name ## _Defined) {				\
    Document s;								\
    s.Parse("{\"type\": \"ndarray\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision ","				\
	    " \"shape\": [2, 3]}");					\
    type a[len];							\
    size_t a_len = len;							\
    for (size_t i = 0; i < a_len; i++)					\
      a[i] = type(__VA_ARGS__);						\
    type b[len];							\
    SET_GET_((&s, a), (&s, &b));					\
    for (size_t i = 0; i < a_len; i++) {				\
      EXPECT_EQ(a[i], b[i]);						\
    }									\
  }
#define SET_GET_SCALAR_(name, type, subtype, precision, ...)		\
  TEST(VarArgs, Scalar_ ## name) {					\
    Document s;								\
    s.Parse("{\"type\": \"scalar\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision "}");				\
    const type a(__VA_ARGS__);						\
    type b;								\
    SET_GET_((&s, a), (&s, &b));					\
    EXPECT_EQ(a, b);							\
  }									\
  TEST(VarArgs, Scalar_ ## name ## _Realloc) {				\
    Document s;								\
    s.Parse("{\"type\": \"scalar\","					\
	    " \"subtype\": \"" #subtype "\","				\
	    " \"precision\": " #precision "}");				\
    const type a(__VA_ARGS__);						\
    type* b = NULL;							\
    SET_GET_REALLOC_((&s, a), (&s, &b));				\
    EXPECT_EQ(a, *b);							\
    free(b);								\
  }									\
  SET_GET_1DARRAY_(name, type, subtype, precision, 5, __VA_ARGS__)	\
  SET_GET_NDARRAY_(name, type, subtype, precision, 6, 2, (2, 3), __VA_ARGS__)
SET_GET_SIMPLE_(Null, void*, null, NULL)
SET_GET_SIMPLE_(Boolean, bool, boolean, true)
SET_GET_SIMPLE_(Int, int, integer, -1234)
// SET_GET_SIMPLE_(Uint, unsigned, integer, 1234u)
// SET_GET_SIMPLE_(Int64, int64_t, integer, -2147483648u)
// SET_GET_SIMPLE_(Uint64, uint64_t, integer, 4294967295u)
SET_GET_SIMPLE_(Double, double, number, 12.34)
// SET_GET_SIMPLE_(Float, float, number, 12.34f)
SET_GET_SCALAR_(Int8, int8_t, int, 1, 12)
SET_GET_SCALAR_(Uint8, uint8_t, uint, 1, 12u)
SET_GET_SCALAR_(Int16, int16_t, int, 2, 12)
SET_GET_SCALAR_(Uint16, uint16_t, uint, 2, 12u)
SET_GET_SCALAR_(Int32, int32_t, int, 4, 12)
SET_GET_SCALAR_(Int64, int64_t, int, 8, 12)
SET_GET_SCALAR_(Uint64, uint64_t, uint, 8, 12u)
SET_GET_SCALAR_(Float, float, float, 4, 12.34f)
SET_GET_SCALAR_(Complex32, std::complex<float>,
		complex, 8, 2.2f, 3.4f);
SET_GET_SCALAR_(Complex64, std::complex<double>,
		complex, 16, 2.2, 3.4);
#ifdef YGGDRASIL_LONG_DOUBLE_AVAILABLE
SET_GET_SCALAR_(Complex128, std::complex<long double>,
		complex, 8, 2.2lf, 3.4lf);
#endif // YGGDRASIL_LONG_DOUBLE_AVAILABLE
TEST(VarArgs, String) {
  Document s;
  s.Parse("{\"type\": \"string\"}");
  const char a[10] = "hello";
  size_t a_len = 5;
  char b[10] = "";
  size_t b_len = 10;
  SET_GET_((&s, a, a_len), (&s, &b, &b_len));
  EXPECT_EQ(a_len, b_len);
  for (size_t i = 0; i < a_len; i++)
    EXPECT_EQ(a[i], b[i]);
}
TEST(VarArgs, Scalar_String) {
  Document s;
  s.Parse("{\"type\": \"scalar\","
	  " \"subtype\": \"string\"}");
  const char a[10] = "hello";
  size_t a_len = 5;
  char b[10] = "";
  size_t b_len = 10;
  SET_GET_((&s, a, a_len), (&s, &b, &b_len));
  EXPECT_EQ(a_len, b_len);
  for (size_t i = 0; i < a_len; i++)
    EXPECT_EQ(a[i], b[i]);
}
TEST(VarArgs, Scalar_String_Realloc) {
  Document s;
  s.Parse("{\"type\": \"scalar\","
	  " \"subtype\": \"string\"}");
  const char a[10] = "hello";
  size_t a_len = 5;
  char* b = NULL;
  size_t b_len = 0;
  SET_GET_REALLOC_((&s, a, a_len), (&s, &b, &b_len));
  EXPECT_EQ(a_len, b_len);
  for (size_t i = 0; i < a_len; i++)
    EXPECT_EQ(a[i], b[i]);
  free(b);
}
TEST(VarArgs, Scalar_String_Defined) {
  Document s;
  s.Parse("{\"type\": \"scalar\","
	  " \"subtype\": \"string\","
	  " \"precision\": 5}");
  const char a[10] = "hello";
  size_t a_prec = 5;
  char b[10] = "";
  size_t b_prec = 10;
  SET_GET_((&s, a, a_prec), (&s, &b, &b_prec));
  EXPECT_EQ(a_prec, b_prec);
  for (size_t i = 0; i < a_prec; i++)
    EXPECT_EQ(a[i], b[i]);
}
TEST(VarArgs, 1DArray_String) {
  Document s;
  s.Parse("{\"type\": \"1darray\","
	  " \"subtype\": \"string\"}");
  char a[3][6];
  size_t a_len = 3;
  size_t a_prec = 6;
  for (size_t i = 0; i < a_len; i++)
    strncpy(&(a[i][0]), "hello", a_prec);
  char b[3][10];
  size_t b_len = 3;
  size_t b_prec = 10;
  SET_GET_((&s, a, a_len, a_prec), (&s, &b, &b_len, &b_prec));
  EXPECT_EQ(a_len, b_len);
  EXPECT_EQ(a_prec, b_prec);
  for (size_t i = 0; i < a_len; i++)
    for (size_t j = 0; j < a_prec; j++)
      EXPECT_EQ(a[i][j], b[i][j]);
}
TEST(VarArgs, 1DArray_String_Realloc) {
  Document s;
  s.Parse("{\"type\": \"1darray\","
	  " \"subtype\": \"string\"}");
  char a[3][6];
  size_t a_len = 3;
  size_t a_prec = 6;
  for (size_t i = 0; i < a_len; i++)
    strncpy(&(a[i][0]), "hello", a_prec);
  char* b = NULL;
  size_t b_len = 0;
  size_t b_prec = 0;
  SET_GET_REALLOC_((&s, a, a_len, a_prec), (&s, &b, &b_len, &b_prec));
  EXPECT_EQ(a_len, b_len);
  EXPECT_EQ(a_prec, b_prec);
  for (size_t i = 0; i < a_len; i++)
    for (size_t j = 0; j < a_prec; j++)
      EXPECT_EQ(a[i][j], b[(i * a_prec) + j]);
  free(b);
}
TEST(VarArgs, 1DArray_String_Defined) {
  Document s;
  s.Parse("{\"type\": \"1darray\","
	  " \"subtype\": \"string\","
	  " \"length\": 3,"
	  " \"precision\": 6}");
  char a[3][6];
  size_t a_len = 3;
  size_t a_prec = 6;
  for (size_t i = 0; i < a_len; i++)
    strncpy(&(a[i][0]), "hello", a_prec);
  char b[3][10];
  size_t b_prec = 10;
  SET_GET_((&s, a, a_prec), (&s, &b, &b_prec));
  EXPECT_EQ(a_prec, b_prec);
  for (size_t i = 0; i < a_len; i++)
    for (size_t j = 0; j < a_prec; j++)
      EXPECT_EQ(a[i][j], b[i][j]);
}
TEST(VarArgs, NDArray_String) {
  Document s;
  s.Parse("{\"type\": \"ndarray\","
	  " \"subtype\": \"string\","
	  " \"ndim\": 2}");
  char a[2][3][6];
  size_t a_ndim = 2;
  size_t a_shape[2] = {2, 3};
  size_t a_prec = 6;
  for (size_t i = 0; i < a_shape[0]; i++)
    for (size_t j = 0; j < a_shape[1]; j++)
      strncpy(&(a[i][j][0]), "hello", a_prec);
  char b[2][3][10];
  size_t b_ndim = 2;
  size_t b_shape[2] = {2, 3};
  size_t b_prec = 10;
  SET_GET_((&s, a, a_ndim, a_shape, a_prec),
	   (&s, &b, &b_ndim, &b_shape, &b_prec));
  EXPECT_EQ(a_ndim, b_ndim);
  EXPECT_EQ(a_prec, b_prec);
  EXPECT_EQ(a_shape[0], b_shape[0]);
  EXPECT_EQ(a_shape[1], b_shape[1]);
  for (size_t i = 0; i < a_shape[0]; i++)
    for (size_t j = 0; j < a_shape[1]; j++)
      for (size_t k = 0; k < a_prec; k++)
	EXPECT_EQ(a[i][j][k], b[i][j][k]);
}
TEST(VarArgs, NDArray_String_Realloc) {
  Document s;
  s.Parse("{\"type\": \"ndarray\","
	  " \"subtype\": \"string\","
	  " \"ndim\": 2}");
  char a[2][3][6];
  size_t a_ndim = 2;
  size_t a_shape[2] = {2, 3};
  size_t a_prec = 6;
  for (size_t i = 0; i < a_shape[0]; i++)
    for (size_t j = 0; j < a_shape[1]; j++)
      strncpy(&(a[i][j][0]), "hello", a_prec);
  char* b = NULL;
  size_t b_ndim = 0;
  size_t* b_shape = NULL;
  size_t b_prec = 0;
  SET_GET_REALLOC_((&s, a, a_ndim, a_shape, a_prec),
		   (&s, &b, &b_ndim, &b_shape, &b_prec));
  EXPECT_EQ(a_ndim, b_ndim);
  EXPECT_EQ(a_prec, b_prec);
  EXPECT_EQ(a_shape[0], b_shape[0]);
  EXPECT_EQ(a_shape[1], b_shape[1]);
  for (size_t i = 0; i < a_shape[0]; i++)
    for (size_t j = 0; j < a_shape[1]; j++)
      for (size_t k = 0; k < a_prec; k++)
	EXPECT_EQ(a[i][j][k], b[(i * a_shape[1] * a_prec) + (j * a_prec) + k]);
  free(b);
  free(b_shape);
}
TEST(VarArgs, NDArray_String_Defined) {
  Document s;
  s.Parse("{\"type\": \"ndarray\","
	  " \"subtype\": \"string\","
	  " \"shape\": [2, 3],"
	  " \"precision\": 6}");
  char a[2][3][6];
  size_t a_shape[2] = {2, 3};
  size_t a_prec = 6;
  for (size_t i = 0; i < a_shape[0]; i++)
    for (size_t j = 0; j < a_shape[1]; j++)
      strncpy(&(a[i][j][0]), "hello", a_prec);
  char b[2][3][10];
  size_t b_prec = 10;
  SET_GET_((&s, a, a_prec), (&s, &b, &b_prec));
  EXPECT_EQ(a_prec, b_prec);
  for (size_t i = 0; i < a_shape[0]; i++)
    for (size_t j = 0; j < a_shape[1]; j++)
      for (size_t k = 0; k < a_prec; k++)
	EXPECT_EQ(a[i][j][k], b[i][j][k]);
}
#define SET_GET_GEOMETRY_(name, type, zero)	\
  TEST(VarArgs, name) {				\
    float vertices[8][3] =			\
      {{0.0, 0.0, 0.0},				\
       {0.0, 0.0, 1.0},				\
       {0.0, 1.0, 1.0},				\
       {0.0, 1.0, 0.0},				\
       {1.0, 0.0, 0.0},				\
       {1.0, 0.0, 1.0},				\
       {1.0, 1.0, 1.0},				\
       {1.0, 1.0, 0.0}};			\
    int faces[2][3] =				\
      {{3 + zero, 0 + zero, 1 + zero},		\
       {3 + zero, 0 + zero, 2 + zero}};		\
    int edges[5][2] =				\
      {{0 + zero, 1 + zero},			\
       {1 + zero, 2 + zero},			\
       {2 + zero, 3 + zero},			\
       {3 + zero, 0 + zero},			\
       {2 + zero, 0 + zero}};			\
    Document s;					\
    s.Parse("{\"type\": \"" #type "\"}");	\
    name a(vertices, faces, edges);		\
    name b;					\
    SET_GET_((&s, &a), (&s, &b));		\
    EXPECT_EQ(a, b);				\
  }						\
  TEST(VarArgs, name ## _Realloc) {		\
    float vertices[8][3] =			\
      {{0.0, 0.0, 0.0},				\
       {0.0, 0.0, 1.0},				\
       {0.0, 1.0, 1.0},				\
       {0.0, 1.0, 0.0},				\
       {1.0, 0.0, 0.0},				\
       {1.0, 0.0, 1.0},				\
       {1.0, 1.0, 1.0},				\
       {1.0, 1.0, 0.0}};			\
    int faces[2][3] =				\
      {{3 + zero, 0 + zero, 1 + zero},		\
       {3 + zero, 0 + zero, 2 + zero}};		\
    int edges[5][2] =				\
      {{0 + zero, 1 + zero},			\
       {1 + zero, 2 + zero},			\
       {2 + zero, 3 + zero},			\
       {3 + zero, 0 + zero},			\
       {2 + zero, 0 + zero}};			\
    Document s;					\
    s.Parse("{\"type\": \"" #type "\"}");	\
    name a(vertices, faces, edges);		\
    name* b = NULL;				\
    SET_GET_REALLOC_((&s, &a), (&s, &b));	\
    EXPECT_EQ(a, *b);				\
    delete b;					\
  }
SET_GET_GEOMETRY_(Ply, ply, 0)
SET_GET_GEOMETRY_(ObjWavefront, obj, 1)
#ifndef YGGDRASIL_DISABLE_PYTHON_C_API
TEST(VarArgs, PythonFunction) {
  Document s;
  s.Parse("{\"type\": \"function\"}");
  PyObject* a = import_python_class("example_python", "example_function");
  YGGDRASIL_RAPIDJSON_ASSERT(a);
  PyObject* b = NULL;
  SET_GET_((&s, a), (&s, &b));
  EXPECT_EQ(PyObject_RichCompareBool(a, b, Py_EQ), 1);
  Py_DECREF(a);
  Py_DECREF(b);
}
TEST(VarArgs, PythonClass) {
  Document s;
  s.Parse("{\"type\": \"class\"}");
  PyObject* a = import_python_class("example_python", "ExampleClass");
  YGGDRASIL_RAPIDJSON_ASSERT(a);
  PyObject* b = NULL;
  SET_GET_((&s, a), (&s, &b));
  EXPECT_EQ(PyObject_RichCompareBool(a, b, Py_EQ), 1);
  Py_DECREF(a);
  Py_DECREF(b);
}
TEST(VarArgs, PythonInstance) {
  Document s;
  s.Parse("{\"type\": \"instance\"}");
  CREATE_PYTHON_INSTANCE(ExampleClass, a)
  YGGDRASIL_RAPIDJSON_ASSERT(a);
  PyObject* b = NULL;
  SET_GET_((&s, a), (&s, &b));
  EXPECT_EQ(PyObject_RichCompareBool(a, b, Py_EQ), 1);
  Py_DECREF(a);
  Py_DECREF(b);
}
#endif // YGGDRASIL_DISABLE_PYTHON_C_API
TEST(VarArgs, Array) {
  Document s;
  s.Parse("{"
	  "  \"type\": \"array\","
	  "  \"items\": ["
	  "    {\"type\": \"boolean\"},"
	  "    {\"type\": \"string\"},"
	  "    {\"type\": \"number\"},"
	  "    {\"type\": \"scalar\","
	  "     \"subtype\": \"int\","
	  "     \"precision\": 1}"
	  "  ]"
	  "}");
  bool a1 = true;
  const char* a2 = "hello";
  size_t a2_len = 5;
  double a3 = 12.34;
  int8_t a4 = 3;
  bool b1 = true;
  char b2[10];
  size_t b2_len = 10;
  double b3 = 0;
  int8_t b4 = 0;
  SET_GET_((&s, a1, a2, a2_len, a3, a4), (&s, &b1, &b2, &b2_len, &b3, &b4));
  EXPECT_EQ(a1, b1);
  EXPECT_EQ(a2_len, b2_len);
  EXPECT_EQ(strcmp(a2, b2), 0);
  EXPECT_EQ(a3, b3);
  EXPECT_EQ(a4, b4);
}
TEST(VarArgs, Object) {
  Document s;
  s.Parse("{"
	  "  \"type\": \"object\","
	  "  \"properties\": {"
	  "    \"a\": {\"type\": \"boolean\"},"
	  "    \"b\": {\"type\": \"string\"},"
	  "    \"c\": {\"type\": \"number\"},"
	  "    \"d\": {\"type\": \"scalar\","
	  "            \"subtype\": \"int\","
	  "            \"precision\": 1}"
	  "  }"
	  "}");
  bool a1 = true;
  const char* a2 = "hello";
  size_t a2_len = 5;
  double a3 = 12.34;
  int8_t a4 = 3;
  bool b1 = true;
  char b2[10];
  size_t b2_len = 10;
  double b3 = 0;
  int8_t b4 = 0;
  SET_GET_((&s, a1, a2, a2_len, a3, a4), (&s, &b1, &b2, &b2_len, &b3, &b4));
  EXPECT_EQ(a1, b1);
  EXPECT_EQ(a2_len, b2_len);
  EXPECT_EQ(strcmp(a2, b2), 0);
  EXPECT_EQ(a3, b3);
  EXPECT_EQ(a4, b4);
}
bool method_variable(Document* schema1, bool realloc1, int set1,
		     Document* schema2, bool realloc2, int set2, ...) {
  size_t nargs1 = countVarArgs(*schema1, static_cast<bool>(set1));
  size_t nargs2 = countVarArgs(*schema2, static_cast<bool>(set2));
  size_t nargs = nargs1 + nargs2;
  VarArgList* ap1 = new VarArgList(nargs, realloc1);
  va_start(ap1->va, set2);
  VarArgList* ap2 = new VarArgList(*ap1);
  Document d;
  if (!d.GetVarArgs(*schema1, *ap1))
    return false;
  ap1->allow_realloc = realloc2;
  if (!ap1->skip(*schema2, static_cast<bool>(set2)))
    return false;
  EXPECT_EQ(ap1->get_nargs(), 0);
  if (!ap2->skip(*schema1, static_cast<bool>(set1)))
    return false;
  ap2->allow_realloc = realloc2;
  if (!d.SetVarArgs(*schema2, *ap2))
    return false;
  EXPECT_EQ(ap2->get_nargs(), 0);
  delete ap1;
  delete ap2;
  return true;
}
TEST(VarArgs, Skip) {
  Document s1;
  s1.Parse("{"
	   "  \"type\": \"array\","
	   "  \"items\": ["
	   "    {\"type\": \"boolean\"},"
	   "    {\"type\": \"string\"},"
	   "    {\"type\": \"number\"},"
	   "    {\"type\": \"scalar\","
	   "     \"subtype\": \"int\","
	   "     \"precision\": 1}"
	   "  ]"
	   "}");
  Document s2;
  s2.Parse("{"
	   "  \"type\": \"array\","
	   "  \"items\": ["
	   "    {\"type\": \"boolean\"},"
	   "    {\"type\": \"string\"},"
	   "    {\"type\": \"number\"},"
	   "    {\"type\": \"scalar\","
	   "     \"subtype\": \"int\","
	   "     \"precision\": 1}"
	   "  ]"
	   "}");
  bool a1 = true;
  const char* a2 = "hello";
  size_t a2_len = 5;
  double a3 = 12.34;
  int8_t a4 = 3;
  bool b1 = true;
  char b2[10];
  size_t b2_len = 10;
  double b3 = 0;
  int8_t b4 = 0;
  EXPECT_TRUE(method_variable(&s1, false, 0,
			      &s2, false, 1,
			      a1, a2, a2_len, a3, a4,
			      &b1, &b2, &b2_len, &b3, &b4));
  EXPECT_EQ(a1, b1);
  EXPECT_EQ(a2_len, b2_len);
  EXPECT_EQ(strcmp(a2, b2), 0);
  EXPECT_EQ(a3, b3);
  EXPECT_EQ(a4, b4);
}
TEST(VarArgs, TableArray) {
  Document s;
  s.Parse("{"
	  "  \"type\": \"array\","
	  "  \"items\": ["
	  "    {"
	  "      \"type\": \"ndarray\","
	  "      \"subtype\": \"string\","
	  "      \"precision\": 6,"
	  "      \"length\": 3"
	  "    },"
	  "    {"
	  "      \"type\": \"ndarray\","
	  "      \"subtype\": \"int\","
	  "      \"precision\": 4,"
	  "      \"length\": 3"
	  "    },"
	  "    {"
	  "      \"type\": \"ndarray\","
	  "      \"subtype\": \"float\","
	  "      \"precision\": 8,"
	  "      \"length\": 3"
	  "    }"
	  "  ]"
	  "}");
  size_t a0 = 3;
  const char a1[3][6] = { "test1", "test2", "test3" };
  int32_t a2[3] = { 0, 1, 2 };
  double a3[3] = { 0.0, 1.1, 2.2 };
  size_t b0 = 0;
  char* b1 = NULL;
  int32_t* b2 = NULL;
  double* b3 = NULL;
  SET_GET_REALLOC_((&s, a0, a1, a2, a3), (&s, &b0, &b1, &b2, &b3));
  EXPECT_EQ(a0, b0);
  for (size_t i = 0; i < a0; i++) {
    EXPECT_EQ(a2[i], b2[i]);
    EXPECT_EQ(a3[i], b3[i]);
    EXPECT_EQ(strcmp(a1[i], b1 + 6*i), 0);
  }
  free(b1);
  free(b2);
  free(b3);
}
TEST(VarArgs, Any) {
  Document s;
  s.Parse("{\"type\": \"any\"}");
  Document a;
  a.Parse("24");
  Document b;
  SET_GET_((&s, &a), (&s, &b));
  EXPECT_EQ(a, b);
}
TEST(VarArgs, AnyRealloc) {
  Document s;
  s.Parse("{\"type\": \"any\"}");
  Document a;
  a.Parse("24");
  Document* b = NULL;
  SET_GET_REALLOC_((&s, &a), (&s, &b));
  EXPECT_EQ(a, *b);
  delete b;
}
#endif // DISABLE_YGGDRASIL_RAPIDJSON

#ifdef __clang__
YGGDRASIL_RAPIDJSON_DIAG_POP
#endif
