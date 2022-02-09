#include "gdal_support.h"

using namespace Emit;


//-------------------------------------------------------------------------
/// GeoCal doesn't happen to have support for writing a file
/// description. This should probably migrate into geocal at some
/// point, but for now just provide our own function in Emit for this.
//-------------------------------------------------------------------------

void Emit::set_file_description
(const boost::shared_ptr<GeoCal::GdalRasterImage>& Img,
 const std::string& Desc)
{
  Img->data_set()->SetDescription(Desc.c_str());
}

//-------------------------------------------------------------------------
/// GeoCal doesn't happen to have support for writing a band
/// description. This should probably migrate into geocal at some
/// point, but for now just provide our own function in Emit for this.
//-------------------------------------------------------------------------

void Emit::set_band_description
(const boost::shared_ptr<GeoCal::GdalRasterImage>& Img,
 const std::string& Desc)
{
  Img->raster_band().SetDescription(Desc.c_str());
}

//-------------------------------------------------------------------------
/// GeoCal doesn't happen to have support for writing a band
/// (as opposed to file) metadata. This should probably migrate into
/// geocal at some
/// point, but for now just provide our own function in Emit for this.
///
/// NOTE: It turns out that gdal (as of 2.4) doesn't support band
/// metadata directly in the ENVI header. This is different than
/// description, which it does support. We can easily work around this
/// by treating thinks like wavelength as a file level item, and just
/// directly create the "{ wavelength 1, wavelength 2, ...}" string in
/// ENVI. GDAL does put this in the auxilary .xml file, but we don't
/// want to depend on that.
//-------------------------------------------------------------------------

void Emit::set_band_metadata
(const boost::shared_ptr<GeoCal::GdalRasterImage>& Img,
 const std::string& M, const std::string& Val,
 const std::string& Domain)
{
  Img->raster_band().SetMetadataItem(M.c_str(), Val.c_str(), Domain.c_str());
}

