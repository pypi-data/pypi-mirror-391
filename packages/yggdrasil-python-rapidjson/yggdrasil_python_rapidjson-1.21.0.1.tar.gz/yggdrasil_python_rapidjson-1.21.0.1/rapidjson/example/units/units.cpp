// Example of using Yggdrasil units

#ifndef DISABLE_YGGDRASIL_RAPIDJSON

#include "yggdrasil_rapidjson/units.h"         // Units
#include "yggdrasil_rapidjson/internal/meta.h" // values_eq for floating point comparison

using namespace yggdrasil_rapidjson;
using namespace std;

int main(int, char*[]) {
    ////////////////////////////////////////////////////////////////////////////
    // 1. Create scalars/arrays with units
    {
      // Scalar
      units::Quantity<float> x(5.0, "cm");
      assert(internal::values_eq(x.value(), (float)5.0));
      assert(x.unitsStr() == "cm");

      // Underlying type can be any number type
      units::Quantity<uint8_t> y(3, "s");
      assert(y.value() == (uint8_t)3);
      assert(y.unitsStr() == "s");
    }
    {
      // Array
      units::QuantityArray<int64_t> x({1, 2, 3, 4}, "cm");
      assert(x.value()[2] == (int64_t)3);
      assert(x.unitsStr() == "cm");
      assert(x.nelements() == 4);
      assert(x.ndim() == 1);
      assert(x.shape()[0] == 4);

      // Arrays can have 1 or more dimensions
      units::QuantityArray<uint32_t> y({{1, 2, 3, 4},
                                        {5, 6, 7, 8}}, "grams");
      assert(y.value()[5] == (uint32_t)6); // Elements stored in column major order
      assert(y.unitsStr() == "g");
      assert(y.nelements() == 8);
      assert(y.ndim() == 2);
      assert(y.shape()[1] == 4);
      
    }

    ////////////////////////////////////////////////////////////////////////////
    // 2. Perform arithmetic operations that track the units
    {
      // Scalars
      units::Quantity<double> x(5.0, "cm");
      units::Quantity<double> y(2.5, "s");
      units::Quantity<double> z = x / y;
      assert(internal::values_eq(z.value(), 2.0));
      assert(z.unitsStr() == "cm*(s**-1)");

      // For addition / subtraction values are converted first
      units::Quantity<double> a(5.0, "cm");
      units::Quantity<double> b(1.0, "m");
      units::Quantity<double> c = a + b;
      assert(internal::values_eq(c.value(), 105.0));
      assert(a.unitsStr() == "cm");

      // Operations can also be performed in place
      c += b;
      assert(internal::values_eq(c.value(), 205.0));
      assert(a.unitsStr() == "cm");
    }
    {
      // Arrays
      units::QuantityArray<double> x({1.0, 2.0, 3.0, 4.0}, "cm");
      units::QuantityArray<double> y({2.0, 2.0, 3.0, 3.0}, "s");
      units::QuantityArray<double> z = x / y;
      assert(z.nelements() == 4);
      assert(internal::values_eq(z.value()[1], 1.0));
      assert(z.unitsStr() == "cm*(s**-1)");
    }
    {
      // Mixed array & scalar
      units::QuantityArray<double> x({1.0, 2.0, 3.0, 4.0}, "cm");
      units::Quantity<double> y(2.5, "s");
      units::QuantityArray<double> z = x / y;
      assert(z.nelements() == 4);
      assert(internal::values_eq(z.value()[1], 0.8));
      assert(z.unitsStr() == "cm*(s**-1)");
    }
  
    ////////////////////////////////////////////////////////////////////////////
    // 3. Comparison
    {
      units::Quantity<double> x(1.0, "cm");
      units::Quantity<double> y(1.0, "mm");
      assert(x > y);
    }

    ////////////////////////////////////////////////////////////////////////////
    // 4. Explicit conversion
    {
      units::Quantity<double> x(1.0, "cm");

      // In-place conversion
      x.convert_to("m");
      assert(internal::values_eq(x.value(), 0.01));
      assert(x.unitsStr() == "m");

      // Copy conversion
      units::Quantity<double> y = x.as("cm");
      assert(internal::values_eq(x.value(), 0.01));
      assert(x.unitsStr() == "m");
      assert(internal::values_eq(y.value(), 1.0));
      assert(y.unitsStr() == "cm");
    }
    
    ////////////////////////////////////////////////////////////////////////////
    // 4. Unit system conversion
    {
      units::Units cgs("cm g s");
      units::Units mks("m kg s");
      units::Quantity<double> x(1.0, "cm*(min**-1)");
      units::Quantity<double> y = x.as_units_system(cgs);
      assert(internal::values_eq(y.value(), 0.016666666666666666));
      assert(y.unitsStr() == "cm*(s**-1)");
      units::Quantity<double> z = x.as_units_system(mks);
      assert(internal::values_eq(z.value(), 0.00016666666666666666));
      assert(z.unitsStr() == "m*(s**-1)");
    }
    
    return 0;
}

#else // DISABLE_YGGDRASIL_RAPIDJSON

int main(int, char*[]) {
  return 0;
}

#endif // DISABLE_YGGDRASIL_RAPIDJSON
