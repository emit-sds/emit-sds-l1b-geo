// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "emit_orbit.h"
%}

%geocal_base_import(hdf_orbit)

%emit_shared_ptr(Emit::EmitOrbit);
namespace Emit {
class EmitOrbit : public GeoCal::HdfOrbit<GeoCal::Eci, GeoCal::TimeJ2000Creator> {
public:
  EmitOrbit(const std::string& Fname);
  EmitOrbit(const std::string& Fname,
	    const blitz::Array<double, 1>& Pos_off);
  bool spacecraft_x_mostly_in_velocity_direction(GeoCal::Time T) const;
  %pickle_serialization();
};
}

// List of things "import *" will include
%python_export("EmitOrbit")
