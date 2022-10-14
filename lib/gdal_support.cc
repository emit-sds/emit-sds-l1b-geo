#include "gdal_support.h"
#include <boost/make_shared.hpp>

using namespace Emit;


//-------------------------------------------------------------------------
/// We ran into an obscure bug in GDAL 3.2.1 where a specific file
/// couldn't be opened because GDAL never identified it as ENVI (see
/// https://github.jpl.nasa.gov/emit-sds/emit-sds-issue-tracking/issues/110
/// for details).
///
/// This function opens a file and forces the ENVI driver to be used.
//-------------------------------------------------------------------------

boost::shared_ptr<GeoCal::GdalRasterImage>
Emit::open_file_force_envi(const std::string& Fname, int Band)
{
  GeoCal::GdalRegister::gdal_register();
  std::vector<std::string> d_string;
  std::vector<char*> d;
  d_string.push_back("ENVI");
  d.push_back(const_cast<char*>(d_string.back().c_str()));
  d.push_back(0);
  boost::shared_ptr<GDALDataset> data_set((GDALDataset *) GDALOpenEx(Fname.c_str(), GA_ReadOnly,&(*d.begin()),0,0));
  return boost::make_shared<GeoCal::GdalRasterImage>(data_set, Band);
}

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

