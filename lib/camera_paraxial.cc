#include "camera_paraxial.h"
#include "emit_serialize_support.h"
#include "geocal/ostream_pad.h"
#include <boost/make_shared.hpp>
using namespace Emit;

template<class Archive>
void ParaxialTransform::serialize
(Archive & ar, const unsigned int version)
{
  EMIT_GENERIC_BASE(ParaxialTransform);
  // Dummy placeholder, just so we can have derived classes call
  // serialization of this. We use to have derived classes "know"
  // that the base class doesn't have anything. But seems better to
  // *always* have base classes do something, so we can add stuff in
  // the future w/o breaking a bunch of code.
  std::string p = "empty";
  ar & GEOCAL_NVP2("placeholder", p);
}

template<class Archive>
void IdentityParaxialTransform::serialize
(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(ParaxialTransform);
}

template<class Archive>
void CaptureParaxialTransform::serialize
(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(ParaxialTransform)
    & GEOCAL_NVP_(predict_x) & GEOCAL_NVP_(predict_y)
    & GEOCAL_NVP_(real_x) & GEOCAL_NVP_(real_y);
}

template<class Archive>
void CameraParaxial::serialize(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(QuaternionCamera)
    & GEOCAL_NVP_(paraxial_transform);
}

EMIT_IMPLEMENT(ParaxialTransform);
EMIT_IMPLEMENT(IdentityParaxialTransform);
EMIT_IMPLEMENT(CameraParaxial);


/// See base class for description
void CameraParaxial::print(std::ostream& Os) const
{
  GeoCal::OstreamPad opad(Os, "    ");
  Os << "CameraParaxial\n";
  opad << *paraxial_transform_ << "\n";
  opad.strict_sync();
  GeoCal::QuaternionCamera::print(opad);
  opad.strict_sync();
}

// See base class for description

void CameraParaxial::dcs_to_focal_plane(int Band,
				    const boost::math::quaternion<double>& Dcs,
				    double& Xfp, double& Yfp) const
{
//---------------------------------------------------------
// Go to paraxial focal plane. Units are millimeters.
//---------------------------------------------------------

  double xf = (focal_length() / Dcs.R_component_4()) * Dcs.R_component_2();
  double yf = (focal_length() / Dcs.R_component_4()) * Dcs.R_component_3();

//-------------------------------------------------------------------------
// Transform paraxial focal plane coordinate to real focal plane coordinate.
// Units are millimeters.
//-------------------------------------------------------------------------
  
  paraxial_transform_->paraxial_to_real(xf, yf, Xfp, Yfp);
}

void CameraParaxial::dcs_to_focal_plane
(int Band,
 const boost::math::quaternion<GeoCal::AutoDerivative<double> >& Dcs,
 GeoCal::AutoDerivative<double>& Xfp, GeoCal::AutoDerivative<double>& Yfp) const
{
//---------------------------------------------------------
// Go to paraxial focal plane. Units are millimeters.
//---------------------------------------------------------

  GeoCal::AutoDerivative<double> xf = 
    (focal_length_with_derivative() / Dcs.R_component_4()) * Dcs.R_component_2();
  GeoCal::AutoDerivative<double> yf = 
    (focal_length_with_derivative() / Dcs.R_component_4()) * Dcs.R_component_3();
  
//-------------------------------------------------------------------------
// Transform paraxial focal plane coordinate to real focal plane coordinate.
// Units are millimeters.
//-------------------------------------------------------------------------
  
  paraxial_transform_->paraxial_to_real(xf, yf, Xfp, Yfp);
}

// See base class for description
boost::math::quaternion<double> 
CameraParaxial::focal_plane_to_dcs(int Band, double Xfp, double Yfp) const
{
//-------------------------------------------------------------------------
/// Convert to paraxial coordinates.
//-------------------------------------------------------------------------

  double xf, yf;
  paraxial_transform_->real_to_paraxial(Xfp, Yfp, xf, yf);

//-------------------------------------------------------------------------
/// Then to detector coordinates look vector.
//-------------------------------------------------------------------------

  return boost::math::quaternion<double>(0, xf, yf, focal_length());
}

boost::math::quaternion<GeoCal::AutoDerivative<double> >
CameraParaxial::focal_plane_to_dcs
(int Band, const GeoCal::AutoDerivative<double>& Xfp, 
 const GeoCal::AutoDerivative<double>& Yfp) const
{
//-------------------------------------------------------------------------
/// Convert to paraxial coordinates.
//-------------------------------------------------------------------------

  GeoCal::AutoDerivative<double> xf, yf;
  paraxial_transform_->real_to_paraxial(Xfp, Yfp, xf, yf);

//-------------------------------------------------------------------------
/// Then to detector coordinates look vector.
//-------------------------------------------------------------------------

  return boost::math::quaternion<GeoCal::AutoDerivative<double> >(0, xf, yf, focal_length_with_derivative());
}


// See base class for description
GeoCal::FrameCoordinate CameraParaxial::focal_plane_to_fc(int Band, double Xfp,
						    double Yfp) const
{
  GeoCal::FrameCoordinate fc =
    GeoCal::QuaternionCamera::focal_plane_to_fc(Band, Xfp, Yfp);
  return fc;
}

// See base class for description

GeoCal::FrameCoordinateWithDerivative CameraParaxial::focal_plane_to_fc
(int Band, const GeoCal::AutoDerivative<double>& Xfp,
 const GeoCal::AutoDerivative<double>& Yfp) const
{
  GeoCal::FrameCoordinateWithDerivative fc =
    GeoCal::QuaternionCamera::focal_plane_to_fc(Band, Xfp, Yfp);
  return fc;
}
  
// See base class for description

void CameraParaxial::fc_to_focal_plane
(const GeoCal::FrameCoordinate& Fc, int Band, double& Xfp, double& Yfp) const
{
  GeoCal::FrameCoordinate t(Fc);
  GeoCal::QuaternionCamera::fc_to_focal_plane(t, Band, Xfp, Yfp);
}

// See base class for description

void CameraParaxial::fc_to_focal_plane
(const GeoCal::FrameCoordinateWithDerivative& Fc, int Band,
 GeoCal::AutoDerivative<double>& Xfp, GeoCal::AutoDerivative<double>& Yfp) const
{
  GeoCal::FrameCoordinateWithDerivative t(Fc);
  GeoCal::QuaternionCamera::fc_to_focal_plane(t, Band, Xfp, Yfp);
}
