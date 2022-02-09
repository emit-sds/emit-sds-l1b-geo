#include "unit_test_support.h"
#include "emit_orbit.h"
#include "geocal/geodetic.h"
using namespace Emit;

BOOST_FIXTURE_TEST_SUITE(emit_orbit, GlobalFixture)

BOOST_AUTO_TEST_CASE(basic_test)
{
  EmitOrbit orb(unit_test_data_dir() + "l1a_att.nc");
  BOOST_CHECK(orb.spacecraft_x_mostly_in_velocity_direction(orb.min_time() + 3.0));
}

BOOST_AUTO_TEST_CASE(serialization)
{
  boost::shared_ptr<EmitOrbit> orb =
    boost::make_shared<EmitOrbit>(unit_test_data_dir() + "l1a_att.nc");
  std::string d = GeoCal::serialize_write_string(orb);
  if(false)
    std::cerr << d;
  boost::shared_ptr<GeoCal::Orbit> orbr =
    GeoCal::serialize_read_string<GeoCal::Orbit>(d);
  BOOST_CHECK_CLOSE(orb->min_time().pgs(), orbr->min_time().pgs(), 1e-4);
  BOOST_CHECK_CLOSE(orb->max_time().pgs(), orbr->max_time().pgs(), 1e-4);
}

BOOST_AUTO_TEST_SUITE_END()
