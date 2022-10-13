#ifndef EMIT_OBS_CALC_H
#define EMIT_OBS_CALC_H
#include "geocal/image_ground_connection.h"
#include "geocal/dem_map_info.h"

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
	      const blitz::Array<double, 2>& Height,
	      const blitz::Array<double, 2>& Latitude_subpixel,
	      const blitz::Array<double, 2>& Longitude_subpixel);
  void view_angle(blitz::Array<double, 2>& View_azimuth,
		  blitz::Array<double, 2>& View_zenith) const;
  void solar_angle(blitz::Array<double, 2>& Solar_azimuth,
		   blitz::Array<double, 2>& Solar_zenith) const;
  void slope_angle(blitz::Array<double, 2>& Slope,
		   blitz::Array<double, 2>& Aspect,
		   blitz::Array<double, 2>& Cosine_i)  const;
  blitz::Array<double, 2> earth_sun_distance() const;
  blitz::Array<double, 2> seconds_in_day() const;
  blitz::Array<double, 2> path_length() const;
  blitz::Array<double, 2> solar_phase() const;
  int subpixel_scale() const { return gcsubpixel.rows() / gc.rows(); }
  void average_slope_aspect(int i, int j, double& slope, double& aspect) const;
private:
  blitz::Array<boost::shared_ptr<GeoCal::GroundCoordinate>,2> gc;
  blitz::Array<boost::shared_ptr<GeoCal::GroundCoordinate>,2> gcsubpixel;
  blitz::Array<boost::shared_ptr<GeoCal::GroundCoordinate>,1> pos;
  blitz::Array<GeoCal::Time,1> tm;
  blitz::Array<GeoCal::LnLookVector,2> lv, slv;
  boost::shared_ptr<GeoCal::DemMapInfo> dem;
  // Don't bother with serialization
};
}

#endif

