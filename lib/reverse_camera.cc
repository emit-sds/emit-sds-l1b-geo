#include "reverse_camera.h"
#include "ostream_pad.h"
#include "emit_serialize_support.h"
#include <boost/make_shared.hpp>
using namespace Emit;
using namespace GeoCal;

template<class Archive>
void ReverseCamera::serialize(Archive & ar, const unsigned int version)
{
  GEOCAL_GENERIC_BASE(Camera);
  GEOCAL_GENERIC_BASE(WithParameter);
  GEOCAL_BASE(Camera, WithParameter);
  boost::serialization::void_cast_register<Emit::ReverseCamera, GeoCal::Camera>();
  ar & GEOCAL_NVP_(cam);
}

EMIT_IMPLEMENT(ReverseCamera);

/// See base class for description
void ReverseCamera::print(std::ostream& Os) const
{
  OstreamPad opad(Os, "    ");
  Os << "ReverseCamera\n";
  opad << *original_camera();
  opad.strict_sync();
}

