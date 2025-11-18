
## An extension of the RapidJSON C++ header-only library for use with yggdrasil

## Introduction

[RapidJSON](https://github.com/Tencent/rapidjson) is a JSON parser and generator for C++. YggdrasilRapidJSON is built upon RapidJSON with support for several features that were required by the [yggdrasil](https://github.com/cropsinsilico/yggdrasil) package for language interoperability between scientific models. Features added by YggdrasilRapidJSON include:

* Serialization/deserialization of non-standard JSON datatypes. The serialized messages are standard JSON, but contain additional information. These types include:
  * Scalars w/ arbitrary precision
  * N-dimensional arrays w/ arbitrary precision
  * Complex number scalars/arrays
  * Scalars/arrays w/ physical units
  * 3D mesh geometries (i.e. ply/obj)
  * Embedded Python functions/classes/instances
  * Tables
  * Schemas
* Light-weight library for scalar & array operations w/ physical units
* Normalization of JSON documents against schemas
  * Default properties
  * Unit transformations
  * Precision/data type transformations
* Schema comparison
* Schema encoding from JSON documents

## Installation

Like RapidJSON, YggdrasilRapidJSON is a header-only C++ library. Just copy the `include/yggdrasil_rapidjson` folder to system or project's include path.

Alternatively, YggdrasilRapidJSON can also be installed from conda-forge via:
* conda install -c conda-forge yggdrasil-rapidjson

YggdrasilRapidJSON uses the following software as its dependencies:
* [CMake](https://cmake.org/) as a general build tool
* (optional) [Doxygen](http://www.doxygen.org) to build documentation
* (optional) [googletest](https://github.com/google/googletest) for unit and performance testing
* (optional) [cpython](https://github.com/python/cpython) for support of embedded Python objects.

To generate user documentation and/or run the tests please proceed with the steps below:

1. Execute `git submodule update --init` to get the files of thirdparty submodules (google test).
2. Create directory called `build` in the yggdrasil-rapidjson source directory.
3. Change to the `build` directory
4. Run `cmake ..` to configure your build.
5. Run `cmake --build .` to complete the build.

On a successful build you will find compiled test and example binaries in the `bin`
directory of the build tree. The generated documentation will be available in the `doc/html`
directory of the build tree. To run the tests after the build finishes, run `ctest` from your build tree. You can get detailed output using `ctest -V` command.

It is possible to install library system-wide by running `cmake --install .` from the build tree with administrative privileges. This will install all files
according to system preferences.  Once YggdrasilRapidJSON is installed, it is possible
to use it from other CMake projects by adding `find_package(YggdrasilRapidJSON)` line to
your CMakeLists.txt.

## Examples of YggdrasilRapidJSON extensions to RapidJSON

* [yggdrasil](https://github.com/cropsinsilico/yggdrasil-rapidjson/blob/yggdrasil/example/yggdrasil/yggdrasil.cpp): Basic usage of yggdrasil types within the RapidJSON DOM API.
* [units](https://github.com/cropsinsilico/yggdrasil-rapidjson/blob/yggdrasil/example/units/units.cpp): Example usage of scalars/arrays with physical units
* [schemanormalizer](https://github.com/cropsinsilico/yggdrasil-rapidjson/blob/yggdrasil/example/schemanormalizer/schemanormalizer.cpp): A command line tool to normalize a JSON with a JSON schema.

## Contributing

YggdrasilRapidJSON welcomes contributions. When contributing, please follow the code below.

### Issues

Feel free to submit issues and enhancement requests.

Please help us by providing **minimal reproducible examples**, because source code is easier to let other people understand what happens.
For crash problems on certain platforms, please bring stack dump content with the detail of the OS, compiler, etc.

Please try breakpoint debugging first, tell us what you found, see if we can start exploring based on more information been prepared.

### Workflow

In general, we follow the "fork-and-pull" Git workflow.

 1. **Fork** the repo on GitHub
 2. **Clone** the project to your own machine
 3. **Checkout** a new branch on your fork, start developing on the branch
 4. **Test** the change before commit, Make sure the changes pass all the tests, including `unittest` and `preftest`, please add test case for each new feature or bug-fix if needed.
 5. **Commit** changes to your own branch
 6. **Push** your work back up to your fork
 7. Submit a **Pull request** so that we can review your changes

NOTE: Be sure to merge the latest from "upstream" before making a pull request!

### Copyright and Licensing

You can copy and paste the RapidJSON license summary from below.

```
Tencent is pleased to support the open source community by making RapidJSON available.

Copyright (C) 2015 THL A29 Limited, a Tencent company, and Milo Yip.

Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed 
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
CONDITIONS OF ANY KIND, either express or implied. See the License for the 
specific language governing permissions and limitations under the License.
```

## Maintenance

### Releases

The steps below outline how a release should be produced.

1. Complete developments desired for the release and merge them via pull request into the default branch (yggdrasil) after all tests pass. Ensure this includes any upstream changes from RapidJSON.
2. Create a new branch with the name of the version with a "v" prefix (i.e. vMAJOR.MINOR.PATCH.EXTEN) by either incrementing the EXTEN version or restarting it at 0 if the upstream RapidJSON version has been incremented.
3. Update CHANGELOG.md with release notes and commit them to the version branch.
4. Update the version in the following files and commit them to the version branch.
   * CMakeLists.txt
   * recipe/meta.yaml
   * conda.recipe/recipe.yaml
5. Merge the version branch via pull request, ensuring that all tests pass.
6. Create an annotated tag for the merged version changes and push it.
   * `git tag -a vX.X.X.X -m "Release vX.X.X.X"`
   * `git push origin --tags`
7. Create a release on github
8. Ensure the conda feedstock is updated
