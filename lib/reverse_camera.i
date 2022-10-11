// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "geocal_time.h"
#include "reverse_camera.h"
%}

%geocal_base_import(camera)
%import "frame_coordinate.i"
%import "look_vector.i"
%import "geocal_time.i"
%include "geocal_time_include.i"
%import "array_ad.i"

%emit_shared_ptr(Emit::ReverseCamera);
namespace Emit {
%feature("notabstract") ReverseCamera;
class ReverseCamera : public GeoCal::Camera {
public:
  ReverseCamera(const boost::shared_ptr<GeoCal::Camera>& Cam);
  virtual int number_line(int Band) const;
  virtual int number_sample(int Band) const;
  virtual GeoCal::FrameCoordinate frame_coordinate(const GeoCal::ScLookVector& Sl, 
					   int Band) const;
  virtual GeoCal::FrameCoordinateWithDerivative 
  frame_coordinate_with_derivative(const GeoCal::ScLookVectorWithDerivative& Sl, 
		   int Band) const;
  virtual GeoCal::ScLookVector sc_look_vector(const GeoCal::FrameCoordinate& F, 
				      int Band) const;
  virtual GeoCal::ScLookVectorWithDerivative 
  sc_look_vector_with_derivative(const GeoCal::FrameCoordinateWithDerivative& F, 
				 int Band) const;
  %python_attribute(original_camera, boost::shared_ptr<GeoCal::Camera>);
  %pickle_serialization();
};
}

// List of things "import *" will include
%python_export("ReverseCamera")
