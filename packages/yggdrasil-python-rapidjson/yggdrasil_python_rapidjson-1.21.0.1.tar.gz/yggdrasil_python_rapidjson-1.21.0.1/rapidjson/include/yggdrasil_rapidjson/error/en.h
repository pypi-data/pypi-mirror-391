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

#ifndef YGGDRASIL_RAPIDJSON_ERROR_EN_H_
#define YGGDRASIL_RAPIDJSON_ERROR_EN_H_

#include "error.h"

#ifdef __clang__
YGGDRASIL_RAPIDJSON_DIAG_PUSH
YGGDRASIL_RAPIDJSON_DIAG_OFF(switch-enum)
YGGDRASIL_RAPIDJSON_DIAG_OFF(covered-switch-default)
#endif

YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

//! Maps error code of parsing into error message.
/*!
    \ingroup YGGDRASIL_RAPIDJSON_ERRORS
    \param parseErrorCode Error code obtained in parsing.
    \return the error message.
    \note User can make a copy of this function for localization.
        Using switch-case is safer for future modification of error codes.
*/
inline const YGGDRASIL_RAPIDJSON_ERROR_CHARTYPE* GetParseError_En(ParseErrorCode parseErrorCode) {
    switch (parseErrorCode) {
        case kParseErrorNone:                           return YGGDRASIL_RAPIDJSON_ERROR_STRING("No error.");

        case kParseErrorDocumentEmpty:                  return YGGDRASIL_RAPIDJSON_ERROR_STRING("The document is empty.");
        case kParseErrorDocumentRootNotSingular:        return YGGDRASIL_RAPIDJSON_ERROR_STRING("The document root must not be followed by other values.");

        case kParseErrorValueInvalid:                   return YGGDRASIL_RAPIDJSON_ERROR_STRING("Invalid value.");

        case kParseErrorObjectMissName:                 return YGGDRASIL_RAPIDJSON_ERROR_STRING("Missing a name for object member.");
        case kParseErrorObjectMissColon:                return YGGDRASIL_RAPIDJSON_ERROR_STRING("Missing a colon after a name of object member.");
        case kParseErrorObjectMissCommaOrCurlyBracket:  return YGGDRASIL_RAPIDJSON_ERROR_STRING("Missing a comma or '}' after an object member.");

        case kParseErrorArrayMissCommaOrSquareBracket:  return YGGDRASIL_RAPIDJSON_ERROR_STRING("Missing a comma or ']' after an array element.");

        case kParseErrorStringUnicodeEscapeInvalidHex:  return YGGDRASIL_RAPIDJSON_ERROR_STRING("Incorrect hex digit after \\u escape in string.");
        case kParseErrorStringUnicodeSurrogateInvalid:  return YGGDRASIL_RAPIDJSON_ERROR_STRING("The surrogate pair in string is invalid.");
        case kParseErrorStringEscapeInvalid:            return YGGDRASIL_RAPIDJSON_ERROR_STRING("Invalid escape character in string.");
        case kParseErrorStringMissQuotationMark:        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Missing a closing quotation mark in string.");
        case kParseErrorStringInvalidEncoding:          return YGGDRASIL_RAPIDJSON_ERROR_STRING("Invalid encoding in string.");

        case kParseErrorNumberTooBig:                   return YGGDRASIL_RAPIDJSON_ERROR_STRING("Number too big to be stored in double.");
        case kParseErrorNumberMissFraction:             return YGGDRASIL_RAPIDJSON_ERROR_STRING("Miss fraction part in number.");
        case kParseErrorNumberMissExponent:             return YGGDRASIL_RAPIDJSON_ERROR_STRING("Miss exponent in number.");

        case kParseErrorTermination:                    return YGGDRASIL_RAPIDJSON_ERROR_STRING("Terminate parsing due to Handler error.");
        case kParseErrorUnspecificSyntaxError:          return YGGDRASIL_RAPIDJSON_ERROR_STRING("Unspecific syntax error.");

        default:                                        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Unknown error.");
    }
}

//! Maps error code of validation into error message.
/*!
    \ingroup YGGDRASIL_RAPIDJSON_ERRORS
    \param validateErrorCode Error code obtained from validator.
    \return the error message.
    \note User can make a copy of this function for localization.
        Using switch-case is safer for future modification of error codes.
*/
inline const YGGDRASIL_RAPIDJSON_ERROR_CHARTYPE* GetValidateError_En(ValidateErrorCode validateErrorCode) {
    switch (validateErrorCode) {
        case kValidateErrors:                           return YGGDRASIL_RAPIDJSON_ERROR_STRING("One or more validation errors have occurred");
        case kValidateErrorNone:                        return YGGDRASIL_RAPIDJSON_ERROR_STRING("No error.");

        case kValidateErrorMultipleOf:                  return YGGDRASIL_RAPIDJSON_ERROR_STRING("Number '%actual' is not a multiple of the 'multipleOf' value '%expected'.");
        case kValidateErrorMaximum:                     return YGGDRASIL_RAPIDJSON_ERROR_STRING("Number '%actual' is greater than the 'maximum' value '%expected'.");
        case kValidateErrorExclusiveMaximum:            return YGGDRASIL_RAPIDJSON_ERROR_STRING("Number '%actual' is greater than or equal to the 'exclusiveMaximum' value '%expected'.");
        case kValidateErrorMinimum:                     return YGGDRASIL_RAPIDJSON_ERROR_STRING("Number '%actual' is less than the 'minimum' value '%expected'.");
        case kValidateErrorExclusiveMinimum:            return YGGDRASIL_RAPIDJSON_ERROR_STRING("Number '%actual' is less than or equal to the 'exclusiveMinimum' value '%expected'.");

        case kValidateErrorMaxLength:                   return YGGDRASIL_RAPIDJSON_ERROR_STRING("String '%actual' is longer than the 'maxLength' value '%expected'.");
        case kValidateErrorMinLength:                   return YGGDRASIL_RAPIDJSON_ERROR_STRING("String '%actual' is shorter than the 'minLength' value '%expected'.");
#ifndef DISABLE_YGGDRASIL_RAPIDJSON
        case kValidateErrorPattern:                     return YGGDRASIL_RAPIDJSON_ERROR_STRING("String '%actual' does not match the 'pattern' regular expression '%expected'.");
#else // DISABLE_YGGDRASIL_RAPIDJSON
        case kValidateErrorPattern:                     return YGGDRASIL_RAPIDJSON_ERROR_STRING("String '%actual' does not match the 'pattern' regular expression.");
#endif // DISABLE_YGGDRASIL_RAPIDJSON

        case kValidateErrorMaxItems:                    return YGGDRASIL_RAPIDJSON_ERROR_STRING("Array of length '%actual' is longer than the 'maxItems' value '%expected'.");
        case kValidateErrorMinItems:                    return YGGDRASIL_RAPIDJSON_ERROR_STRING("Array of length '%actual' is shorter than the 'minItems' value '%expected'.");
        case kValidateErrorUniqueItems:                 return YGGDRASIL_RAPIDJSON_ERROR_STRING("Array has duplicate items at indices '%duplicates' but 'uniqueItems' is true.");
        case kValidateErrorAdditionalItems:             return YGGDRASIL_RAPIDJSON_ERROR_STRING("Array has an additional item at index '%disallowed' that is not allowed by the schema.");

        case kValidateErrorMaxProperties:               return YGGDRASIL_RAPIDJSON_ERROR_STRING("Object has '%actual' members which is more than 'maxProperties' value '%expected'.");
        case kValidateErrorMinProperties:               return YGGDRASIL_RAPIDJSON_ERROR_STRING("Object has '%actual' members which is less than 'minProperties' value '%expected'.");
        case kValidateErrorRequired:                    return YGGDRASIL_RAPIDJSON_ERROR_STRING("Object is missing the following members required by the schema: '%missing'.");
        case kValidateErrorAdditionalProperties:        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Object has an additional member '%disallowed' that is not allowed by the schema.");
        case kValidateErrorPatternProperties:           return YGGDRASIL_RAPIDJSON_ERROR_STRING("Object has 'patternProperties' that are not allowed by the schema.");
        case kValidateErrorDependencies:                return YGGDRASIL_RAPIDJSON_ERROR_STRING("Object has missing property or schema dependencies, refer to following errors.");

        case kValidateErrorEnum:                        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has a value that is not one of its allowed enumerated values: %expected.");
        case kValidateErrorType:                        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has a type '%actual' that is not in the following list: '%expected'.");

        case kValidateErrorOneOf:                       return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property did not match any of the sub-schemas specified by 'oneOf', refer to following errors.");
        case kValidateErrorOneOfMatch:                  return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property matched more than one of the sub-schemas specified by 'oneOf', indices '%matches'.");
        case kValidateErrorAllOf:                       return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property did not match all of the sub-schemas specified by 'allOf', refer to following errors.");
        case kValidateErrorAnyOf:                       return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property did not match any of the sub-schemas specified by 'anyOf', refer to following errors.");
        case kValidateErrorNot:                         return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property matched the sub-schema specified by 'not'.");
#ifndef DISABLE_YGGDRASIL_RAPIDJSON
        case kValidateErrorRequiredSchema:              return YGGDRASIL_RAPIDJSON_ERROR_STRING("Schema is missing a required property.");
        case kValidateErrorSubType:                     return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has a subtype '%actual' that is not in the following list '%expected'.");
        case kValidateErrorPrecision:                   return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has a precision of %actual that is incompatible with the schema precision %expected.");
        case kValdiateErrorUnits:                       return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has units '%actual' that are not compatible with the schema '%expected'.");
        case kValidateErrorShape:                       return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has a shape %actual that does not match the schema %expected.");
        case kValidateErrorEncoding:                    return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has an encoding '%actual' that does not match the schema '%expected'.");
        case kValidateErrorPythonImport:                return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is not an importable Python object: '%disallowed'.");
        case kValidateErrorPythonClass:                 return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is not a Python instance of the class '%expected' specified in the schema (actual = '%actual').");
        case kValidateErrorPythonDisabled:              return YGGDRASIL_RAPIDJSON_ERROR_STRING("Python was disabled so Python objects cannot be serialized: '%disallowed'");
        case kValidateErrorInvalidSchema:               return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is not a valid JSON schema.");
        case kValidateErrorPly:                         return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is not a valid Ply document: %disallowed");
        case kValidateErrorObjWavefront:                return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is not a valid ObjWavefront document: %disallowed");
        case kNormalizeErrorAliasDuplicate:             return YGGDRASIL_RAPIDJSON_ERROR_STRING("Aliased property already exists in the normalized document.");
        case kNormalizeErrorCircularAlias:              return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has circular aliases.");
        case kNormalizeErrorConflictingAliases:         return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has conflicting values for %conflicting aliases: %expected vs %actual.");
        case kNormalizeErrorMergeConflict:              return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property has conflicting normalized documents, %expected and %actual");
	// Warnings
        case kValidateWarnings:                         return YGGDRASIL_RAPIDJSON_ERROR_STRING("One or more validation warnings have occurred");
        case kDeprecatedWarning:                        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is being deprecated.");
	// Generic error for debugging
        case kValidateErrorGeneric:                     return YGGDRASIL_RAPIDJSON_ERROR_STRING("Generic error occurred: %message");
        case kIncompatibleSchemas:                      return YGGDRASIL_RAPIDJSON_ERROR_STRING("Incompatible schema property '%property': %expected vs %actual.");
        case kValidateErrorMissingSubschema:            return YGGDRASIL_RAPIDJSON_ERROR_STRING("Subschema is missing from one of the two schemas.");
        case kValidateErrorSubschemas:                  return YGGDRASIL_RAPIDJSON_ERROR_STRING("Object has one or more invalid subschemas.");
#endif // DISABLE_YGGDRASIL_RAPIDJSON

        case kValidateErrorReadOnly:                    return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is read-only but has been provided when validation is for writing.");
        case kValidateErrorWriteOnly:                   return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property is write-only but has been provided when validation is for reading.");

        default:                                        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Unknown error.");
    }
}

//! Maps error code of schema document compilation into error message.
/*!
    \ingroup YGGDRASIL_RAPIDJSON_ERRORS
    \param schemaErrorCode Error code obtained from compiling the schema document.
    \return the error message.
    \note User can make a copy of this function for localization.
        Using switch-case is safer for future modification of error codes.
*/
  inline const YGGDRASIL_RAPIDJSON_ERROR_CHARTYPE* GetSchemaError_En(SchemaErrorCode schemaErrorCode) {
      switch (schemaErrorCode) {
          case kSchemaErrorNone:                        return YGGDRASIL_RAPIDJSON_ERROR_STRING("No error.");

          case kSchemaErrorStartUnknown:                return YGGDRASIL_RAPIDJSON_ERROR_STRING("Pointer '%value' to start of schema does not resolve to a location in the document.");
          case kSchemaErrorRefPlainName:                return YGGDRASIL_RAPIDJSON_ERROR_STRING("$ref fragment '%value' must be a JSON pointer.");
          case kSchemaErrorRefInvalid:                  return YGGDRASIL_RAPIDJSON_ERROR_STRING("$ref must not be an empty string.");
          case kSchemaErrorRefPointerInvalid:           return YGGDRASIL_RAPIDJSON_ERROR_STRING("$ref fragment '%value' is not a valid JSON pointer at offset '%offset'.");
          case kSchemaErrorRefUnknown:                  return YGGDRASIL_RAPIDJSON_ERROR_STRING("$ref '%value' does not resolve to a location in the target document.");
          case kSchemaErrorRefCyclical:                 return YGGDRASIL_RAPIDJSON_ERROR_STRING("$ref '%value' is cyclical.");
          case kSchemaErrorRefNoRemoteProvider:         return YGGDRASIL_RAPIDJSON_ERROR_STRING("$ref is remote but there is no remote provider.");
          case kSchemaErrorRefNoRemoteSchema:           return YGGDRASIL_RAPIDJSON_ERROR_STRING("$ref '%value' is remote but the remote provider did not return a schema.");
          case kSchemaErrorRegexInvalid:                return YGGDRASIL_RAPIDJSON_ERROR_STRING("Invalid regular expression '%value' in 'pattern' or 'patternProperties'.");
          case kSchemaErrorSpecUnknown:                 return YGGDRASIL_RAPIDJSON_ERROR_STRING("JSON schema draft or OpenAPI version is not recognized.");
          case kSchemaErrorSpecUnsupported:             return YGGDRASIL_RAPIDJSON_ERROR_STRING("JSON schema draft or OpenAPI version is not supported.");
          case kSchemaErrorSpecIllegal:                 return YGGDRASIL_RAPIDJSON_ERROR_STRING("Both JSON schema draft and OpenAPI version found in document.");
          case kSchemaErrorReadOnlyAndWriteOnly:        return YGGDRASIL_RAPIDJSON_ERROR_STRING("Property must not be both 'readOnly' and 'writeOnly'.");

          default:                                      return YGGDRASIL_RAPIDJSON_ERROR_STRING("Unknown error.");
    }
  }

//! Maps error code of pointer parse into error message.
/*!
    \ingroup YGGDRASIL_RAPIDJSON_ERRORS
    \param pointerParseErrorCode Error code obtained from pointer parse.
    \return the error message.
    \note User can make a copy of this function for localization.
        Using switch-case is safer for future modification of error codes.
*/
inline const YGGDRASIL_RAPIDJSON_ERROR_CHARTYPE* GetPointerParseError_En(PointerParseErrorCode pointerParseErrorCode) {
    switch (pointerParseErrorCode) {
        case kPointerParseErrorNone:                       return YGGDRASIL_RAPIDJSON_ERROR_STRING("No error.");

        case kPointerParseErrorTokenMustBeginWithSolidus:  return YGGDRASIL_RAPIDJSON_ERROR_STRING("A token must begin with a '/'.");
        case kPointerParseErrorInvalidEscape:              return YGGDRASIL_RAPIDJSON_ERROR_STRING("Invalid escape.");
        case kPointerParseErrorInvalidPercentEncoding:     return YGGDRASIL_RAPIDJSON_ERROR_STRING("Invalid percent encoding in URI fragment.");
        case kPointerParseErrorCharacterMustPercentEncode: return YGGDRASIL_RAPIDJSON_ERROR_STRING("A character must be percent encoded in a URI fragment.");

        default:                                           return YGGDRASIL_RAPIDJSON_ERROR_STRING("Unknown error.");
    }
}

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#ifdef __clang__
YGGDRASIL_RAPIDJSON_DIAG_POP
#endif

#endif // YGGDRASIL_RAPIDJSON_ERROR_EN_H_
