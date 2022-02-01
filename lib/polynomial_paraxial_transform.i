// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "geocal_time.h"
#include "polynomial_paraxial_transform.h"
%}

%emit_base_import(camera_paraxial)

%emit_shared_ptr(Emit::ParaxialTransform);
%emit_shared_ptr(Emit::IdentityParaxialTransform);
%emit_shared_ptr(Emit::CaptureParaxialTransform);
%emit_shared_ptr(Emit::CameraParaxial);

namespace Emit {

template<int D1, int D2> class PolynomialParaxialTransform :
  public ParaxialTransform {
public:
  PolynomialParaxialTransform();
  virtual void paraxial_to_real(double Paraxial_x,
			double Paraxial_y, double& OUTPUT, 
				double& OUTPUT) const;
  virtual void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& OUTPUT, 
			GeoCal::AutoDerivative<double>& OUTPUT) const;
  %python_attribute(par_to_real, blitz::Array<double, 2>&);
  %python_attribute(real_to_par, blitz::Array<double, 2>&);
  %pickle_serialization();
};
}

%emit_shared_ptr(Emit::PolynomialParaxialTransform<3, 3>);
%template(PolynomialParaxialTransform_3d_3d) Emit::PolynomialParaxialTransform<3, 3>;
%emit_shared_ptr(Emit::PolynomialParaxialTransform<5, 5>);
%template(PolynomialParaxialTransform_5d_5d) Emit::PolynomialParaxialTransform<5, 5>;

// List of things "import *" will include
%python_export("PolynomialParaxialTransform_3d_3d", "PolynomialParaxialTransform_5d_5d")

