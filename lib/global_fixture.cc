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

