#ifndef YGGDRASIL_RAPIDJSON_UNITS_H_
#define YGGDRASIL_RAPIDJSON_UNITS_H_

#include "encodings.h"
#include "stream.h"
#include "stringbuffer.h"
#include "internal/meta.h"
#include "internal/strfunc.h"
#include "precision.h"
#include "yggdrasil_rapidjson.h"
#include <wchar.h>
#include <locale.h>
#include <map>
#include <vector>
#include <set>
#include <iostream>
#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>

#if defined(__GNUC__) || defined(__clang__)
#define UNIT_TYPE \
  static double __attribute__((unused))
#else
#define UNIT_TYPE \
  static double
#endif

YGGDRASIL_RAPIDJSON_NAMESPACE_BEGIN

#ifndef DISABLE_YGGDRASIL_RAPIDJSON

#if YGGDRASIL_RAPIDJSON_HAS_CXX11
#define OVERRIDE_CXX11 override
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
#define OVERRIDE_CXX11
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11

namespace units {

  enum DeltaFlag {
    kNoDelta,
    kInactiveDelta,
    kActiveDelta
  };

  namespace constants {
    
    // Elementary masses
    UNIT_TYPE mass_electron_kg = 9.10938291e-31;
    UNIT_TYPE amu_kg = 1.660538921e-27;
    UNIT_TYPE amu_grams = amu_kg * 1.0e3;
    UNIT_TYPE mass_hydrogen_kg = 1.007947 * amu_kg;
    // UNIT_TYPE mass_proton_kg = 1.672623110e-27;

    // Solar values (see Mamajek 2012)
    // https://sites.google.com/site/mamajeksstarnotes/bc-scale
    UNIT_TYPE mass_sun_kg = 1.98841586e30;
    UNIT_TYPE temp_sun_kelvin = 5870.0;
    UNIT_TYPE luminosity_sun_watts = 3.8270e26;

    // Consistent with solar abundances used in Cloudy
    UNIT_TYPE metallicity_sun = 0.01295;

    // Conversion Factors:  X au * mpc_per_au = Y mpc
    // length
    // UNIT_TYPE mpc_per_mpc = 1e0;
    UNIT_TYPE mpc_per_kpc = 1e-3;
    UNIT_TYPE mpc_per_pc = 1e-6;
    UNIT_TYPE mpc_per_au = 4.84813682e-12;
    UNIT_TYPE mpc_per_rsun = 2.253962e-14;
    UNIT_TYPE mpc_per_rearth = 2.06470307893e-16;
    UNIT_TYPE mpc_per_rjup = 2.26566120943e-15;
    UNIT_TYPE mpc_per_miles = 5.21552871e-20;
    UNIT_TYPE mpc_per_km = 3.24077929e-20;
    UNIT_TYPE mpc_per_m = 3.24077929e-23;
    UNIT_TYPE kpc_per_m = mpc_per_m / mpc_per_kpc;
    UNIT_TYPE pc_per_m = mpc_per_m / mpc_per_pc;
    UNIT_TYPE km_per_pc = 3.08567758e13;
    // UNIT_TYPE cm_per_pc = 3.08567758e18;
    // UNIT_TYPE cm_per_mpc = 3.08567758e21;
    UNIT_TYPE km_per_m = 1e-3;
    UNIT_TYPE km_per_cm = 1e-5;
    UNIT_TYPE m_per_cm = 1e-2;
    UNIT_TYPE ly_per_m = 1.05702341e-16;
    UNIT_TYPE rsun_per_m = 1.4378145e-9;
    UNIT_TYPE rearth_per_m = 1.56961033e-7;  // Mean (volumetric) radius
    UNIT_TYPE rjup_per_m = 1.43039006737e-8;  // Mean (volumetric) radius
    UNIT_TYPE au_per_m = 6.68458712e-12;
    UNIT_TYPE ang_per_m = 1.0e10;

    // UNIT_TYPE m_per_fpc = 0.0324077929;

    UNIT_TYPE kpc_per_mpc = 1.0 / mpc_per_kpc;
    UNIT_TYPE pc_per_mpc = 1.0 / mpc_per_pc;
    UNIT_TYPE au_per_mpc = 1.0 / mpc_per_au;
    UNIT_TYPE rsun_per_mpc = 1.0 / mpc_per_rsun;
    UNIT_TYPE rearth_per_mpc = 1.0 / mpc_per_rearth;
    UNIT_TYPE rjup_per_mpc = 1.0 / mpc_per_rjup;
    UNIT_TYPE miles_per_mpc = 1.0 / mpc_per_miles;
    UNIT_TYPE km_per_mpc = 1.0 / mpc_per_km;
    UNIT_TYPE m_per_mpc = 1.0 / mpc_per_m;
    UNIT_TYPE m_per_kpc = 1.0 / kpc_per_m;
    UNIT_TYPE m_per_km = 1.0 / km_per_m;
    UNIT_TYPE cm_per_km = 1.0 / km_per_cm;
    UNIT_TYPE cm_per_m = 1.0 / m_per_cm;
    UNIT_TYPE pc_per_km = 1.0 / km_per_pc;
    UNIT_TYPE m_per_pc = 1.0 / pc_per_m;
    UNIT_TYPE m_per_ly = 1.0 / ly_per_m;
    UNIT_TYPE m_per_rsun = 1.0 / rsun_per_m;
    UNIT_TYPE m_per_rearth = 1.0 / rearth_per_m;
    UNIT_TYPE m_per_rjup = 1.0 / rjup_per_m;
    UNIT_TYPE m_per_au = 1.0 / au_per_m;
    UNIT_TYPE m_per_ang = 1.0 / ang_per_m;

    // time
    // "IAU Style Manual" by G.A. Wilkins, Comm. 5, in IAU Transactions XXB (1989)
    // UNIT_TYPE sec_per_Gyr = 31.5576e15;
    // UNIT_TYPE sec_per_Myr = 31.5576e12;
    // UNIT_TYPE sec_per_kyr = 31.5576e9;
    UNIT_TYPE sec_per_year = 31.5576e6;
    UNIT_TYPE sec_per_day = 86400.0;
    UNIT_TYPE sec_per_hr = 3600.0;
    UNIT_TYPE sec_per_min = 60.0;
    // UNIT_TYPE day_per_year = 365.25;

    // velocities, accelerations
    UNIT_TYPE speed_of_light_m_per_s = 2.99792458e8;
    UNIT_TYPE speed_of_light_cm_per_s = speed_of_light_m_per_s * 100.0;
    UNIT_TYPE standard_gravity_m_per_s2 = 9.80665;

    // some constants
    UNIT_TYPE newton_mks = 6.67408e-11;
    UNIT_TYPE planck_mks = 6.62606957e-34;
    // permeability of Free Space
    UNIT_TYPE mu_0 = 4.0e-7 * M_PI;
    // permittivity of Free Space
    UNIT_TYPE eps_0 = 1.0 / (pow(speed_of_light_m_per_s, 2) * mu_0);
    // UNIT_TYPE avogadros_number = 6.02214085774e23;

    // temperature / energy
    UNIT_TYPE boltzmann_constant_J_per_K = 1.3806488e-23;
    UNIT_TYPE erg_per_eV = 1.602176562e-12;
    UNIT_TYPE J_per_eV = erg_per_eV * 1.0e-7;
    UNIT_TYPE erg_per_keV = erg_per_eV * 1.0e3;
    UNIT_TYPE J_per_keV = J_per_eV * 1.0e3;
    UNIT_TYPE K_per_keV = J_per_keV / boltzmann_constant_J_per_K;
    UNIT_TYPE keV_per_K = 1.0 / K_per_keV;
    UNIT_TYPE keV_per_erg = 1.0 / erg_per_keV;
    UNIT_TYPE eV_per_erg = 1.0 / erg_per_eV;
    UNIT_TYPE kelvin_per_rankine = 5.0 / 9.0;
    UNIT_TYPE watt_per_horsepower = 745.69987158227022;
    UNIT_TYPE celcius_zero_kelvin = -273.15;
    UNIT_TYPE farenheit_zero_celcius = 32.0;
    UNIT_TYPE farenheit_zero_kelvin = celcius_zero_kelvin / kelvin_per_rankine + farenheit_zero_celcius;
    // UNIT_TYPE erg_per_s_per_watt = 1e7;

    // Solar System masses
    // Standish, E.M. (1995) "Report of the IAU WGAS Sub-Group on Numerical
    // Standards", in Highlights of Astronomy (I. Appenzeller, ed.), Table 1,
    // Kluwer Academic Publishers, Dordrecht.
    // REMARK: following masses include whole systems (planet + moons)
    UNIT_TYPE mass_jupiter_kg = mass_sun_kg / 1047.3486;
    UNIT_TYPE mass_mercury_kg = mass_sun_kg / 6023600.0;
    UNIT_TYPE mass_venus_kg = mass_sun_kg / 408523.71;
    UNIT_TYPE mass_earth_kg = mass_sun_kg / 328900.56;
    UNIT_TYPE mass_mars_kg = mass_sun_kg / 3098708.0;
    UNIT_TYPE mass_saturn_kg = mass_sun_kg / 3497.898;
    UNIT_TYPE mass_uranus_kg = mass_sun_kg / 22902.98;
    UNIT_TYPE mass_neptune_kg = mass_sun_kg / 19412.24;

    // flux
    UNIT_TYPE jansky_mks = 1.0e-26;
    // Cosmological constants
    // Calculated with H = 100 km/s/Mpc, value given in units of h^2 g cm^-3
    // Multiply by h^2 to get the critical density in units of g cm^-3
    // UNIT_TYPE rho_crit_g_cm3_h2 = 1.8788e-29;
    // UNIT_TYPE primordial_H_mass_fraction = 0.76;

    // Misc. Approximations
    // UNIT_TYPE mass_mean_atomic_cosmology = 1.22;
    // UNIT_TYPE mass_mean_atomic_galactic = 2.3;

    // Miscellaneous
    // UNIT_TYPE HUGE = 1.0e90;
    // UNIT_TYPE TINY = 1.0e-40;

    // Planck units
    UNIT_TYPE hbar_mks = 0.5 * planck_mks / M_PI;
    UNIT_TYPE planck_mass_kg = sqrt(hbar_mks * speed_of_light_m_per_s / newton_mks);
    UNIT_TYPE planck_length_m = sqrt(hbar_mks * newton_mks / pow(speed_of_light_m_per_s, 3));
    UNIT_TYPE planck_time_s = planck_length_m / speed_of_light_m_per_s;
    UNIT_TYPE planck_energy_J = planck_mass_kg * speed_of_light_m_per_s * speed_of_light_m_per_s;
    UNIT_TYPE planck_temperature_K = planck_energy_J / boltzmann_constant_J_per_K;
    UNIT_TYPE planck_charge_C = sqrt(4.0 * M_PI * eps_0 * hbar_mks * speed_of_light_m_per_s);

    // Imperial and other non-metric units
    UNIT_TYPE kg_per_pound = 0.45359237;
    UNIT_TYPE pascal_per_atm = 101325.0;
    UNIT_TYPE m_per_inch = 0.0254;
    UNIT_TYPE m_per_ft = 0.3048;

    // logarithmic units
    // IEC 60027-3: https://webstore.iec.ch/publication/94
    // NIST Special Publication 811: https://www.nist.gov/pml/special-publication-811
    // UNIT_TYPE neper_per_bel = log(10) / 2;
  }

  enum BaseDimension {
    kLengthUnit = 0,
    kMassUnit = 1,
    kTimeUnit = 2,
    kElectricCurrentUnit = 3,
    kTemperatureUnit = 4,
    kNumberUnit = 5,
    kLuminousIntensityUnit = 6,
    kAngleUnit = 7,
    kDimensionlessUnit = 8
  };

  template<typename Ch>
  std::vector<std::basic_string<Ch> > pack_strings(const Ch* first...) {
    std::vector<std::basic_string<Ch> > out;
    out.push_back(first);
    va_list args;
    va_start(args, first);
    while (true) {
      Ch* i = va_arg(args, Ch*);
      if (i == NULL) break;
      out.push_back(i);
    }
    va_end(args);
    return out;
  }
  
#define PACK_LUT(x, args) (void*)(new x args)

  template<typename T>
  class CachedLUT {
  public:
    CachedLUT(void* first...) :
      base_(), cache_() {
      if (!first) return;
      T* firstT = (T*)first;
      base_.push_back(*firstT);
      va_list args;
      va_start(args, first);
      _add_from_va(args);
      va_end(args);
      delete firstT;
    }
    CachedLUT(const std::vector<T>* base...) :
      base_(), cache_() {
      va_list args;
      va_start(args, base);
      _add_from_va(args);
      va_end(args);
      base_.insert(base_.end(), base->begin(), base->end());
    }
    ~CachedLUT() {
      for (std::map<int32_t, void*>::iterator it = cache_.begin(); it != cache_.end(); it++)
        free(it->second);
    }
  private:
    void _add_from_va(va_list args) {
      while (true) {
	T* i = (T*)va_arg(args, void*);
	if (!i) return;
	base_.push_back(*i);
	delete i;
      }
    }
  public:
    template<typename T2>
    const std::vector<T2>* get(YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<T, T2>)))
    { return &base_; }
    template<typename T2>
    const std::vector<T2>* get(YGGDRASIL_RAPIDJSON_DISABLEIF((internal::IsSame<T, T2>))) {
      int32_t idx = T2::EncodingType::HashCode();
      std::map<int32_t, void*>::iterator match = cache_.find(idx);
      if (match == cache_.end()) {
        std::vector<T2>* new_entry = (std::vector<T2>*)malloc(sizeof(std::vector<T2*>));
	YGGDRASIL_RAPIDJSON_ASSERT(new_entry);
        new (new_entry) std::vector<T2>();
	// new_entry[0] = std::vector<T2>();
        for (typename std::vector<T>::const_iterator it = base_.begin(); it != base_.end(); it++)
          new_entry->push_back(it->template transcode<typename T2::EncodingType>());
	cache_[idx] = (void*)(new_entry);
        return new_entry;
      } else {
	return (std::vector<T2>*)(match->second);
      }
    }
  private:
    std::vector<T> base_;
    std::map<int32_t, void*> cache_;
  };

// Forward declarations
template<typename Encoding>
class GenericUnit;
template<typename Encoding>
class GenericUnits;
template<typename T, typename Encoding>
class GenericQuantity;
template<typename T, typename Encoding>
class GenericQuantityArray;

class Dimension {
private:
  struct DimArray { double values[8]; };
  static DimArray const& packArray() {
    static DimArray const values = {
      {0, 0, 0, 0, 0, 0, 0, 0} };
    return values;
  }
  static DimArray packArray(const double powers[8]) {
    DimArray values = {
      {powers[0], powers[1], powers[2], powers[3], powers[4], powers[5],
       powers[6], powers[7]} };
    return values;
  }
  static DimArray packArray(const double p0, const double p1, const double p2,
			    const double p3, const double p4, const double p5,
			    const double p6, const double p7) {
    DimArray values = {p0, p1, p2, p3, p4, p5, p6, p7};
    return values;
  }
public:
  Dimension(const BaseDimension k, const double power=1.0) :
    powers_(packArray()) {
    if (k != kDimensionlessUnit)
      powers_.values[k] = power;
  }
  Dimension(const double L = 0.0,
	    const double M = 0.0,
	    const double T = 0.0,
	    const double EC = 0.0,
	    const double Temp = 0.0,
	    const double N = 0.0,
	    const double LI = 0.0,
	    const double A = 0.0) :
    powers_(packArray(L, M, T, EC, Temp, N, LI, A)) {}
  Dimension(const double powers[8]) : powers_(packArray(powers)) {}
  Dimension operator*(const Dimension& x) const {
    double new_powers[8];
    for (size_t i = 0; i < 8; i++)
      new_powers[i] = powers_.values[i] + x.powers_.values[i];
    return Dimension(new_powers);
  }
  Dimension operator/(const Dimension& x) const {
    double new_powers[8];
    for (size_t i = 0; i < 8; i++)
      new_powers[i] = powers_.values[i] - x.powers_.values[i];
    return Dimension(new_powers);
  }
  void pow_inplace(const double x) {
    for (size_t i = 0; i < 8; i++)
      powers_.values[i] = powers_.values[i] * x;
  }
  Dimension pow(const double x) const {
    Dimension new_dim = Dimension(*this);
    new_dim.pow_inplace(x);
    return new_dim;
  }
  bool operator==(const Dimension& x) const {
    for (size_t i = 0; i < 8; i++)
      if (!(internal::values_eq(powers_.values[i], x.powers_.values[i])))
	return false;
    return true;
  }
  bool operator!=(const Dimension& x) const { return (!(*this == x)); }
  int ndim() const {
    int ndim = 0;
    for (size_t i = 0; i < 8; i++)
      if (!(internal::values_eq(powers_.values[i], 0.0)))
	ndim++;
    return ndim;
  }
  bool is_irreducible() const { return (ndim() == 1); }
  bool is_dimensionless() const { return (ndim() == 0); }
  std::vector<Dimension> reduced() const {
    std::vector<Dimension> out;
    for (size_t i = 0; i < 8; i++)
      if (!(internal::values_eq(powers_.values[i], 0.0)))
	out.push_back(Dimension((BaseDimension)i, powers_.values[i]));
    return out;
  }
protected:
  DimArray powers_;
  template<typename Ch>
  friend std::basic_ostream<Ch> & operator << (std::basic_ostream<Ch> &os, const Dimension &x);
};
template<typename Ch>
inline std::basic_ostream<Ch> & operator << (std::basic_ostream<Ch>& os, const Dimension &x) {
  os << '[' << x.powers_.values[0];
  for (size_t i = 1; i < 8; i++)
    os << ',' << x.powers_.values[i];
  os << ']';
  return os;
}

namespace dimensions {
  // Base
  static Dimension dimensionless(0, 0);
  static Dimension length(1, 0);
  static Dimension mass(0, 1);
  static Dimension time(0, 0, 1);
  static Dimension current(0, 0, 0, 1);
  static Dimension temperature(0, 0, 0, 0, 1);
  static Dimension number(0, 0, 0, 0, 0, 1);
  static Dimension luminous_intensity(0, 0, 0, 0, 0, 0, 1);
  static Dimension angle(0, 0, 0, 0, 0, 0, 0, 1);
  // Derived
  static Dimension rate = dimensionless / time;
  static Dimension frequency = rate;
  static Dimension spatial_frequency = dimensionless / length;
  static Dimension solid_angle = angle * angle;
  static Dimension velocity = length / time;
  static Dimension acceleration = length / time.pow(2);
  static Dimension jerk = length / time.pow(3);
  static Dimension snap = length / time.pow(4);
  static Dimension crackle = length / time.pow(5);
  static Dimension pop = length / time.pow(6);
  static Dimension area = length * length;
  static Dimension volume = area * length;
  static Dimension momentum = mass * velocity;
  static Dimension force = mass * acceleration;
  static Dimension pressure = force / area;
  static Dimension energy = force * length;
  static Dimension power = energy / time;
  static Dimension flux = power / area;
  static Dimension specific_flux = flux / rate;
  static Dimension number_density = number / volume;
  static Dimension density = mass / volume;
  static Dimension angular_momentum = mass * length * velocity;
  static Dimension specific_energy = energy / mass;
  static Dimension count_flux = number / (area * time);
  static Dimension count_intensity = count_flux / solid_angle;
  static Dimension luminous_flux = luminous_intensity * solid_angle;
  static Dimension luminance = luminous_intensity / area;
  static Dimension charge_cgs = (energy * length).pow(2);
  static Dimension current_cgs = charge_cgs / time;
  static Dimension electric_field_cgs = charge_cgs / (length.pow(2));
  static Dimension magnetic_field_cgs = electric_field_cgs;
  static Dimension electric_potential_cgs = energy / charge_cgs;
  static Dimension resistance_cgs = electric_potential_cgs / current_cgs;
  static Dimension magnetic_flux_cgs = magnetic_field_cgs * area;
  static Dimension charge = current * time;
  static Dimension electric_field = force / charge;
  static Dimension magnetic_field = electric_field / velocity;
  static Dimension electric_potential = energy / charge;
  static Dimension resistance = electric_potential / current;
  static Dimension capacitance = charge / electric_potential;
  static Dimension magnetic_flux = magnetic_field * area;
  static Dimension inductance = magnetic_flux / current;
} // namespace dimensions

template<typename T1>
double char_to_double(const std::basic_string<T1>& x,
		      YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<T1,char>))) {
  return atof(x.c_str());
}
template<typename T1>
double char_to_double(const std::basic_string<T1>& x,
		      YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<T1,wchar_t>))) {
  return wcstod(x.c_str(), NULL);
}
template<typename SourceEncoding, typename DestEncoding>
const std::basic_string<typename DestEncoding::Ch> convert_chars(const std::basic_string<typename SourceEncoding::Ch>& x,
								 YGGDRASIL_RAPIDJSON_ENABLEIF((internal::IsSame<SourceEncoding, DestEncoding>))) {
  return x;
}
  
template<typename SourceEncoding, typename DestEncoding>
const std::basic_string<typename DestEncoding::Ch> convert_chars(const std::basic_string<typename SourceEncoding::Ch>& x,
								 YGGDRASIL_RAPIDJSON_DISABLEIF((internal::IsSame<SourceEncoding, DestEncoding>))) {
  GenericStringStream<SourceEncoding> src(x.c_str());
  GenericStringBuffer<DestEncoding> dst;
  if (DestEncoding::supportUnicode)
    PutReserve(dst, x.size() * 6);
  else
    PutReserve(dst, x.size() * 12);
  while (YGGDRASIL_RAPIDJSON_LIKELY(src.Tell() < x.size())) {
    YGGDRASIL_RAPIDJSON_ASSERT(src.Peek() != '\0');
    Transcoder<SourceEncoding, DestEncoding>::Transcode(src, dst);
  }
  std::basic_string<typename DestEncoding::Ch> out(dst.GetString(), dst.GetLength());
  return out;
}
								 
//! GenericUnit prefix.
template<typename Encoding>
class GenericUnitPrefix {
public:
  typedef Encoding EncodingType;    //!< Encoding type from template parameter.
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
  GenericUnitPrefix() : abbr(), factor(1.0), name() {}
  GenericUnitPrefix(const Ch* abbr0, const double& factor0, const Ch* name0) :
    abbr(abbr0), factor(factor0), name(name0) {}
  GenericUnitPrefix(const std::basic_string<Ch> abbr0, const double& factor0,
		    const std::basic_string<Ch> name0) :
    abbr(abbr0), factor(factor0), name(name0) {}
#if YGGDRASIL_RAPIDJSON_HAS_CXX20
  GenericUnitPrefix(const char8_t* abbr0, const double& factor0, const Ch* name0) :
    abbr(reinterpret_cast<const char*>(abbr0)),
    factor(factor0), name(name0) {}
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX20
  //! Abbreviation associated with the prefix.
  std::basic_string<Ch> abbr;
  //! Factor that the prefix implies.
  double factor;
  //! Full name associated with the prefix.
  std::basic_string<Ch> name;

  //! \brief Determine if this unit prefix is identical to another.
  //! \param x Unit prefix for comparison.
  //! \return true if the unit prefixes are identical.
  bool operator==(const GenericUnitPrefix& x) const {
    if (abbr != x.abbr) return false;
    return internal::values_eq(factor, x.factor);
  }
  //! \brief Determine if this unit prefix is not identical to another.
  //! \param x Unit prefix for comparison.
  //! \return true if the unit prefixes are not identical.
  bool operator!=(const GenericUnitPrefix& x) const { return (!(*this == x)); }

  //! \brief Create a copy of the prefix with a different encoding.
  //! \tparam DestEncoding Encoding that the copy should use.
  //! \return Copy w/ DestEncoding.
  template<typename DestEncoding>
  GenericUnitPrefix<DestEncoding> transcode() const {
    return GenericUnitPrefix<DestEncoding>(convert_chars<Encoding, DestEncoding>(abbr),
					   factor,
					   convert_chars<Encoding, DestEncoding>(name));
  }

  //! \brief Write the prefix to an output stream with class information.
  //! \param os Output stream.
  template<typename Ch2>
  void display(std::basic_ostream<Ch2>& os) const {
    os << 'G' << 'e' << 'n' << 'e' << 'r' << 'i' << 'c' << 'U' <<
      'n' << 'i' << 't' << 'P' << 'r' << 'e' << 'f' << 'i' << 'x' << '('
       << convert_chars<Encoding,UTF8<Ch2> >(name)
       << ',' << ' ' << convert_chars<Encoding,UTF8<Ch2> >(abbr)
       << ',' << ' ' << factor << ')';
  }
  
  friend class GenericUnit<Encoding>;
  template<typename Ch2, typename Enc2>
  friend std::basic_ostream<Ch2> & operator << (std::basic_ostream<Ch2>& os, const GenericUnitPrefix<Enc2> &x);
};
template<typename Ch, typename Encoding>
inline std::basic_ostream<Ch> & operator << (std::basic_ostream<Ch>& os, const GenericUnitPrefix<Encoding> &x) {
  if (x.abbr.size() > 0)
    os << convert_chars<Encoding,UTF8<Ch> >(x.abbr);
  return os;
}

  //! Generic UnitPrefix with UTF8 encoding
  typedef GenericUnitPrefix<UTF8<char> > UnitPrefix;

#define PACK_PREFIX(...) PACK_LUT(UnitPrefix, (__VA_ARGS__))
  
  // This dictionary formatting from magnitude package (secondarily via unyt), credit to Juan Reyero.
  static CachedLUT<UnitPrefix> _unit_prefixes(
      PACK_PREFIX("Y", 1e24, "yotta"),
      PACK_PREFIX("Z", 1e21, "zetta"),
      PACK_PREFIX("E", 1e18, "exa"),
      PACK_PREFIX("P", 1e15, "peta"),
      PACK_PREFIX("T", 1e12, "tera"),
      PACK_PREFIX("G", 1e9, "giga"),
      PACK_PREFIX("M", 1e6, "mega"),
      PACK_PREFIX("k", 1e3, "kilo"),
      PACK_PREFIX("h", 1e2, "hecto"),
      PACK_PREFIX("da", 1e1, "deca"),
      PACK_PREFIX("d", 1e-1, "deci"),
      PACK_PREFIX("c", 1e-2, "centi"),
      PACK_PREFIX("m", 1e-3, "mili"),
      PACK_PREFIX("u", 1e-6, "micro"),
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
      PACK_PREFIX(u8"\u00b5", 1e-6, "micro"),  // ('MICRO SIGN' U+00B5)
      PACK_PREFIX(u8"\u03bc", 1e-6, "micro"),  // ('GREEK SMALL LETTER MU' U+03BC)
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
      PACK_PREFIX("\u00b5", 1e-6, "micro"),  // ('MICRO SIGN' U+00B5)
      PACK_PREFIX("\u03bc", 1e-6, "micro"),  // ('GREEK SMALL LETTER MU' U+03BC)
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
      PACK_PREFIX("n", 1e-9, "nano"),
      PACK_PREFIX("p", 1e-12, "pico"),
      PACK_PREFIX("f", 1e-15, "femto"),
      PACK_PREFIX("a", 1e-18, "atto"),
      PACK_PREFIX("z", 1e-21, "zepto"),
      PACK_PREFIX("y", 1e-24, "yocto"),
      (void*)NULL
    );

#undef PACK_PREFIX

//! GenericUnit.
template<typename Encoding>
class GenericUnit {
public:
  typedef Encoding EncodingType;    //!< Encoding type from template parameter.
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
  //! \brief Empty constructor.
  GenericUnit() :
    names_(), abbrs_(), dim_(), factor_(1.0), offset_(0.0), delta_(0), power_(1.0), prefix_() {}
  //! \brief Constructor from a look-up table.
  //! \param x Base unit.
  //! \param prefix Prefix that should be applied to the base unit.
  GenericUnit(const GenericUnit& x, const GenericUnitPrefix<Encoding>& prefix) :
    names_(x.names_), abbrs_(x.abbrs_), dim_(x.dim_), factor_(x.factor_), offset_(x.offset_), delta_(x.delta_), power_(x.power_), prefix_() {
    prefix_ = prefix;
    if (is_null()) {
      factor_ = std::pow(factor_, power_);
      power_ = 1.0;
    }
    _check_valid();
    YGGDRASIL_RAPIDJSON_ASSERT(_check_valid());
  }
  //! \brief Construct from a single name/abbreviation.
  //! \param name Name.
  //! \param abbr Abbreviation.
  //! \param dim Dimensions.
  //! \param factor Scale factor from the base unit system.
  //! \param offset Offset from the zero point of the base unit system.
  //! \param power Power that will be applied to the unit during conversion.
  //! \param delta Flag indicating if a unit has special handling of
  //!   differences.
  //! \param prefix Prefix that should be applied to the base unit.
  GenericUnit(const Ch* name, const Ch* abbr, const Dimension dim,
	      const double factor=1.0, const double offset=0.0,
	      const int delta=0, const double power=1.0, 
	      const GenericUnitPrefix<Encoding>& prefix=GenericUnitPrefix<Encoding>()) :
    names_(), abbrs_(), dim_(dim), factor_(factor), offset_(offset), delta_(delta), power_(power), prefix_(prefix) {
    names_.push_back(std::basic_string<Ch>(name));
    abbrs_.push_back(std::basic_string<Ch>(abbr));
    _add_plural();
    _check_valid();
    YGGDRASIL_RAPIDJSON_ASSERT(_check_valid());
  }
  //! \brief Construct from a single name/abbreviation.
  //! \param names Names.
  //! \param abbrs Abbreviations.
  //! \param dim Dimensions.
  //! \param factor Scale factor from the base unit system.
  //! \param offset Offset from the zero point of the base unit system.
  //! \param power Power that will be applied to the unit during conversion.
  //! \param delta Flag indicating if a unit has special handling of
  //!   differences.
  //! \param prefix Prefix that should be applied to the base unit.
  //! \param no_plural If true, the plural versions of the names will not be
  //!   added.
  GenericUnit(const std::vector<std::basic_string<Ch> >& names,
	      const std::vector<std::basic_string<Ch> >& abbrs,
	      const Dimension dim, const double factor=1.0, const double offset=0.0,
	      const int delta=0, const double power=1.0,
	      const GenericUnitPrefix<Encoding>& prefix=GenericUnitPrefix<Encoding>(),
	      const bool& no_plural=false) :
    names_(names), abbrs_(abbrs), dim_(dim), factor_(factor), offset_(offset), delta_(delta), power_(power), prefix_(prefix) {
    if (!no_plural) _add_plural();
    if (is_null()) {
      factor_ = std::pow(factor_, power_);
      power_ = 1.0;
    }
    _check_valid();
    YGGDRASIL_RAPIDJSON_ASSERT(_check_valid());
  }
  //! \brief Construct a unit by looking up a string in the tables of
  //!   recognized units.
  //! \param str Unit string.
  //! \param power Power that should be applied to the located unit.
  //! \param prefix Prefix that should be applied to the base unit.
  GenericUnit(const std::basic_string<Ch> str, const double& power=1.0) :
    names_(), abbrs_(), dim_(), factor_(1.0), offset_(0.0), delta_(0), power_(1.0), prefix_() {
    bool errorFlag = (!from_table(str));
    (void)errorFlag;
    power_ = power; // Base units do not have powers
    (void)str;
    if (is_null()) {
      factor_ = std::pow(factor_, power_);
      power_ = 1.0;
    }
    _check_valid();
    YGGDRASIL_RAPIDJSON_ASSERT(_check_valid());
  }
  //! \brief Set instance attributes based on an entry from one of the lookup
  //!   tables.
  //! \param found Table entry.
  //! \param If true, the unit will be marked as a difference.
  //! \param prefix Prefix that should be applied to the base unit.
  //! \return true if the unit could be initialized, false otherwise.
  bool from_table(const GenericUnit<Encoding>& found, bool delta,
		  const GenericUnitPrefix<Encoding>& prefix=GenericUnitPrefix<Encoding>()) {
    YGGDRASIL_RAPIDJSON_ASSERT((found.names_.size() > 0) && (found.abbrs_.size() > 0));
    names_.insert(names_.begin(), found.names_.begin(), found.names_.end());
    abbrs_.insert(abbrs_.begin(), found.abbrs_.begin(), found.abbrs_.end());
    YGGDRASIL_RAPIDJSON_ASSERT((names_.size() > 0) && (abbrs_.size() > 0));
    dim_ = found.dim_;
    factor_ = found.factor_;
    offset_ = found.offset_;
    delta_ = found.delta_;
    if (delta)
      delta_ = kActiveDelta;
    prefix_ = prefix;
    return true;
  }
  //! \brief Write the unit to an output stream with class information.
  //! \param os Output stream.
  template<typename Ch2>
  void display(std::basic_ostream<Ch2>& os) const {
    YGGDRASIL_RAPIDJSON_ASSERT(names_.size() > 0);
    os << 'G' << 'e' << 'n' << 'e' << 'r' << 'i' << 'c' << 'U' <<
      'n' << 'i' << 't' << '(' << '\"';
    if (delta_ == kActiveDelta)
      os << get_delta<Ch2>();
    if (prefix_.name.size() > 0)
      os << convert_chars<Encoding,UTF8<Ch2> >(prefix_.name);
    os << convert_chars<Encoding,UTF8<Ch2> >(names_[0]) << '\"' << ','
       << '\"' << dim_ << ',' << ' '
       << factor_ << ',' << ' ' << offset_ << ')' << '*' << '*' << power_;
  }
  //! \brief Get the dimensions of the unit, including the power.
  //! \return The dimensions of the unit.
  Dimension dimension() const { return dim_.pow(power_); }
  //! \brief Determine if the unit is dimensionless.
  //! \return true if the unit is dimensionless, false otherwise.
  bool is_dimensionless() const { return dim_.is_dimensionless(); }
  //! \brief Check if this unit is equal to another.
  //! \param x Unit to check against.
  //! \return true if this unit is equal to x.
  bool operator==(const GenericUnit& x) const {
    if (names_ != x.names_) return false;
    if (abbrs_ != x.abbrs_) return false;
    if (dim_ != x.dim_) return false;
    if (!(internal::values_eq(factor_, x.factor_))) return false;
    if (!(internal::values_eq(offset_, x.offset_))) return false;
    if (delta_ != x.delta_) return false;
    if (!(internal::values_eq(power_, x.power_))) return false;
    if (prefix_ != x.prefix_) return false;
    return true;
  }
  //! \brief Check if this unit is not equal to another.
  //! \param x GenericUnit to check against.
  //! \return true if this unit is not equal to x.
  bool operator!=(const GenericUnit& x) const { return (!(*this == x)); }
  //! \brief Create a copy of the unit with a different encoding.
  //! \tparam DestEncoding Encoding that the copy should use.
  //! \return Copy w/ DestEncoding.
  template<typename DestEncoding>
  GenericUnit<DestEncoding> transcode() const {
    std::vector<std::basic_string<typename DestEncoding::Ch> > names, abbrs;
    for (typename std::vector<std::basic_string<Ch> >::const_iterator it = names_.begin(); it != names_.end(); it++)
      names.push_back(convert_chars<Encoding, DestEncoding>(*it));
    for (typename std::vector<std::basic_string<Ch> >::const_iterator it = abbrs_.begin(); it != abbrs_.end(); it++)
      abbrs.push_back(convert_chars<Encoding, DestEncoding>(*it));
    return GenericUnit<DestEncoding>(names, abbrs, dim_, factor_, offset_, delta_, power_,
				     prefix_.template transcode<DestEncoding>());
  }
  //! \brief Perform power operation in place.
  //! \param x Power to raise this unit to.
  template<typename T>
  void pow_inplace(const T x) {
    if (is_null())
      factor_ = std::pow(factor_, x);
    else
      power_ = power_ * x;
    _check_valid();
    YGGDRASIL_RAPIDJSON_ASSERT(_check_valid());
  }
  //! \brief Raise this unit to a power.
  //! \param x Power to raise this unit to.
  //! \return Resulting unit.
  template<typename T>
  GenericUnit pow(const T x) const {
    GenericUnit new_unit(*this);
    new_unit.pow_inplace(x);
    return new_unit;
  }
  //! \brief Check if this unit and another have the same base unit.
  //! \param x Unit to compare this unit to.
  //! \return true if this unit and x have the same base unit.
  bool is_same_base(const GenericUnit& x) const {
    YGGDRASIL_RAPIDJSON_ASSERT(x.names_.size() > 0);
    YGGDRASIL_RAPIDJSON_ASSERT(names_.size() > 0);
    return (x.names_[0] == names_[0]);
  }
  //! \brief Check if a string matches any of the names or abbreviations
  //!   associated with this unit.
  //! \param str String to check.
  //! \return true if str matches this unit.
  bool matches(const std::basic_string<Ch> str) const {
    for (typename std::vector<std::basic_string<Ch> >::const_iterator n = names_.begin(); n != names_.end(); n++) {
      if (str.compare(*n) == 0)
	return true;
    }
    for (typename std::vector<std::basic_string<Ch> >::const_iterator n = abbrs_.begin(); n != abbrs_.end(); n++) {
      if (n->compare(str) == 0)
	return true;
    }
    return false;
  }
  //! \brief Check if a string matches any of the names or abbreviations
  //!   associated with this unit with the provided prefix added.
  //! \param str String to check.
  //! \param prefix Prefix to add when checking against the provided string.
  //! \return true if str matches this unit.
  bool matches(const std::basic_string<Ch> str,
	       const GenericUnitPrefix<Encoding>& prefix) const {
    for (typename std::vector<std::basic_string<Ch> >::const_iterator n = names_.begin(); n != names_.end(); n++) {
      if (str.compare(prefix.name + (*n)) == 0)
	return true;
    }
    for (typename std::vector<std::basic_string<Ch> >::const_iterator n = abbrs_.begin(); n != abbrs_.end(); n++)
      if (str.compare(prefix.abbr + (*n)) == 0)
	return true;
    return false;
  }
  //! \brief Check if a string matches any of the names or abbreviations
  //!   associated with this unit, checking for a partial match that allows
  //!   the possibility that there is a prefix present.
  //! \param str String to check.
  //! \param possibilities Vector to add this unit to if it matches the
  //!   end of the provided string.
  //! \return true if str matches this unit.
  bool prefix_matches(const std::basic_string<Ch> str,
		      std::vector<const GenericUnit*>& possibilities) const {
    for (typename std::vector<std::basic_string<Ch> >::const_iterator n = names_.begin(); n != names_.end(); n++) {
      if ((str.length() > n->length()) &&
	  (str.compare(str.length() - n->length(), n->length(), *n) == 0))
	possibilities.push_back(this);
    }
    for (typename std::vector<std::basic_string<Ch> >::const_iterator n = abbrs_.begin(); n != abbrs_.end(); n++) {
      if ((str.length() > n->length()) &&
	  (str.compare(str.length() - n->length(), n->length(), *n) == 0))
	possibilities.push_back(this);
    }
    return false;
  }
  //! \brief Check if this unit has a non-zero offset.
  //! \return true if this unit has a non-zero offset.
  bool has_offset() const { return (!is_difference() &&
				    !(internal::values_eq(offset_, 0.0))); }
  //! \brief Check if this unit has a power other than 1.
  //! \return true if this unit has a power other than 1.
  bool has_power() const { return (!(internal::values_eq(power_, 1.0))); }
  //! \brief Check if this unit has a factor other than 1.
  //! \return true if this unit has a factor other than 1.
  bool has_factor() const { return (!(internal::values_eq(factor_, 1.0))); }
  //! \brief Check if this unit is irreducible or a product of more than
  //!   one irreducible unit.
  //! \return true if the unit is irreducible.
  bool is_irreducible() const { return dim_.is_irreducible(); }
  //! \brief Check if the unit definition is empty.
  //! \return true if there arn't any units, false otherwise.
  bool is_empty() const { return (names_.size() == 0); }
  //! \brief Check if the unit is the dimensionless null unit.
  //! \return true if the unit is null, false otherwise.
  bool is_null() const { return ((names_.size() > 0) && (names_[0].size() == 0)); }
  //! \brief Check if this unit has a specialized difference unit.
  //! \return true if this unit has a specialized difference unit.
  bool has_difference() const { return delta_ == kInactiveDelta; }
  //! \brief Check if this unit is a specialized difference unit.
  //! \return true if this unit is a specialized difference unit.
  bool is_difference() const { return delta_ == kActiveDelta; }
  
  //! \brief Get the conversion factors necessary to convert from this
  //!   unit to another.
  //! \param x Unit to convert to.
  //! \return Two element vector where the first element is the scale factor
  //!   and the second element is the offset.
  std::vector<double> conversion_factor(const GenericUnit& x) const {
    std::vector<double> out;
    YGGDRASIL_RAPIDJSON_ASSERT(dimension() == x.dimension() &&
		     _check_valid() && x._check_valid());
    if (dimension() != x.dimension() || !_check_valid() || !x._check_valid()) {
      out.push_back(1);
      out.push_back(0);
      return out;
    }
    // If offsets == 0
    // x * a1**p = y * b1**p
    // y = x * (a1/b2)**p
    // If power == 1
    // a1 * (x - a2) = b2 * (x - b2)
    // y = [a1 * (x - a2)] / b1 + b2
    // y = (a1 / b1) * x - (a1 / b1) * a2 + b2
    // y = (a1 / b1) * [x - a2 + (b1 / a1) * b2]
    // ratio = a1 / b1
    // y = ratio * [x - (a2 - b2 / ratio)]
    std::vector<double> a = conversion_factor();
    std::vector<double> b = x.conversion_factor();
    double ratio = a[0] / b[0];
    out.push_back(ratio);
    if (is_difference())
      out.push_back(0.0);
    else
      out.push_back(a[1] - b[1] / ratio);
    return out;
  }
  //! \brief Get the conversion factors necessary to convert to/from this
  //!   unit from the base system of units.
  //! \return Two element vector where the first element is the scale factor
  //!   and the second element is the offset.
  std::vector<double> conversion_factor() const {
    std::vector<double> out;
    out.push_back(std::pow(factor_ * prefix_.factor, power_));
    out.push_back(offset_);
    return out;
  }
  //! \brief Find the unit that matches a string in one of the look up tables.
  //! \param str String to find a unit for.
  //! \return true if a unit could be located, false otherwise.
  bool from_table(const std::basic_string<Ch> str);
private:
  std::vector<std::basic_string<Ch> > names_;
  std::vector<std::basic_string<Ch> > abbrs_;
  Dimension dim_;
  double factor_;
  double offset_;
  int delta_;
  double power_;
  GenericUnitPrefix<Encoding> prefix_;

  void _add_plural() {
    size_t N = names_.size();
    std::basic_string<Ch> iname;
    for (size_t i = 0; i < N; i++) {
      iname = names_[i];
      iname.push_back('s');
      names_.push_back(iname);
    }
  }
  bool _check_valid() const {
    return (!(has_power() && has_offset()));
  }
  static const std::basic_string<Ch> get_whitespace() {
    static const Ch s[] = {' ', '\t', '\f', '\v', '\n', '\r', '\0'};
    return std::basic_string<Ch>(s);
  }
  template<typename Ch2>
  static const std::basic_string<Ch2> get_delta() {
    std::string s = "Δ";
    return convert_chars<UTF8<char>, UTF8<Ch2> >(s);
  }
  
  friend class GenericUnits<Encoding>;
  template<typename Ch2, typename Encoding2>
  friend std::basic_ostream<Ch2> & operator << (std::basic_ostream<Ch2>& os, const GenericUnit<Encoding2> &x);
};
template<typename Ch2, typename Encoding>
inline std::basic_ostream<Ch2> & operator << (std::basic_ostream<Ch2>& os, const GenericUnit<Encoding> &x) {
  bool has_factor = x.has_factor();
  bool has_power = x.has_power();
  bool has_delta = x.is_difference();
  YGGDRASIL_RAPIDJSON_ASSERT(x.abbrs_.size() > 0);
  if (has_factor && (x.abbrs_.size() > 0) && (x.abbrs_[0].size() == 0))
    os << x.factor_;
  if (has_delta)
    os << x.template get_delta<Ch2>();
  os << x.prefix_;
  if (x.abbrs_.size() > 0)
    os << convert_chars<Encoding,UTF8<Ch2> >(x.abbrs_[0]);
  if (has_power)
    os << '*' << '*' << x.power_;
  return os;
}

//! GenericUnit with UTF8 encoding
typedef GenericUnit<UTF8<char> > Unit;

//! \brief GenericUnits class.
template<typename Encoding>
class GenericUnits {
public:
  typedef Encoding EncodingType;    //!< Encoding type from template parameter.
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
  //! \brief Empty constructor.
  GenericUnits() : units_() {}
  //! \brief Initialize from a vector of units.
  //! \param units Vector of units.
  GenericUnits(const std::vector<GenericUnit<Encoding> > units) :
    units_(units) {}
  //! \brief Initialize from a string.
  //! \param str Units string.
  //! \param verbose If true, verbose information is displayed when
  //!   parsing the units string.
  GenericUnits(const std::basic_string<Ch> str, const bool& verbose=false) :
    units_() {
    GenericUnits<Encoding> new_units = parse_units(str.c_str(), str.length(), verbose);
    units_.insert(units_.begin(), new_units.units_.begin(), new_units.units_.end());
  }
  //! \brief Initialize from a string.
  //! \tparam N Number of characters in the string.
  //! \param str Units string.
  //! \param verbose If true, verbose information is displayed when
  //!   parsing the units string.
  template<size_t N>
  GenericUnits(const Ch str[N], const bool& verbose=false) :
    units_() {
    GenericUnits<Encoding> new_units = parse_units(str, N, verbose);
    units_.insert(units_.begin(), new_units.units_.begin(), new_units.units_.end());
  }
  //! \brief Initialize from a string.
  //! \param str Units string. The length is determined by assuming str is
  //!   null terminated.
  //! \param verbose If true, verbose information is displayed when
  //!   parsing the units string.
  GenericUnits(const Ch* str, const bool& verbose=false) :
    units_() {
    GenericUnits<Encoding> new_units = parse_units(str, internal::StrLen(str), verbose);
    units_.insert(units_.begin(), new_units.units_.begin(), new_units.units_.end());
  }
  //! \brief Initialize from a string.
  //! \param str Units string.
  //! \param len Number of characters in str.
  //! \param verbose If true, verbose information is displayed when
  //!   parsing the units string.
  GenericUnits(const Ch* str, const size_t len, const bool& verbose=false) :
    units_() {
    GenericUnits<Encoding> new_units = parse_units(str, len, verbose);
    units_.insert(units_.begin(), new_units.units_.begin(), new_units.units_.end());
  }
  GenericUnits(const GenericUnits<Encoding>& rhs) :
    units_() {
    units_.insert(units_.begin(), rhs.units_.begin(), rhs.units_.end());
  }
  GenericUnits<Encoding>& operator=(const GenericUnits<Encoding>& rhs) {
    units_.clear();
    this->~GenericUnits();
    new (this) GenericUnits<Encoding>(rhs);
    return *this;
  }
  //! \brief Parse a units string.
  //! \param str Units string.
  //! \param len Number of characters in str.
  //! \param verbose If true, verbose information is displayed when
  //!   parsing the units string.
  static GenericUnits parse_units(const Ch* str, const size_t len,
				  const bool verbose=false);  // Forward declaration
  //! \brief Add a unit to the unit set from a string.
  //! \param str Unit string.
  //! \returns true if the unit was added successfully, false otherwise.
  bool add_unit(const std::basic_string<Ch> str) {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    units_.emplace_back(str);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    units_.push_back(GenericUnit<Encoding>(str));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    if ((units_.end() - 1)->is_empty()) {
      units_.clear();
      return false;
    }
    if (((units_.end() - 1)->is_null()) && (units_.size() > 1))
      units_.pop_back();
    return true;
  }
  //! \brief Clear all units.
  void clear() {
    units_.clear();
  }
  //! \brief Display the units instance.
  //! \param os Output stream.
  template<typename Ch2>
  void display(std::basic_ostream<Ch2>& os) const {
    size_t i = 0;
    os << 'G' << 'e' << 'n' << 'e' << 'r' << 'i' << 'c' << 'U' <<
      'n' << 'i' << 't' << 's' << '(' << '[';
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++, i++) {
      if (i != 0) os << ',';
      it->display(os);
    }
    os << ']' << ')';
  }
  //! \brief Get the units as a string.
  //! \return Units string.
  std::basic_string<Ch> str() const {
    std::basic_stringstream<Ch> ss;
    ss << *this;
    return ss.str();
  }
  //! \brief Create a copy of the units with a different encoding.
  //! \tparam DestEncoding Encoding that the copy should use.
  //! \return Copy w/ DestEncoding.
  template<typename DestEncoding>
  GenericUnits<DestEncoding> transcode() const {
    GenericUnits<DestEncoding> out;
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++)
      out.units_.push_back(it->template transcode<DestEncoding>());
    return out;
  }
  //! \brief Get the dimensions of the units.
  //! \returns Consolidated dimensions of the units.
  Dimension dimension() const {
    Dimension out(dimensions::dimensionless);
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++)
      out = out * it->dimension();
    return out;
  }
  //! \brief Determine if the units are dimensionless.
  //! \return true if the units are dimensionless, false otherwise.
  bool is_dimensionless() const {
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++)
      if (!it->is_dimensionless())
	return false;
    return true;
  }
  //! \brief Determine if the units are null.
  //! \return true if the units are null.
  bool is_null() const {
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++)
      if (!it->is_null())
	return false;
    return true;
  }
  //! \brief Determine if another set of units are compatible and share the
  //!   same dimensions.
  //! \param x Units for comparison.
  //! \return true if the units are compatible, false otherwise.
  bool is_compatible(const GenericUnits& x) const {
    return (dimension() == x.dimension());
  }
  //! \brief Determine if this set of units is identical to another.
  //! \param x Units for comparison.
  //! \return true if the units are identical.
  bool operator==(const GenericUnits& x) const {
    if (units_.size() != x.units_.size())
      return false;
    for (size_t i = 0; i < units_.size(); i++) {
      size_t j = 0;
      for (j = 0; j < x.units_.size(); j++) {
	if (units_[i] == x.units_[j])
	  break;
      }
      if (j >= x.units_.size())
	return false;
    }
    return true;
  }
  //! \brief Determine if this set of units is not identical to another.
  //! \param x Units for comparison.
  //! \return true if the units are not identical.
  bool operator!=(const GenericUnits& x) const { return (!(*this == x)); }
  //! \brief Perform multiplication with another set of units in place.
  //! \param x Units for multiplication.
  //! \return Multiplied units.
  GenericUnits& operator*=(const GenericUnits& x) {
    double factor = 1.0;
    size_t old_size = units_.size();
    std::set<size_t> idx_remove;
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it2 = x.units_.begin(); it2 != x.units_.end(); it2++) {
      if (it2->has_offset())
	continue;
      size_t i = 0;
      for (i = 0; i < old_size; i++) {
	if (!units_[i].has_offset() && !it2->has_offset() && it2->dim_ == units_[i].dim_)
	  break;
      }
      if (i < old_size) {
	// (a1*ap*x)**a2 * (b1*bp*x)**b2
	//     = (a1**a2)*(b1**b2)*(ap**a2)*(bp**b2)*(x**(a2+b2))
	//     = (a1**a2)*(b1**b2)*(ap**-b2)*(bp**b2)*((ap*x)**(a2+b2))
	//     = (a1**-b2)*(b1**b2)*(ap**-b2)*(bp**b2)*((a1*ap*x)**(a2+b2))
	//     = (a1*ap)**-b2 * (b1*bp)**b2 * (a1*ap*x)**(a2+b2)
	if (it2->is_null()) {
	  factor *= std::pow(it2->factor_, it2->power_);
	  idx_remove.insert(i);
	} else {
	  double new_power = units_[i].power_ + it2->power_;
	  factor *= std::pow((it2->factor_ * it2->prefix_.factor) /
			     (units_[i].factor_ * units_[i].prefix_.factor),
			     it2->power_);
	  if (internal::values_eq(new_power, 0))
	    idx_remove.insert(i);
	  units_[i].power_ = new_power;
	}
      } else {
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
	units_.emplace_back(*it2);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
	units_.push_back(GenericUnit<Encoding>(*it2));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
      }
    }
    for (typename std::set<size_t>::reverse_iterator it = idx_remove.rbegin(); it != idx_remove.rend(); it++)
      units_.erase(units_.begin() + (int)(*it));
    typename std::vector<GenericUnit<Encoding> >::iterator nodim = units_.end();
    for (typename std::vector<GenericUnit<Encoding> >::iterator it = units_.begin(); it != units_.end(); it++) {
      if (it->is_null()) {
	nodim = it;
	break;
      }
    }
    if (nodim == units_.end()) {
      std::basic_string<Ch> empty;
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
      units_.emplace_back(empty);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
      units_.push_back(GenericUnit<Encoding>(empty));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
      nodim = (units_.end() - 1);
    }
    YGGDRASIL_RAPIDJSON_ASSERT(internal::values_eq(nodim->power_, 1.0));
    nodim->factor_ *= factor;
    if (!nodim->has_factor() && (units_.size() > 1))
      units_.erase(nodim);
    YGGDRASIL_RAPIDJSON_ASSERT(_check_valid());
    return *this;
  }
  bool has_factor() const {
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++) {
      if (!(it->is_null())) continue;
      if (!internal::values_eq(it->factor_, 1.0))
	return true;
    }
    return false;
  }
  double pull_factor() {
    double factor = 1.0;
    std::vector<size_t> idx_remove;
    size_t i = 0;
    for (typename std::vector<GenericUnit<Encoding> >::iterator it = units_.begin(); it != units_.end(); it++, i++) {
      if (!(it->is_null())) continue;
      factor *= std::pow(it->factor_, it->power_);
      it->factor_ = 1.0;
      if (units_.size() > 1)
	idx_remove.push_back(i);
    }
    for (typename std::vector<size_t>::reverse_iterator it = idx_remove.rbegin(); it != idx_remove.rend(); it++)
      units_.erase(units_.begin() + (int)(*it));
    return factor;
  }
  void add_factor(double factor) {
    std::basic_string<Ch> empty;
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
    units_.emplace_back(empty);
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
    units_.push_back(GenericUnit<Encoding>(empty));
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
    units_[units_.size() - 1].factor_ = factor;
  }
  //! \brief Perform multiplication with another set of units.
  //! \param x Units for multiplication.
  //! \return Multiplied units.
  friend GenericUnits operator*(GenericUnits lhs, const GenericUnits& rhs) {
    lhs *= rhs;
    return lhs;
  }
  //! \brief Perform division with another set of units in place
  //! \param x Units for division.
  //! \return Divided units.
  GenericUnits& operator/=(const GenericUnits& x) {
    return *this *= x.pow(-1);
  }
  //! \brief Perform division with another set of units.
  //! \param x Units for division.
  //! \return Divided units.
  friend GenericUnits operator/(GenericUnits lhs, const GenericUnits& rhs) {
    lhs /= rhs;
    return lhs;
  }
  //! \brief Raise these units to a power without creating a new instance.
  //! \param x Power.
  template<typename T>
  void pow_inplace(const T x) {
    for (typename std::vector<GenericUnit<Encoding> >::iterator it = units_.begin(); it != units_.end(); it++)
      it->pow_inplace(x);
  }
  //! \brief Raise these units to a power.
  //! \param x Power.
  //! \return Resulting units.
  template<typename T>
  GenericUnits pow(const T x) const {
    GenericUnits out(*this);
    out.pow_inplace(x);
    return out;
  }
  //! \brief Check if there are any units in the instance.
  //! \return true if there arn't any units, false otherwise.
  bool is_empty() const { return (units_.size() == 0); }
  //! \brief Check if the units have an offset.
  //! \return true if the units have an offset, false otherwise.
  bool has_offset() const {
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++)
      if (it->has_offset())
	return true;
    return false;
  }
  //! \brief Get the number of units with dimensions.
  //! \return Number of units with dimensions.
  size_t size() const {
    size_t out = 0;
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++)
      if (!it->is_null())
	out++;
    return out;
  }
  //! \brief Check if the units have a specialized difference unit.
  //! \return true if the units have a difference unit.
  bool has_difference() const {
    if (units_.size() != 1)
      return false;
    return units_[0].has_difference();
  }
  //! \brief Check if the units are a specialized difference unit.
  //! \return true if the units are a difference unit.
  bool is_difference() const {
    if (units_.size() != 1)
      return false;
    return units_[0].is_difference();
  }
  //! \brief Get the difference flag.
  //! \return Flag specifying if the unit has or is a difference unit.
  int get_delta() const {
    if (units_.size() != 1)
      return kNoDelta;
    return units_[0].delta_;
  }
  //! \brief Set the difference flag.
  //! \param delta New difference flag.
  void set_delta(int delta) {
    YGGDRASIL_RAPIDJSON_ASSERT(has_difference() || is_difference());
    if ((has_difference() || is_difference()) && delta > 0)
      units_[0].delta_ = delta;
  }
  //! \brief Determine the conversion factors necessary to convert quantities
  //!   with these units to another set of units.
  //! \param x Units that conversion factors should convert to.
  //! \return Array of conversion factors where the first element is the
  //!   factor that values should be multiplied by and the second element is
  //!   the offset between the zero points in this and x.
  std::vector<double> conversion_factor(const GenericUnits& x) const {
    if ((x.units_.size() == 1) && (units_.size() == 1))
      return units_[0].conversion_factor(x.units_[0]);
    std::vector<double> out;
    bool singular = (x.size() == 1 && size() == 1);
    YGGDRASIL_RAPIDJSON_ASSERT(dimension() == x.dimension() &&
		     (is_difference() || !has_offset() || singular));
    if (!(dimension() == x.dimension() &&
	  (is_difference() || !has_offset() || singular))) {
      out.push_back(1);
      out.push_back(0);
      return out;
    }
    out.push_back(1.0);
    out.push_back(0.0);
    typename std::vector<GenericUnit<Encoding> >::const_iterator x_it, y_it;
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++) {
      out[0] = out[0] * it->conversion_factor()[0];
      if (!it->is_null())
	x_it = it;
    }
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = x.units_.begin(); it != x.units_.end(); it++) {
      out[0] = out[0] / it->conversion_factor()[0];
      if (!it->is_null())
	y_it = it;
    }
    if (singular)
      out[1] = x_it->conversion_factor(*y_it)[1];
    return out;
  }
  //! \brief Determine the conversion factors necessary to convert quantities
  //!   with these units to another set of units and convert these units to
  //!   the other set of units in place.
  //! \param x Units that conversion factors should convert to.
  //! \return Array of conversion factors where the first element is the
  //!   factor that values should be multiplied by and the second element is
  //!   the offset between the zero points in this and x.
  std::vector<double> convert_to(const GenericUnits& x) {
    int delta = get_delta();
    std::vector<double> out = conversion_factor(x);
    units_.clear();
    units_.insert(units_.begin(), x.units_.begin(), x.units_.end());
    // units_ = x.units_;
    if (delta)
      set_delta(delta);
    return out;
  }
  //! \brief Find the unit in the current unit set that matches a particular
  //!   dimension at its base (ignoring powers).
  //! \param d Dimension to find.
  //! \return Pointer to the unit that matches or NULL if there is not a match.
  const GenericUnit<Encoding>* find_dimension(const Dimension& d) const {
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++) {
      if (it->dim_ == d)
	return &(*it);
    }
    return NULL;
  }
  //! \brief Get the equivalent of this set of units in the units system
  //!   used by another set of units.
  //! \param x Unit system to get units in.
  //! \return Equivalent units in the x unit system.
  GenericUnits<Encoding> as_units_system(const GenericUnits& x) const {
    GenericUnits<Encoding> new_Units;
    as_units_system(x, new_Units);
    return new_Units;
  }
  //! \brief Get the equivalent of this set of units in the units system
  //!   used by another set of units.
  //! \param x Unit system to get units in.
  //! \param[out] dest Destination for equivalent units in the x unit
  //!   system.
  void as_units_system(const GenericUnits& x, GenericUnits& dest) const {
    std::vector<GenericUnit<Encoding> > new_units;
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++) {
      if (it->is_null())
	continue;
      const GenericUnit<Encoding>* x_dim = x.find_dimension(it->dim_);
      if (x_dim == NULL) {
	new_units.push_back(*it);
      } else {
	GenericUnit<Encoding> tmp(*x_dim);
	tmp.power_ = it->power_;
	tmp.delta_ = it->delta_;
	new_units.push_back(tmp);
      }
    }
    dest = GenericUnits<Encoding>(new_units);
  }
  
  //! \brief Convert units to the system used by another set of units in place
  //!   and determine the conversion factors necessary to convert quantities
  //!   with these units to the new unit system.
  //! \param x Unit system to convert to.
  //! \return Array of conversion factors where the first element is the
  //!   factor that values should be multiplied by and the second element is
  //!   the offset between the zero points in this and x.
  std::vector<double> convert_to_units_system(const GenericUnits& x) {
    if (dimension() == x.dimension())
      return convert_to(x);
    GenericUnits<Encoding> new_Units = as_units_system(x);
    return convert_to(new_Units);
  }
private:
  std::vector<GenericUnit<Encoding> > units_;

  bool _check_valid() const {
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = units_.begin(); it != units_.end(); it++) {
      if (!it->_check_valid())
	return false;
    }
    return (!(has_offset() && size() > 1));
  }
  
  template<typename Ch2, typename Enc2>
  friend std::basic_ostream<Ch2> & operator << (std::basic_ostream<Ch2> &os, const GenericUnits<Enc2> &x);
};
template<typename Ch2, typename Encoding>
inline std::basic_ostream<Ch2> & operator << (std::basic_ostream<Ch2> &os, const GenericUnits<Encoding> &x) {
    size_t i = 0;
    size_t N = x.units_.size();
    for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = x.units_.begin(); it != x.units_.end(); it++, i++) {
      if (i != 0) os << '*';
      if ((N > 1) && it->has_power())
	os << '(';
      os << *it;
      if ((N > 1) && it->has_power())
	os << ')';
    }
    return os;
}

template<typename Encoding>
GenericUnits<Encoding> operator*(const GenericUnit<Encoding>& a, const GenericUnit<Encoding>& b) {
  std::vector<GenericUnit<Encoding> > units_a, units_b;
  units_a.push_back(a);
  units_b.push_back(b);
  GenericUnits<Encoding> Units_a = GenericUnits<Encoding>(units_a);
  GenericUnits<Encoding> Units_b = GenericUnits<Encoding>(units_b);
  Units_a *= Units_b;
  return Units_a; }
template<typename Encoding>
GenericUnits<Encoding> operator/(const GenericUnit<Encoding>& a, const GenericUnit<Encoding>& b) {
  return a * b.pow(-1); }


//! GenericUUnits with UTF8 encoding
typedef GenericUnits<UTF8<char> > Units;

#define PACK_UNIT(...) PACK_LUT(Unit, (__VA_ARGS__))
#define VSTR(...) pack_strings<char>(__VA_ARGS__, (char*)NULL)

  // MKS as base, units that can have SI prefixes
  static CachedLUT<Unit> _base_units (
      PACK_UNIT(VSTR("meter", "metre"), VSTR("m"), dimensions::length),
      PACK_UNIT(VSTR("gram", "gramme"), VSTR("g"), dimensions::mass, 1.0e-3),
      PACK_UNIT("second", "s", dimensions::time),
      PACK_UNIT(VSTR("ampere", "amp", "Amp"), VSTR("A"), dimensions::current),
      PACK_UNIT(VSTR("kelvin", "degree_kelvin"), VSTR("K", "degK"), dimensions::temperature, 1, 0, 1),
      PACK_UNIT("mole", "mol", dimensions::number, 1.0 / constants::amu_grams),
      PACK_UNIT("candela", "cd", dimensions::luminous_intensity),
      PACK_UNIT("radian", "rad", dimensions::angle),
      (void*)NULL
    );
  
  static CachedLUT<Unit> _prefixable_units (
#if YGGDRASIL_RAPIDJSON_HAS_CXX11
      _base_units.template get<Unit>(),
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
      _base_units.get<Unit>(),
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11
      // cgs
      PACK_UNIT("dyne", "dyn", dimensions::force, 1.0e-5),
      PACK_UNIT("erg", "erg", dimensions::energy, 1.0e-7),
      PACK_UNIT("barye", "Ba", dimensions::pressure, 0.1),
      PACK_UNIT("gauss", "G", dimensions::magnetic_field_cgs, pow(0.1, 0.5)),
      PACK_UNIT(VSTR("statcoulomb", "esu", "ESU", "electrostatic_unit"), VSTR("statC"), dimensions::charge_cgs, pow(1.0e-3, 1.5)),
      PACK_UNIT("statampere", "statA", dimensions::current_cgs, pow(1.0e-3, 1.5)),
      PACK_UNIT("statvolt", "statV", dimensions::electric_potential_cgs, 0.1 * pow(1.0e-3, 1.5)),
      PACK_UNIT("statohm", "statohm", dimensions::resistance_cgs, 100.0),
      PACK_UNIT("maxwell", "Mx", dimensions::magnetic_flux_cgs, pow(1.0e-3, 1.5)),
      // SI
      PACK_UNIT("joule", "J", dimensions::energy),
      PACK_UNIT("watt", "W", dimensions::power),
      PACK_UNIT("hertz", "Hz", dimensions::rate),
      PACK_UNIT("newton", "N", dimensions::force),
      PACK_UNIT("coulomb", "C", dimensions::charge),
      PACK_UNIT("tesla", "T", dimensions::magnetic_field),
      PACK_UNIT("pascal", "Pa", dimensions::pressure),
      PACK_UNIT("bar", "bar", dimensions::pressure, 1.0e5),
      PACK_UNIT("volt", "V", dimensions::electric_potential),
      PACK_UNIT("farad", "F", dimensions::capacitance),
      PACK_UNIT("henry", "H", dimensions::inductance),
      PACK_UNIT(VSTR("ohm", "Ohm"), VSTR("Ω"), dimensions::resistance),
      PACK_UNIT("weber", "Wb", dimensions::magnetic_flux),
      PACK_UNIT("lumen", "lm", dimensions::luminous_flux),
      PACK_UNIT("lux", "lx", dimensions::luminous_flux / dimensions::area),
      PACK_UNIT(VSTR("celcius", "degree_celsius", "degree_Celsius", "celsius"), VSTR("degC", "°C"), dimensions::temperature, 1.0, constants::celcius_zero_kelvin, 1),
      // other
      PACK_UNIT("calorie", "cal", dimensions::energy, 4.184),
      PACK_UNIT("year", "yr", dimensions::time, constants::sec_per_year),
      PACK_UNIT("parsec", "pc", dimensions::length, constants::m_per_pc),
      PACK_UNIT("electronvolt", "eV", dimensions::energy, constants::J_per_eV),
      PACK_UNIT(VSTR("jansky"), VSTR("J", "j"), dimensions::specific_flux, constants::jansky_mks),
      PACK_UNIT("sievert", "Sv", dimensions::specific_energy),
      PACK_UNIT("molar", "M", dimensions::number_density, 100.0 / constants::amu_grams),
      (void*)NULL
    );
  
  static CachedLUT<Unit> _unprefixable_units(
    // Imperial units
    PACK_UNIT(VSTR("mil", "thou", "thousandth"), VSTR("mil"), dimensions::length, 1.0e-3 * constants::m_per_inch),
    PACK_UNIT("incl", "incl", dimensions::length, constants::m_per_inch),
    PACK_UNIT("feet", "ft", dimensions::length, constants::m_per_ft),
    PACK_UNIT("yard", "yd", dimensions::length, 0.9144),
    PACK_UNIT("mile", "mi", dimensions::length, 1609.344),
    PACK_UNIT("furlong", "fur", dimensions::length, constants::m_per_ft * 660.0),
    PACK_UNIT(VSTR("farenheit", "degree_fahrenheit", "degree_Fahrenheit"), VSTR("degF", "°F"), dimensions::temperature, constants::kelvin_per_rankine, constants::farenheit_zero_kelvin, 1),
    PACK_UNIT(VSTR("rankine", "degree_rankine"), VSTR("degR"), dimensions::temperature, constants::kelvin_per_rankine, 0, 1),
    PACK_UNIT("pound_force", "lbf", dimensions::force, constants::kg_per_pound * constants::standard_gravity_m_per_s2),
    PACK_UNIT(VSTR("pound", "pound_mass"), VSTR("lb", "lbm"), dimensions::mass, constants::kg_per_pound),
    PACK_UNIT("atmosphere", "atm", dimensions::pressure, constants::pascal_per_atm),
    PACK_UNIT("horsepower", "hp", dimensions::power, constants::watt_per_horsepower),
    PACK_UNIT("ounce", "oz", dimensions::mass, constants::kg_per_pound / 16.0),
    PACK_UNIT("ton", "ton", dimensions::mass, constants::kg_per_pound * 2000.0),
    PACK_UNIT("slug", "slug", dimensions::mass, constants::kg_per_pound * constants::standard_gravity_m_per_s2 / constants::m_per_ft),
    PACK_UNIT(VSTR("BTU", "british_thermal_unit"), VSTR("BTU"), dimensions::energy, 1055.0559),
    PACK_UNIT("pounds_per_square_inch", "psi", dimensions::pressure, constants::kg_per_pound * constants::standard_gravity_m_per_s2 / pow(constants::m_per_inch, 2)),
    PACK_UNIT("smoot", "smoot", dimensions::length, 1.7018),
    PACK_UNIT("percent", "%", dimensions::dimensionless, 0.01),
    PACK_UNIT("fraction", "100%", dimensions::dimensionless, 1.0),
    PACK_UNIT("minute", "min", dimensions::time, constants::sec_per_min),
    PACK_UNIT(VSTR("hour"), VSTR("hr", "h", "hrs"), dimensions::time, constants::sec_per_hr),
    PACK_UNIT(VSTR("day"), VSTR("day", "d"), dimensions::time, constants::sec_per_day),
    // Astronomy units
    PACK_UNIT("c", "c", dimensions::velocity, constants::speed_of_light_m_per_s),
    PACK_UNIT(VSTR("solar_mass", "solMass", "mass_sun"), VSTR("Msun", "Msol", "msun", "m_sun", "M_sun", "m_Sun"), dimensions::mass, constants::mass_sun_kg),
    PACK_UNIT(VSTR("solar_radius", "solRadius"), VSTR("Rsun", "Rsol", "rsun", "r_sun", "R_sun", "r_Sun"), dimensions::length, constants::m_per_rsun),
    PACK_UNIT(VSTR("solar_luminosity", "solLumin"), VSTR("Lsun", "Lsol", "lsun", "l_sun", "L_sun", "l_Sun"), dimensions::power, constants::luminosity_sun_watts),
    PACK_UNIT(VSTR("solar_temperature", "solTemperature"), VSTR("Tsun", "Tsol", "tsun", "t_sun", "T_sun", "t_Sun"), dimensions::temperature, constants::temp_sun_kelvin, 0, 1),
    PACK_UNIT(VSTR("solar_metallicity", "solMetallicity"), VSTR("Zsun", "Zsol", "zsun", "z_sun", "Z_sun", "z_Sun"), dimensions::dimensionless, constants::metallicity_sun),
    PACK_UNIT(VSTR("jupiter_mass"), VSTR("Mjup", "m_jup"), dimensions::mass, constants::mass_jupiter_kg),
    PACK_UNIT(VSTR("jupiter_radius"), VSTR("Rjup", "r_jup"), dimensions::length, constants::m_per_rjup),
    PACK_UNIT(VSTR("earth_mass"), VSTR("Mearth", "m_earth"), dimensions::mass, constants::mass_earth_kg),
    PACK_UNIT(VSTR("earth_radius"), VSTR("Rearth", "r_earth"), dimensions::length, constants::m_per_rearth),
    PACK_UNIT(VSTR("astronomical_unit"), VSTR("AU", "au"), dimensions::length, constants::m_per_au),
    PACK_UNIT("light_year", "ly", dimensions::length, constants::m_per_ly),
    PACK_UNIT("degree", "deg", dimensions::angle, M_PI / 180.0),
    PACK_UNIT("arcmin", "arcmin", dimensions::angle, M_PI / 10800.0),
    PACK_UNIT("arcsec", "arcsec", dimensions::angle, M_PI / 648000.0),
    PACK_UNIT("miliarcsec", "mas", dimensions::angle, M_PI / 648000000.0),
    PACK_UNIT("hourangle", "hourangle", dimensions::angle, M_PI / 12.0),
    PACK_UNIT("steradian", "sr", dimensions::solid_angle),
    PACK_UNIT(VSTR("latitude", "degree_latitude"), VSTR("lat"), dimensions::angle, -M_PI / 180.0, 90.0),
    PACK_UNIT(VSTR("longitude", "degree_longitude"), VSTR("long"), dimensions::angle, M_PI / 180.0, -180.0),
    // Physics
    PACK_UNIT("amu", "amu", dimensions::mass, constants::amu_kg),
    PACK_UNIT("angstrom", "Å", dimensions::length, constants::m_per_ang),
    PACK_UNIT("counts", "counts", dimensions::number),
    PACK_UNIT("photons", "photons", dimensions::number),
    PACK_UNIT("me", "me", dimensions::mass, constants::mass_electron_kg),
    PACK_UNIT("mp", "mp", dimensions::mass, constants::mass_hydrogen_kg),
    PACK_UNIT("rayleigh", "rayleigh", dimensions::count_intensity, 2.5e9 / M_PI),
    PACK_UNIT("lambert", "lambert", dimensions::luminance, 1.0e4 / M_PI),
    PACK_UNIT("nit", "nt", dimensions::luminance),
    // Planck
    PACK_UNIT("m_pl", "m_pl", dimensions::mass, constants::planck_mass_kg),
    PACK_UNIT("l_pl", "l_pl", dimensions::length, constants::planck_length_m),
    PACK_UNIT("t_pl", "t_pl", dimensions::time, constants::planck_time_s),
    PACK_UNIT("T_pl", "T_pl", dimensions::temperature, constants::planck_temperature_K),
    PACK_UNIT("q_pl", "q_pl", dimensions::charge, constants::planck_charge_C),
    PACK_UNIT("E_pl", "E_pl", dimensions::energy, constants::planck_energy_J),
    // Geometrized
    PACK_UNIT("m_geom", "m_geom", dimensions::mass, constants::mass_sun_kg),
    PACK_UNIT("l_geom", "l_geom", dimensions::length, constants::newton_mks * constants::mass_sun_kg / pow(constants::speed_of_light_m_per_s, 2)),
    PACK_UNIT("t_geom", "t_geom", dimensions::time, constants::newton_mks * constants::mass_sun_kg / pow(constants::speed_of_light_m_per_s, 3)),
    // Logarithmic
    // PACK_UNIT("bel", "B", dimensions::logarithmic, neper_per_bel),
    // PACK_UNIT("neper", "Np", dimensions::logarithmic),
    // misc
    PACK_UNIT("acre", "ac", dimensions::area, 4046.86),
    PACK_UNIT("are", "a", dimensions::area, 100.0),
    PACK_UNIT("hectare", "ha", dimensions::area, 10000.0),
    PACK_UNIT(VSTR(""), VSTR("", "n/a", "dimensionless"), dimensions::dimensionless, 1.0),
    (void*)NULL
  );

#undef PACK_UNIT
#undef VSTR

template<typename Encoding>
bool GenericUnit<Encoding>::from_table(const std::basic_string<typename Encoding::Ch> str) {
  size_t idx_beg, idx_end;
  std::basic_string<Ch> whitespace = get_whitespace();
  idx_beg = str.find_first_not_of(whitespace);
  idx_end = str.find_last_not_of(whitespace);
  if (idx_end >= str.size())
    idx_end = str.size() - 1;
  std::basic_string<Ch> substr;
  bool delta = false;
  if (str.size() == 0) {
    substr = str;
  } else {
    std::basic_string<Ch> delta_str = get_delta<Ch>();
    std::size_t found = str.find(delta_str, idx_beg);
    if (found != std::string::npos) {
      delta = true;
      idx_beg += delta_str.size();
    }
    substr = str.substr(idx_beg, idx_end + 1);
  }
  
  std::vector<const GenericUnit<Encoding>*> possibilities;
  const std::vector<GenericUnit<Encoding> >* prefix_units = _prefixable_units.template get<GenericUnit<Encoding> >();
  for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = prefix_units->begin(); it != prefix_units->end(); it++) {
    if (it->matches(substr))
      return from_table(*it, delta);
    it->prefix_matches(substr, possibilities);
  }
  const std::vector<GenericUnit<Encoding> >* unprefix_units = _unprefixable_units.template get<GenericUnit<Encoding> >();
  for (typename std::vector<GenericUnit<Encoding> >::const_iterator it = unprefix_units->begin(); it != unprefix_units->end(); it++)
    if (it->matches(substr))
      return from_table(*it, delta);
  if (possibilities.size() > 0) {
    const std::vector<GenericUnitPrefix<Encoding> >* prefixes = _unit_prefixes.template get<GenericUnitPrefix<Encoding> >();
    for (typename std::vector<const GenericUnit<Encoding>*>::const_iterator it = possibilities.begin(); it != possibilities.end(); it++)
      for (typename std::vector<GenericUnitPrefix<Encoding> >::const_iterator p = prefixes->begin(); p != prefixes->end(); p++)
	if ((*it)->matches(substr, *p))
	  return from_table(**it, delta, *p);
  }
  return false; // GCOVR_EXCL_LINE
}

namespace parser {

enum TokenType {
  kWhitespaceToken = 0,
  kOperatorToken = 1,
  kWordToken = 2,
  kGroupToken = 3
};
enum TokenFinalization {
  kTokenFinalizeNull,
  kTokenFinalizeAlways,
  kTokenFinalizeBracket,
  kTokenFinalizeSpace,
  kTokenFinalizeValue,
  kTokenFinalizeNext,
  kTokenFinalizeGroup,
  kTokenFinalizeFinal
};

template<typename Encoding>
class GroupToken; // Forward declaration


template<typename Encoding>
class TokenBase {
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
private:
  TokenBase(const TokenBase<Encoding>& rhs);
public:
  TokenBase(const TokenType t0, TokenBase *parent0=NULL) : t(t0), units(), finalized(kTokenFinalizeNull), parent(parent0), value_(0.0), errorFlag(false) {}
  virtual ~TokenBase() {}
  virtual TokenBase<Encoding>* current_token() { return this; }
  virtual GenericUnits<Encoding> finalize(TokenFinalization x) {
    if (!finalized)
      finalized = x;
    return units;
  }
  void reset() {
    finalized = kTokenFinalizeNull;
    units.clear();
    value_ = 0.0;
  }
  double value() {
    YGGDRASIL_RAPIDJSON_ASSERT(is_numeric());
    finalize(kTokenFinalizeValue);
    return value_;
  }
  virtual bool is_numeric() { return false; }
  virtual void set_error() {
    errorFlag = true;
    if (parent)
      parent->set_error();
  }
  virtual void append(const Ch) = 0;
  virtual std::ostream & display(std::ostream &os) const = 0;
  TokenBase<Encoding>& operator=(const TokenBase<Encoding>& other);
  TokenType t;
  GenericUnits<Encoding> units;
  TokenFinalization finalized;
  TokenBase<Encoding> *parent;
  double value_;
  bool errorFlag;
  template<typename Encoding2>
  friend std::ostream & operator << (std::ostream &os, const TokenBase<Encoding2>* x);
};
template<typename Encoding2>
inline std::ostream & operator << (std::ostream &os, const TokenBase<Encoding2>* x) {
  return x->display(os);
}
  
template<typename Encoding>
class OperatorToken : public TokenBase<Encoding> {
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
public:
  OperatorToken(const Ch op0, TokenBase<Encoding> *parent0=NULL) : TokenBase<Encoding>(kOperatorToken, parent0), op(op0) { this->finalize(kTokenFinalizeAlways); }
  void append(const Ch c) OVERRIDE_CXX11 { YGGDRASIL_RAPIDJSON_ASSERT(!c); (void)c; } // GCOVR_EXCL_LINE
  GenericUnits<Encoding> operate(const GenericUnits<Encoding>& a, const GenericUnits<Encoding>& b) {
    switch (op) {
    case '*':
      return a * b;
    case '/':
      return a / b;
    default:
      YGGDRASIL_RAPIDJSON_ASSERT((op == '*') || (op == '/')); // GCOVR_EXCL_LINE
    }
    return this->units; // GCOVR_EXCL_LINE
  }
  GenericUnits<Encoding> operate(const GenericUnits<Encoding>& a, const double& b) {
    YGGDRASIL_RAPIDJSON_ASSERT(op == '^');
    return a.pow(b);
  }
  double operate(const double& a, const double& b) {
    switch (op) {
    case '*':
      return a * b;
    case '/':
      return a / b;
    case '^':
      return std::pow(a, b);
    case '+':
      return a + b;
    case '-':
      return a - b;
    default:
      YGGDRASIL_RAPIDJSON_ASSERT((op == '*') || (op == '/') || (op == '^') // GCOVR_EXCL_LINE
		       || (op == '+') || (op == '-'));
    }
    return 0.0; // GCOVR_EXCL_LINE
  }
  bool is_numeric() OVERRIDE_CXX11 { return true; }
  bool is_exp() { return (op == '^'); }
  bool matches(const std::vector<char> ops) {
    for (std::vector<char>::const_iterator iop = ops.begin(); iop != ops.end(); iop++)
      if (*iop == op)
	return true;
    return false;
  }
  std::ostream & display(std::ostream &os) const OVERRIDE_CXX11 {
    os << "OperatorToken(" << op << ")";
    return os;
  }
  Ch op;
};

template<typename Encoding>
class NumberToken; // Forward declaration
  
template<typename Encoding>
class WordToken : public TokenBase<Encoding> {
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
public:
  WordToken(const Ch c, TokenBase<Encoding> *parent0=NULL) : TokenBase<Encoding>(kWordToken, parent0), word() {
    word.push_back(c);
  }
  void append(const Ch c) OVERRIDE_CXX11 {
    word.push_back(c);
  }
  GenericUnits<Encoding> finalize(TokenFinalization x) OVERRIDE_CXX11 {
    YGGDRASIL_RAPIDJSON_ASSERT(word.size());
    if (!(this->finalized))
      if (!this->units.add_unit(word))
	this->set_error();
      // this->units = GenericUnits<Encoding>({GenericUnit<Encoding>(word)});
    return TokenBase<Encoding>::finalize(x);
  }
  std::ostream & display(std::ostream &os) const OVERRIDE_CXX11 {
    os << "WordToken(" << convert_chars<Encoding,UTF8<char> >(word) << ")";
    return os;
  }
  std::basic_string<Ch> word;
  friend class NumberToken<Encoding>;
};

template<typename Encoding>
class NumberToken : public WordToken<Encoding> {
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
public:
  NumberToken(const Ch c, TokenBase<Encoding> *parent0=NULL) : WordToken<Encoding>(c, parent0) {}
  bool is_numeric() OVERRIDE_CXX11 { return true; }
  GenericUnits<Encoding> finalize(TokenFinalization x) OVERRIDE_CXX11 {
    if (!(this->finalized)) {
      this->value_ = char_to_double<Ch>(this->word);
      this->units.add_factor(this->value_);
    }
    return TokenBase<Encoding>::finalize(x);
  }
  std::ostream & display(std::ostream &os) const OVERRIDE_CXX11 {
    os << "NumericToken(" << convert_chars<Encoding,UTF8<char> >(this->word) << ")";
    return os;
  }
};

template<typename Encoding>
class GroupToken : public TokenBase<Encoding> {
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
public:
  GroupToken(TokenBase<Encoding> *parent0=NULL) : TokenBase<Encoding>(kGroupToken, parent0), tokens() {}
  ~GroupToken() OVERRIDE_CXX11 {
    for (size_t i = 0; i < tokens.size(); i++)
      delete tokens[i];
    tokens.clear();
  }
  TokenBase<Encoding>* current_token() OVERRIDE_CXX11 {
    if (tokens.size() == 0)
      return TokenBase<Encoding>::current_token();
    return tokens[tokens.size() - 1]->current_token();
  }
  GroupToken<Encoding>* current_group() {
    int idx = (int)(tokens.size()) - 1;
    if ((idx >= 0) && (tokens[(size_t)idx]->t == kGroupToken)
	&& (!(tokens[(size_t)idx]->finalized))) {
      GroupToken<Encoding>* grp = static_cast<GroupToken<Encoding>*>(tokens[(size_t)idx]);
      return grp->current_group();
    }
    return this;
  }
  OperatorToken<Encoding>* append_op(const Ch c, bool dont_descend=false) {
    OperatorToken<Encoding>* op = new OperatorToken<Encoding>(c, this);
    append(op, dont_descend);
    return op;
  }
  void append(const Ch c) OVERRIDE_CXX11 {
    TokenBase<Encoding>* curr = current_token();
    if ((curr->t == kGroupToken) || curr->finalized) {
      switch (c) {
      case '-':
      case '+':
      case '0':
      case '1':
      case '2':
      case '3':
      case '4':
      case '5':
      case '6':
      case '7':
      case '8':
      case '9':
	curr = append(new NumberToken<Encoding>(c, (TokenBase<Encoding>*)(this)));
	break;
      default:
	curr = append(new WordToken<Encoding>(c, (TokenBase<Encoding>*)(this)));
      }
      return;
    } else if ((c == '-') || (c == '+')) {
      append_op(c);
      return;
    }
    YGGDRASIL_RAPIDJSON_ASSERT(curr->t == kWordToken);
    if ((!curr->is_numeric()) &&
	(c == '0' || c == '1' || c == '2' || c == '3' || c == '4' ||
	 c == '5' || c == '6' || c == '7' || c == '8' || c == '9')) {
      append_op('^');
      append(c);
      return;
    }
    YGGDRASIL_RAPIDJSON_ASSERT(curr->t == kWordToken);
    WordToken<Encoding>* word = static_cast<WordToken<Encoding>*>(curr);
    word->append(c);
  }
  TokenBase<Encoding>* append(TokenBase<Encoding>* x, bool dont_descend=false) {
    GroupToken<Encoding>* curr;
    if (dont_descend)
      curr = this;
    else {
      curr = current_group();
      if (curr->tokens.size() > 0) {
	TokenBase<Encoding>* prev = curr->current_token();
	if (!(prev->finalized))
	  prev->finalize(kTokenFinalizeNext);
	// Handle special case where exponent is set by having number
	// directly following the unit
	if (curr->tokens.size() >= 2) {
	  TokenBase<Encoding>* prev2 = curr->tokens[curr->tokens.size() - 2];
	  if (prev->t == kOperatorToken &&
	      prev2->t == kWordToken && !prev2->is_numeric() &&
	      prev2->finalized == kTokenFinalizeNext &&
	      x->t == kWordToken && x->is_numeric() &&
	      (static_cast<OperatorToken<Encoding>*>(prev)->op == '-' ||
	       static_cast<OperatorToken<Encoding>*>(prev)->op == '+')) {
	    OperatorToken<Encoding>* prev_op = static_cast<OperatorToken<Encoding>*>(prev);
	    if (prev_op->op == '-') {
	      prev2->reset();
	      static_cast<WordToken<Encoding>*>(x)->word.insert(0, 1, prev_op->op);
	      prev2->finalize(kTokenFinalizeNext);
	    }
	    prev_op->op = '^';
	  }
	}
	if ((x->t != kOperatorToken) && (prev->t != kOperatorToken))
	  curr->append_op('*', true);
      }
    }
    YGGDRASIL_RAPIDJSON_ASSERT(!(curr->finalized));
    curr->tokens.push_back(x);
    x->parent = curr;
    return x;
  }
  void group_operators(const char op) {
    std::vector<char> ops;
    ops.push_back(op);
    group_operators(ops);
  }
  void group_operators(const char op1, const char op2) {
    std::vector<char> ops;
    ops.push_back(op1);
    ops.push_back(op2);
    group_operators(ops);
  }
  void group_operators(const std::vector<char> ops) {
    if (tokens.size() <= 3)
      return;
    std::vector<size_t> exponents;
    for (size_t i = 1; i < tokens.size(); i++) {
      if (tokens[i]->t == kOperatorToken) {
	OperatorToken<Encoding> *op = static_cast<OperatorToken<Encoding>*>(tokens[i]);
	if (op->matches(ops)) {
	  YGGDRASIL_RAPIDJSON_ASSERT((i + 1) < tokens.size());
	  GroupToken<Encoding>* new_group = new GroupToken<Encoding>(this);
	  for (size_t ii = i - 1; ii <= (i + 1); ii++) {
	    tokens[ii]->parent = new_group;
	    new_group->append(tokens[ii]);
	    tokens[ii] = NULL;
	  }
	  tokens[i + 1] = (TokenBase<Encoding>*)(new_group);
	  new_group->finalize(kTokenFinalizeAlways);
	  exponents.push_back(i - 1);
	  exponents.push_back(i);
	  i++;
	}
      }
    }
    for (std::vector<size_t>::reverse_iterator it = exponents.rbegin(); it != exponents.rend(); it++)
      tokens.erase(tokens.begin() + (int)(*it));
  }
  GenericUnits<Encoding> finalize(TokenFinalization x) OVERRIDE_CXX11 {
    if ((tokens.size() == 0) || this->finalized)
      return this->units;
    // Group operators first in order of operations
    if (tokens.size() > 3) {
      group_operators('^');
      group_operators('*', '/');
      group_operators('+', '-');
    }
    // Complete operations from left to right
    GenericUnits<Encoding> out = tokens[0]->finalize(kTokenFinalizeGroup);
    if (is_numeric()) {
      this->value_ = tokens[0]->value();
      for (size_t i = 1; i < tokens.size(); i = i+2) {
	YGGDRASIL_RAPIDJSON_ASSERT(tokens[i]->t == kOperatorToken);
	YGGDRASIL_RAPIDJSON_ASSERT(tokens[i + 1]->t != kOperatorToken);
	OperatorToken<Encoding> *op = static_cast<OperatorToken<Encoding>*>(tokens[i]);
	this->value_ = op->operate(this->value_, tokens[i + 1]->value());
      }
    } else {
      for (size_t i = 1; i < tokens.size(); i = i+2) {
	YGGDRASIL_RAPIDJSON_ASSERT(tokens[i]->t == kOperatorToken);
	YGGDRASIL_RAPIDJSON_ASSERT(tokens[i + 1]->t != kOperatorToken);
	OperatorToken<Encoding> *op = static_cast<OperatorToken<Encoding>*>(tokens[i]);
	if (tokens[i + 1]->is_numeric()) {
	  out = op->operate(out, tokens[i + 1]->value());
	} else {
	  out = op->operate(out, tokens[i + 1]->finalize(kTokenFinalizeGroup));
	}
      }
    }
    this->units = out;
    return TokenBase<Encoding>::finalize(x);
  }
  bool is_numeric() OVERRIDE_CXX11 {
    for (typename std::vector<TokenBase<Encoding>*>::iterator it = tokens.begin(); it != tokens.end(); it++) {
      if (!((*it)->is_numeric()))
	return false;
    }
    return true;
  }
  std::ostream & display(std::ostream &os) const OVERRIDE_CXX11 {
    os << "GroupToken(";
    size_t i = 0;
    for (typename std::vector<TokenBase<Encoding>*>::const_iterator it = tokens.begin(); it != tokens.end(); it++, i++) {
      if (i > 0) os << ", ";
      (*it)->display(os);
    }
    os << ")";
    return os;
  }
  std::vector<TokenBase<Encoding>*> tokens;
};

} // namespace parser


template<typename Encoding>
GenericUnits<Encoding> GenericUnits<Encoding>::parse_units(const typename Encoding::Ch* str,
							   const size_t len,
							   const bool verbose) {
  if (verbose)
    std::cout << "parse_units(\"" << convert_chars<Encoding,UTF8<char> >(str) << "\")" << std::endl;
  size_t i = 0;
  parser::GroupToken<Encoding> token;
  typename Encoding::Ch c;
  for (i = 0; i < len; i++) {
    c = str[i];
    switch (c) {
    case '(':
    case '[': // TODO: Concentration?
    case '{': {
      token.append(new parser::GroupToken<Encoding>());
      break;
    }
    case ')':
    case ']':
    case '}': {
      token.current_group()->finalize(parser::kTokenFinalizeBracket);
      break;
    }
    // + and - operators will be handled by the word token append
    case '/':
    case '^': {
      token.append_op(c);
      break;
    }
    case '*': {
      if (str[i + 1] == '*') {
	c = '^';
	i++;
      }
      token.append_op(c);
      break;
    }
    case ' ':
    case '\t':
    case '\n':
    case '\v':
    case '\f':
    case '\r': {
      parser::TokenBase<Encoding>* word = token.current_token();
      if (word->t == parser::kWordToken)
	word->finalize(parser::kTokenFinalizeSpace);
      break;
    }
    case 'e': {
      if (((i + 1) < len) &&
	  ((str[i + 1] == '+') || (str[i + 1] == '-') ||
	   (str[i + 1] == '0') || (str[i + 1] == '1') ||
	   (str[i + 1] == '2') || (str[i + 1] == '3') ||
	   (str[i + 1] == '4') || (str[i + 1] == '5') ||
	   (str[i + 1] == '6') || (str[i + 1] == '7') ||
	   (str[i + 1] == '8') || (str[i + 1] == '9'))) {
	parser::TokenBase<Encoding>* curr = token.current_token();
	if ((curr->t == parser::kWordToken) && curr->is_numeric() &&
	    (!curr->finalized)) {
	  curr->append(str[i++]);
	  curr->append(str[i]);
	  break;
	}
      }
      // fall through to default
      YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH;
    }
    case 'n': {
      // Special case of n/a
      if (((i + 2) < len) && (str[i + 1] == '/') && (str[i + 2] == 'a')) {
	parser::TokenBase<Encoding>* curr = token.current_token();
	if ((curr->t == parser::kGroupToken) || curr->finalized) {
	  token.append(str[i++]);
	  token.append(str[i++]);
	  token.append(str[i++]);
	  break;
	}
      }
      // fall through to default
      YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH;
    }
    case '%': {
      parser::TokenBase<Encoding>* curr = token.current_token();
      if ((curr->t == parser::kWordToken) && !(curr->finalized) &&
	  curr->is_numeric()) {
	std::basic_string<Ch> hundred;
	hundred.push_back('1');
	hundred.push_back('0');
	hundred.push_back('0');
	if (static_cast<parser::WordToken<Encoding>*>(curr)->word == hundred &&
	    curr->parent && curr->parent->t == parser::kGroupToken) {
	  parser::GroupToken<Encoding>* curr_parent = static_cast<parser::GroupToken<Encoding>*>(curr->parent);
	  curr_parent->tokens.pop_back();
	  parser::TokenBase<Encoding>* old_curr = curr;
	  curr = new parser::WordToken<Encoding>(hundred[0], curr_parent);
	  for (size_t ii = 1; ii < hundred.size(); ii++)
	    curr->append(hundred[ii]);
	  curr_parent->tokens.push_back(curr);
	  delete old_curr;
	}
      }
      // fall through to default
      YGGDRASIL_RAPIDJSON_DELIBERATE_FALLTHROUGH;
    }
    default:
      token.append(c);
    }
    if (verbose) {
      std::cout << c << ": ";
      token.display(std::cout);
      std::cout << std::endl;
    }
    if (token.errorFlag)
      break;
  }
  GenericUnits<Encoding> out = token.finalize(parser::kTokenFinalizeFinal);
  if (len == 0) {
    YGGDRASIL_RAPIDJSON_ASSERT(!token.errorFlag);
    token.errorFlag = (!out.add_unit(std::basic_string<Ch>()));
  }
  if (token.errorFlag)
    out = GenericUnits<Encoding>();
  return out;
}

#define DELEGATE_TO_INPLACE_(TMP, CLS, TYP, OP, IOP, IN, ARG)	\
  TMP								\
  CLS OP IN const {						\
    TYP(T) out(*this);						\
    out.IOP ARG;						\
    return out;							\
  }
#define DELEGATE_TO_INPLACE_OP_QUANTITY_(TYP, OP, IOP)			\
  template<typename T2>							\
  friend TYP(T) operator OP(TYP(T) lhs, const TYP(T2)& rhs) {		\
    lhs IOP rhs;							\
    return lhs;								\
  }
#define DELEGATE_TO_INPLACE_OP_SCALAR_(TYP, OP, IOP)			\
  template<typename T2>							\
  friend TYP(T) operator OP(TYP(T) lhs, const T2& rhs) {		\
    lhs IOP rhs;							\
    return lhs;								\
  }
  

#define INHERIT_OP_BASE_INPLACE_(TMP, CLS, TYP, BASE, IOP, IN, ARGBASE)	\
  TMP									\
  CLS& IOP IN {								\
    BASE(T)::IOP ARGBASE;						\
    return *this;							\
  }
#define INHERIT_OP_BASE_(TMP, CLS, TYP, BASE, OP, IOP, IN, ARG, ARGBASE) \
  INHERIT_OP_BASE_INPLACE_(TMP, CLS, TYP, BASE, IOP, IN, ARGBASE)	\
  DELEGATE_TO_INPLACE_(TMP, CLS, TYP, OP, IOP, IN, ARG)
#define INHERIT_OP_BASE_QUANTITY_(CLS, TYP, BASE, OP, IOP)		\
  INHERIT_OP_BASE_(template<typename T2>, CLS, TYP, BASE, OP, IOP, (const TYP(T2)& x), (x), (*static_cast<const BASE(T2)*>(&x)))
  // INHERIT_OP_BASE_(template<typename T2>, CLS, TYP, BASE, OP, IOP, (const BASE(T2)& x), (x), (x))
#define INHERIT_OP_INPLACE_(CLS, TYP, BASE, IOP)			\
  INHERIT_OP_BASE_INPLACE_(, CLS, TYP, BASE, IOP, (const TYP(T)& x), (*static_cast<const BASE(T)*>(&x)))
#define INHERIT_OP_BASE_SCALAR_(CLS, TYP, BASE, OP, IOP)	\
  INHERIT_OP_BASE_(template<typename T2>, CLS, TYP, BASE, OP, IOP, (const T2& x), (x), (x))
#define INHERIT_OP_(CLS, TYP, BASE, OP, IOP)				\
  INHERIT_OP_BASE_QUANTITY_(CLS, TYP, BASE, operator OP, operator IOP)
#define INHERIT_OP_SCALAR_(CLS, TYP, BASE, OP, IOP)			\
  INHERIT_OP_BASE_QUANTITY_(CLS, TYP, BASE, operator OP, operator IOP)	\
  INHERIT_OP_BASE_SCALAR_(CLS, TYP, BASE, operator OP, operator IOP)

#define INHERIT_CONSTRUCTORS_(CLS, BASE)				\
  CLS() : BASE(T)() {}							\
  CLS(const CLS& rhs) : BASE(T)(rhs) {}					\
  CLS(const T& value) : BASE(T)(value) {}				\
  CLS(const T& value, const Ch* units) : BASE(T)(value, units) {}	\
  CLS(const T& value, const UnitsType& units) : BASE(T)(value, units) {}
#define INHERIT_CONSTRUCTORS_ARRAY_(CLS, BASE)				\
  INHERIT_CONSTRUCTORS_(CLS, BASE)					\
  CLS(const T* value, const SizeType& ndim, const SizeType* shape,	\
      const UnitsType& units = UnitsType()) :				\
  BASE(T)(value, ndim, shape, units) {}					\
  CLS(const T* value, const SizeType& len,				\
      const UnitsType& units = UnitsType()) :				\
    BASE(T)(value, len, units) {}					\
  CLS(const T* value, const SizeType& ndim, const SizeType* shape,	\
      const Ch* units) :						\
    BASE(T)(value, ndim, shape, units) {}				\
  template<SizeType N>							\
  CLS(const T (&value)[N], const UnitsType& units = UnitsType()) :	\
    BASE(T)(value, units) {}						\
  template<SizeType N>							\
  CLS(const T (&value)[N], const Ch* units) :				\
    BASE(T)(value, units) {}						\
  template<SizeType N, SizeType M>					\
  CLS(const T (&value)[N][M], const UnitsType& units = UnitsType()) :	\
    BASE(T)(value, units) {}						\
  template<SizeType N, SizeType M>					\
  CLS(const T (&value)[N][M], const Ch* units) :			\
    BASE(T)(value, units) {}
#define INHERIT_OPERATORS_(CLS, TYP, BASE)				\
  INHERIT_OP_(CLS, TYP, BASE, +, +=)					\
  INHERIT_OP_(CLS, TYP, BASE, -, -=)					\
  INHERIT_OP_SCALAR_(CLS, TYP, BASE, *, *=)				\
  INHERIT_OP_SCALAR_(CLS, TYP, BASE, /, /=)				\
  INHERIT_OP_SCALAR_(CLS, TYP, BASE, %, %=)				\
  INHERIT_OP_BASE_SCALAR_(CLS, TYP, BASE, pow, pow_inplace)		\
  INHERIT_OP_BASE_(, CLS, TYP, BASE, floor, floor_inplace, (), (), ())	\
  INHERIT_OP_INPLACE_(CLS, TYP, BASE, operator=)			\
  TYP(T)* copy() const { return new TYP(T)(*this); }			\
  void* copy_void() const { return (void*)copy(); }			\
  CLS as(const char* units) const {					\
    CLS out(*this);							\
    out.convert_to(units);						\
    return out;								\
  }									\
  CLS as(const UnitsType& units) const {				\
    CLS out(*this);							\
    out.convert_to(units);						\
    return out;								\
  }									\
  CLS as_units_system(const UnitsType& units) const {			\
    CLS out(*this);							\
    out.convert_to_units_system(units);					\
    return out;								\
  }
  
#define GENERIC_QUANTITY_ARRAY_TYPE(TT) GenericQuantityArray<TT, Encoding>
#define GENERIC_QUANTITY_TYPE(TT) GenericQuantity<TT, Encoding>
#define QUANTITY_ARRAY_TYPE(TT) QuantityArray<TT>
#define QUANTITY_TYPE(TT) Quantity<TT>

#if YGGDRASIL_RAPIDJSON_HAS_CXX11
#define ADD_DEFAULT_OPERATOR(DEF, TYP, OP)
#else
template<typename T>
class Quantity;
template<typename T>
class QuantityArray;
#define ADD_DEFAULT_OPERATOR(DEF, TYP, OP)				\
  template<typename T2>							\
  TYP(T)& operator OP (const DEF<T2>& x) {				\
    if (!internal::IsSame<Encoding,UTF8<char> >::Value) {		\
      TYP(T2) tmp = x.template transcode<Encoding>();			\
      return *this OP tmp;						\
    }									\
    return *this OP *((TYP(T2)*)(&x));					\
  }
#endif

#define METHOD_FACTOR_PULL_(UOP, ARGS)					\
  double factor = 1.0;							\
  units_.UOP ARGS;							\
  factor = units_.pull_factor()
#define METHOD_FACTOR_APPLY_						\
  for (SizeType i = 0; i < nelements(); i++) {				\
    value_[i] *= castPrecision<double,T>(factor);			\
  }
#define INPLACE_OP_QUANTITY_BASE_(OP)					\
  YGGDRASIL_RAPIDJSON_ASSERT(is_same_shape(x) || (nelements() == 1) || (x.nelements() == 1)); \
  SizeType N = nelements();						\
  if (is_same_shape(x)) {						\
    for (SizeType i = 0; i < N; i++) {					\
      value_[i] OP castPrecision<T2,T>(x.value()[i]);			\
    }									\
  } else if (N == 1) {							\
    T value0 = value_[0];						\
    *this = x;								\
    N = nelements();							\
    for (SizeType i = 0; i < N; i++) {					\
      value_[i] = value0;						\
    }									\
    this->operator OP(x);						\
  } else if (x.nelements() == 1) {					\
    T2 value0 = x.value()[0];						\
    GenericQuantityArray<T2, Encoding> x_cpy(*this);			\
    for (SizeType i = 0; i < N; i++) {					\
      x_cpy.value_[i] = value0;						\
    }									\
    this->operator OP(x_cpy);						\
  } else {								\
    return *this;							\
  }
#define INPLACE_OP_SCALAR_(OP, IOP)					\
  template<typename T2>							\
  GenericQuantityArray& operator IOP(const T2& x) {			\
    SizeType N = nelements();						\
    for (SizeType i = 0; i < N; i++) {					\
      value_[i] IOP castPrecision<T2,T>(x);				\
    }									\
    return *this;							\
  }									\
  DELEGATE_TO_INPLACE_OP_SCALAR_(GENERIC_QUANTITY_ARRAY_TYPE, OP, IOP)
#define INPLACE_OP_QUANTITY_CONVERT_(OP, IOP)				\
  template<typename T2>							\
  GenericQuantityArray& operator IOP(const GenericQuantityArray<T2, Encoding>& x0) { \
    GenericQuantityArray<T2, Encoding> x = x0.as_units_system(units_);	\
    INPLACE_OP_QUANTITY_BASE_(IOP)					\
    raw_set_delta_from_add(x, #OP);					\
    return *this;							\
  }									\
  DELEGATE_TO_INPLACE_OP_QUANTITY_(GENERIC_QUANTITY_ARRAY_TYPE, OP, IOP) \
  ADD_DEFAULT_OPERATOR(QuantityArray, GENERIC_QUANTITY_ARRAY_TYPE, IOP)	\
  ADD_DEFAULT_OPERATOR(Quantity, GENERIC_QUANTITY_ARRAY_TYPE, IOP)
#define INPLACE_OP_QUANTITY_DIFF_(OP, IOP)                              \
  template<typename T2>							\
  GenericQuantityArray& operator IOP(const GenericQuantity<T2, Encoding>& x) { \
    METHOD_FACTOR_PULL_(operator IOP, (x.units()));			\
    METHOD_FACTOR_APPLY_						\
    SizeType N = nelements();						\
    for (SizeType i = 0; i < N; i++) {					\
      value_[i] IOP castPrecision<T2,T>(x.value());			\
    }									\
    return *this;							\
  }
  // DELEGATE_TO_INPLACE_OP_QUANTITY_(GENERIC_QUANTITY_TYPE, OP, IOP)
#define INPLACE_OP_QUANTITY_COMBINE_(OP, IOP)				\
  template<typename T2>							\
  GenericQuantityArray& operator IOP(const GenericQuantityArray<T2, Encoding>& x) { \
    if (is_same_shape(x)) {						\
      METHOD_FACTOR_PULL_(operator IOP, (x.units()));			\
      METHOD_FACTOR_APPLY_						\
    }									\
    INPLACE_OP_QUANTITY_BASE_(IOP)					\
    return *this;							\
  }									\
  DELEGATE_TO_INPLACE_OP_QUANTITY_(GENERIC_QUANTITY_ARRAY_TYPE, OP, IOP) \
  INPLACE_OP_SCALAR_(OP, IOP)						\
  ADD_DEFAULT_OPERATOR(QuantityArray, GENERIC_QUANTITY_ARRAY_TYPE, IOP)	\
  ADD_DEFAULT_OPERATOR(Quantity, GENERIC_QUANTITY_ARRAY_TYPE, IOP)

#if YGGDRASIL_RAPIDJSON_HAS_CXX11
#define FRIEND_DEFAULT_(CLS)
#define CREATE_DEFAULT_(CLS, TYP, BASE, BASETYP, ENCODING, CTORS)	\
  template<typename T>							\
  using CLS = BASE<T, ENCODING>
#else // YGGDRASIL_RAPIDJSON_HAS_CXX11
#define FRIEND_DEFAULT_(CLS)						\
  friend class CLS<T>;
#define CREATE_DEFAULT_(CLS, TYP, BASE, BASETYP, ENCODING, CTORS)	\
  template<typename T>							\
  class CLS : public BASE<T, ENCODING> {				\
  public:								\
    typedef ENCODING Encoding;						\
    typedef typename BASETYP(T)::Ch Ch;					\
    typedef typename BASETYP(T)::UnitsType UnitsType;			\
    typedef typename BASETYP(T)::ScalarType ScalarType;			\
    CTORS(CLS, BASETYP)							\
    INHERIT_OPERATORS_(CLS, TYP, BASETYP)				\
    TYP(T)& operator=(const BASETYP(T)& other) {			\
      BASETYP(T)::operator=(other);					\
      return *this;							\
    }									\
    operator BASETYP(T)() const {					\
      return BASETYP(T)(*static_cast<const BASETYP(T)*>(this));		\
    }									\
  }
#endif // YGGDRASIL_RAPIDJSON_HAS_CXX11

//! Array quantity with units.
//! \tparam T Type of the underlying scalar.
//! \tparam Encoding Encoding used to store the unit strings.
template<typename T, typename Encoding>
class GenericQuantityArray {
public:
  typedef Encoding EncodingType;    //!< Encoding type from template parameter.
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
  typedef GenericUnits<Encoding> UnitsType; //!< Units type.
  typedef T ScalarType; //!< Scalar type.
  //! \brief Empty constructor.
  GenericQuantityArray() : value_(), units_(), shape_() {}
  //! \brief Create a quantity.
  //! \param value Pointer to an array.
  //! \param ndim Number of dimensions in the array.
  //! \param shape Size of the array in each dimension.
  //! \param units Units instance.
  GenericQuantityArray(const ScalarType* value,
		       const SizeType& ndim, const SizeType* shape,
		       const UnitsType& units = UnitsType()) :
    value_(), units_(units), shape_()
  { _init(value, ndim, shape); }
  //! \brief Create a scalar quantity.
  //! \param value Scalar value.
  //! \param units Units instance.
  GenericQuantityArray(const ScalarType value,
		       const UnitsType& units = UnitsType()) :
    value_(), units_(units), shape_()
  { SizeType len = 1; _init(&value, 1, &len); }
  //! \brief Create a scalar quantity.
  //! \param value Scalar value.
  //! \param units Units string.
  GenericQuantityArray(const ScalarType value, const Ch* units) :
    value_(), units_(UnitsType(units)), shape_()
  { SizeType len = 1; _init(&value, 1, &len); }
  //! \brief Create a quantity.
  //! \param value Pointer to an array.
  //! \param len Number of elements in the 1D array.
  //! \param units Units instance.
  GenericQuantityArray(const ScalarType* value, const SizeType& len,
		const UnitsType& units = UnitsType()) :
    value_(), units_(units), shape_()
  { _init(value, 1, &len); }
  //! \brief Create a quantity from units string.
  //! \param value Pointer to an array.
  //! \param ndim Number of dimensions in the array.
  //! \param shape Size of the array in each dimension.
  //! \param units Units string.
  GenericQuantityArray(const ScalarType* value, const SizeType& ndim, const SizeType* shape,
		const Ch* units) :
    value_(), units_(UnitsType(units)), shape_()
  { _init(value, ndim, shape); }
  //! \brief Create a quantity without units.
  //! \tparam N Number of elements in the array.
  //! \param value 1D array.
  //! \param units Units instance.
  template<SizeType N>
  GenericQuantityArray(const ScalarType (&value)[N], const UnitsType& units = UnitsType()) :
    value_(), units_(units), shape_()
  { SizeType len = N; _init(&(value[0]), 1, &len); }
  //! \brief Constructor from units string.
  //! \tparam N Number of elements in the array.
  //! \param value 1D array.
  //! \param units Units string.
  template<SizeType N>
  GenericQuantityArray(const ScalarType (&value)[N], const Ch* units) :
    value_(), units_(UnitsType(units)), shape_()
  { SizeType len = N; _init(&(value[0]), 1, &len); }
  //! \brief Create a quantity without units.
  //! \tparam N Number of elements in the array in dimension 1.
  //! \tparam M Number of elements in the array in dimension 2.
  //! \param value 1D array.
  //! \param units Units instance.
  template<SizeType N, SizeType M>
  GenericQuantityArray(const ScalarType (&value)[N][M], const UnitsType& units = UnitsType()) :
    value_(), units_(units), shape_()
  { SizeType shape[] = {N, M}; _init(&(value[0][0]), 2, &(shape[0])); }
  //! \brief Constructor from units string.
  //! \tparam N Number of elements in the array in dimension 1.
  //! \tparam M Number of elements in the array in dimension 2.
  //! \param value 1D array.
  //! \param units Units string.
  template<SizeType N, SizeType M>
  GenericQuantityArray(const ScalarType (&value)[N][M], const Ch* units) :
    value_(), units_(UnitsType(units)), shape_()
  { SizeType shape[] = {N, M}; _init(&(value[0][0]), 2, &(shape[0])); }
  //! \brief Copy constructor.
  //! \param other QuantityArray to copy.
  GenericQuantityArray(const GenericQuantityArray<ScalarType, Encoding>& other) :
    value_(), units_(other.units_), shape_()
  { _init(other.value_.data(), other.ndim(), other.shape_.data()); }
  //! \brief Destructor.
  ~GenericQuantityArray() {
    value_.clear();
    shape_.clear();
  }
  //! \brief Copy assignment.
  //! \param other GenericQuantityArray to copy.
  //! \return Copy.
  GenericQuantityArray<ScalarType, Encoding>& operator=(const GenericQuantityArray<ScalarType, Encoding>& other) {
    this->~GenericQuantityArray();
    new (this) GenericQuantityArray(other);
    return *this;
  }
  //! \brief Print instance information to an output stream.
  //! \param os Output stream.
  template<typename Ch2>
  void display(std::basic_ostream<Ch2>& os) const {
    os << 'Q' << 'u' << 'a' << 'n' << 't' << 'i' << 't' << 'y' <<
      'A' << 'r' << 'r' << 'a' << 'y' << '(';
    _write_array(os);
    os << ',' << ' ';
    os << units_;
    os << ')';
  }
  //! \brief Get the quantity array as a string.
  //! \return QuantityArray string.
  std::basic_string<Ch> str() const {
    std::basic_stringstream<Ch> ss;
    ss << *this;
    return ss.str();
  }
  //! \brief Create a copy of the quantity with units in a different encoding.
  //! \tparam DestEncoding Encoding that the copy should use.
  //! \return Copy w/ DestEncoding.
  template<typename DestEncoding>
  GenericQuantityArray<ScalarType, DestEncoding> transcode() const {
    GenericUnits<DestEncoding> new_units = units_.template transcode<DestEncoding>();
    return GenericQuantityArray<ScalarType, DestEncoding>(value(), ndim(), shape(), new_units);
  }
private:
  std::vector<SizeType> _index(const SizeType idx) const {
    SizeType ndim_ = ndim();
    YGGDRASIL_RAPIDJSON_ASSERT(ndim_ > 0);
    std::vector<SizeType> out;
    SizeType prev = 0;
    for (SizeType i = 0; i < (ndim_ - 1); i++) {
      out.push_back((idx - prev) / shape_[i]);
      prev += shape_[i] * out[i];
    }
    out.push_back(idx - prev);
    return out;
  }
  template<typename T2>
  void _init(const T2*, const SizeType, const SizeType*,
	     YGGDRASIL_RAPIDJSON_DISABLEIF((YGGDRASIL_IS_CASTABLE(T2, ScalarType)))) {
    YGGDRASIL_RAPIDJSON_ASSERT(((YGGDRASIL_IS_CASTABLE(T2, ScalarType)::Value)));
  }
  template<typename T2>
  void _init(const T2* value, const SizeType ndim, const SizeType* shape,
	     YGGDRASIL_RAPIDJSON_ENABLEIF((YGGDRASIL_IS_CASTABLE(T2, ScalarType)))) {
    YGGDRASIL_RAPIDJSON_ASSERT(ndim > 0);
    // Shape
    shape_.resize(ndim);
    for (SizeType i = 0; i < ndim; i++)
      shape_[i] = shape[i];
    // Value
    SizeType N = nelements();
    value_.resize(N);
    for (SizeType i = 0; i < N; i++)
      value_[i] = castPrecision<T2,ScalarType>(value[i]);
  }
  template<typename Ch2>
  void _write_array(std::basic_ostream<Ch2>& os) const {
    SizeType ndim_ = ndim();
    SizeType N = nelements();
    std::vector<SizeType> idx;
    for (SizeType i = 0; i < N; i++) {
      idx = _index(i);
      for (SizeType j = 0; j < ndim_; j++) {
	if (idx[j] == 0) {
	  if (j == 0) {
	    if (i == 0)
	      os << '[';
	  } else if (idx[j - 1] == 0) {
	    os << '[';
	  } else {
	    os << ']' << ',' << ' ' << '[';
	  }
	}
      }
      if (idx[ndim_ - 1] > 0)
	os << ',' << ' ';
      os << value_[i];
    }
    for (SizeType i = 0; i < ndim_; i++)
      os << ']';
  }
  template<typename T2>
  static T2 do_conv(const T2& value, const double& factor, const double& offset,
		    YGGDRASIL_RAPIDJSON_DISABLEIF((YGGDRASIL_IS_COMPLEX_TYPE(T2)))) {
    return static_cast<T2>((static_cast<double>(value) - offset) * factor);
  }
  template<typename T2>
  static T2 do_conv(const T2& value, const double& factor, const double& offset,
		    YGGDRASIL_RAPIDJSON_ENABLEIF((YGGDRASIL_IS_COMPLEX_TYPE(T2)))) {
    T2 offset2(static_cast<typename T2::value_type>(offset), 0);
    typename T2::value_type factor2 = static_cast<typename T2::value_type>(factor);
    return (value - offset2) * factor2;
  }
  template<typename T2>
  void raw_set_delta_from_add(const GenericQuantityArray<T2, Encoding>& x,
			      std::string op) {
    // if (op == std::string("%"))
    //   return;
    if ((units_.has_difference() && x.units_.is_difference()) ||
	(units_.is_difference() && x.units_.has_difference()))
      units_.set_delta(kInactiveDelta);
    else if (op == std::string("-") && units_.has_difference())
      units_.set_delta(kActiveDelta);
  }
public:
  //! \brief Get the quantity value without units.
  //! \return Value.
  const ScalarType* value() const { return value_.data(); }
  //! \brief Get the units instance.
  //! \return Units.
  UnitsType units() const { return units_; }
  //! \brief Get the number of dimensions in the array.
  //! \return Number of dimensions.
  SizeType ndim() const { return static_cast<SizeType>(shape_.size()); }
  //! \brief Get the size of the array in each dimension.
  //! \return Array shape.
  const SizeType* shape() const { return shape_.data(); }
  //! \brief Set the quantity value.
  //! \param new_value New quantity value.
  //! \brief Get the total number of elements in the array.
  //! \return The number of elements.
  SizeType nelements() const {
    SizeType out = 0;
    SizeType ndim_ = ndim();
    if (ndim_ > 0) {
      out = 1;
      for (SizeType i = 0; i < ndim_; i++)
	out = out * shape_[i];
    }
    return out;
  }
  template<typename T2>
  void set_value(const T2* new_value, SizeType ndim, SizeType* shape) {
    _init(new_value, ndim, shape);
  }
  //! \brief Set the quantity units without conversion.
  //! \param new_units New quantity units.
  void set_units(const UnitsType& new_units) {
    units_ = new_units;
  }
  //! \brief Get the units string.
  //! \return Units string.
  std::basic_string<Ch> unitsStr() const { return units_.str(); }
  //! \brief Check if another quantity array has the same shape.
  //! \param x QuantityArray for comparison.
  //! \return true if the shapes are equivalent, false otherwise.
  template<typename T2>
  bool is_same_shape(const GenericQuantityArray<T2, Encoding>& x) const {
    SizeType ndim_ = ndim();
    if (ndim_ != x.ndim()) return false;
    for (SizeType i = 0; i < ndim_; i++)
      if (shape_[i] != x.shape()[i]) return false;
    return true;
  }
  //! \brief Check if two quantities are identical. The units must be
  //!   identical, not just compatible.
  //! \param x QuantityArray for comparison.
  //! \return true if the two quantities are identical, false otherwise.
  template<typename T2>
  bool operator==(const GenericQuantityArray<T2, Encoding>& x) const {
    if (units_ != x.units()) return false;
    if (!is_same_shape(x)) return false;
    for (SizeType i = 0; i < nelements(); i++)
      if (!(internal::values_eq(value_[i], x.value()[i]))) return false;
    return true;
  }
  //! \brief Check if two quantities are not identical.
  //! \param x QuantityArray for comparison.
  //! \return true if the two quantities are not identical, false otherwise.
  template<typename T2>
  bool operator!=(const GenericQuantityArray<T2, Encoding>& x) const { return (!(*this==x)); }
  //! \brief Less than comparison operator.
  //! \param x Quantity for comparison.
  //! \return true if less than, false otherwise.
  template<typename T2>
  bool operator<(const GenericQuantityArray<T2, Encoding>& x) const {
    if (!is_same_shape(x)) return false;
    if (units_ != x.units()) {
      if (is_compatible(x.units()))
	return *this < x.as(units_);
      return false;
    }
    for (SizeType i = 0; i < nelements(); i++)
      if (!(internal::values_lt(value_[i], x.value()[i]))) return false;
    return true;
  }
  //! \brief Greater than comparison operator.
  //! \param x QuantityArray for comparison.
  //! \return true if greater than, false otherwise.
  template<typename T2>
  bool operator>(const GenericQuantityArray<T2, Encoding>& x) const {
    if (!is_same_shape(x)) return false;
    if (units_ != x.units()) {
      if (is_compatible(x.units()))
	return *this > x.as(units_);
      return false;
    }
    for (SizeType i = 0; i < nelements(); i++)
      if (!(internal::values_gt(value_[i], x.value()[i]))) return false;
    return true;
  }
  //! \brief Less than or equal to comparison operator.
  //! \param x QuantityArray for comparison.
  //! \return true if less than or equal to, false otherwise.
  template<typename T2>
  bool operator<=(const GenericQuantityArray<T2, Encoding>& x) const { return (!(*this > x)); }
  //! \brief Greater than or equal to comparison operator.
  //! \param x QuantityArray for comparison.
  //! \return true if greater than or equal to, false otherwise.
  template<typename T2>
  bool operator>=(const GenericQuantityArray<T2, Encoding>& x) const { return (!(*this < x)); }
  //! \brief Multiply by a scalar or QuantityArray element by element inplace
  //! \param x Scalar or QuantityArray to multiply by.
  //! \return Result of multiplication.
  INPLACE_OP_QUANTITY_COMBINE_(*, *=)
  INPLACE_OP_QUANTITY_DIFF_(*, *=)
  //! \brief Divide by a scalar or QuantityArray element by element inplace.
  //! \param x Scalar or QuantityArray to divide by.
  //! \return Result of division.
  INPLACE_OP_QUANTITY_COMBINE_(/, /=)
  INPLACE_OP_QUANTITY_DIFF_(/, /=)
  //! \brief Modulo by another quantity in place element by element.
  //! \param x QuantityArray to modulo by.
  //! \return Result of modulo.
  template<typename T2>
  GenericQuantityArray<ScalarType, Encoding>& operator%=(const GenericQuantityArray<T2, Encoding>& x) {
    GenericQuantityArray<ScalarType, Encoding> val = *this / x;
    val.floor_inplace();
    val *= x;
    *this -= val;
    return *this;
  }
  DELEGATE_TO_INPLACE_OP_QUANTITY_(GENERIC_QUANTITY_ARRAY_TYPE, %, %=)
  DELEGATE_TO_INPLACE_OP_QUANTITY_(GENERIC_QUANTITY_TYPE, %, %=)
  //! \brief Modulo by a scalar in place.
  //! \tparam T2 Scalar type.
  //! \param x Scalar to modulo by.
  //! \return Result of division.
  INPLACE_OP_SCALAR_(%, %=)
  ADD_DEFAULT_OPERATOR(QuantityArray, GENERIC_QUANTITY_ARRAY_TYPE, %=)
  //! \brief Add a quantity with compatible units.
  //! \param x QuantityArray to add.
  //! \return Result of addition.
  INPLACE_OP_QUANTITY_CONVERT_(+, +=)
  //! \brief Subtract a quantity with compatible units.
  //! \param x QuantityArray to subtract.
  //! \return Result of subtraction.
  INPLACE_OP_QUANTITY_CONVERT_(-, -=)
  //! \brief Perform floor operation in place.
  //! \return Resulut of floor.
  GenericQuantityArray& floor_inplace() {
    if (YGGDRASIL_IS_FLOAT_TYPE(ScalarType)::Value) {
      SizeType N = nelements();
      for (SizeType i = 0; i < N; i++) {
	value_[i] = internal::value_floor(value_[i]);
      }
    }
    return *this;
  }
  //! \brief Perform floor operation in place.
  //! \return Resulut of floor.
  DELEGATE_TO_INPLACE_(, GenericQuantityArray, GENERIC_QUANTITY_ARRAY_TYPE,
		       floor, floor_inplace, (), ())
  //! \brief Perform power operation in place.
  //! \param x Power to raise this quantity to.
  template<typename T2>
  GenericQuantityArray& pow_inplace(const T2& x,
				    YGGDRASIL_RAPIDJSON_DISABLEIF((YGGDRASIL_IS_COMPLEX_TYPE(T2)))) {
    METHOD_FACTOR_PULL_(pow_inplace, (x));
    SizeType N = nelements();
    for (SizeType i = 0; i < N; i++) {
      value_[i] = std::pow(value_[i], x);
    }
    METHOD_FACTOR_APPLY_
    return *this;
  }
  //! \brief Raise this quantity to a power.
  //! \param x Power to raise this quantity to.
  //! \return Resulting quantity.
  DELEGATE_TO_INPLACE_(template<typename T2>,
		       GenericQuantityArray, GENERIC_QUANTITY_ARRAY_TYPE,
		       pow, pow_inplace,
		       (const T2& x, YGGDRASIL_RAPIDJSON_DISABLEIF((YGGDRASIL_IS_COMPLEX_TYPE(T2)))),
		       (x))
  //! \brief Explicity copy.
  //! \return Copy.
  GenericQuantityArray<ScalarType, Encoding>* copy() const {
    return new GenericQuantityArray<ScalarType, Encoding>(*this);
  }
  //! \brief Explicity copy and cast to void pointer.
  //! \return Copy.
  void* copy_void() const { return (void*)copy(); }
  //! \brief Get the dimensions of this quantity's units.
  //! \return The dimensions of the units.
  Dimension dimension() const { return units_.dimension(); }
  //! \brief Determine if the quantity's units are dimensionless.
  //! \return true if the units are dimensionless, false otherwise.
  bool is_dimensionless() const { return units_.is_dimensionless(); }
  //! \brief Check if another quantity has compatible units with the same
  //!   dimensions.
  //! \param x QuantityArray for comparison.
  //! \return true if the units are compatible, false otherwise.
  template<typename T2>
  bool is_compatible(const GenericQuantityArray<T2, Encoding>& x) const {
    return (dimension() == x.dimension() &&
	    units_.get_delta() == x.units_.get_delta());
  }
  //! \brief Check if a set of units is compatible.
  //! \param x Units for comparison.
  //! \return true if the units are compatible, false otherwise.
  bool is_compatible(const GenericUnits<Encoding>& x) const {
    return (dimension() == x.dimension() &&
	    units_.get_delta() == x.get_delta());
  }
  //! \brief Check if another quantity is equivalent to this one, allowing
  //!    for the possibility that it has different, but compatible, units.
  //! \param x QuantityArray for comparison.
  //! \return true if the two quantities are equivalent, false otherwise.
  template<typename T2>
  bool equivalent_to(const GenericQuantityArray<T2, Encoding>& x) {
    if (!(is_compatible(x)))
      return false;
    return (*this==x.as(units_));
  }
  //! \brief Apply a conversion factor to each element in the array.
  //! \param factor Scale and offset to be applied.
  void apply_conversion_factor(std::vector<double> factor) {
    SizeType N = nelements();
    for (SizeType i = 0; i < N; i++)
      value_[i] = do_conv<ScalarType>(value_[i], factor[0], factor[1]);
  }
  //! \brief Convert the quantity to a different set of units. The new units
  //!   must be compatible with the current ones.
  //! \param units New units.
  void convert_to(const UnitsType& units) {
    std::vector<double> factor = units_.convert_to(units);
    apply_conversion_factor(factor);
  }
  //! \brief Convert quantity to the system used by another set of units in
  //!   place.
  //! \param unitSystem Unit system to convert to.
  void convert_to_units_system(const UnitsType& unitSystem) {
    // UnitsType new_units = units_.as_units_system(unitSystem);
    // std::vector<double> factor = units_.convert_to(new_units);
    std::vector<double> factor = units_.convert_to_units_system(unitSystem);
    apply_conversion_factor(factor);
  }
  //! \brief Create a new quantity by converting this one to a new set of
  //!   compatible units.
  //! \param units New units.
  //! \return New quantity.
  GenericQuantityArray as(const char* units0) const {
    UnitsType units(units0);
    return as(units);
  }
  //! \brief Create a new quantity by converting this one to a new set of
  //!   compatible units.
  //! \param units New units.
  //! \return New quantity.
  GenericQuantityArray as(const UnitsType& units) const {
    GenericQuantityArray out(*this);
    out.convert_to(units);
    return out;
  }
  //! \brief Create a new quantity by converting to a new units system.
  //! \param units New unit system.
  //! \return New quantity.
  GenericQuantityArray as_units_system(const UnitsType& units) const {
    GenericQuantityArray out(*this);
    out.convert_to_units_system(units);
    return out;
  }
private:
  std::vector<T> value_;
  UnitsType units_;
  std::vector<SizeType> shape_;
  template<typename Ch2, typename U, typename Encoding2>
  friend std::basic_ostream<Ch2> & operator << (std::basic_ostream<Ch2> &os, const GenericQuantityArray<U,Encoding2> &x);
  
  FRIEND_DEFAULT_(QuantityArray)
};
template<typename Ch, typename T, typename Encoding>
inline std::basic_ostream<Ch> & operator << (std::basic_ostream<Ch> &os, const GenericQuantityArray<T, Encoding> &x) {
  x._write_array(os);
  os << ' ' << x.units_;
  return os;
}

//! GenericQuantityArray with UTF8 encoding
CREATE_DEFAULT_(QuantityArray, QUANTITY_ARRAY_TYPE,
		GenericQuantityArray, GENERIC_QUANTITY_ARRAY_TYPE,
		UTF8<char>, INHERIT_CONSTRUCTORS_ARRAY_);
  
//! Scalar quantity with units.
//! \tparam T Type of the underlying scalar.
//! \tparam Encoding Encoding used to store the unit strings.
template<typename T, typename Encoding>
class GenericQuantity : public GenericQuantityArray<T, Encoding> {
public:
  typedef GenericQuantityArray<T, Encoding> Base;
  typedef Encoding EncodingType;    //!< Encoding type from template parameter.
  typedef typename Encoding::Ch Ch; //!< Character type from encoding.
  typedef GenericUnits<Encoding> UnitsType; //!< Units type.
  typedef T ScalarType; //!< Scalar type.
  //! \brief Empty constructor.
  GenericQuantity() : Base(_initialize_value<ScalarType>()) {}
  //! \brief Copy constructor.
  GenericQuantity(const GenericQuantity<ScalarType, Encoding>& rhs) :
    Base(rhs.value(), rhs.units()) {}
  //! \brief Create a quantity without units.
  //! \param value Scalar value.
  GenericQuantity(const ScalarType& value) :
    Base(value) {}
  //! \brief Constructor from units string.
  //! \param value Scalar value.
  //! \param units Units string.
  GenericQuantity(const ScalarType& value, const Ch* units) :
    Base(value, units) {}
  //! \brief Constructor from units string.
  //! \param value Scalar value.
  //! \param units Units instance.
  GenericQuantity(const ScalarType& value, const UnitsType& units) :
    Base(value, units) {}
  //! \brief Print instance information to an output stream.
  //! \param os Output stream.
  template<typename Ch2>
  void display(std::basic_ostream<Ch2>& os) const {
    os << 'Q' << 'u' << 'a' << 'n' << 't' << 'i' << 't' << 'y' <<
      '(' << value() << ',' << ' ' << '\"';
    os << this->units();
    os << '\"' << ')';
  }
  //! \brief Get the quantity value without units.
  //! \return Value.
  ScalarType value() const { return Base::value()[0]; }
  //! \brief Set the quantity value.
  //! \param new_value New quantity value.
  template<typename T2>
  void set_value(const T2& new_value,
		 YGGDRASIL_RAPIDJSON_ENABLEIF((YGGDRASIL_IS_CASTABLE(T2, ScalarType))))
  {
    SizeType N = 1;
    Base::set_value(&new_value, 1, &N);
  }
  //! \brief Arithmetic operators
  INHERIT_OPERATORS_(GenericQuantity, GENERIC_QUANTITY_TYPE, GENERIC_QUANTITY_ARRAY_TYPE)
  
private:
  template<typename T1>
  static T1 _initialize_value(YGGDRASIL_RAPIDJSON_DISABLEIF((YGGDRASIL_IS_COMPLEX_TYPE(T1))))
  { return (T1)(0); }
  template<typename T1>
  static T1 _initialize_value(YGGDRASIL_RAPIDJSON_ENABLEIF((YGGDRASIL_IS_COMPLEX_TYPE(T1))))
  { return T1(0.0, 0.0); }
  
  template<typename Ch2, typename U, typename Encoding2>
  friend std::basic_ostream<Ch2> & operator << (std::basic_ostream<Ch2> &os, const GenericQuantity<U,Encoding2> &x);

  FRIEND_DEFAULT_(Quantity)
};
template<typename Ch, typename T, typename Encoding>
inline std::basic_ostream<Ch> & operator << (std::basic_ostream<Ch> &os, const GenericQuantity<T, Encoding> &x) {
  os << x.value() << ' ' << x.units();
  return os;
}

//! GenericQuantity with UTF8 encoding
CREATE_DEFAULT_(Quantity, QUANTITY_TYPE,
		GenericQuantity, GENERIC_QUANTITY_TYPE,
		UTF8<char>, INHERIT_CONSTRUCTORS_);

  template <typename T, typename Encoding>
  void changeUnits(const unsigned char* src_bytes,
		   const GenericUnits<Encoding>& src_units,
		   unsigned char* dst_bytes,
		   const GenericUnits<Encoding>& dst_units,
		   const SizeType nbytes,
		   SizeType nelements=0) {
    if (nelements == 0)
      nelements = nbytes / (SizeType)sizeof(T);
    else
      YGGDRASIL_RAPIDJSON_ASSERT(nelements == (nbytes / (SizeType)sizeof(T)));
    YGGDRASIL_RAPIDJSON_ASSERT(!(nbytes % (SizeType)sizeof(T)));
    GenericQuantityArray<T, Encoding> qa((T*)src_bytes, nelements, src_units);
    qa.convert_to(dst_units);
    memcpy(dst_bytes, qa.value(), (size_t)nelements * sizeof(T));
  }


  template <typename Encoding>
  void changeUnits(YggSubType subtype, SizeType precision,
		   const unsigned char* src_bytes,
		   const GenericUnits<Encoding>& src_units,
		   unsigned char* dst_bytes,
		   const GenericUnits<Encoding>& dst_units,
		   const SizeType nbytes,
		   const SizeType nelements=0) {
    SWITCH_SUBTYPE(subtype, precision, changeUnits, PACK_MACRO(Encoding),
		   (src_bytes, src_units, dst_bytes, dst_units, nbytes, nelements),
		   YGGDRASIL_RAPIDJSON_ASSERT(false));
  }
  
#undef ARRAY_ARRAY_OP
#undef ARRAY_SCALAR_OP
#undef PACK_LUT
#undef DELEGATE_TO_INPLACE_
#undef DELEGATE_TO_INPLACE_OP_QUANTITY_
#undef DELEGATE_TO_INPLACE_OP_SCALAR_
#undef INHERIT_OP_BASE_INPLACE_
#undef INHERIT_OP_BASE_
#undef INHERIT_OP_BASE_QUANTITY_
#undef INHERIT_OP_INPLACE_
#undef INHERIT_OP_BASE_SCALAR_
#undef INHERIT_OP_
#undef INHERIT_OP_SCALAR_
#undef INHERIT_CONSTRUCTORS_
#undef INHERIT_CONSTRUCTORS_ARRAY_
#undef INHERIT_OPERATORS_
#undef GENERIC_QUANTITY_ARRAY_TYPE
#undef GENERIC_QUANTITY_TYPE
#undef QUANTITY_ARRAY_TYPE
#undef QUANTITY_TYPE
#undef ADD_DEFAULT_OPERATOR
#undef METHOD_FACTOR_PULL_
#undef METHOD_FACTOR_APPLY_
#undef INPLACE_OP_QUANTITY_BASE_
#undef INPLACE_OP_SCALAR_
#undef INPLACE_OP_QUANTITY_CONVERT_
#undef INPLACE_OP_QUANTITY_COMBINE_
#undef FRIEND_DEFAULT_
#undef CREATE_DEFAULT_

} // namespace units

#undef OVERRIDE_CXX11
  
#endif // DISABLE_YGGDRASIL_RAPIDJSON

YGGDRASIL_RAPIDJSON_NAMESPACE_END

#endif // YGGDRASIL_RAPIDJSON_UNITS_H_
