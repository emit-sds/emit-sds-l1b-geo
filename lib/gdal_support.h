#ifndef EMIT_GDAL_SUPPORT_H
#define EMIT_GDAL_SUPPORT_H
#include <geocal/gdal_raster_image.h>

namespace Emit {
  void set_file_description(const boost::shared_ptr<GeoCal::GdalRasterImage>& Img,
			    const std::string& Desc);
  void set_band_description(const boost::shared_ptr<GeoCal::GdalRasterImage>& Img,
			    const std::string& Desc);
  void set_band_metadata(const boost::shared_ptr<GeoCal::GdalRasterImage>& Img,
			 const std::string& M, const std::string& Val,
			 const std::string& Domain = "ENVI");
  boost::shared_ptr<GeoCal::GdalRasterImage>
  open_file_force_envi(const std::string& Fname, int Band);
}
#endif
