#ifndef EMIT_ORBIT_H
#define EMIT_ORBIT_H
#include "geocal/hdf_orbit.h"

namespace Emit {
/****************************************************************//**
  This is the Emit orbit (not including any fixes or
  modifications). This is used to read a l1a_arr or l1b_att file.

  This is mostly just a plain vanilla HdfOrbit, we just wrap this up
  in a simple C++ class so serialization maintains the type and we
  have a place to attach python functions (see emit_orbit_extension.py)
*******************************************************************/

class EmitOrbit : public GeoCal::HdfOrbit<GeoCal::Eci,
				     GeoCal::TimeJ2000Creator> {
public:
//-------------------------------------------------------------------------
/// Constructor.
//-------------------------------------------------------------------------
  EmitOrbit(const std::string& Fname)
    : GeoCal::HdfOrbit<GeoCal::Eci, GeoCal::TimeJ2000Creator>
    (Fname, "", "Ephemeris/time_j2000", "Ephemeris/eci_position",
     "Ephemeris/eci_velocity", "Attitude/time_j2000", "Attitude/quaternion")
  {
  }

//-------------------------------------------------------------------------
/// Constructor, has an offset in position like OrbitScCoorOffset.
//-------------------------------------------------------------------------

  EmitOrbit(const std::string& Fname,
		 const blitz::Array<double, 1>& Pos_off)
    : GeoCal::HdfOrbit<GeoCal::Eci, GeoCal::TimeJ2000Creator>
    (Fname, "", "Ephemeris/time_j2000", "Ephemeris/eci_position",
     "Ephemeris/eci_velocity", "Attitude/time_j2000", "Attitude/quaternion"),
    pos_off_(Pos_off.copy())
  {
    if(Pos_off.rows() != 3)
      throw GeoCal::Exception("Pos_off needs to be size 3");
  }
  virtual ~EmitOrbit() {}

  bool spacecraft_x_mostly_in_velocity_direction(GeoCal::Time T) const;

  virtual void print(std::ostream& Os) const;
protected:
  virtual boost::shared_ptr<GeoCal::QuaternionOrbitData>
  orbit_data_create(GeoCal::Time T) const;
private:
  blitz::Array<double, 1> pos_off_;
  EmitOrbit() {}
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
}

BOOST_CLASS_EXPORT_KEY(Emit::EmitOrbit);
#endif

