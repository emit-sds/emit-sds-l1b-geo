// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "emit_igc_collection.h"
%}
%geocal_base_import(igc_array)
%import "geocal_time.i"
%import "ipi_image_ground_connection.i"
%emit_shared_ptr(Emit::EmitIgcCollection);
namespace Emit {
class EmitIgcCollection : public GeoCal::IgcArray {
public:
  EmitIgcCollection();
  virtual void add_igc
  (const boost::shared_ptr<GeoCal::IpiImageGroundConnection>& Igc);
  void nearest_attitude_time_point(const boost::shared_ptr<GeoCal::Time>& T,
				   boost::shared_ptr<GeoCal::Time>& OUTPUT,
				   boost::shared_ptr<GeoCal::Time>& OUTPUT) const;
  %pickle_serialization();
};
}

// List of things "import *" will include
%python_export("EmitIgcCollection")

