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

// Using forward declared types here.

#include "yggdrasil_rapidjson/fwd.h"

#ifdef __GNUC__
YGGDRASIL_RAPIDJSON_DIAG_PUSH
YGGDRASIL_RAPIDJSON_DIAG_OFF(effc++)
#endif

using namespace yggdrasil_rapidjson;

struct Foo {
    Foo();
    ~Foo();

    // encodings.h
    UTF8<char>* utf8;
    UTF16<wchar_t>* utf16;
    UTF16BE<wchar_t>* utf16be;
    UTF16LE<wchar_t>* utf16le;
    UTF32<unsigned>* utf32;
    UTF32BE<unsigned>* utf32be;
    UTF32LE<unsigned>* utf32le;
    ASCII<char>* ascii;
    AutoUTF<unsigned>* autoutf;
    Transcoder<UTF8<char>, UTF8<char> >* transcoder;

    // allocators.h
    CrtAllocator* crtallocator;
    MemoryPoolAllocator<CrtAllocator>* memorypoolallocator;

    // stream.h
    StringStream* stringstream;
    InsituStringStream* insitustringstream;

    // stringbuffer.h
    StringBuffer* stringbuffer;

    // // filereadstream.h
    // FileReadStream* filereadstream;

    // // filewritestream.h
    // FileWriteStream* filewritestream;

    // memorybuffer.h
    MemoryBuffer* memorybuffer;

    // memorystream.h
    MemoryStream* memorystream;

    // reader.h
    BaseReaderHandler<UTF8<char>, void>* basereaderhandler;
    Reader* reader;

    // writer.h
    Writer<StringBuffer, UTF8<char>, UTF8<char>, CrtAllocator, 0>* writer;

    // prettywriter.h
    PrettyWriter<StringBuffer, UTF8<char>, UTF8<char>, CrtAllocator, 0>* prettywriter;

    // document.h
    Value* value;
    Document* document;

    // pointer.h
    Pointer* pointer;

    // schema.h
    SchemaDocument* schemadocument;
    SchemaValidator* schemavalidator;

    // char buffer[16];
};

// Using type definitions here.

#include "yggdrasil_rapidjson/stringbuffer.h"
#include "yggdrasil_rapidjson/filereadstream.h"
#include "yggdrasil_rapidjson/filewritestream.h"
#include "yggdrasil_rapidjson/memorybuffer.h"
#include "yggdrasil_rapidjson/memorystream.h"
#include "yggdrasil_rapidjson/document.h" // -> reader.h
#include "yggdrasil_rapidjson/writer.h"
#include "yggdrasil_rapidjson/prettywriter.h"
#include "yggdrasil_rapidjson/schema.h"   // -> pointer.h

typedef Transcoder<UTF8<>, UTF8<> > TranscoderUtf8ToUtf8;
typedef BaseReaderHandler<UTF8<>, void> BaseReaderHandlerUtf8Void;

Foo::Foo() : 
    // encodings.h
    utf8(YGGDRASIL_RAPIDJSON_NEW(UTF8<>)),
    utf16(YGGDRASIL_RAPIDJSON_NEW(UTF16<>)),
    utf16be(YGGDRASIL_RAPIDJSON_NEW(UTF16BE<>)),
    utf16le(YGGDRASIL_RAPIDJSON_NEW(UTF16LE<>)),
    utf32(YGGDRASIL_RAPIDJSON_NEW(UTF32<>)),
    utf32be(YGGDRASIL_RAPIDJSON_NEW(UTF32BE<>)),
    utf32le(YGGDRASIL_RAPIDJSON_NEW(UTF32LE<>)),
    ascii(YGGDRASIL_RAPIDJSON_NEW(ASCII<>)),
    autoutf(YGGDRASIL_RAPIDJSON_NEW(AutoUTF<unsigned>)),
    transcoder(YGGDRASIL_RAPIDJSON_NEW(TranscoderUtf8ToUtf8)),

    // allocators.h
    crtallocator(YGGDRASIL_RAPIDJSON_NEW(CrtAllocator)),
    memorypoolallocator(YGGDRASIL_RAPIDJSON_NEW(MemoryPoolAllocator<>)),

    // stream.h
    stringstream(YGGDRASIL_RAPIDJSON_NEW(StringStream)(NULL)),
    insitustringstream(YGGDRASIL_RAPIDJSON_NEW(InsituStringStream)(NULL)),

    // stringbuffer.h
    stringbuffer(YGGDRASIL_RAPIDJSON_NEW(StringBuffer)),

    // // filereadstream.h
    // filereadstream(YGGDRASIL_RAPIDJSON_NEW(FileReadStream)(stdout, buffer, sizeof(buffer))),

    // // filewritestream.h
    // filewritestream(YGGDRASIL_RAPIDJSON_NEW(FileWriteStream)(stdout, buffer, sizeof(buffer))),

    // memorybuffer.h
    memorybuffer(YGGDRASIL_RAPIDJSON_NEW(MemoryBuffer)),

    // memorystream.h
    memorystream(YGGDRASIL_RAPIDJSON_NEW(MemoryStream)(NULL, 0)),

    // reader.h
    basereaderhandler(YGGDRASIL_RAPIDJSON_NEW(BaseReaderHandlerUtf8Void)),
    reader(YGGDRASIL_RAPIDJSON_NEW(Reader)),

    // writer.h
    writer(YGGDRASIL_RAPIDJSON_NEW(Writer<StringBuffer>)),

    // prettywriter.h
    prettywriter(YGGDRASIL_RAPIDJSON_NEW(PrettyWriter<StringBuffer>)),

    // document.h
    value(YGGDRASIL_RAPIDJSON_NEW(Value)),
    document(YGGDRASIL_RAPIDJSON_NEW(Document)),

    // pointer.h
    pointer(YGGDRASIL_RAPIDJSON_NEW(Pointer)),

    // schema.h
    schemadocument(YGGDRASIL_RAPIDJSON_NEW(SchemaDocument)(*document)),
    schemavalidator(YGGDRASIL_RAPIDJSON_NEW(SchemaValidator)(*schemadocument))
{

}

Foo::~Foo() {
    // encodings.h
    YGGDRASIL_RAPIDJSON_DELETE(utf8);
    YGGDRASIL_RAPIDJSON_DELETE(utf16);
    YGGDRASIL_RAPIDJSON_DELETE(utf16be);
    YGGDRASIL_RAPIDJSON_DELETE(utf16le);
    YGGDRASIL_RAPIDJSON_DELETE(utf32);
    YGGDRASIL_RAPIDJSON_DELETE(utf32be);
    YGGDRASIL_RAPIDJSON_DELETE(utf32le);
    YGGDRASIL_RAPIDJSON_DELETE(ascii);
    YGGDRASIL_RAPIDJSON_DELETE(autoutf);
    YGGDRASIL_RAPIDJSON_DELETE(transcoder);

    // allocators.h
    YGGDRASIL_RAPIDJSON_DELETE(crtallocator);
    YGGDRASIL_RAPIDJSON_DELETE(memorypoolallocator);

    // stream.h
    YGGDRASIL_RAPIDJSON_DELETE(stringstream);
    YGGDRASIL_RAPIDJSON_DELETE(insitustringstream);

    // stringbuffer.h
    YGGDRASIL_RAPIDJSON_DELETE(stringbuffer);

    // // filereadstream.h
    // YGGDRASIL_RAPIDJSON_DELETE(filereadstream);

    // // filewritestream.h
    // YGGDRASIL_RAPIDJSON_DELETE(filewritestream);

    // memorybuffer.h
    YGGDRASIL_RAPIDJSON_DELETE(memorybuffer);

    // memorystream.h
    YGGDRASIL_RAPIDJSON_DELETE(memorystream);

    // reader.h
    YGGDRASIL_RAPIDJSON_DELETE(basereaderhandler);
    YGGDRASIL_RAPIDJSON_DELETE(reader);

    // writer.h
    YGGDRASIL_RAPIDJSON_DELETE(writer);

    // prettywriter.h
    YGGDRASIL_RAPIDJSON_DELETE(prettywriter);

    // document.h
    YGGDRASIL_RAPIDJSON_DELETE(value);
    YGGDRASIL_RAPIDJSON_DELETE(document);

    // pointer.h
    YGGDRASIL_RAPIDJSON_DELETE(pointer);

    // schema.h
    YGGDRASIL_RAPIDJSON_DELETE(schemadocument);
    YGGDRASIL_RAPIDJSON_DELETE(schemavalidator);
}

TEST(Fwd, Fwd) {
    Foo f;
}

#ifdef __GNUC__
YGGDRASIL_RAPIDJSON_DIAG_POP
#endif
