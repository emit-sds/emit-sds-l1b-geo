#ifndef EMIT_L1B_IMAGE_H
#define EMIT_L1B_IMAGE_H
#include "geocal/gdal_raster_image.h"
#include "geocal/scale_image.h"
#include "gdal_support.h"

namespace Emit {
/****************************************************************//**
  We ran into an obscure bug in GDAL 3.2.1 where a specific file
  couldn't be opened because GDAL never identified it as ENVI (see
  https://github.jpl.nasa.gov/emit-sds/emit-sds-issue-tracking/issues/110
  for details).

  This class opens a file and forces the ENVI driver to be used. We
  also scale the image, which is needed for doing image matching
*******************************************************************/

class EmitL1bImage : public GeoCal::ScaleImage {
public:
  ~EmitL1bImage() {}
  EmitL1bImage(const std::string& Fname, int Band, double Scale_factor)
    : ScaleImage(open_file_force_envi(Fname, Band), Scale_factor),
      fname(Fname),
      band_(Band)
  {}
  virtual void print(std::ostream& Os) const;
  const std::string& file_name() const { return fname;}
  int band_id() const { return band_;}
private:
  EmitL1bImage() {}
  std::string fname;
  int band_;
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
}

// This is a little more complicated, because we can't really
// construct a object using a default constructor. So we need to
// directly handle the object construction.
namespace boost { namespace serialization {
template<class Archive> 
void save_construct_data(Archive & ar, const Emit::EmitL1bImage* d, 
				const unsigned int version);
template<class Archive>
void load_construct_data(Archive & ar, Emit::EmitL1bImage* d,
			 const unsigned int version);
  }
}

BOOST_CLASS_EXPORT_KEY(Emit::EmitL1bImage);
  
#endif
