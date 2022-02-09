#include "global_fixture.h"
#include <boost/test/unit_test.hpp>
#include <boost/filesystem.hpp>
#include <cstdlib>
using namespace Emit;

//-----------------------------------------------------------------------
/// Setup for all unit tests.
//-----------------------------------------------------------------------

GlobalFixture::GlobalFixture() 
{
  set_default_value();
}

//-----------------------------------------------------------------------
/// Return the directory landsat 7 data is in. If we don't have the
/// mosaic data, return an empty string to indicated this - tests can
/// use this to skip if the mosaic data isn't available.
//-----------------------------------------------------------------------

std::string GlobalFixture::landsat7_dir() const
{
  if(boost::filesystem::is_directory("/raid22/band5_VICAR"))
    return "/raid22/";
  if(boost::filesystem::is_directory("/beegfs/store/shared/landsat/band5_VICAR"))
    return "/beegfs/store/shared/landsat/";
  return "";
}
