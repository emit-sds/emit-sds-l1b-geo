// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "emit_obs_calc.h"
%}

%geocal_base_import(generic_object)
%import "image_ground_connection.i"

%emit_shared_ptr(Emit::EmitObsCalc);
namespace Emit {
class EmitObsCalc : public GeoCal::GenericObject {
public:
  EmitObsCalc(const GeoCal::ImageGroundConnection& Igc,
	      const blitz::Array<double, 2>& Latitude,
	      const blitz::Array<double, 2>& Longitude,
	      const blitz::Array<double, 2>& Height);
  void view_angle(blitz::Array<double, 2>& OUTPUT,
		  blitz::Array<double, 2>& OUTPUT) const;
  void solar_angle(blitz::Array<double, 2>& OUTPUT,
		   blitz::Array<double, 2>& OUTPUT) const;
  blitz::Array<double, 2> earth_sun_distance() const;
  blitz::Array<double, 2> seconds_in_day() const;
  blitz::Array<double, 2> path_length() const;
  blitz::Array<double, 2> solar_phase() const;
};
}

// List of things "import *" will include
%python_export("EmitObsCalc")
