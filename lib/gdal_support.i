// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "gdal_support.h"
#include <geocal/ecr.h>
#include <geocal/image_ground_connection.h>
%}

%import "gdal_raster_image.i"

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


