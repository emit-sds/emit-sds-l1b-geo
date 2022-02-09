#include "emit_orbit.h"
#include "emit_serialize_support.h"
#include <boost/make_shared.hpp>
using namespace Emit;
using namespace GeoCal;

template<class Archive>
void EmitOrbit::serialize(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(HdfOrbit_Eci_TimeJ2000)
    & GEOCAL_NVP_(pos_off);
}

EMIT_IMPLEMENT(EmitOrbit);

/// See base class for description
void EmitOrbit::print(std::ostream& Os) const
{
  Os << "EmitOrbit\n"
     << "  File name:        " << file_name() << "\n"
     << "  Min time:         " << min_time() << "\n"
     << "  Max time:         " << max_time() << "\n";
  if(pos_off_.rows() < 3)
    Os << "  Position offset:   None";
  else
    Os << "  Position offset:   ("
       << pos_off_(0) << ", " 
       << pos_off_(1) << ", " 
       << pos_off_(2) << ")\n";
}


/// See base class for description

boost::shared_ptr<GeoCal::QuaternionOrbitData>
EmitOrbit::orbit_data_create(GeoCal::Time T) const
{
  boost::shared_ptr<QuaternionOrbitData> od =
  GeoCal::HdfOrbit<GeoCal::Eci, GeoCal::TimeJ2000Creator>::orbit_data_create(T);
  if(pos_off_.rows() < 3)
    return od;
  ScLookVector slv(pos_off_(0), pos_off_(1), pos_off_(2));
  boost::array<double, 3> pos_off;
  if(od->from_cf()) {
    CartesianFixedLookVector lv = od->cf_look_vector(slv);
    pos_off = lv.look_vector;
  } else {
    CartesianInertialLookVector lv = od->ci_look_vector(slv);
    pos_off = lv.look_vector;
  }
  return boost::make_shared<QuaternionOrbitData>(*od, pos_off,
			 boost::math::quaternion<double>(1,0,0,0));
}

//-------------------------------------------------------------------------
/// Indicate if spacecraft orientation is mostly in the forward
/// direction, or has the 180 degree yaw used sometimes in
/// maneuvers.
//-------------------------------------------------------------------------

bool EmitOrbit::spacecraft_x_mostly_in_velocity_direction
(GeoCal::Time T) const
{
  boost::shared_ptr<OrbitData> od = orbit_data(T);
  CartesianInertialLookVector clv(od->velocity_ci());
  ScLookVector slv = od->sc_look_vector(clv);
  return (slv.look_vector[0] > 0);
}
