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

#ifndef DISABLE_YGGDRASIL_RAPIDJSON

#define YGGDRASIL_RAPIDJSON_SCHEMA_VERBOSE 0
#define YGGDRASIL_RAPIDJSON_HAS_STDSTRING 1

#include "unittest.h"
#include "yggdrasil_rapidjson/schema.h"
#include "yggdrasil_rapidjson/stringbuffer.h"
#include "yggdrasil_rapidjson/writer.h"
#include "yggdrasil_rapidjson/prettywriter.h"
#include "yggdrasil_rapidjson/error/error.h"
#include "yggdrasil_rapidjson/error/en.h"

#ifdef __clang__
YGGDRASIL_RAPIDJSON_DIAG_PUSH
YGGDRASIL_RAPIDJSON_DIAG_OFF(variadic-macros)
#elif defined(_MSC_VER)
YGGDRASIL_RAPIDJSON_DIAG_PUSH
YGGDRASIL_RAPIDJSON_DIAG_OFF(4822) // local class member function does not have a body
#endif

using namespace yggdrasil_rapidjson;

#define NORMALIZE(schema, json, expected, normalized)	\
{\
    SchemaNormalizer normalizer(schema);\
    Document d;\
    d.Parse(json);\
    EXPECT_FALSE(d.HasParseError());\
    EXPECT_TRUE(expected == d.Accept(normalizer));	\
    EXPECT_TRUE(expected == normalizer.IsValid());\
    ValidateErrorCode code = normalizer.GetInvalidSchemaCode();\
    if (expected) {\
      EXPECT_TRUE(code == kValidateErrorNone ||			\
		  code == kValidateWarnings);			\
      EXPECT_TRUE(normalizer.GetInvalidSchemaKeyword() == 0 ||		\
		  (strcmp(normalizer.GetInvalidSchemaKeyword(), "warnings") == 0)); \
      EXPECT_TRUE(normalizer.WasNormalized());\
      SchemaValidator validator(schema);\
      EXPECT_TRUE(normalizer.GetNormalized().Accept(validator));\
      if (!validator.IsValid()) {				\
	StringBuffer sb;					\
	PrettyWriter<StringBuffer> w(sb);			\
	validator.GetError().Accept(w);				\
	printf("Validation error: %s\n", sb.GetString());	\
      }								\
    }\
    if ((expected) && !normalizer.IsValid()) {\
        normalizer.GetNormalizedDoc().FinalizeFromStack(true);	\
        StringBuffer sb;\
        normalizer.GetInvalidSchemaPointer().StringifyUriFragment(sb);\
        printf("Invalid schema: %s\n", sb.GetString());\
        printf("Invalid keyword: %s\n", normalizer.GetInvalidSchemaKeyword());\
        printf("Invalid code: %d\n", code);\
        printf("Invalid message: %s\n", GetValidateError_En(code));\
        sb.Clear();\
        normalizer.GetInvalidDocumentPointer().StringifyUriFragment(sb);\
        printf("Invalid document: %s\n", sb.GetString());\
        sb.Clear();\
        PrettyWriter<StringBuffer> w(sb);	\
        normalizer.GetError().Accept(w);\
        printf("Validation error: %s\n", sb.GetString());\
    }\
    Document n;\
    n.Parse(normalized);\
    EXPECT_FALSE(n.HasParseError());\
    if (normalizer.GetNormalized() != n) {\
        StringBuffer sb;\
        PrettyWriter<StringBuffer> w(sb);		\
        normalizer.GetNormalized().Accept(w);\
	StringBuffer sb0;\
	PrettyWriter<StringBuffer> w0(sb0);\
	n.Accept(w0);\
        printf("GetNormalized() Expected: %s Actual: %s\n", sb0.GetString(), sb.GetString()); \
        ADD_FAILURE();\
    }\
}
#define NO_NORMALIZE(schema, json)		\
{\
    SchemaNormalizer normalizer(schema);\
    Document d;\
    d.Parse(json);\
    EXPECT_FALSE(d.HasParseError());\
    EXPECT_TRUE(true == d.Accept(normalizer));	\
    EXPECT_TRUE(true == normalizer.IsValid());\
    ValidateErrorCode code = normalizer.GetInvalidSchemaCode();\
    EXPECT_TRUE(code == kValidateErrorNone);		       \
    EXPECT_TRUE(normalizer.GetInvalidSchemaKeyword() == 0);    \
    EXPECT_FALSE(normalizer.WasNormalized());		       \
    if (!normalizer.IsValid()) {\
        StringBuffer sb;\
        normalizer.GetInvalidSchemaPointer().StringifyUriFragment(sb);\
        printf("Invalid schema: %s\n", sb.GetString());\
        printf("Invalid keyword: %s\n", normalizer.GetInvalidSchemaKeyword());\
        printf("Invalid code: %d\n", code);\
        printf("Invalid message: %s\n", GetValidateError_En(code));\
        sb.Clear();\
        normalizer.GetInvalidDocumentPointer().StringifyUriFragment(sb);\
        printf("Invalid document: %s\n", sb.GetString());\
        sb.Clear();\
        PrettyWriter<StringBuffer> w(sb);	\
        normalizer.GetError().Accept(w);\
        printf("Validation error: %s\n", sb.GetString());\
    }\
    if (normalizer.GetNormalized() != d) {\
        StringBuffer sb;\
        PrettyWriter<StringBuffer> w(sb);		\
        normalizer.GetNormalized().Accept(w);\
	StringBuffer sb0;\
	PrettyWriter<StringBuffer> w0(sb0);\
	d.Accept(w0);							\
        printf("GetNormalized() Expected: %s Actual: %s\n", sb0.GetString(), sb.GetString()); \
        ADD_FAILURE();\
    }\
}

#define FAILED_NORMALIZE(schema, json, invalidSchemaPointer, invalidSchemaKeyword, invalidDocumentPointer, error) \
{\
    FAILED_NORMALIZE_(schema, json, invalidSchemaPointer, invalidSchemaKeyword, invalidDocumentPointer, error, SchemaNormalizer, Pointer) \
}
#define FAILED_NORMALIZE_(schema, json, invalidSchemaPointer, invalidSchemaKeyword, invalidDocumentPointer, error, \
    SchemaNormalizerType, PointerType) \
{\
    SchemaNormalizerType normalizer(schema);\
    Document d;\
    d.Parse(json);\
    EXPECT_FALSE(d.HasParseError());\
    d.Accept(normalizer);\
    EXPECT_FALSE(normalizer.IsValid());\
    ValidateErrorCode code = normalizer.GetInvalidSchemaCode();\
    normalizer.GetNormalizedDoc().FinalizeFromStack(true);     \
    ASSERT_TRUE(code != kValidateErrorNone);\
    ASSERT_TRUE(strcmp(GetValidateError_En(code), "Unknown error.") != 0);\
    if (normalizer.GetInvalidSchemaPointer() != PointerType(invalidSchemaPointer)) {\
        StringBuffer sb;\
        normalizer.GetInvalidSchemaPointer().Stringify(sb);\
        printf("GetInvalidSchemaPointer() Expected: %s Actual: %s\n", invalidSchemaPointer, sb.GetString());\
        ADD_FAILURE();\
    }\
    ASSERT_TRUE(normalizer.GetInvalidSchemaKeyword() != 0);\
    if (strcmp(normalizer.GetInvalidSchemaKeyword(), invalidSchemaKeyword) != 0) {\
        printf("GetInvalidSchemaKeyword() Expected: %s Actual %s\n", invalidSchemaKeyword, normalizer.GetInvalidSchemaKeyword());\
        ADD_FAILURE();\
    }\
    if (normalizer.GetInvalidDocumentPointer() != PointerType(invalidDocumentPointer)) {\
        StringBuffer sb;\
        normalizer.GetInvalidDocumentPointer().Stringify(sb);\
        printf("GetInvalidDocumentPointer() Expected: %s Actual: %s\n", invalidDocumentPointer, sb.GetString());\
        ADD_FAILURE();\
    }\
    Document e;							\
    e.Parse(error);						\
    YGGDRASIL_RAPIDJSON_DEFAULT_ALLOCATOR error_msg_allocator;		\
    Value e_msg;						\
    if (!normalizer.GetErrorMsg(e_msg, error_msg_allocator)) {	\
      StringBuffer sb_t;					\
      PrettyWriter<StringBuffer> w_t(sb_t);			\
      printf("ErrorMsg = %s\n", sb_t.GetString());		\
      StringBuffer sb;						\
      PrettyWriter<StringBuffer> w(sb);				\
      normalizer.GetError().Accept(w);				\
      printf("GetError(): %s", sb.GetString());			\
      ADD_FAILURE();						\
    }								\
    if (normalizer.GetError() != e) {\
        StringBuffer sb;\
        PrettyWriter<StringBuffer> w(sb);		\
        normalizer.GetError().Accept(w);\
        StringBuffer sb_e;\
        PrettyWriter<StringBuffer> w_e(sb_e);\
	e.Accept(w_e);\
        printf("GetError() Expected: %s Actual: %s\n", sb_e.GetString(), sb.GetString()); \
        ADD_FAILURE();\
    }\
}
#define MERGE_CONFLICT_ERROR(type, value, method)		\
  {								\
    Document sd;						\
    sd.Parse(							\
	     "{"						\
	     "  \"type\": \"object\","				\
	     "  \"allOf\": ["					\
	     "    { \"properties\": {"				\
	     "        \"a\": { \"type\": \"string\","		\
	     "                 \"default\": \"foo\" }},"	\
	     "      \"required\": [\"a\"]"			\
	     "    },"						\
	     "    { \"properties\": {"				\
	     "        \"a\": { \"type\": \"" #type "\","	\
	     "                 \"default\": " #value " }},"	\
	     "      \"required\": [\"a\"]"			\
	     "    }"						\
	     "  ]"						\
	     "}");						\
    SchemaDocument s(sd);					\
    FAILED_NORMALIZE(s, "{}", "/allOf/1", "normalization",	\
		     "/a",					\
		     "{ \"normalization\": {"			\
		     "    \"errorCode\": 41,"			\
		     "    \"instanceRef\": \"#/a\","		\
		     "    \"schemaRef\": \"#/allOf/1\","	\
		     "    \"conflicting\": \"" #method "\","	\
		     "    \"expected\": \"foo\","		\
		     "    \"actual\": " #value			\
		     "}}");					\
  }

#define MERGE_CONFLICT_ERROR_STRING(type, value0, value1, method)	\
  {								\
    Document sd;						\
    sd.Parse(							\
	     "{"						\
	     "  \"type\": \"object\","				\
	     "  \"allOf\": ["					\
	     "    { \"properties\": {"				\
	     "        \"a\": { \"type\": \"boolean\","		\
	     "                 \"default\": false }},"		\
	     "      \"required\": [\"a\"]"			\
	     "    },"						\
	     "    { \"properties\": {"				\
	     "        \"a\": { \"type\": \"" #type "\","	\
	     "                 \"default\": " value0 " }},"	\
	     "      \"required\": [\"a\"]"			\
	     "    }"						\
	     "  ]"						\
	     "}");						\
    SchemaDocument s(sd);					\
    FAILED_NORMALIZE(s, "{}", "/allOf/1", "normalization",	\
		     "/a",					\
		     "{ \"normalization\": {"			\
		     "    \"errorCode\": 41,"			\
		     "    \"instanceRef\": \"#/a\","		\
		     "    \"schemaRef\": \"#/allOf/1\","	\
		     "    \"conflicting\": \"" #method "\","	\
		     "    \"expected\": false,"			\
		     "    \"actual\": " value1			\
		     "}}");					\
  }

TEST(SchemaNormalizer, BaseTypes) {
    Document sd;
    sd.Parse(
        "{"
	"  \"type\": \"object\","
	"  \"allOf\": ["
	"    {"
	"      \"properties\": {"
	"        \"a\": {\"type\": \"null\", \"default\": null},"
	"        \"b\": {\"type\": \"boolean\", \"default\": false},"
	"        \"c\": {\"type\": \"integer\", \"default\": -1},"
	"        \"d\": {\"type\": \"integer\", \"default\": -9223372036854775808},"
	"        \"e\": {\"type\": \"integer\", \"default\": 9223372036854775807},"
	"        \"f\": {\"type\": \"integer\", \"default\": 1},"
	"        \"g\": {\"type\": \"number\", \"default\": 3.583},"
	"        \"h\": {\"type\": \"string\", \"default\": \"foo\"},"
	"        \"i\": {\"type\": \"array\", \"default\": [ 2, 4, 8 ]," 
	"                \"items\": {\"type\": \"integer\"}},"
	"        \"j\": {\"type\": \"object\", "
	"                \"default\": { \"x\": 2, \"y\": 7, \"z\": -1},"
	"                \"additionalProperties\": {\"type\": \"integer\"}}"
	"      },"
	"      \"required\": [\"a\", \"b\", \"c\", \"d\", \"e\", \"f\", \"g\", \"h\", \"i\", \"j\"]"
	"    },"
        "    {"
	"      \"properties\": {"
	"        \"k\": {\"type\": \"scalar\", \"subtype\": \"uint\","
	"                \"precision\": 1,"
	"                \"default\": \"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InVpbnQiLCJwcmVjaXNpb24iOjEsInVuaXRzIjoiZyJ9-YGG-DA==-YGG-\"},"
	"        \"n\": {\"type\": \"schema\","
	"                \"default\": \"-YGG-eyJ0eXBlIjoic2NoZW1hIn0=-YGG-eyJ0eXBlIjoic2NhbGFyIiwicHJlY2lzaW9uIjo4LCJzdWJ0eXBlIjoiaW50In0=-YGG-\"},"
	"        \"o\": {\"type\": \"1darray\", \"subtype\": \"float\","
	"                \"precision\": 8, \"length\": 4,"
	"                \"default\": \"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6OCwic2hhcGUiOls0XX0=-YGG-AAAAAAAAAAAAAAAAAADwPwAAAAAAAABAAAAAAAAACEA=-YGG-\"},"
	"        \"p\": {\"type\": \"ndarray\", \"subtype\": \"float\","
	"                \"precision\": 4, \"shape\": [2, 3],"
	"                \"default\": \"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6NCwic2hhcGUiOlsyLDNdfQ==-YGG-AAAAAAAAgD8AAABAAABAQAAAgEAAAKBA-YGG-\"}"
	"      },"
	"      \"required\": [\"k\", "
	"\"n\", \"o\", \"p\"]"
	"    }"
	"  ]"
	"}");
    SchemaDocument s(sd);
    NO_NORMALIZE(s, "{ \"a\": null, \"b\": false, \"c\": -1, \"d\": -9223372036854775808, \"e\": 9223372036854775807, \"f\": 1, \"g\": 3.583, \"h\": \"foo\", \"i\": [ 2, 4, 8 ], \"j\": { \"x\": 2, \"y\": 7, \"z\": -1}, "
		 "\"k\": \"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InVpbnQiLCJwcmVjaXNpb24iOjEsInVuaXRzIjoiZyJ9-YGG-DA==-YGG-\", "
		 "\"n\": \"-YGG-eyJ0eXBlIjoic2NoZW1hIn0=-YGG-eyJ0eXBlIjoic2NhbGFyIiwicHJlY2lzaW9uIjo4LCJzdWJ0eXBlIjoiaW50In0=-YGG-\", "
		 "\"o\": \"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6OCwic2hhcGUiOls0XX0=-YGG-AAAAAAAAAAAAAAAAAADwPwAAAAAAAABAAAAAAAAACEA=-YGG-\", "
		 "\"p\": \"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6NCwic2hhcGUiOlsyLDNdfQ==-YGG-AAAAAAAAgD8AAABAAABAQAAAgEAAAKBA-YGG-\" }");
    NORMALIZE(s, "{}", true,
	      "{ \"a\": null, \"b\": false, \"c\": -1, \"d\": -9223372036854775808, \"e\": 9223372036854775807, \"f\": 1, \"g\": 3.583, \"h\": \"foo\", \"i\": [ 2, 4, 8 ], \"j\": { \"x\": 2, \"y\": 7, \"z\": -1}, "
	      "\"k\": \"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InVpbnQiLCJwcmVjaXNpb24iOjEsInVuaXRzIjoiZyJ9-YGG-DA==-YGG-\", "
	      "\"n\": \"-YGG-eyJ0eXBlIjoic2NoZW1hIn0=-YGG-eyJ0eXBlIjoic2NhbGFyIiwicHJlY2lzaW9uIjo4LCJzdWJ0eXBlIjoiaW50In0=-YGG-\", "
	      "\"o\": \"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6OCwic2hhcGUiOls0XX0=-YGG-AAAAAAAAAAAAAAAAAADwPwAAAAAAAABAAAAAAAAACEA=-YGG-\", "
	      "\"p\": \"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6NCwic2hhcGUiOlsyLDNdfQ==-YGG-AAAAAAAAgD8AAABAAABAQAAAgEAAAKBA-YGG-\" }");
}

#ifdef YGGDRASIL_DISABLE_PYTHON_C_API
TEST(SchemaNormalizer, PythonType) {
    Document sd;
    sd.Parse(
        "{"
	"  \"type\": \"object\","
	"  \"allOf\": ["
	"    {"
	"      \"properties\": {"
	"        \"l\": {\"type\": \"function\","
	"                \"default\": \"-YGG-eyJ0eXBlIjoiY2xhc3MifQ==-YGG-ZXhhbXBsZV9weXRob246RXhhbXBsZUNsYXNz-YGG-\"},"
	"        \"m\": {\"type\": \"instance\","
	"                \"default\": \"-YGG-eyJ0eXBlIjoiaW5zdGFuY2UifQ==-YGG-eyJjbGFzcyI6ImV4YW1wbGVfcHl0aG9uOkV4YW1wbGVTdWJDbGFzcyIsImFyZ3MiOlsiaGVsbG8iLDAuNV0sImt3YXJncyI6eyJhIjoid29ybGQiLCJiIjoxfX0=-YGG-\"}"
	"      },"
	"      \"required\": [\"l\", \"m\"]"
	"    }"
	"  ]"
	"}");
    SchemaDocument s(sd);
    NO_NORMALIZE(s,
		 "{"
		 "  \"k\": \"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InVpbnQiLCJwcmVjaXNpb24iOjEsInVuaXRzIjoiZyJ9-YGG-DA==-YGG-\", "
		 "  \"l\": \"-YGG-eyJ0eXBlIjoiY2xhc3MifQ==-YGG-ZXhhbXBsZV9weXRob246RXhhbXBsZUNsYXNz-YGG-\", "
		 "  \"m\": \"-YGG-eyJ0eXBlIjoiaW5zdGFuY2UifQ==-YGG-eyJjbGFzcyI6ImV4YW1wbGVfcHl0aG9uOkV4YW1wbGVTdWJDbGFzcyIsImFyZ3MiOlsiaGVsbG8iLDAuNV0sImt3YXJncyI6eyJhIjoid29ybGQiLCJiIjoxfX0=-YGG-\""
		 "}");
    NORMALIZE(s, "{}", true,
	      "{"
	      "  \"l\": \"-YGG-eyJ0eXBlIjoiY2xhc3MifQ==-YGG-ZXhhbXBsZV9weXRob246RXhhbXBsZUNsYXNz-YGG-\", "
	      "  \"m\": \"-YGG-eyJ0eXBlIjoiaW5zdGFuY2UifQ==-YGG-eyJjbGFzcyI6ImV4YW1wbGVfcHl0aG9uOkV4YW1wbGVTdWJDbGFzcyIsImFyZ3MiOlsiaGVsbG8iLDAuNV0sImt3YXJncyI6eyJhIjoid29ybGQiLCJiIjoxfX0=-YGG-\""
	      "}");
}
#endif // YGGDRASIL_DISABLE_PYTHON_C_API

TEST(SchemaNormalizer, Default) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\"} }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }");
}

TEST(SchemaNormalizer, InvalidDefault) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\" },"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": 1 }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\"} }",
		     "/properties/shipping_address", "enum",
		     "/shipping_address",
		     "{ \"enum\": {"
		     "    \"expected\": [ \"residential\", \"business\" ],"
		     "    \"errorCode\": 19,"
		     "    \"instanceRef\": \"#/shipping_address/type\","
		     "    \"schemaRef\": \"#/properties/shipping_address/properties/type\""
		     "}}");
}

// TODO: Fix this so that it works
// TEST(SchemaNormalizer, PushWithDefault) {
//   Document sd;
//   sd.Parse("{ \"type\": \"object\","
// 	   "  \"pushProperties\": {"
// 	   "    \"$properties/x\": true"
// 	   "  },"
// 	   "  \"properties\": { \"x\": {"
// 	   "  \"allOf\": ["
// 	   "    {"
// 	   "      \"type\": \"object\","
// 	   "      \"properties\": {"
// 	   "        \"subtype\": {\"enum\": [\"a\", \"b\"]},"
// 	   "        \"subval\": {\"type\": \"string\"}"
// 	   "      }"
// 	   "    },"
// 	   "    {"
// 	   "      \"anyOf\": ["
// 	   "        {"
// 	   "          \"type\": \"object\","
// 	   "          \"properties\": {"
// 	   "            \"subtype\": {\"enum\": [\"a\"], \"default\": \"a\"},"
// 	   "            \"subval\": {\"type\": \"string\", \"default\": \"hello\"}"
// 	   "          },"
// 	   "          \"required\": [\"subtype\", \"subval\"]"
// 	   "        },"
// 	   "        {"
// 	   "          \"type\": \"object\","
// 	   "          \"properties\": {"
// 	   "            \"subtype\": {\"enum\": [\"b\"], \"default\": \"b\"}"
// 	   "          },"
// 	   "          \"required\": [\"subtype\"]"
// 	   "        }"
// 	   "      ]"
// 	   "    }"
// 	   "  ]"
// 	   "}}}");
//   SchemaDocument s(sd);
//   NORMALIZE(s, "{\"subtype\": \"b\", \"x\": {}}", true,
// 	    "{\"x\": {\"subtype\": \"b\"}}");
// }

TEST(SchemaNormalizer, ConditionalDefault) {
    Document sd;
    sd.Parse("{"
	     "  \"allOf\": ["
	     "    {\"type\": \"object\","
	     "     \"properties\": {"
	     "       \"a\": {\"type\": \"string\", \"default\": \"0\"},"
	     "       \"b\": {\"type\": \"string\"}"
	     "     }"
	     "    },"
	     "    {"
	     "      \"anyOf\": ["
	     "        {"
	     "          \"type\": \"object\","
	     "          \"properties\": {"
	     "            \"a\": {\"type\": \"string\","
	     "                    \"default\": \"1\","
	     "                    \"enum\": [\"1\"]},"
	     "            \"b\": {\"type\": \"string\"}"
	     "          },"
	     "          \"required\": [\"a\", \"b\"]"
	     "        },"
	     "        {"
	     "          \"type\": \"object\","
	     "          \"properties\": {"
	     "            \"a\": {\"type\": \"string\","
	     "                    \"default\": \"2\","
	     "                    \"enum\": [\"2\"]},"
	     "            \"b\": {\"type\": \"string\","
	     "                    \"default\": \"10\"}"
	     "          },"
	     "          \"required\": [\"a\", \"b\"]"
	     "        }"
	     "      ]"
	     "    }"
	     "  ]"
	     "}");
    SchemaDocument s(sd);
    NORMALIZE(s, "{\"b\": \"1\"}", true,
	      "{\"b\": \"1\", \"a\": \"1\"}");
    NORMALIZE(s, "{}", true,
	      "{\"a\": \"2\", \"b\": \"10\"}");
    FAILED_NORMALIZE(s, "{\"a\": \"1\"}",
		     "", "allOf", "",
		     "{ \"allOf\": {"
		     "  \"errorCode\": 23,"
		     "  \"instanceRef\": \"#\","
		     "  \"schemaRef\": \"#\","
		     "  \"errors\": ["
		     "    {},"
		     "    { \"anyOf\": {"
		     "      \"errorCode\": 24,"
		     "      \"instanceRef\": \"#\","
		     "      \"schemaRef\": \"#/allOf/1\","
		     "      \"errors\": ["
		     "        { \"required\": {"
		     "          \"errorCode\": 15,"
		     "          \"instanceRef\": \"#\","
		     "          \"schemaRef\": \"#/allOf/1/anyOf/0\","
		     "          \"missing\": [\"b\"]"
		     "        } },"
		     "        { \"enum\": {"
		     "          \"errorCode\": 19,"
		     "          \"instanceRef\": \"#/a\","
		     "          \"schemaRef\": \"#/allOf/1/anyOf/1/properties/a\","
		     "          \"expected\": [\"2\"]"
		     "        } }"
		     "      ]"
		     "    }}"
		     "  ]"
		     "}}");
}

TEST(SchemaNormalizer, MergeAllOf) {
    // TODO: Allow normalization when aliases not in base schema
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"allOf\": ["
        "    { \"properties\": {"
	"        \"field\": {"
	"          \"type\": \"string\","
	"          \"default\": \"b\","
	"          \"aliases\": [ \"column\" ]"
	"        }"
	"      },"
	"      \"required\": [\"field\"]"
	"    },"
        "    { \"properties\": {"
	"        \"field\": {"
	"          \"type\": \"string\","
	"          \"default\": \"c\","
	"          \"aliases\": [ \"column\" ]"
	"        }"
	"      },"
	"      \"required\": [\"field\"]"
	"    }"
	"  ]"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"column\": \"foo\"}",
	      true,
	      "{\"field\": \"foo\"}");
    NO_NORMALIZE(s, "{\"field\": \"foo\"}");
    FAILED_NORMALIZE(s, "{}", "/allOf/1", "normalization",
		     "/field",
		     "{ \"normalization\": {"
		     "    \"errorCode\": 41,"
		     "    \"instanceRef\": \"#/field\","
		     "    \"schemaRef\": \"#/allOf/1\","
		     "    \"conflicting\": \"string\","
		     "    \"expected\": \"b\","
		     "    \"actual\": \"c\""
		     "}}");
}

TEST(SchemaNormalizer, MergeAnyOf) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"field\": {"
	"      \"default\": \"a\","
	"      \"aliases\": [ \"column\" ]"
	"    }"
	"  },"
	"  \"required\": [\"field\"],"
	"  \"anyOf\": ["
        "    { \"properties\": {"
	"        \"field\": {"
	"          \"type\": \"string\","
	"          \"default\": \"b\","
	"          \"aliases\": [ \"column\" ]"
	"        }"
	"      },"
	"      \"required\": [\"field\"]"
	"    },"
        "    { \"properties\": {"
	"        \"field\": {"
	"          \"type\": \"string\","
	"          \"default\": \"c\","
	"          \"aliases\": [ \"column\" ]"
	"        }"
	"      },"
	"      \"required\": [\"field\"]"
	"    }"
	"  ]"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"column\": \"foo\"}",
	      true,
	      "{\"field\": \"foo\"}");
    NO_NORMALIZE(s, "{\"field\": \"foo\"}");
    FAILED_NORMALIZE(s, "{}", "/anyOf/0", "normalization",
		     "/field",
		     "{ \"normalization\": {"
		     "    \"errorCode\": 41,"
		     "    \"instanceRef\": \"#/field\","
		     "    \"schemaRef\": \"#/anyOf/0\","
		     "    \"conflicting\": \"string\","
		     "    \"expected\": \"a\","
		     "    \"actual\": \"b\""
		     "}}");
}

TEST(SchemaNormalizer, MergeOneOf) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"field\": {"
	"      \"default\": \"a\","
	"      \"aliases\": [ \"column\" ]"
	"    }"
	"  },"
	"  \"required\": [\"field\"],"
	"  \"oneOf\": ["
        "    { \"properties\": {"
	"        \"field\": {"
	"          \"type\": \"string\","
	"          \"default\": \"b\","
	"          \"aliases\": [ \"column\" ]"
	"        }"
	"      },"
	"      \"required\": [\"field\"],"
	"      \"additionalProperties\": false"
	"    },"
        "    { \"properties\": {"
	"        \"field\": {"
	"          \"type\": \"string\","
	"          \"default\": \"c\","
	"          \"aliases\": [ \"column\" ]"
	"        },"
	"        \"color\": {"
	"          \"type\": \"string\""
	"        }"
	"      },"
	"      \"required\": [\"field\", \"color\"]"
	"    }"
	"  ]"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"column\": \"foo\", \"color\": \"red\"}",
	      true,
	      "{\"field\": \"foo\", \"color\": \"red\"}");
    NO_NORMALIZE(s, "{\"field\": \"foo\", \"color\": \"red\"}");
    FAILED_NORMALIZE(s, "{}", "/oneOf/0", "normalization",
		     "/field",
		     "{ \"normalization\": {"
		     "    \"errorCode\": 41,"
		     "    \"instanceRef\": \"#/field\","
		     "    \"schemaRef\": \"#/oneOf/0\","
		     "    \"conflicting\": \"string\","
		     "    \"expected\": \"a\","
		     "    \"actual\": \"b\""
		     "}}");
}

TEST(SchemaNormalizer, MergeConflict) {
  {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"allOf\": ["
        "    { \"properties\": {"
        "        \"shipping_address\": { \"default\": \"a\" }},"
	"      \"required\": [\"shipping_address\"]"
	"    },"
        "    { \"properties\": {"
        "        \"shipping_address\": { \"default\": \"b\" }},"
	"      \"required\": [\"shipping_address\"]"
	"    }"
	"  ]"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s, "{}", "/allOf/1", "normalization",
		     "/shipping_address",
		     "{ \"normalization\": {"
		     "    \"errorCode\": 41,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/allOf/1\","
		     "    \"conflicting\": \"string\","
		     "    \"expected\": \"a\","
		     "    \"actual\": \"b\""
		     "}}");
  }
  MERGE_CONFLICT_ERROR(boolean, false, bool);
  MERGE_CONFLICT_ERROR(null, null, null);
  MERGE_CONFLICT_ERROR(integer, -2147483647, int);
  MERGE_CONFLICT_ERROR(integer, 2147483648, uint);  // 2^31, cannot cast
  MERGE_CONFLICT_ERROR(integer, -1234567890123456789, int64);
  MERGE_CONFLICT_ERROR(integer, 9223372036854775808, uint64);
  MERGE_CONFLICT_ERROR(number, 0.123, double);
  MERGE_CONFLICT_ERROR_STRING(scalar, "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImcifQ==-YGG-AAAAAABAj0A=-YGG-\"", "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImcifQ==-YGG-AAAAAABAj0A=-YGG-\"", yggString);
#ifndef YGGDRASIL_DISABLE_PYTHON_C_API
  MERGE_CONFLICT_ERROR_STRING(instance, "\"-YGG-eyJ0eXBlIjoiaW5zdGFuY2UifQ==-YGG-eyJjbGFzcyI6ImV4YW1wbGVfcHl0aG9uOkV4YW1wbGVTdWJDbGFzcyIsImFyZ3MiOlsiaGVsbG8iLDAuNV0sImt3YXJncyI6eyJhIjoid29ybGQiLCJiIjoxfX0=-YGG-\"", "\"-YGG-eyJ0eXBlIjoiaW5zdGFuY2UifQ==-YGG-e30=-YGG-\"", yggObject);
#endif // YGGDRASIL_DISABLE_PYTHON_C_API
}

TEST(SchemaNormalizer, MergeConflictNested) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"properties\": {"
	"    \"client\": {"
	"      \"allOf\": ["
        "        { \"properties\": {"
        "            \"shipping_address\": { \"default\": \"a\" }},"
	"          \"required\": [\"shipping_address\"]"
	"        },"
        "        { \"properties\": {"
        "            \"shipping_address\": { \"default\": \"b\" }},"
	"          \"required\": [\"shipping_address\"]"
	"        }"
	"      ]"
	"    }"
	"  }"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s, "{ \"client\": {} }",
		     "/properties/client/allOf/1", "normalization",
		     "/client/shipping_address",
		     "{ \"normalization\": {"
		     "    \"errorCode\": 41,"
		     "    \"instanceRef\": \"#/client/shipping_address\","
		     "    \"schemaRef\": \"#/properties/client/allOf/1\","
		     "    \"conflicting\": \"string\","
		     "    \"expected\": \"a\","
		     "    \"actual\": \"b\""
		     "}}");
}

TEST(SchemaNormalizer, DefaultNested) {
    Document sd;
    sd.Parse(
        "{"
        "  \"$schema\": \"http://json-schema.org/draft-04/schema#\","
        ""
        "  \"definitions\": {"
        "    \"address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"}"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\"]"
        "    }"
        "  },"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"allOf\": ["
        "        { \"$ref\": \"#/definitions/address\" },"
        "        { \"properties\":"
        "          { \"type\": { \"enum\": [ \"residential\", \"business\" ],"
	"                        \"default\": \"residential\" } },"
        "          \"required\": [\"type\"]"
        "        }"
        "      ]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\"} }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"default_state\", \"type\": \"residential\"} }");
}

TEST(SchemaNormalizer, Alias) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street\"]},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"street_address\": \"1700 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
		     "/properties/shipping_address", "aliases",
		     "/shipping_address/street_address",
		     "{ \"aliases\": {"
		     "    \"errorCode\": 38,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"duplicates\": [\"street\", \"street_address\"]"
		     "}}");
}

TEST(SchemaNormalizer, AliasArray) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_addresses\": { \"type\": \"array\","
	"                                \"items\": {\"type\": \"string\"},"
	"                                \"aliases\": [\"streets\"] }"
        "      },"
        "      \"required\": [\"street_addresses\"]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"streets\": [\"a\", \"b\"]}}",
	      true,
	      "{\"shipping_address\": {\"street_addresses\": [\"a\", \"b\"]}}");
}

TEST(SchemaNormalizer, AliasConflict) {
    Document sd;
    sd.Parse(
        "{"
	"  \"allOf\": ["
	"    {"
	"      \"type\": \"object\","
	"      \"properties\": {"
	"        \"a\": {\"aliases\": [\"a2\"]},"
	"        \"b\": {\"default\": \"foobar\","
	"                \"aliases\": [\"b3\"]}"
	"      },"
	"      \"required\": [\"b\"]"
	"    },"
	"    {"
	"      \"type\": \"object\","
	"      \"properties\": {"
	"        \"b\": {\"aliases\": [\"b2\"]}"
	"      }"
	"    }"
	"  ]"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s, "{\"b3\": \"foo\"}", true,
	      "{\"b\": \"foo\"}");
    FAILED_NORMALIZE(s,
		     "{\"b2\": \"bar\"}",
		     "", "aliases", "",
		     "{ \"aliases\": {"
		     "    \"errorCode\": 38,"
		     "    \"instanceRef\": \"#\","
		     "    \"schemaRef\": \"#\","
		     "    \"duplicates\": [\"b\", \"b2\"]"
		     "}}");
}

TEST(SchemaNormalizer, ArrayWrapped) {
  Document sd;
  sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"properties\": {"
	"     \"streets\": { \"type\": \"string\","
	"                    \"allowWrapped\": true,"
	"                    \"aliases\": [\"street\"] }},"
	"  \"required\": [\"streets\"]"
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s, "{ \"streets\": [\"1600 Pennsylvania Ave.\"] }", true,
	    "{ \"streets\": \"1600 Pennsylvania Ave.\" }");
}

TEST(SchemaNormalizer, ObjectWrapped) {
  Document sd;
  sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"properties\": {"
	"     \"streets\": { \"type\": \"string\","
	"                    \"allowWrapped\": \"key\","
	"                    \"aliases\": [\"street\"] }},"
	"  \"required\": [\"streets\"]"
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s, "{ \"streets\": {\"key\": \"1600 Pennsylvania Ave.\"} }", true,
	    "{ \"streets\": \"1600 Pennsylvania Ave.\" }");
}

TEST(SchemaNormalizer, SingularArray) {
  Document sd;
  sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"properties\": {"
	"     \"streets\": { \"type\": \"array\","
	"                    \"items\": {\"type\": \"string\"},"
	"                    \"allowSingular\": true,"
	"                    \"aliases\": [\"street\"] }},"
	"  \"required\": [\"streets\"]"
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s, "{ \"streets\": \"1600 Pennsylvania Ave.\" }", true,
	    "{ \"streets\": [\"1600 Pennsylvania Ave.\"] }");
  NORMALIZE(s, "{ \"street\": \"1600 Pennsylvania Ave.\" }", true,
	    "{ \"streets\": [\"1600 Pennsylvania Ave.\"] }");
  NO_NORMALIZE(s, "{ \"streets\": [\"1600 Pennsylvania Ave.\"] }");
}

TEST(SchemaNormalizer, SingularObject) {
  Document sd;
  sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"properties\": {"
	"     \"streets\": { \"type\": \"object\","
	"                    \"properties\": {"
	"                       \"key\": {\"type\": \"string\"}},"
	"                    \"allowSingular\": true,"
	"                    \"aliases\": [\"street\"] }},"
	"  \"required\": [\"streets\"]"
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s, "{ \"streets\": \"1600 Pennsylvania Ave.\" }", true,
	    "{ \"streets\": {\"key\": \"1600 Pennsylvania Ave.\"} }");
  NORMALIZE(s, "{ \"street\": \"1600 Pennsylvania Ave.\" }", true,
	    "{ \"streets\": {\"key\": \"1600 Pennsylvania Ave.\"} }");
  NO_NORMALIZE(s, "{ \"streets\": {\"key\": \"1600 Pennsylvania Ave.\"} }");
}

TEST(SchemaNormalizer, SingularNested) {
  Document sd;
  sd.Parse(
        "{"
	"  \"type\": \"array\","
	"  \"allowSingular\": true,"
	"  \"items\": {"
        "    \"type\": \"object\","
	"    \"allowSingular\": true,"
	"    \"properties\": {"
	"       \"streets\": { \"type\": \"string\" }"
	"    }"
	"  }"
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s, "\"1600 Pennsylvania Ave.\"", true,
	    "[ { \"streets\": \"1600 Pennsylvania Ave.\"} ]");
  NO_NORMALIZE(s, "[ { \"streets\": \"1600 Pennsylvania Ave.\"} ]");
  NORMALIZE(s, "[ \"1600 Pennsylvania Ave.\", \"1700 Pennsylvania Ave.\" ]",
	    true,
	    "[ { \"streets\": \"1600 Pennsylvania Ave.\"}, { \"streets\": \"1700 Pennsylvania Ave.\"} ]");
}

TEST(SchemaNormalizer, SingularNestedRef) {
  Document sd;
  sd.Parse(
        "{"
	"  \"definitions\": {"
	"    \"asub\": {"
        "       \"type\": \"object\","
	"       \"allowSingular\": true,"
	"       \"properties\": {"
	"          \"streets\": { \"type\": \"string\" }"
	"       }"
	"    }"
	"  },"
	"  \"type\": \"object\","
	"  \"allOf\": ["
	"    { \"properties\": {"
	"      \"a\": {"
	"        \"type\": \"array\","
	"        \"allowSingular\": true,"
	"        \"items\": { \"$ref\": \"#/definitions/asub\" }"
	"      }"
	"    } },"
	"    { \"properties\": {"
	"      \"b\": {"
	"        \"type\": \"array\","
	"        \"allowSingular\": true,"
	"        \"items\": {"
        "          \"type\": \"object\","
	"          \"allowSingular\": true,"
	"          \"properties\": {"
	"             \"streets\": { \"type\": \"string\" }"
	"          }"
	"        },"
	"        \"aliases\": [\"bb\"]"
	"      }"
	"    } }"
	"  ]"
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s, "{\"a\": \"1600 Pennsylvania Ave.\", \"b\": \"1600 Pennsylvania Ave.\"}", true,
	    "{\"a\": [ { \"streets\": \"1600 Pennsylvania Ave.\"} ], \"b\": [ { \"streets\": \"1600 Pennsylvania Ave.\"} ]}");
  NO_NORMALIZE(s, "{\"a\": [ { \"streets\": \"1600 Pennsylvania Ave.\"} ], \"b\": [ { \"streets\": \"1600 Pennsylvania Ave.\"} ]}");
  NORMALIZE(s, "{\"a\": \"1600 Pennsylvania Ave.\", \"bb\": \"1700 Pennsylvania Ave.\"}", true,
	    "{\"a\": [ { \"streets\": \"1600 Pennsylvania Ave.\"} ], \"b\": [ { \"streets\": \"1700 Pennsylvania Ave.\"} ]}");
}


TEST(SchemaNormalizer, SingularAlias) {
  {
    Document sd;
    sd.Parse("{"
	     "    \"type\": \"object\","
	     "    \"required\": [\"inputs\"],"
	     "    \"properties\": {"
	     "      \"inputs\": {"
	     "        \"aliases\": [\"input\"],"
	     "        \"type\": \"array\","
	     "        \"allowSingular\": true,"
	     "        \"items\": {"
	     "          \"type\": \"object\","
	     "          \"allowSingular\": \"name\","
	     "          \"required\": [\"name\"],"
	     "          \"properties\": {"
	     "            \"name\": {"
	     "              \"type\": \"string\""
	     "            }"
	     "          }"
	     "        }"
	     "      }"
	     "    }"
	     "}");
    SchemaDocument s(sd);
    NORMALIZE(s, "{\"input\": \"hello\"}", true,
	      "{ \"inputs\": [ { \"name\": \"hello\" } ] }");
  }
  {
    Document sd;
    sd.Parse("{"
	     "  \"type\": \"array\","
	     "  \"allowSingular\": true,"
	     "  \"items\": {"
	     "    \"type\": \"object\","
	     "    \"required\": [\"inputs\"],"
	     "    \"properties\": {"
	     "      \"inputs\": {"
	     "        \"aliases\": [\"input\"],"
	     "        \"type\": \"string\""
	     "      }"
	     "    }"
	     "  }"
	     "}");
    SchemaDocument s(sd);
    NORMALIZE(s, "{ \"input\": \"hello\" }", true,
	      "[ { \"inputs\": \"hello\" } ]");
  }
  {
    Document sd;
    sd.Parse("{"
	     "  \"type\": \"array\","
	     "  \"allowSingular\": true,"
	     "  \"items\": {"
	     "    \"type\": \"object\","
	     "    \"required\": [\"inputs\"],"
	     "    \"properties\": {"
	     "      \"inputs\": {"
	     "        \"aliases\": [\"input\"],"
	     "        \"type\": \"array\","
	     "        \"allowSingular\": true,"
	     "        \"items\": {"
	     "          \"type\": \"object\","
	     "          \"allowSingular\": \"name\","
	     "          \"required\": [\"name\"],"
	     "          \"properties\": {"
	     "            \"name\": {"
	     "              \"type\": \"string\""
	     "            },"
	     "            \"value\": {"
	     "              \"type\": \"string\""
	     "            }"
	     "          }"
	     "        }"
	     "      }"
	     "    }"
	     "  }"
	     "}");
    SchemaDocument s(sd);
    NORMALIZE(s, "{\"input\": \"hello\"}", true,
	      "[ { \"inputs\": [ { \"name\": \"hello\" } ] } ]");
  }
}


TEST(SchemaNormalizer, AliasCircular) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street\"]},"
        "        \"street\":         { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street_address\"]},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
		     "/properties/shipping_address", "aliases",
		     "/shipping_address/street",
		     "{ \"aliases\": {"
		     "    \"errorCode\": 39,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"circular\": [\"street\", \"street_address\"]"
		     "}}");
}

TEST(SchemaNormalizer, AliasConflicting) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street\"]},"
        "        \"address\":        { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street\"]},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
		     "/properties/shipping_address", "aliases",
		     "/shipping_address/street",
		     "{ \"aliases\": {"
		     "    \"errorCode\": 40,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"conflicting\": \"street\","
		     "    \"expected\": \"street_address\","
		     "    \"actual\": \"address\""
		     "}}");
}

TEST(SchemaNormalizer, AliasNested) {
    Document sd;
    sd.Parse(
        "{"
        "  \"$schema\": \"http://json-schema.org/draft-04/schema#\","
        ""
        "  \"definitions\": {"
        "    \"address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street\"]},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"}"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\"]"
        "    }"
        "  },"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"allOf\": ["
        "        { \"$ref\": \"#/definitions/address\" },"
        "        { \"properties\":"
        "          { \"type\": { \"enum\": [ \"residential\", \"business\" ],"
	"                        \"default\": \"residential\" } },"
        "          \"required\": [\"type\"]"
        "        }"
        "      ]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"street_address\": \"1700 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
		     "/properties/shipping_address", "allOf",
		     "/shipping_address",
		     "{ \"allOf\": {"
		     "    \"errors\": ["
		     "       { \"aliases\": {"
		     "           \"errorCode\": 38,"
		     "           \"instanceRef\": \"#/shipping_address\","
		     "           \"schemaRef\": \"#/definitions/address\","
		     "           \"duplicates\": [\"street\", \"street_address\"]"
		     "       }},"
		     "       {}],"
		     "    \"errorCode\": 23,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\""
		     "}}");
}

TEST(SchemaNormalizer, AliasNestedCircular) {
    Document sd;
    sd.Parse(
        "{"
        "  \"$schema\": \"http://json-schema.org/draft-04/schema#\","
        ""
        "  \"definitions\": {"
        "    \"address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street\"]},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"}"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\"]"
        "    }"
        "  },"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"allOf\": ["
        "        { \"$ref\": \"#/definitions/address\" },"
        "        { \"properties\":"
        "          { \"type\":   { \"enum\": [ \"residential\", \"business\" ],"
	"                          \"default\": \"residential\" },"
        "            \"street\": { \"type\": \"string\","
	"                          \"default\": \"default_address\","
	"                          \"aliases\": [\"street_address\"] }},"
        "          \"required\": [\"type\"]"
        "        }"
        "      ]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
		     "/properties/shipping_address", "aliases",
		     "/shipping_address",
		     "{ \"aliases\": {"
		     "    \"errorCode\": 39,"
		     "    \"instanceRef\": \"#\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"circular\": [\"street\", \"street_address\"]"
		     "}}");
}

TEST(SchemaNormalizer, AliasNestedConflicting) {
    Document sd;
    sd.Parse(
        "{"
        "  \"$schema\": \"http://json-schema.org/draft-04/schema#\","
        ""
        "  \"definitions\": {"
        "    \"address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\","
	"                              \"aliases\": [\"street\"]},"
        "        \"city\":           { \"type\": \"string\","
	"                              \"default\": \"default_city\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"}"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\"]"
        "    }"
        "  },"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": { \"$ref\": \"#/definitions/address\" },"
        "    \"shipping_address\": {"
        "      \"allOf\": ["
        "        { \"$ref\": \"#/definitions/address\" },"
        "        { \"properties\":"
        "          { \"type\":    { \"enum\": [ \"residential\", \"business\" ],"
	"                           \"default\": \"residential\" },"
        "            \"address\": { \"type\": \"string\","
	"                           \"default\": \"default_address\","
	"                           \"aliases\": [\"street\"] }},"
        "          \"required\": [\"type\"]"
        "        }"
        "      ]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"} }",
		     "/properties/shipping_address", "aliases",
		     "/shipping_address",
		     "{ \"aliases\": {"
		     "    \"errorCode\": 40,"
		     "    \"instanceRef\": \"#\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "  \"conflicting\": \"street\","
		     "  \"expected\": \"address\","
		     "  \"actual\": \"street_address\""
		     "}}");
}

TEST(SchemaNormalizer, Encoding) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"scalar\","
	"  \"subtype\": \"string\","
	"  \"encoding\": \"UCS4\""
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"hello\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InN0cmluZyIsInByZWNpc2lvbiI6MjAsImVuY29kaW5nIjoiVUNTNCJ9-YGG-aAAAAGUAAABsAAAAbAAAAG8AAAA=-YGG-\"");
}
TEST(SchemaNormalizer, EncodingBackwards) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"scalar\","
	"  \"subtype\": \"string\","
	"  \"encoding\": \"UTF8\""
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InN0cmluZyIsInByZWNpc2lvbiI6MjAsImVuY29kaW5nIjoiVUNTNCJ9-YGG-aAAAAGUAAABsAAAAbAAAAG8AAAA=-YGG-\"",
	      true,
	      "\"hello\"");
}
TEST(SchemaNormalizer, EncodingArray) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"ndarray\","
	"  \"subtype\": \"string\","
	"  \"encoding\": \"UCS4\""
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJzdHJpbmciLCJwcmVjaXNpb24iOjYsInNoYXBlIjpbM119-YGG-cmVkAPj4Z3JlZW4AYmx1ZQAA-YGG-\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJzdHJpbmciLCJwcmVjaXNpb24iOjIxLCJzaGFwZSI6WzNdLCJlbmNvZGluZyI6IlVDUzQifQ==-YGG-cgAAAGUAAABkAAAAAAAAAGcAAAByAAAAZQAAAGUAAABuAAAAAAAAAGIAAABsAAAAdQAAAGUAAAAAAAAAAAAAAA==-YGG-\"");
}
TEST(SchemaNormalizer, EncodingArrayFailure) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"ndarray\","
	"  \"subtype\": \"string\","
	"  \"encoding\": \"UTF8\""
	"}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s,
		     "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJzdHJpbmciLCJwcmVjaXNpb24iOjIxLCJzaGFwZSI6WzNdLCJlbmNvZGluZyI6IlVDUzQifQ==-YGG-cgAAAGUAAABkAAAAAAAAAGcAAAByAAAAZQAAAGUAAABuAAAAAAAAAGIAAABsAAAAdQAAAGUAAAAAAAAAAAAAAA==-YGG-\"",
		     "", "encoding", "",
		     "{ \"encoding\": {"
		     "    \"errorCode\": 31,"
		     "    \"instanceRef\": \"#\", \"schemaRef\": \"#\","
		     "    \"expected\": \"UTF8\","
		     "    \"actual\": \"UCS4\""
		     "}}");
		     
}

TEST(SchemaNormalizer, Units) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"scalar\","
	"  \"subtype\": \"float\","
	"  \"precision\": 8,"
	"  \"units\": \"g\""
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImtnIn0=-YGG-AAAAAAAA8D8=-YGG-\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImcifQ==-YGG-AAAAAABAj0A=-YGG-\"");
    NORMALIZE(s,
	      "\"10.0 g\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImcifQ==-YGG-AAAAAAAAJEA=-YGG-\"");
    NORMALIZE(s,
	      "\"5.27e-30 g\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImcifQ==-YGG-GRhr4tm42jk=-YGG-\"");
}

TEST(SchemaNormalizer, ScalarFloat) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"scalar\","
	"  \"subtype\": \"float\","
	"  \"precision\": 8,"
	"  \"units\": \"g\""
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InVpbnQiLCJwcmVjaXNpb24iOjEsInVuaXRzIjoia2cifQ==-YGG-AQ==-YGG-\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImcifQ==-YGG-AAAAAABAj0A=-YGG-\"");
}

TEST(SchemaNormalizer, ScalarNumber) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"number\""
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6InVpbnQiLCJwcmVjaXNpb24iOjEsInVuaXRzIjoia2cifQ==-YGG-AQ==-YGG-\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImZsb2F0IiwicHJlY2lzaW9uIjo4LCJ1bml0cyI6ImtnIn0=-YGG-AAAAAAAA8D8=-YGG-\"");
    // "\"3\"");
}

TEST(SchemaNormalizer, ScalarInt) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"scalar\","
	"  \"subtype\": \"int\","
	"  \"precision\": 8,"
	"  \"units\": \"g\""
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "1",
	      true,
	      "\"-YGG-eyJ0eXBlIjoic2NhbGFyIiwic3VidHlwZSI6ImludCIsInByZWNpc2lvbiI6OH0=-YGG-AQAAAAAAAAA=-YGG-\"");
}

TEST(SchemaNormalizer, OneDArray) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"1darray\","
	"  \"subtype\": \"float\","
	"  \"precision\": 4,"
	"  \"units\": \"g\","
	"  \"length\": 4"
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJpbnQiLCJwcmVjaXNpb24iOjEsInVuaXRzIjoia2ciLCJzaGFwZSI6WzRdfQ==-YGG-AAECAw==-YGG-\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6NCwidW5pdHMiOiJnIiwic2hhcGUiOls0XX0=-YGG-AAAAAAAAekQAAPpEAIA7RQ==-YGG-\"");
    FAILED_NORMALIZE(s,
		     "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6OCwidW5pdHMiOiJnIiwic2hhcGUiOls0XX0=-YGG-AAAAAAAAAAAAAAAAAAAAAP///////+9/AAAAAAAAAAA=-YGG-\"",
		     "", "precision", "",
		     "{ \"precision\": {"
		     "    \"errorCode\": 28,"
		     "    \"instanceRef\": \"#\","
		     "    \"schemaRef\": \"#\","
		     "    \"expected\": 4, \"actual\": 8"
		     "}}");
}

TEST(SchemaNormalizer, NDArray) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"ndarray\","
	"  \"subtype\": \"float\","
	"  \"precision\": 8,"
	"  \"units\": \"g\","
	"  \"shape\": [2, 3]"
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6NCwidW5pdHMiOiJrZyIsInNoYXBlIjpbMiwzXX0=-YGG-AAAAAAAAgD8AAABAAABAQAAAgEAAAKBA-YGG-\"",
	      true,
	      "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJmbG9hdCIsInByZWNpc2lvbiI6OCwidW5pdHMiOiJnIiwic2hhcGUiOlsyLDNdfQ==-YGG-AAAAAAAAAAAAAAAAAECPQAAAAAAAQJ9AAAAAAABwp0AAAAAAAECvQAAAAAAAiLNA-YGG-\"");
    FAILED_NORMALIZE(s,
		     "\"-YGG-eyJ0eXBlIjoibmRhcnJheSIsInN1YnR5cGUiOiJjb21wbGV4IiwicHJlY2lzaW9uIjoxNiwidW5pdHMiOiJnIiwic2hhcGUiOlsyLDNdfQ==-YGG-AAAAAAAA4D8AAAAAAAD4PwAAAAAAAAAAAAAAAAAA4D8AAAAAAADwPwAAAAAAAPA/AAAAAAAA4D8AAAAAAAD4PwAAAAAAAAAAAAAAAAAA4D8AAAAAAADwPwAAAAAAAPA/-YGG-\"",
		     "", "subtype", "",
		     "{ \"subtype\": {"
		     "    \"errorCode\": 27,"
		     "    \"instanceRef\": \"#\","
		     "    \"schemaRef\": \"#\","
		     "    \"expected\": [\"float\"], \"actual\": \"complex\""
		     "}}");
}

TEST(SchemaNormalizer, ObjWavefront2Ply) {
  Document sd;
  sd.Parse(
        "{"
        "  \"type\": \"ply\""
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s,
	    "\"-YGG-eyJ0eXBlIjoib2JqIn0=-YGG-diAwLjAgMC4wIDAuMAp2IDAuMCAwLjAgMS4wCnYgMC4wIDEuMCAxLjAKdiAwLjAgMS4wIDAuMAp2IDEuMCAwLjAgMC4wCnYgMS4wIDAuMCAxLjAKdiAxLjAgMS4wIDEuMAp2IDEuMCAxLjAgMC4wCmYgNCAxIDIKZiA0IDEgMwpsIDEgMgpsIDIgMwpsIDMgNApsIDQgMQpsIDMgMQo=-YGG-\"",
	    true,
	    "\"-YGG-eyJ0eXBlIjoicGx5In0=-YGG-cGx5CmZvcm1hdCBhc2NpaSAxLjAKZWxlbWVudCB2ZXJ0ZXggOApwcm9wZXJ0eSBkb3VibGUgeApwcm9wZXJ0eSBkb3VibGUgeQpwcm9wZXJ0eSBkb3VibGUgegplbGVtZW50IGZhY2UgMgpwcm9wZXJ0eSBsaXN0IHVjaGFyIGludCB2ZXJ0ZXhfaW5kZXgKZWxlbWVudCBlZGdlIDUKcHJvcGVydHkgaW50IHZlcnRleDEKcHJvcGVydHkgaW50IHZlcnRleDIKZW5kX2hlYWRlcgowIDAgMAowIDAgMQowIDEgMQowIDEgMAoxIDAgMAoxIDAgMQoxIDEgMQoxIDEgMAozIDMgMCAxCjMgMyAwIDIKMCAxCjEgMgoyIDMKMyAwCjIgMAo=-YGG-\"");
}

TEST(SchemaNormalizer, Ply2ObjWavefront) {
  Document sd;
  sd.Parse(
        "{"
        "  \"type\": \"obj\""
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s,
	    "\"-YGG-eyJ0eXBlIjoicGx5In0=-YGG-cGx5CmZvcm1hdCBhc2NpaSAxLjAKZWxlbWVudCB2ZXJ0ZXggOApwcm9wZXJ0eSBkb3VibGUgeApwcm9wZXJ0eSBkb3VibGUgeQpwcm9wZXJ0eSBkb3VibGUgegplbGVtZW50IGZhY2UgMgpwcm9wZXJ0eSBsaXN0IHVjaGFyIGludCB2ZXJ0ZXhfaW5kZXgKZWxlbWVudCBlZGdlIDUKcHJvcGVydHkgaW50IHZlcnRleDEKcHJvcGVydHkgaW50IHZlcnRleDIKZW5kX2hlYWRlcgowIDAgMAowIDAgMQowIDEgMQowIDEgMAoxIDAgMAoxIDAgMQoxIDEgMQoxIDEgMAozIDMgMCAxCjMgMyAwIDIKMCAxCjEgMgoyIDMKMyAwCjIgMAo=-YGG-\"",
	    true,
	    "\"-YGG-eyJ0eXBlIjoib2JqIn0=-YGG-diAwLjAgMC4wIDAuMAp2IDAuMCAwLjAgMS4wCnYgMC4wIDEuMCAxLjAKdiAwLjAgMS4wIDAuMAp2IDEuMCAwLjAgMC4wCnYgMS4wIDAuMCAxLjAKdiAxLjAgMS4wIDEuMAp2IDEuMCAxLjAgMC4wCmYgNCAxIDIKZiA0IDEgMwpsIDEgMgpsIDIgMwpsIDMgNApsIDQgMQpsIDMgMQo=-YGG-\"");
}

TEST(SchemaNormalizer, Schema) {
  Document sd;
  sd.Parse(
        "{"
        "  \"type\": \"schema\""
        "}");
  SchemaDocument s(sd);
  NORMALIZE(s,
	    "{\"type\": \"bytes\"}",
	    true,
	    "{\"type\": \"scalar\", \"subtype\": \"string\"}");
  NORMALIZE(s,
	    "{\"type\": \"unicode\"}",
	    true,
	    "{\"type\": \"scalar\", \"subtype\": \"string\", \"encoding\": \"UCS4\"}");
  NORMALIZE(s,
	    "{\"type\": \"float\"}",
	    true,
	    "{\"type\": \"scalar\", \"subtype\": \"float\", \"precision\": 8}");
}

TEST(SchemaNormalizer, SharedProperties) {
  { // Pull a, pull b
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
	"    \"a\": {"
	"      \"type\": \"object\","
	"      \"properties\": {"
	"        \"asub\": {\"type\": \"integer\"}"
	"      },"
	"      \"required\": [\"asub\"],"
	"      \"pullProperties\": {\"../b\": true}"
	"    },"
	"    \"b\": {"
	"      \"type\": \"object\","
	"      \"properties\": {"
	"        \"bsub\": {\"type\": \"integer\"}"
	"      },"
	"      \"required\": [\"bsub\"],"
	"      \"pullProperties\": {\"../a\": true}"
	"    }"
	"  },"
	"  \"required\": [\"a\", \"b\"],"
	"  \"pullProperties\": {"
	"    \"a\": true,"
	"    \"b\": true"
	"  }"
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s, "{\"a\": {\"asub\": 1, \"b\": {\"bsub\": 2}}}", true,
	      "{\"a\": {\"asub\": 1}, \"b\": {\"bsub\": 2}}");
    NORMALIZE(s, "{\"b\": {\"bsub\": 2, \"a\": {\"asub\": 1}}}", true,
	      "{\"a\": {\"asub\": 1}, \"b\": {\"bsub\": 2}}");
    NORMALIZE(s, "{\"a\": {\"asub\": 1, \"bsub\": 2, \"b\": {}}}", true,
	      "{\"a\": {\"asub\": 1}, \"b\": {\"bsub\": 2}}");
    NORMALIZE(s, "{\"b\": {\"asub\": 1, \"bsub\": 2, \"a\": {}}}", true,
	      "{\"a\": {\"asub\": 1}, \"b\": {\"bsub\": 2}}");
  }
  { // Push a, push b
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
	"    \"a\": {"
	"      \"type\": \"object\","
	"      \"properties\": {"
	"        \"asub\": {\"type\": \"integer\"}"
	"      },"
	"      \"required\": [\"asub\"],"
	"      \"pushProperties\": {"
	"        \"../b\": true,"
	"        \"..\": true"
	"      }"
	"    },"
	"    \"b\": {"
	"      \"type\": \"object\","
	"      \"properties\": {"
	"        \"bsub\": {\"type\": \"integer\"}"
	"      },"
	"      \"required\": [\"bsub\"],"
	"      \"pushProperties\": {"
	"        \"../a\": true,"
	"        \"..\": true"
	"      }"
	"    }"
	"  },"
	"  \"required\": [\"a\", \"b\"]"
	"}");
    SchemaDocument s(sd);
    NORMALIZE(s, "{\"a\": {\"asub\": 1, \"bsub\": 2, \"b\": {}}}", true,
	      "{\"a\": {\"asub\": 1}, \"b\": {\"bsub\": 2}}");
    NORMALIZE(s, "{\"b\": {\"asub\": 1, \"bsub\": 2, \"a\": {}}}", true,
	      "{\"a\": {\"asub\": 1}, \"b\": {\"bsub\": 2}}");
  }
}

TEST(SchemaNormalizer, PullProperties) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
	"      \"pullProperties\": true,"
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" },"
	"        \"unit\":           { \"type\": \"string\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    },"
	"    \"zip\": {"
	"      \"type\": \"string\""
	"    }"
        "  },"
	"  \"required\": [\"zip\"],"
	"  \"pullProperties\": {"
	"    \"$properties/shipping_address\": [\"zip\"]"
	"  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"zip\": \"12345\"}, \"city\": \"Washington\", \"state\": \"DC\" }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"}, \"zip\": \"12345\" }");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"zip\": \"12345\"}, \"state\": \"DC\" }",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"zip\": \"12345\"}, \"city\": \"Washington\", \"state\": \"DC\", \"type\": 1 }",
		     "", "enum", "",
		     "{ \"enum\": {"
		     "    \"expected\": [\"residential\", \"business\"],"
		     "    \"errorCode\": 19,"
		     "    \"instanceRef\": \"#/shipping_address/type\","
		     "    \"schemaRef\": \"#/properties/shipping_address/properties/type\""
		     "}}");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\"}, \"city\": \"Washington\", \"state\": \"DC\" }",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#\","
		     "    \"schemaRef\": \"#\","
		     "    \"missing\": [\"zip\"]"
		     "}}");
}

TEST(SchemaNormalizer, PushProperties) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" },"
	"        \"unit\":           { \"type\": \"string\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"],"
	"      \"pushProperties\": {"
	"        \"$../../\": [\"zip\"]"
	"      }"
        "    },"
        "    \"state\": {"
	"      \"type\": \"string\","
	"      \"default\": \"default_state\""
	"    },"
	"    \"zip\": {"
	"      \"type\": \"string\""
	"    }"
        "  },"
	"  \"required\": [\"zip\"],"
	"  \"pushProperties\": {"
	"    \"shipping_address\": [\"city\", \"state\"]"
	"  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"zip\": \"12345\"}, \"city\": \"Washington\", \"state\": \"DC\" }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"DC\", \"type\": \"residential\"},  \"state\": \"DC\", \"zip\": \"12345\" }");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"zip\": \"12345\"}, \"state\": \"DC\" }",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\"}, \"city\": \"Washington\", \"state\": \"DC\" }",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#\","
		     "    \"schemaRef\": \"#\","
		     "    \"missing\": [\"zip\"]"
		     "}}");
}

TEST(SchemaNormalizer, PullPropertiesInvalidDefault) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
	"      \"pullProperties\": true,"
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": 1 },"
	"        \"unit\":           { \"type\": \"string\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\", \"zip\"]"
        "    },"
	"    \"zip\": {"
	"      \"type\": \"string\""
	"    }"
        "  },"
	"  \"pullProperties\": {"
	"    \"$properties/shipping_address\": [\"zip\"]"
	"  }"
        "}");
    SchemaDocument s(sd);
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"zip\": \"12345\"}, \"city\": \"Washington\", \"state\": \"DC\" }",
		     "", "enum", "",
		     "{ \"enum\": {"
		     "    \"expected\": [ \"residential\", \"business\" ],"
		     "    \"errorCode\": 19,"
		     "    \"instanceRef\": \"#/shipping_address/type\","
		     "    \"schemaRef\": \"#/properties/shipping_address/properties/type\""
		     "}}");
}

TEST(SchemaNormalizer, PullPropertiesExclude) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
	"      \"pullProperties\": {\"!..\": [\"state\"]},"
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\"}, \"city\": \"Washington\", \"state\": \"DC\" }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"default_state\", \"type\": \"residential\"}, \"state\": \"DC\" }");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\"}, \"state\": \"DC\" }",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
}

TEST(SchemaNormalizer, PushPropertiesExclude) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\"},"
        "        \"state\":          { \"type\": \"string\","
	"                              \"default\": \"default_state\"},"
        "        \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                              \"default\": \"residential\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\", \"state\", \"type\"]"
        "    },"
        "    \"state\": {"
	"      \"type\": \"string\","
	"      \"default\": \"default_state\""
	"    }"
        "  },"
	"  \"pushProperties\": {"
	"    \"!shipping_address\": [\"state\"]"
	"  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\"}, \"city\": \"Washington\", \"state\": \"DC\" }",
	      true,
	      "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\", \"city\": \"Washington\", \"state\": \"default_state\", \"type\": \"residential\"}, \"state\": \"DC\" }");
    FAILED_NORMALIZE(s,
		     "{\"shipping_address\": {\"street_address\": \"1600 Pennsylvania Avenue NW\"}, \"state\": \"DC\" }",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/shipping_address\","
		     "    \"schemaRef\": \"#/properties/shipping_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
}

TEST(SchemaNormalizer, PullPropertiesPath) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": {"
        "      \"type\": \"object\","
	"      \"pullProperties\": true,"
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\" }"
        "      },"
	"      \"additionalProperties\": false,"
        "      \"required\": [\"street_address\", \"city\"]"
        "    },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
	"      \"allOf\": [{"
	"        \"pullProperties\": {"
	"          \"../billing_address\": true,"
	"          \"..\": [\"street_address\"]"
	"        },"
        "        \"properties\": {"
        "          \"street_address\": { \"type\": \"string\","
	"                                \"default\": \"default_address\"},"
        "          \"city\":           { \"type\": \"string\" }"
        "        },"
        "        \"required\": [\"street_address\", \"city\"]"
	"      }, {"
	"        \"pullProperties\": {"
	"          \"../billing_address\": true"
	"        },"
        "        \"properties\": {"
        "          \"state\":          { \"type\": \"string\","
	"                                \"default\": \"default_state\"},"
        "          \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                                \"default\": \"residential\" }"
        "        },"
        "        \"required\": [\"state\", \"type\"]"
	"      }]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{"
	      "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "  \"city\": \"Washington\","
	      "  \"shipping_address\": {"
	      "  },"
	      "  \"billing_address\": {"
	      "    \"state\": \"DC\","
	      "    \"type\": \"residential\""
	      "  }"
	      "}",
	      true,
	      "{"
	      "  \"shipping_address\": {"
	      "    \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "    \"city\": \"Washington\","
	      "    \"state\": \"DC\","
	      "    \"type\": \"residential\""
	      "  },"
	      "  \"billing_address\": {"
	      "    \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "    \"city\": \"Washington\""
	      "  }"
	      "}");
    FAILED_NORMALIZE(s,
		     "{"
		     "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
		     "  \"shipping_address\": {"
		     "  },"
		     "  \"billing_address\": {"
		     "    \"state\": \"DC\","
		     "    \"type\": \"residential\""
		     "  }"
		     "}",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/billing_address\","
		     "    \"schemaRef\": \"#/properties/billing_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
}

TEST(SchemaNormalizer, PushPropertiesWildcard) {
  Document sd;
  sd.Parse("{"
	   "  \"type\": \"object\","
	   "  \"pushProperties\": {"
	   "    \"$properties/x/anyOf/*/properties/y\": true"
	   "  },"
	   "  \"additionalProperties\": false,"
	   "  \"properties\": {"
	   "    \"x\": {"
	   "      \"type\": \"object\","
	   "      \"anyOf\": ["
	   "        {"
	   "          \"type\": \"object\","
	   "          \"additionalProperties\": false,"
	   "          \"required\": [\"y\"],"
	   "          \"properties\": {"
	   "            \"y\": {"
	   "              \"type\": \"object\","
	   "              \"required\": [\"a\", \"c\"],"
	   "              \"default\": {},"
	   "              \"properties\": {"
	   "                \"a\": {\"type\": \"integer\"},"
	   "                \"c\": {\"type\": \"integer\"}"
	   "              }"
	   "            }"
	   "          }"
	   "        },"
	   "        {"
	   "          \"type\": \"object\","
	   "          \"additionalProperties\": false,"
	   "          \"required\": [\"y\"],"
	   "          \"properties\": {"
	   "            \"y\": {"
	   "              \"type\": \"object\","
	   "              \"required\": [\"a\", \"b\"],"
	   "              \"default\": {},"
	   "              \"properties\": {"
	   "                \"a\": {\"type\": \"integer\"},"
	   "                \"b\": {\"type\": \"integer\"}"
	   "              }"
	   "            }"
	   "          }"
	   "        }"
	   "      ]"
	   "    }"
	   "  }"
	   "}");
  EXPECT_FALSE(sd.HasParseError());
  SchemaDocument s(sd);
  NORMALIZE(s, "{\"a\": 1, \"c\": 2, \"x\": {}}",
	    true, "{\"x\": {\"y\": {\"a\": 1, \"c\": 2}}}");
  // Fix this so that pushed properties can be used to rull out anyOf
  // branch before properties are visited or unvisited anyOf branches are
  // cached when the target of pushed properties
  // NORMALIZE(s, "{\"a\": 1, \"b\": 2, \"x\": {}}",
  // 	    true, "{\"x\": {\"y\": {\"a\": 1, \"b\": 2}}}");
}

TEST(SchemaNormalizer, PushPropertiesPath) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"pushProperties\": {"
	"    \"billing_address\": true,"
	"    \"shipping_address\": [\"street_address\"]"
	"  },"
        "  \"properties\": {"
        "    \"street_address\": {"
	"      \"type\": \"string\","
	"      \"default\": \"default_address\""
	"    },"
        "    \"billing_address\": {"
        "      \"type\": \"object\","
	"      \"pushProperties\": {"
	"        \"../shipping_address\": true"
	"      },"
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\"]"
        "    },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
	"      \"allOf\": [{"
        "        \"properties\": {"
        "          \"street_address\": { \"type\": \"string\","
	"                                \"default\": \"default_address\"},"
        "          \"city\":           { \"type\": \"string\" }"
        "        },"
        "        \"required\": [\"street_address\", \"city\"]"
	"      }, {"
        "        \"properties\": {"
        "          \"state\":          { \"type\": \"string\","
	"                                \"default\": \"default_state\"},"
        "          \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                                \"default\": \"residential\" }"
        "        },"
        "        \"required\": [\"state\", \"type\"]"
	"      }]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{"
	      "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "  \"shipping_address\": {"
	      "  },"
	      "  \"billing_address\": {"
	      "    \"city\": \"Washington\","
	      "    \"state\": \"DC\","
	      "    \"type\": \"residential\""
	      "  }"
	      "}",
	      true,
	      "{"
	      "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "  \"shipping_address\": {"
	      "    \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "    \"city\": \"Washington\","
	      "    \"state\": \"DC\","
	      "    \"type\": \"residential\""
	      "  },"
	      "  \"billing_address\": {"
	      "    \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "    \"city\": \"Washington\""
	      "  }"
	      "}");
    FAILED_NORMALIZE(s,
		     "{"
		     "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
		     "  \"shipping_address\": {"
		     "  },"
		     "  \"billing_address\": {"
		     "    \"state\": \"DC\","
		     "    \"type\": \"residential\""
		     "  }"
		     "}",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/billing_address\","
		     "    \"schemaRef\": \"#/properties/billing_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
}

TEST(SchemaNormalizer, PullPropertiesPathExclude) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
        "  \"properties\": {"
        "    \"billing_address\": {"
        "      \"type\": \"object\","
	"      \"pullProperties\": true,"
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\"]"
        "    },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
	"      \"allOf\": [{"
	"        \"pullProperties\": {"
	"          \"!../billing_address\": [\"street_address\"],"
	"          \"..\": [\"street_address\"]"
	"        },"
        "        \"properties\": {"
        "          \"street_address\": { \"type\": \"string\","
	"                                \"default\": \"default_address\"},"
        "          \"city\":           { \"type\": \"string\" }"
        "        },"
        "        \"required\": [\"street_address\", \"city\"]"
	"      }, {"
	"        \"pullProperties\": {"
	"          \"!../billing_address\": [\"state\"]"
	"        },"
        "        \"properties\": {"
        "          \"state\":          { \"type\": \"string\","
	"                                \"default\": \"default_state\"},"
        "          \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                                \"default\": \"residential\" }"
        "        },"
        "        \"required\": [\"state\", \"type\"]"
	"      }]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{"
	      "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "  \"city\": \"Washington\","
	      "  \"shipping_address\": {"
	      "  },"
	      "  \"billing_address\": {"
	      "    \"state\": \"DC\","
	      "    \"type\": \"residential\""
	      "  }"
	      "}",
	      true,
	      "{"
	      "  \"shipping_address\": {"
	      "    \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "    \"city\": \"Washington\","
	      "    \"state\": \"default_state\","
	      "    \"type\": \"residential\""
	      "  },"
	      "  \"billing_address\": {"
	      "    \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "    \"state\": \"DC\","
	      "    \"city\": \"Washington\""
	      "  }"
	      "}");
    FAILED_NORMALIZE(s,
		     "{"
		     "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
		     "  \"shipping_address\": {"
		     "  },"
		     "  \"billing_address\": {"
		     "    \"state\": \"DC\","
		     "    \"type\": \"residential\""
		     "  }"
		     "}",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/billing_address\","
		     "    \"schemaRef\": \"#/properties/billing_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
}

TEST(SchemaNormalizer, PushPropertiesPathExclude) {
    Document sd;
    sd.Parse(
        "{"
        "  \"type\": \"object\","
	"  \"pushProperties\": {"
	"    \"!billing_address\": [\"street_address\"],"
	"    \"shipping_address\": [\"street_address\"]"
	"  },"
        "  \"properties\": {"
        "    \"street_address\": {"
	"      \"type\": \"string\","
	"      \"default\": \"default_address\""
	"    },"
        "    \"billing_address\": {"
        "      \"type\": \"object\","
	"      \"pushProperties\": {"
	"        \"!../shipping_address\": [\"state\"]"
	"      },"
        "      \"properties\": {"
        "        \"street_address\": { \"type\": \"string\","
	"                              \"default\": \"default_address\"},"
        "        \"city\":           { \"type\": \"string\" }"
        "      },"
        "      \"required\": [\"street_address\", \"city\"]"
        "    },"
        "    \"shipping_address\": {"
        "      \"type\": \"object\","
	"      \"allOf\": [{"
        "        \"properties\": {"
        "          \"street_address\": { \"type\": \"string\","
	"                                \"default\": \"default_address\"},"
        "          \"city\":           { \"type\": \"string\" }"
        "        },"
        "        \"required\": [\"street_address\", \"city\"]"
	"      }, {"
        "        \"properties\": {"
        "          \"state\":          { \"type\": \"string\","
	"                                \"default\": \"default_state\"},"
        "          \"type\":           { \"enum\": [ \"residential\", \"business\" ],"
	"                                \"default\": \"residential\" }"
        "        },"
        "        \"required\": [\"state\", \"type\"]"
	"      }]"
        "    }"
        "  }"
        "}");
    SchemaDocument s(sd);
    NORMALIZE(s,
	      "{"
	      "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "  \"shipping_address\": {"
	      "  },"
	      "  \"billing_address\": {"
	      "    \"city\": \"Washington\","
	      "    \"state\": \"DC\","
	      "    \"type\": \"residential\""
	      "  }"
	      "}",
	      true,
	      "{"
	      "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "  \"shipping_address\": {"
	      "    \"street_address\": \"1600 Pennsylvania Avenue NW\","
	      "    \"city\": \"Washington\","
	      "    \"state\": \"default_state\","
	      "    \"type\": \"residential\""
	      "  },"
	      "  \"billing_address\": {"
	      "    \"street_address\": \"default_address\","
	      "    \"state\": \"DC\","
	      "    \"city\": \"Washington\""
	      "  }"
	      "}");
    FAILED_NORMALIZE(s,
		     "{"
		     "  \"street_address\": \"1600 Pennsylvania Avenue NW\","
		     "  \"shipping_address\": {"
		     "  },"
		     "  \"billing_address\": {"
		     "    \"state\": \"DC\","
		     "    \"type\": \"residential\""
		     "  }"
		     "}",
		     "", "required", "",
		     "{ \"required\": {"
		     "    \"errorCode\": 15,"
		     "    \"instanceRef\": \"#/billing_address\","
		     "    \"schemaRef\": \"#/properties/billing_address\","
		     "    \"missing\": [\"city\"]"
		     "}}");
}

#ifndef YGGDRASIL_DISABLE_PYTHON_C_API
#ifdef METASCHEMA_YGG_TESTS
TEST(SchemaNormalizer, YggSchema) {
    Document sd;
    sd.Parse(get_yggschema<char>());
    if (sd.HasParseError()) {
      Reader reader;
      BaseReaderHandler<> handler;
      StringStream json(get_yggschema<char>());
      reader.Parse(json, handler);
      std::cerr << get_yggschema<char>() + reader.GetErrorOffset() << std::endl;
    }
    EXPECT_FALSE(sd.HasParseError());
    SchemaDocument s(sd);
    NORMALIZE(s, get_testschema<char>(), true, get_testschema_result<char>());
}
#endif // METASCHEMA_YGG_TESTS
#endif // YGGDRASIL_DISABLE_PYTHON_C_API
#if defined(_MSC_VER) || defined(__clang__)
YGGDRASIL_RAPIDJSON_DIAG_POP
#endif

#endif // DISABLE_YGGDRASIL_RAPIDJSON
