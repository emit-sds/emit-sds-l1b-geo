// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "geocal_time.h"
#include "camera_paraxial.h"
%}

%geocal_base_import(generic_object)
%geocal_base_import(quaternion_camera)
%import "geocal_time.i"
%include "geocal_time_include.i"
%import "auto_derivative.i"
%import "look_vector.i"

%emit_shared_ptr(Emit::ParaxialTransform);
%emit_shared_ptr(Emit::IdentityParaxialTransform);
%emit_shared_ptr(Emit::CaptureParaxialTransform);
%emit_shared_ptr(Emit::CameraParaxial);

namespace Emit {

class ParaxialTransform : public GeoCal::GenericObject {
public:
  virtual void paraxial_to_real(double Paraxial_x,
			double Paraxial_y, double& OUTPUT, 
			double& OUTPUT) const = 0;
  virtual void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& OUTPUT, 
			GeoCal::AutoDerivative<double>& OUTPUT) const;
  virtual void real_to_paraxial(double Real_x,
			double Real_y, double& OUTPUT, 
			double& OUTPUT) const;
  virtual void real_to_paraxial(const GeoCal::AutoDerivative<double>& Real_x,
			const GeoCal::AutoDerivative<double>& Real_y,
			GeoCal::AutoDerivative<double>& OUTPUT, 
			GeoCal::AutoDerivative<double>& OUTPUT) const;
  std::string print_to_string() const;
  %pickle_serialization();
};

class IdentityParaxialTransform : public ParaxialTransform {
public:
  IdentityParaxialTransform();
  virtual void paraxial_to_real(double Paraxial_x,
			double Paraxial_y, double& OUTPUT, 
				double& OUTPUT) const;
  virtual void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& OUTPUT, 
			GeoCal::AutoDerivative<double>& OUTPUT) const;
  %pickle_serialization();
};

class CaptureParaxialTransform : public ParaxialTransform {
public:
  CaptureParaxialTransform();
  virtual void paraxial_to_real(double Paraxial_x,
			double Paraxial_y, double& OUTPUT, 
				double& OUTPUT) const;
  virtual void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& OUTPUT, 
			GeoCal::AutoDerivative<double>& OUTPUT) const;
  void clear();
  %python_attribute(predict_x, const std::vector<double>&);
  %python_attribute(predict_y, const std::vector<double>&);
  %python_attribute(real_x, const std::vector<double>&);
  %python_attribute(real_y, const std::vector<double>&);
  %pickle_serialization();
};
  
class CameraParaxial : public GeoCal::QuaternionCamera {
public:
  CameraParaxial(boost::math::quaternion<double> Frame_to_sc_q, 
		 double Number_line, double Number_sample,
		 double Line_pitch, double Sample_pitch,
		 double Focal_length, 
		 const GeoCal::FrameCoordinate& Principal_point,
		 const boost::shared_ptr<ParaxialTransform>& P_transform,
		 FrameConvention Frame_convention = GeoCal::QuaternionCamera::LINE_IS_X,
		 FrameDirection Line_direction = GeoCal::QuaternionCamera::INCREASE_IS_POSITIVE,
		 FrameDirection Sample_direction = GeoCal::QuaternionCamera::INCREASE_IS_POSITIVE);
  %python_attribute_with_set(paraxial_transform, boost::shared_ptr<ParaxialTransform>);
  %pickle_serialization();
};
 
}

// List of things "import *" will include
%python_export("ParaxialTransform", "IdentityParaxialTransform", "CaptureParaxialTransform", "CameraParaxial")

