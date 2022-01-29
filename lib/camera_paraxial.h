#ifndef CAMERA_PARAXIAL_H
#define CAMERA_PARAXIAL_H
#include "geocal/quaternion_camera.h"

namespace Emit {

/****************************************************************//**
  Pariaxial Transform to go with CameraParaxial.  
*******************************************************************/
class ParaxialTransform: public GeoCal::Printable<ParaxialTransform> {
public:
  virtual ~ParaxialTransform() {}
  virtual void print(std::ostream& Os) const
  { Os << "ParaxialTransform"; }

  virtual void paraxial_to_real(double Paraxial_x,
				double Paraxial_y, double& Real_x, 
				double& Real_y) const = 0;
  virtual void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& Real_x, 
				GeoCal::AutoDerivative<double>& Real_y) const = 0;
  virtual void real_to_paraxial(double Real_x,
				double Real_y, double& Paraxial_x, 
				double& Paraxial_y) const = 0;
  virtual void real_to_paraxial(const GeoCal::AutoDerivative<double>& Real_x,
		const GeoCal::AutoDerivative<double>& Real_y,
		GeoCal::AutoDerivative<double>& Paraxial_x, 
		GeoCal::AutoDerivative<double>& Paraxial_y) const = 0;
private:
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};

/****************************************************************//**
  Identity ParaxialTransform, e.g., just a linear camera model.
*******************************************************************/
  
class IdentityParaxialTransform: public ParaxialTransform {
public:
  IdentityParaxialTransform() {}
  virtual ~IdentityParaxialTransform() {}
  virtual void print(std::ostream& Os) const
  { Os << "IdentityParaxialTransform"; }

  virtual void paraxial_to_real(double Paraxial_x,
				double Paraxial_y, double& Real_x, 
				double& Real_y) const
  { Real_x = Paraxial_x; Real_y = Paraxial_y; }
  virtual void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& Real_x, 
			GeoCal::AutoDerivative<double>& Real_y) const
  { Real_x = Paraxial_x; Real_y = Paraxial_y; }
  virtual void real_to_paraxial(double Real_x,
				double Real_y, double& Paraxial_x, 
				double& Paraxial_y) const
  { Paraxial_x = Real_x; Paraxial_y = Real_y; }
  virtual void real_to_paraxial(const GeoCal::AutoDerivative<double>& Real_x,
		const GeoCal::AutoDerivative<double>& Real_y,
		GeoCal::AutoDerivative<double>& Paraxial_x, 
		GeoCal::AutoDerivative<double>& Paraxial_y) const
  { Paraxial_x = Real_x; Paraxial_y = Real_y; }
private:
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
  
/****************************************************************//**
  One model for a camera is to capture the nonlinearities by a 
  ParaxialTransform. This maps between the focal plane x, y predicted
  by a linear camera, and the real x,y for the actual camera.

  Note that this is actually a fairly general model, we should
  probably move this into GeoCal. But for now keep separate so we
  don't need to depend on an updated version of geocal.
*******************************************************************/

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
		 FrameDirection Sample_direction = GeoCal::QuaternionCamera::INCREASE_IS_POSITIVE)
  : GeoCal::QuaternionCamera(Frame_to_sc_q, Number_line, Number_sample,
			     Line_pitch, Sample_pitch, Focal_length,
			     Principal_point, Frame_convention,
			     Line_direction, Sample_direction),
    paraxial_transform_(P_transform)
  {
  }
  virtual ~CameraParaxial() {}
  virtual void print(std::ostream& Os) const;
  const boost::shared_ptr<ParaxialTransform>& paraxial_transform()
    const { return paraxial_transform_; }
  void paraxial_transform(const boost::shared_ptr<ParaxialTransform>& v)
  { paraxial_transform_ = v; }
  virtual void dcs_to_focal_plane(int Band,
				  const boost::math::quaternion<double>& Dcs,
				  double& Xfp, double& Yfp) const;
  virtual void dcs_to_focal_plane
  (int Band,
   const boost::math::quaternion<GeoCal::AutoDerivative<double> >& Dcs,
   GeoCal::AutoDerivative<double>& Xfp, 
   GeoCal::AutoDerivative<double>& Yfp) const;
  virtual boost::math::quaternion<double> 
  focal_plane_to_dcs(int Band, double Xfp, double Yfp) const;
  virtual boost::math::quaternion<GeoCal::AutoDerivative<double> > 
  focal_plane_to_dcs(int Band, const GeoCal::AutoDerivative<double>& Xfp, 
		     const GeoCal::AutoDerivative<double>& Yfp) const;
  virtual GeoCal::FrameCoordinate focal_plane_to_fc(int Band, double Xfp, double Yfp)
    const;
  virtual GeoCal::FrameCoordinateWithDerivative focal_plane_to_fc
  (int Band, const GeoCal::AutoDerivative<double>& Xfp,
   const GeoCal::AutoDerivative<double>& Yfp) const;
  virtual void fc_to_focal_plane(const GeoCal::FrameCoordinate& Fc, int Band,
				 double& Xfp, double& Yfp) const;
  virtual void fc_to_focal_plane
  (const GeoCal::FrameCoordinateWithDerivative& Fc, int Band,
   GeoCal::AutoDerivative<double>& Xfp,
   GeoCal::AutoDerivative<double>& Yfp) const;
private:
  boost::shared_ptr<ParaxialTransform> paraxial_transform_;
  CameraParaxial() {}
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
}

BOOST_CLASS_EXPORT_KEY(Emit::ParaxialTransform);
BOOST_CLASS_EXPORT_KEY(Emit::IdentityParaxialTransform);
BOOST_CLASS_EXPORT_KEY(Emit::CameraParaxial);
#endif
