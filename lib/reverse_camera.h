#ifndef REVERSE_CAMERA_H
#define REVERSE_CAMERA_H
#include "geocal/camera.h"

namespace Emit {
/****************************************************************//**
  We should be able to reverse the image with our EmitTimeTable,
  however geocal incorrectly assumes that FrameCoordinate and
  ImageCoordinate are the same thing when it is doing IgcRayCaster.
  We should fix that, but in the mean time we can handle the image
  reversal by reversing the camera rather than the time table.
*******************************************************************/

class ReverseCamera : public GeoCal::Camera {
public:
  ReverseCamera(const boost::shared_ptr<GeoCal::Camera>& Cam)
    : cam_(Cam)
  { }

//-----------------------------------------------------------------------
/// Destructor.
//-----------------------------------------------------------------------

  virtual ~ReverseCamera() {}
  virtual double integration_time(int Band) const
  { return cam_->integration_time(Band); }
  virtual int number_band() const
  { return cam_->number_band(); }
  virtual int number_line(int Band) const
  { return cam_->number_line(Band);}
  virtual int number_sample(int Band) const
  { return cam_->number_sample(Band); }
  virtual GeoCal::FrameCoordinate frame_coordinate
  (const GeoCal::ScLookVector& Sl, int Band) const
  {
    GeoCal::FrameCoordinate fc = cam_->frame_coordinate(Sl, Band);
    fc.sample = (cam_->number_sample(Band) - 1) - fc.sample;
    return fc;
  }
  virtual GeoCal::FrameCoordinateWithDerivative 
  frame_coordinate_with_derivative
  (const GeoCal::ScLookVectorWithDerivative& Sl, int Band) const
  {
    GeoCal::FrameCoordinateWithDerivative fc =
      cam_->frame_coordinate_with_derivative(Sl, Band);
    fc.sample = (cam_->number_sample(Band) - 1) - fc.sample;
    return fc;
  }
  virtual double frame_line_coordinate
  (const GeoCal::ScLookVector& Sl, int Band) const
  { return cam_->frame_coordinate(Sl, Band).line; }
  virtual GeoCal::ScLookVector sc_look_vector
  (const GeoCal::FrameCoordinate& F, int Band) const
  {
    GeoCal::FrameCoordinate fc = F;
    fc.sample = (cam_->number_sample(Band) - 1) - fc.sample;
    return cam_->sc_look_vector(fc, Band);
  }
  virtual GeoCal::ScLookVectorWithDerivative 
  sc_look_vector_with_derivative
  (const GeoCal::FrameCoordinateWithDerivative& F, int Band) const
  {
    GeoCal::FrameCoordinateWithDerivative fc = F;
    fc.sample = (cam_->number_sample(Band) - 1) - fc.sample;
    return cam_->sc_look_vector_with_derivative(fc, Band);
  }
  virtual void print(std::ostream& Os) const;
  const boost::shared_ptr<GeoCal::Camera>& original_camera() const
  { return cam_;}
private:
  boost::shared_ptr<GeoCal::Camera> cam_;
  ReverseCamera() {}
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
}

BOOST_CLASS_EXPORT_KEY(Emit::ReverseCamera);
#endif

