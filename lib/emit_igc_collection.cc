#include "emit_igc_collection.h"
#include "emit_serialize_support.h"
#include "geocal/orbit_offset_correction.h"
using namespace Emit;

template<class Archive>
void EmitIgcCollection::serialize(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(IgcArray);
}

EMIT_IMPLEMENT(EmitIgcCollection);

// See base class for description.
void EmitIgcCollection::print(std::ostream& Os) const
{
  Os << "EmitIgcCollection:\n"
     << "  Number of images: " << number_image() << "\n"
     << "  Images:\n";
  for(int i = 0; i < number_image(); ++i)
    Os << "    " << title(i) << "\n";
  Os << "  Parameter:\n";
  blitz::Array<double, 1> p = parameter_subset();
  std::vector<std::string> pname = parameter_name_subset();
  for(int i = 0; i < p.rows(); ++i)
    Os << "    " << pname[i] << ": " << p(i) << "\n";
}

//-----------------------------------------------------------------------
/// Return the nearest attitude correction time point, so Tbefore <= T
/// <= Tafter. Note that Tbefore or Tafter will be returned as
/// Time::max_valid_time() if there isn't a before/after time.
//-----------------------------------------------------------------------

void EmitIgcCollection::nearest_attitude_time_point(
const boost::shared_ptr<GeoCal::Time>& T,
boost::shared_ptr<GeoCal::Time>& Tbefore,
boost::shared_ptr<GeoCal::Time>& Tafter) const
{
  Tbefore = boost::make_shared<GeoCal::Time>(GeoCal::Time::max_valid_time);
  Tafter = boost::make_shared<GeoCal::Time>(GeoCal::Time::max_valid_time);
  if(number_image() == 0)
    return;
  auto igc = boost::dynamic_pointer_cast<GeoCal::IpiImageGroundConnection>(image_ground_connection(0));
  auto orb = boost::dynamic_pointer_cast<GeoCal::OrbitOffsetCorrection>(igc->ipi()->orbit());
  if(!orb)
    throw GeoCal::Exception("nearest_attitude_time_point only works with OrbitOffsetCorrection");
  std::vector<GeoCal::Time> att_tp = orb->attitude_time_point();
  auto lb = std::lower_bound(att_tp.begin(), att_tp.end(), *T);
  if(lb == att_tp.end() && lb == att_tp.begin())
    // Case with no data
    return;
  if(lb == att_tp.end()) {
    // Case where T is after last att_tp
    Tbefore = boost::make_shared<GeoCal::Time>(*att_tp.rbegin());
    return;
  }
  Tafter = boost::make_shared<GeoCal::Time>(*lb);
  if(fabs(lb->pgs() - T->pgs()) < 1e-3) {
    // Case where we are on top to T
    Tbefore = boost::make_shared<GeoCal::Time>(*lb);
    return;
  }
  if(lb == att_tp.begin())
    // Case where T is before first att_tp
    return;
  --lb;
  Tbefore = boost::make_shared<GeoCal::Time>(*lb);
}
