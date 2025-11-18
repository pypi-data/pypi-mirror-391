import copy
import json
import argparse
import os
import requests


def create_full_schema(fname):
    from yggdrasil import schema
    s = schema.get_schema()
    s.save(fname, schema=s.get_schema())


def get_ygg_tests():
    import yaml
    fname = os.path.join(os.path.dirname(__file__),
                         'test', 'full_schema.yml')
    if args.create_full_schema or not os.path.isfile(fname):
        try:
            create_full_schema(fname)
        except ImportError:
            return []
    with open(fname, 'r') as fd:
        base = yaml.load(fd, yaml.SafeLoader)
    try:
        base_file = base[
            'definitions']['file-subtype-base']['properties']['name']
        base_file['pattern'] = base_file['pattern'].replace('\\', '\\\\')
    except KeyError:
        pass
    if 'allOf' in base['definitions']['file']:
        subtypes = base['definitions']['file']['allOf'][1]['anyOf']
    else:
        subtypes = base['definitions']['file']['anyOf']
    for x_def in subtypes:
        x = base['definitions'][x_def['$ref'].split('#/definitions/')[-1]]
        try:
            x['properties']['name']['pattern'] = x[
                'properties']['name']['pattern'].replace('\\', '\\\\')
        except KeyError:
            pass
    default_datatype = ("-YGG-eyJ0eXBlIjoic2NoZW1hIn0=-YGG-eyJ0eXBlIj"
                        "oic2NhbGFyIiwic3VidHlwZSI6InN0cmluZyJ9-YGG-")
    test_yaml = (
        {'models': [
            {'name': 'fortran_modelA',
             'language': 'fortran',
             'args': './src/gs_lesson4b_modelA.f90',
             'inputs': [
                 {'name': 'inputA',
                  'driver': 'FileInputDriver',
                  'args': './Input/input.txt'}],
             'outputs': [
                 {'name': 'outputA',
                  'driver': 'OutputDriver',
                  'args': 'A_to_B'}]},
            {'name': 'fortran_modelB',
             'language': 'fortran',
             'args': './src/gs_lesson4b_modelB.f90',
             'inputs': [
                 {'name': 'inputA',
                  'driver': 'InputDriver',
                  'args': 'A_to_B'}],
             'outputs': [
                 {'name': 'outputA',
                  'driver': 'FileOutputDriver',
                  'args': './output.txt'}]},
            {'name': 'modelA',
             'language': 'python',
             'args': ['model.py', '-v'],
             'outputs': [
                 {'name': 'outputA',
                  'column_names': ['a', 'b'],
                  'column_units': ['cm', 'g'],
                  'filter': {
                     'function': 'example_python:example_filter'}}],
             'working_dir': os.getcwd()},
            {'name': 'modelB',
             'language': 'c',
             'args': './src/modelA.c',
             'function': 'fake',
             'is_server': {'input': 'A', 'output': 'B'},
             'outputs': 'B',
             'working_dir': os.getcwd()},
            {'args': './src/modelA.c',
             'driver': 'GCCModelDriver',
             'inputs': ['inputA'],
             'name': 'modelA',
             'outputs': ['outputA']}],
         'connections': [
             {'input': 'outputA',
              'output': 'fileA.txt',
              'seritype': 'ply'},
             {'inputs': [('/var/folders/6y/tnvg4kjn4n72pcpqw__8jjmh00'
                          '00gn/T/tmp_7c25e645_0.yml')],
              'outputs': 'inputA',
              'read_meth': 'all'},
             {'input': 'outputA',
              'output': ['output.txt'],
              'write_meth': 'all'}],
         'working_dir': os.getcwd()},
        {'models': [
            {'name': 'fortran_modelA',
             'language': 'fortran',
             'args': ['./src/gs_lesson4b_modelA.f90'],
             'working_dir': os.getcwd(),
             'inputs': [
                 {'name': 'inputA',
                  'filetype': 'binary',
                  'driver': 'FileInputDriver',
                  "serializer": {'seritype': 'default'},
                  'working_dir': os.getcwd(),
                  'args': './Input/input.txt'}],
             'outputs': [
                 {'name': 'outputA',
                  'commtype': 'default',
                  "datatype": default_datatype,
                  'driver': 'OutputDriver',
                  'args': 'A_to_B'}]},
            {'name': 'fortran_modelB',
             'language': 'fortran',
             'args': ['./src/gs_lesson4b_modelB.f90'],
             'working_dir': os.getcwd(),
             'inputs': [
                 {'name': 'inputA',
                  'commtype': 'default',
                  "datatype": default_datatype,
                  'driver': 'InputDriver',
                  'args': 'A_to_B'}],
             'outputs': [
                 {'name': 'outputA',
                  'filetype': 'binary',
                  "serializer": {'seritype': 'default'},
                  'driver': 'FileOutputDriver',
                  'working_dir': os.getcwd(),
                  'args': './output.txt'}]},
            {'name': 'modelA',
             'language': 'python',
             'args': ['model.py', '-v'],
             'inputs': [{'commtype': 'default',
                         'datatype': default_datatype,
                         'is_default': True,
                         'name': 'input'}],
             'outputs': [{'name': 'outputA',
                          'commtype': 'default',
                          'datatype': default_datatype,
                          'filter': {
                              'function': (
                                  '-YGG-eyJ0eXBlIjoiZnVuY3Rpb24ifQ=='
                                  '-YGG-ZXhhbXBsZV9weXRob246ZXhhbXBsZV9'
                                  'maWx0ZXI=-YGG-')},
                          'field_names': ['a', 'b'],
                          'field_units': ['cm', 'g']}],
             'working_dir': os.getcwd()},
            {'name': 'modelB',
             'language': 'c',
             'args': ['./src/modelA.c'],
             'function': 'fake',
             'is_server': {'input': 'A', 'output': 'B'},
             'inputs': [{'commtype': 'default',
                         'datatype': default_datatype,
                         'is_default': True,
                         'name': 'input'}],
             'outputs': [{'name': 'B',
                          'commtype': 'default',
                          'datatype': default_datatype}],
             'working_dir': os.getcwd()},
            {'args': ['./src/modelA.c'],
             'driver': 'GCCModelDriver',
             'inputs': [{'name': 'inputA',
                         'commtype': 'default',
                         'datatype': default_datatype}],
             'name': 'modelA',
             'language': 'c',
             'outputs': [{'name': 'outputA',
                          'commtype': 'default',
                          'datatype': default_datatype}],
             'working_dir': os.getcwd()}],
         'connections': [
             {'inputs': [
                 {'name': 'outputA',
                  'datatype': default_datatype,
                  'commtype': 'default',
                  'working_dir': os.getcwd()}],
              'outputs': [
                  {'name': 'fileA.txt',
                   'filetype': 'binary',
                   'serializer': {'seritype': 'ply'},
                   'working_dir': os.getcwd()}],
              'working_dir': os.getcwd()},
             {'inputs': [{'name': ('/var/folders/6y/tnvg4kjn4n72pcpqw'
                                   '__8jjmh0000gn/T/tmp_7c25e645_0.yml'),
                          'filetype': 'binary',
                          'serializer': {'seritype': 'default'},
                          'working_dir': os.getcwd()}],
              'outputs': [{'name': 'inputA',
                           'commtype': 'default',
                           'datatype': default_datatype}],
              'working_dir': os.getcwd(),
              'read_meth': 'all'},
             {'inputs': [{'name': 'outputA',
                          'commtype': 'default',
                          'datatype': default_datatype,
                          'working_dir': os.getcwd()}],
              'outputs': [{'name': 'output.txt',
                           'filetype': 'binary',
                           'serializer': {'seritype': 'default'},
                           'working_dir': os.getcwd()}],
              'working_dir': os.getcwd(),
              'write_meth': 'all'}
         ],
         'working_dir': os.getcwd()})
    if args.create_full_schema:
        test_yaml[0]['models'].append(
            {'name': 'modelA',
             'args': './src/modelA.c',
             'driver': 'GCCModelDriver',
             'inputs': [{'name': 'inputA',
                         'args': (
                             '/var/folders/6y/tnvg4kjn4n72pcpqw__8jj'
                             'mh0000gn/T/tmp_5729eb32_0.yml'),
                         'driver': 'FileInputDriver',
                         'onexit': 'printStatus',
                         'translator': (
                             'tests.test_yamlfile:direct_translate')
                         }],
             'outputs': [{'name': 'outputA',
                          'driver': 'FileOutputDriver',
                          'args': 'fileA.txt',
                          'onexit': 'printStatus',
                          'translator': (
                              'tests.test_yamlfile:direct_translate')
                          },
                         {'name': 'outputA2',
                          'driver': 'OutputDriver',
                          'args': 'A_to_B',
                          'onexit': 'printStatus',
                          'translator': (
                              'tests.test_yamlfile:direct_translate')
                          }]})
        test_yaml[1]['models'].append(
            {'name': 'modelA',
             'args': ['./src/modelA.c'],
             'driver': 'GCCModelDriver',
             'language': 'c',
             'working_dir': os.getcwd(),
             'inputs': [{'name': 'inputA',
                         'args': ('/var/folders/6y/tnvg4kjn4n72pcpqw_'
                                  '_8jjmh0000gn/T/tmp_5729eb32_0.yml'),
                         'driver': 'FileInputDriver',
                         'onexit': 'printStatus',
                         'transform': [
                             '-YGG-eyJ0eXBlIjoiY2xhc3MifQ==-YGG-dGVz'
                             'dHMudGVzdF95YW1sZmlsZTpkaXJlY3RfdHJhbn'
                             'NsYXRl-YGG-'],
                         'working_dir': os.getcwd(),
                         'serializer': {'seritype': 'default'},
                         'filetype': 'binary'}],
             'outputs': [{'name': 'outputA',
                          'driver': 'FileOutputDriver',
                          'args': 'fileA.txt',
                          'onexit': 'printStatus',
                          'transform': [
                              '-YGG-eyJ0eXBlIjoiY2xhc3MifQ==-YGG-dGVz'
                              'dHMudGVzdF95YW1sZmlsZTpkaXJlY3RfdHJhbn'
                              'NsYXRl-YGG-'],
                          'working_dir': os.getcwd(),
                          'serializer': {'seritype': 'default'},
                          'filetype': 'binary'},
                         {'name': 'outputA2',
                          'driver': 'OutputDriver',
                          'args': 'A_to_B',
                          'onexit': 'printStatus',
                          'transform': [
                              '-YGG-eyJ0eXBlIjoiY2xhc3MifQ==-YGG-dGVz'
                              'dHMudGVzdF95YW1sZmlsZTpkaXJlY3RfdHJhbn'
                              'NsYXRl-YGG-'],
                          'datatype': default_datatype,
                          'commtype': 'default'}]})
    if False:
        test_yaml = (
            {'connections': {'in_temp': True,
                             'input': 'output_log',
                             'output': 'client_output.txt'},
             'models': [{'args': ['./src/client.R', 3],
                         'client_of': 'server',
                         'language': 'R',
                         'name': 'client',
                         'outputs': 'output_log'}],
             'working_dir': (
                 '/Users/langmm/yggdrasil/yggdrasil/examples/rpc_lesson1')},
            {'connections': [
                {'inputs': [
                    {'name': 'output_log',
                     'commtype': 'default',
                     'datatype': default_datatype,
                     'working_dir': (
                         '/Users/langmm/yggdrasil/yggdrasil/examples/'
                         'rpc_lesson1')}],
                 'outputs': [
                     {'name': 'client_output.txt',
                      'in_temp': True,
                      'filetype': 'binary',
                      'serializer': {'seritype': 'default'},
                      'working_dir': (
                          '/Users/langmm/yggdrasil/yggdrasil/examples/'
                          'rpc_lesson1')}],
                 'working_dir': (
                     '/Users/langmm/yggdrasil/yggdrasil/examples/'
                     'rpc_lesson1')}],
             'models': [
                 {'args': ['./src/client.R', 3],
                  'client_of': ['server'],
                  'inputs': [
                      {'commtype': 'default',
                       'datatype': default_datatype,
                       'is_default': True,
                       'name': 'input'}],
                  'language': 'R',
                  'name': 'client',
                  'outputs': [
                      {'commtype': 'default',
                       'datatype': default_datatype,
                       'name': 'output_log'}],
                  'working_dir': (
                      '/Users/langmm/yggdrasil/yggdrasil/examples/'
                      'rpc_lesson1')}],
             'working_dir': (
                 '/Users/langmm/yggdrasil/yggdrasil/examples/rpc_lesson1')})
    return (["#define METASCHEMA_YGG_TESTS", ""]
            + make_function("get_yggschema", base)
            + make_function("get_testschema", test_yaml[0])
            + make_function("get_testschema_result", test_yaml[1]))


def make_function(name, base):
    return [
        "template<typename T>",
        "inline const typename item_return<T>::type* " + name + "() {"
        " return NULL; }", "",
        "template<>",
        "inline const item_return<char>::type* " + name + "<char>() {",
        "  const char* out = \""
        + json.dumps(base, indent=1).replace(
            "\"\\t\"", "\"\\\\t\"").replace(
            "\"\\n\"", "\"\\\\n\"").replace(
            "\\\"", "\\\\\"").replace(
            "\"", "\\\"").replace(
            '\n', "\"\n    \"")
        + "\";",
        "  return out;",
        "}", "",
        "template<>",
        "inline const item_return<wchar_t>::type* " + name + "<wchar_t>() {",
        "  const wchar_t* out = L\""
        + json.dumps(base, indent=1).replace(
            "\"\\t\"", "\"\\\\t\"").replace(
            "\"\\n\"", "\"\\\\n\"").replace(
            "\\\"", "\\\\\"").replace(
            "\"", "\\\"").replace(
            '\n', "\"\n    L\"")
        + "\";",
        "  return out;",
        "}", ""]


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Create a C++ header file containing "
                                     "the YGGDRASIL schema")
    parser.add_argument("dest",
                        help=("Path to header file where the metaschema "
                              "should be saved."))
    parser.add_argument("--base-draft", default="draft-04",
                        help="JSON schema draft that should be used as a base")
    parser.add_argument("--ygg-tests", action='store_true',
                        help='Include tests for the yggdrasil schema')
    parser.add_argument("--create-full-schema", action='store_true',
                        help='Create a full_schema.yml file')
    args = parser.parse_args()
    url = f'https://json-schema.org/{args.base_draft}/schema'
    r = requests.get(url)
    r.raise_for_status()
    standard = r.json()
    base = copy.deepcopy(standard)
    base['title'] = "Ygg meta-schema for data type schemas"
    base['definitions']['simpleTypes']['enum'] += [
        "1darray", "any", "bytes", "class", "complex", "float",
        "function", "instance", "int", "ndarray", "obj", "ply",
        "scalar", "schema", "uint", "unicode"]
    base['properties'].update({
        "args": {
            "description": (
                "Arguments required to recreate a class instance."),
            "type": "array"
        },
        "class": {
            "anyOf": [
                {"type": "class"},
                {"items": {"type": "class"},
                 "minItems": 1,
                 "type": "array"}],
            "description": (
                "One or more classes that the object should be an "
                "instance of.")
        },
        "kwargs": {
            "description": (
                "Keyword arguments required to recreate a class "
                "instance."),
            "type": "object"
        },
        "length": {
            "description": "Number of elements in the 1D array.",
            "minimum": 1,
            "type": "number"
        },
        "precision": {
            "description": "The size (in bits) of each item.",
            "minimum": 1,
            "type": "number"
        },
        "encoding": {
            "description": "The encoding of string elements",
            "enum": ["UTF8", "UTF16", "UTF32", "ASCII", "UCS4"]
        },
        "shape": {
            "description": "Shape of the ND array in each dimension.",
            "items": {
                "minimum": 1,
                "type": "integer"
            },
            "type": "array"
        },
        "ndim": {
            "description": "Number of dimensions in the ND array.",
            "minimum": 1,
            "type": "integer"
        },
        "subtype": {
            "description": "The base type for each item.",
            "enum": [
                "string",
                "complex",
                "float",
                "int",
                "uint",
                "bytes",
                "unicode",
                "any",
            ],
            "type": "string"
        },
        "units": {
            "description": "Physical units.",
            "type": "string"
        },
        "aliases": {
            "description": "Aliases for a property that also be used.",
            "type": "array",
            "items": {"type": "string"}
        },
        "allowSingular": {
            "description": (
                "If true, the value may only contain an element "
                "matching the schema for 1) all array items, 2) the "
                "only array item in a 1-element long array, 3) the "
                "first required object property, 4) the only object "
                "property in a 1-element long object. Only valid for "
                "array & object schemas."),
            "type": ["boolean", "string"],
            "default": False
        },
        "allowWrapped": {
            "description": (
                "If true, the value may be wrapped in an array. If a "
                "string, the value may be wrapped in an object at the "
                "property specified by the string."),
            "type": ["boolean", "string"],
            "default": False
        },
        "deprecated": {
            "description": (
                "Message about the deprecation of a schema property "
                "that will be displayed during validation."
                " If true, a generic warning will be displayed."),
            "type": ["boolean", "string"],
        },
        "pullProperties": {
            "description": (
                "Pull properties from another location in the "
                "provided JSON document. If true, any missing local "
                "properties will be pulled from the parent object. "
                "If an array of property names is provided, only "
                "those local properties in the array will be pulled "
                "from the parent object. If an object is provided, "
                "the keys should be relative or absolute paths to "
                "objects in the JSON document that properties will "
                "be pulled from with the values specifying which "
                "properties should be pulled (true for all "
                "properties and an array or a select subset)."),
            "oneOf": [
                {"type": "boolean"},
                {"type": "array",
                 "items": {"type": "string"}},
                {"type": "object",
                 "additionalProperties": {
                     "oneOf": [
                         {"type": "boolean"},
                         {"type": "array",
                          "items": {"type": "string"}}]}}],
            "default": False
        },
        "pushProperties": {
            "description": (
                "Push properties to another location in the provided "
                "JSON document. If true, any properties missing from "
                "the parent will be pushed to the parent object. If "
                "an array of property names is provided, only those "
                "parent properties in the array will be pushed to "
                "the parent object. If an object is provided, the "
                "keys should be relative or absolute paths to "
                "objects in the JSON document that properties will "
                "be pushed to with the values specifying which "
                "properties should be pushed (true for all missing "
                "destination properties and an array or a select "
                "subset)."),
            "oneOf": [
                {"type": "boolean"},
                {"type": "array",
                 "items": {"type": "string"}},
                {"type": "object",
                 "additionalProperties": {
                     "oneOf": [
                         {"type": "boolean"},
                         {"type": "array",
                          "items": {"type": "string"}}]}}],
            "default": False
        }
    })
    contents = ["// This file is generated by create_metaschema.py do"
                " not modify directly", "",
                "#ifndef YGGDRASIL_RAPIDJSON_METASCHEMA_H_",
                "#define YGGDRASIL_RAPIDJSON_METASCHEMA_H_", "",
                "template<class T>",
                "struct item_return{ typedef T type; };", ""]
    contents += (make_function("get_metaschema", base)
                 + make_function("get_standard_metaschema", standard))
    # Create test
    if args.ygg_tests:
        contents += get_ygg_tests()
    # End test
    contents += ["", "#endif // YGGDRASIL_RAPIDJSON_METASCHEMA_H_", ""]
    with open(args.dest, 'w') as fd:
        fd.write('\n'.join(contents))
