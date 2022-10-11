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
};
}

// List of things "import *" will include
%python_export("EmitObsCalc")
