// Hello World example w/ Yggdrasil extension types
// This example shows basic usage of DOM-style API for the yggdrasil types.

#ifndef DISABLE_YGGDRASIL_RAPIDJSON

#include "yggdrasil_rapidjson/document.h"     // rapidjson's DOM-style API
#include "yggdrasil_rapidjson/prettywriter.h" // for stringify JSON
#include "yggdrasil_rapidjson/internal/meta.h" // values_eq for floating point comparison
#include <cstdio>

using namespace yggdrasil_rapidjson;
using namespace std;

int main(int, char*[]) {
    ////////////////////////////////////////////////////////////////////////////
    // 1. Modify the document w/ yggdrasil types
  
    Document document(kObjectType);

    // Scalars with precisions not supported by rapidjson core
    {
      uint8_t x = 25;
      document.AddMember("uint8", x, document.GetAllocator());
      assert(document["uint8"].IsScalar());
    }

    // ND Arrays
    {
      // Array on stack
      float array2d[8][3] = {
        {0.0, 0.0, 0.0},
        {0.0, 0.0, 1.0},
        {0.0, 1.0, 1.0},
        {0.0, 1.0, 0.0},
        {1.0, 0.0, 0.0},
        {1.0, 0.0, 1.0},
        {1.0, 1.0, 1.0},
        {1.0, 1.0, 0.0}};
      Value v(array2d, document.GetAllocator());
      document.AddMember("Array2D", v, document.GetAllocator());
    }
    {
      // Array on heap
      Document::AllocatorType& allocator = document.GetAllocator();
      SizeType shape[3] = {2, 3, 3};
      SizeType nelements = 2 * 3 * 3;
      float* array3d = (float*)allocator.Malloc(nelements * sizeof(float));
      for (SizeType i = 0; i < nelements; i++) {
        array3d[i] = (float)(i * 0.05);
      }
      Value v(array3d, shape, 3, allocator);
      document.AddMember("Array3D", v, allocator);
      allocator.Free(array3d);
    }

    // Scalars/arrays with units
    {
      units::Quantity<double> scalar(0.5, "cm/s");
      document.AddMember("ScalarUnits", scalar, document.GetAllocator());
    }
    {
      float array2d[8][3] = {
        {0.0, 0.0, 0.0},
        {0.0, 0.0, 1.0},
        {0.0, 1.0, 1.0},
        {0.0, 1.0, 0.0},
        {1.0, 0.0, 0.0},
        {1.0, 0.0, 1.0},
        {1.0, 1.0, 1.0},
        {1.0, 1.0, 0.0}};
      units::QuantityArray<float> array(array2d, "cm/s");
      document.AddMember("ArrayUnits", array, document.GetAllocator());
    }

    // Strings with specific encoding
    {
      StringBuffer os;
      os.Clear();
      UTF8<>::Encode(os, 0x0370);
      Value v(os.GetString(), static_cast<SizeType>(os.GetLength()),
              "UCS4", 4, document.GetAllocator());
      document.AddMember("Encoded", v, document.GetAllocator());
    }

    ////////////////////////////////////////////////////////////////////////////
    // 2. Access yggdrasil types in document.

    // Scalars with precisions not supported by rapidjson core
    {
      assert(document["uint8"].IsScalar());
      assert(document["uint8"].IsScalar<uint8_t>()); // Check type
      assert(document["uint8"].GetScalar<uint8_t>() == 25);
      // Get scalar converted to higher precision
      assert(document["uint8"].GetScalar<uint32_t>() == 25);
    }
    
    // ND Arrays
    {
      // Array on stack
      assert(document["Array2D"].IsNDArray());
      assert(document["Array2D"].IsNDArray<float>()); // Check type
      assert(!document["Array2D"].IsNDArray<uint8_t>());
      assert(document["Array2D"].GetNDim() == 2);
      assert(document["Array2D"].GetShape()[0] == 8);
      assert(document["Array2D"].GetNElements() == (8 * 3));
      float dest_stack[8][3];
      document["Array2D"].GetNDArray(dest_stack);
      assert(internal::values_eq(dest_stack[6][2], (float)1.0));
      // Can also get the array in a version allocated on heap
      float* dest_heap = document["Array2D"].GetNDArray<float>(document.GetAllocator());
      assert(internal::values_eq(dest_heap[6 * 3 + 2], (float)1.0));
      document.GetAllocator().Free(dest_heap);
    }
    {
      // Array on heap
      assert(document["Array3D"].IsNDArray());
      assert(document["Array3D"].IsNDArray<float>()); // Check type
      assert(!document["Array3D"].IsNDArray<uint8_t>());
      assert(document["Array3D"].GetNDim() == 3);
      assert(document["Array3D"].GetShape()[0] == 2);
      SizeType nelements = 2 * 3 * 3;
      assert(document["Array3D"].GetNElements() == nelements);
      float dest_stack[2][3][3];
      document["Array3D"].GetNDArray(dest_stack);
      assert(internal::values_eq(dest_stack[1][2][2], (float)0.85));
      // Can also get the array in a version allocated on heap
      float* dest_heap = document["Array3D"].GetNDArray<float>(document.GetAllocator());
      assert(internal::values_eq(dest_heap[nelements - 1], (float)0.85));
      document.GetAllocator().Free(dest_heap);
      UNUSED(nelements);
    }

    // Scalars/arrays with units
    {
      assert(document["ScalarUnits"].IsScalar());
      assert(document["ScalarUnits"].IsScalar<double>());
      assert(document["ScalarUnits"].HasUnits());
      assert(internal::values_eq(document["ScalarUnits"].GetScalar<double>(), 0.5));
      assert(internal::values_eq(document["ScalarUnits"].GetScalar<double>("mm/s"), 5.0));
      units::Quantity<double> scalar = document["ScalarUnits"].GetScalarQuantity<double>();
      assert(internal::values_eq(scalar.value(), 0.5));
    }
    {
      assert(document["ArrayUnits"].IsNDArray());
      assert(document["ArrayUnits"].IsNDArray<float>()); // Check type
      assert(!document["ArrayUnits"].IsNDArray<uint8_t>());
      assert(document["ArrayUnits"].GetNDim() == 2);
      assert(document["ArrayUnits"].GetShape()[0] == 8);
      assert(document["ArrayUnits"].GetNElements() == (8 * 3));
      float dest_stack[8][3];
      document["ArrayUnits"].GetNDArray(dest_stack);
      assert(internal::values_eq(dest_stack[6][2], 1.0));
      float dest_stack_mmps[8][3];
      document["ArrayUnits"].GetNDArray(dest_stack_mmps, "mm/s");
      assert(internal::values_eq(dest_stack_mmps[6][2], (float)10.0));
      units::QuantityArray<float> array = document["ArrayUnits"].GetArrayQuantity<float>(document.GetAllocator());
      assert(internal::values_eq(array.value()[6 * 3 + 2], (float)1.0));
    }

    // Strings with specific encoding
    {
      assert(document["Encoded"].IsScalar());
      assert(document["Encoded"].HasEncoding());
      assert(std::strcmp(document["Encoded"].GetEncoding().GetString(), "UCS4") == 0);
    }
    
    ////////////////////////////////////////////////////////////////////////////
    // 3. Stringify JSON

    printf("\nModified JSON with reformatting:\n");
    StringBuffer sb;
    PrettyWriter<StringBuffer> writer(sb);
    document.Accept(writer);    // Accept() traverses the DOM and generates Handler events.
    puts(sb.GetString());

    ////////////////////////////////////////////////////////////////////////////
    // 4. Parse a JSON text string to a document.

    Document document2;  // Default template parameter uses UTF8 and MemoryPoolAllocator.

    if (document2.Parse(sb.GetString()).HasParseError())
        return 1;

    printf("\nParsing to document succeeded.\n");
    
    return 0;
}

#else // DISABLE_YGGDRASIL_RAPIDJSON

int main(int, char*[]) {
  return 0;
}

#endif // DISABLE_YGGDRASIL_RAPIDJSON
