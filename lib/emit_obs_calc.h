#ifndef EMIT_OBS_CALC_H
#define EMIT_OBS_CALC_H
#include "geocal/image_ground_connection.h"


namespace Emit {
/****************************************************************//**
  This is used to calculate the OBS data. We have this in C++ just
  for speed. We should perhaps move this in some form into geocal,
  it would be useful to have a reference implementation there.
*******************************************************************/

class EmitObsCalc : public GeoCal::GenericObject {
public:
  EmitObsCalc(const GeoCal::ImageGroundConnection& Igc,
	      const blitz::Array<double, 2>& Latitude,
	      const blitz::Array<double, 2>& Longitude,
	      const blitz::Array<double, 2>& Height);
private:
  blitz::Array<boost::shared_ptr<GeoCal::GroundCoordinate>,2> gc;
  blitz::Array<boost::shared_ptr<GeoCal::GroundCoordinate>,1> pos;
  blitz::Array<boost::shared_ptr<GeoCal::Time>,1> tm;
  // Don't bother with serialization
};
}

#endif

