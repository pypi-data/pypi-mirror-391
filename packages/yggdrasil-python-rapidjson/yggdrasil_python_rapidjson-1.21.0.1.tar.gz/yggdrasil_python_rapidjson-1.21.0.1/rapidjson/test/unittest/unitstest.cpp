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
#include "yggdrasil_rapidjson/units.h"
#include "yggdrasil_rapidjson/encodings.h"
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

#define CHECK_QUANTITY_EQUIVALENCE(a, b, expected)			\
  {									\
    if (a.equivalent_to(b) != expected) {				\
      std::cerr << "a = " << a << ", b = " << b;			\
      if (a.is_compatible(b)) {						\
	std::cerr << ", b.as(a.units) = " << b.as(a.units()) << ", a.value - b.value = " << std::abs(b.value() - a.as(b.units()).value()) << ", b.value - a.value = " << std::abs(a.value() - b.as(a.units()).value()) << ", " << internal::values_eq(b.value(), a.as(b.units()).value()) << ", " << internal::values_eq(a.value(), b.as(a.units()).value()); \
      }	else if (expected) {						\
	std::cerr << ", not compat, adim = " << a.dimension() << ", bdim = " << b.dimension(); \
      }									\
      std::cerr << std::endl;						\
    }									\
    EXPECT_TRUE(a.equivalent_to(b) == expected);			\
  }

#define CHECK_QUANTITY_DIRECT_EQUALITY(a, b, expected)			\
  {									\
    if ((a==b) != expected) {						\
      std::cerr << "a = " << a << ", b = " << b << std::endl;		\
    }									\
    EXPECT_TRUE((a==b) == expected);					\
    EXPECT_FALSE((a!=b) == expected);					\
  }

#define COMPARE_UNITS(av, au, bv, bu, expected, direct)			\
  {									\
    units::Quantity<double> a(av, au);			\
    units::Quantity<double> b(bv, bu);			\
    CHECK_QUANTITY_EQUIVALENCE(a, b, expected);				\
    CHECK_QUANTITY_EQUIVALENCE(b, a, expected);				\
    CHECK_QUANTITY_DIRECT_EQUALITY(a, b, direct);			\
    CHECK_QUANTITY_DIRECT_EQUALITY(b, a, direct);			\
    if (expected) {							\
      EXPECT_TRUE(internal::values_eq(a.value(), b.as(a.units()).value())); \
      EXPECT_TRUE(internal::values_eq(b.value(), a.as(b.units()).value())); \
    }									\
  }

TEST(Unit, Base) {
  units::Quantity<double> x(1.0, "kg");
  std::cout << "x = " << x << ", dim = " << x.units().dimension() << std::endl;
  COMPARE_UNITS(1.0, "g", 0.001, "kg", true, false);
  COMPARE_UNITS(1.0, "gram", 0.001, "kilogram", true, false);
  COMPARE_UNITS(1.0, "grams", 0.001, "kilograms", true, false);
  COMPARE_UNITS(1.0, "g", 1.0, "kg", false, false);
  COMPARE_UNITS(1.0, "cm", 1.0, "g", false, false);
  COMPARE_UNITS(1.0, "cm", 1.0, "cm/s", false, false);
  COMPARE_UNITS(1.0, "g**2", 1e-6, "kg^2", true, false);
  COMPARE_UNITS(1.0, "hp", 745.69987158227022, "W", true, false);
  COMPARE_UNITS(1.0, "km/s", 2236.936292054402, "mi/hr", true, false);
  COMPARE_UNITS(0.0, "°C", 273.15, "K", true, false);
  COMPARE_UNITS(32.0, "°F", 0.0, "°C", true, false);
  COMPARE_UNITS(41.0, "°F", 5.0, "°C", true, false);
  COMPARE_UNITS(1.0, "Δ°C", 1.0, "ΔK", true, false);
  COMPARE_UNITS(1.0, "Δ°C", 9.0/5.0, "Δ°F", true, false);
  COMPARE_UNITS(1.0, "km s", 1.0, "km*s", true, true);
  COMPARE_UNITS(1.0, "g**(1+1)", 1.0, "g^2", true, true);
  COMPARE_UNITS(1.0, "g**(3-1)", 1.0, "g^2", true, true);
  COMPARE_UNITS(1.0, "g**(6/3)", 1.0, "g^2", true, true);
  COMPARE_UNITS(1.0, "g**(1*2)", 1.0, "g^2", true, true);
  COMPARE_UNITS(1.0, "(km**2)(s**-1)", 1.0, "km**2/s", true, true);
  COMPARE_UNITS(1.0, "(km*A)**2/((s**2)(g**3))", 1.0, "(km^2)*(A^2)*(s^-2)*(g^-3)", true, true);
  COMPARE_UNITS(1.0, "%", 1.0, "percent", true, true);
  COMPARE_UNITS(0.01, "100%", 1.0, "percent", true, false);
  const UTF8<char>::Ch test_units[] = "(km*A)**2/((s**2)(g**3))";
  units::Units(test_units, strlen(test_units), true);
};

#define UNIT_OPERATOR_BASE(au, op, bu, cu, factor)			\
  {									\
    units::Quantity<double> a(1.0, #au);				\
    units::Quantity<double> b(1.0, #bu);				\
    units::Quantity<double> c(factor, #cu);				\
    units::Quantity<double> d = a op b;					\
    CHECK_QUANTITY_EQUIVALENCE(c, d, true);				\
    CHECK_QUANTITY_DIRECT_EQUALITY(c, d, true);				\
  }
#define UNIT_OPERATOR(au, op, bu, cu)					\
  UNIT_OPERATOR_BASE(au, op, bu, cu, 1.0)

TEST(Unit, MultDiv) {
  UNIT_OPERATOR(kg, *, kg, kg**2);
  UNIT_OPERATOR(kg, *, cm, kg*cm);
  UNIT_OPERATOR(kg, /, cm, kg/cm);
  UNIT_OPERATOR(kg, *, cm**-1, kg/cm);
  UNIT_OPERATOR(kg, /, cm**-1, kg*cm);
  UNIT_OPERATOR(cm/s, *, kg, kg*cm/s);
  UNIT_OPERATOR_BASE(hr, /, day, n/a, 0.041666666666666664);
};

TEST(Unit, AddSubtract) {
  UNIT_OPERATOR_BASE(degC, +, degC, degC, 2);
  UNIT_OPERATOR_BASE(degC, -, degC, ΔdegC, 0);
  UNIT_OPERATOR_BASE(degC, +, ΔK, degC, 2);
  UNIT_OPERATOR_BASE(ΔdegC, +, K, degC, -271.15);
  UNIT_OPERATOR_BASE(degC, -, K, ΔdegC, 273.15);
  UNIT_OPERATOR_BASE(K, -, degC, ΔK, -273.15);
};

TEST(Unit, Exponent) {
  units::Quantity<double> a(1.0, "kg");
  units::Quantity<double> b(1.0, "kg**2");
  units::Quantity<double> c(1.0, "kg^2");
  units::Quantity<double> d = a.pow(2);
  units::Quantity<double> e(1.0, "kg2");
  CHECK_QUANTITY_EQUIVALENCE(d, b, true);
  CHECK_QUANTITY_EQUIVALENCE(d, c, true);
  CHECK_QUANTITY_EQUIVALENCE(e, b, true);
  units::Quantity<double> x(1.0, "g2 km s-2");
  units::Quantity<double> y(1.0, "(g**2)*km*(s**-2)");
  CHECK_QUANTITY_EQUIVALENCE(x, y, true);
};

#if defined(_MSC_VER) || defined(__clang__)
YGGDRASIL_RAPIDJSON_DIAG_POP
#endif

#endif // DISABLE_YGGDRASIL_RAPIDJSON
