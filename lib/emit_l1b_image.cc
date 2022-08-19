#include "emit_l1b_image.h"
#include "emit_serialize_support.h"
using namespace Emit;

template<class Archive>
void EmitL1bImage::serialize(Archive & ar, const unsigned int version)
{
  boost::serialization::void_cast_register<Emit::EmitL1bImage,
					   GeoCal::RasterImage>();
  GEOCAL_GENERIC_BASE(RasterImage);
  // Nothing more to do
}

template<class Archive> 
void boost::serialization::save_construct_data
(Archive & ar, const EmitL1bImage* d, const unsigned int version)
{
  // Note although we are using local variables, we don't run into the
  // object serialization tracking problem because all these types are
  // primitive so they aren't tracked.
  std::string file_name = d->file_name();
  int band_id = d->band_id();
  double scale_factor = d->scale_factor();
  ar << GEOCAL_NVP(file_name)
     << GEOCAL_NVP(band_id)
     << GEOCAL_NVP(scale_factor);
}

template<class Archive>
void boost::serialization::load_construct_data
(Archive & ar, EmitL1bImage* d, const unsigned int version)
{
  // Note although we are using local variables, we don't run into the
  // object serialization tracking problem because all these types are
  // primitive so they aren't tracked.
  std::string file_name;
  int band_id;
  double scale_factor;
  ar >> GEOCAL_NVP(file_name)
     >> GEOCAL_NVP(band_id)
     >> GEOCAL_NVP(scale_factor);
  ::new(d)EmitL1bImage(file_name, band_id, scale_factor);
}

EMIT_IMPLEMENT(EmitL1bImage);
template
void boost::serialization::save_construct_data
(polymorphic_oarchive & ar, const EmitL1bImage* d, 
 const unsigned int version);

template
void boost::serialization::load_construct_data
(polymorphic_iarchive & ar, EmitL1bImage* d, const unsigned int version);


// See base class for description.
void EmitL1bImage::print(std::ostream& Os) const
{
  Os << "EmitL1bImage:\n"
     << "  File name:    " << fname << "\n"
     << "  Band:         " << band_ << "\n"
     << "  Scale factor: " << scale_factor() << "\n";
}

