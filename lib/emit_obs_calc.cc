#include "emit_obs_calc.h"

using namespace Emit;
using namespace GeoCal;

EmitObsCalc::EmitObsCalc
(const ImageGroundConnection& Igc,
 const blitz::Array<double, 2>& Latitude,
 const blitz::Array<double, 2>& Longitude,
 const blitz::Array<double, 2>& Height)
  : gc(Igc.number_line(), Igc.number_sample()),
    pos(Igc.number_line()),
    tm(Igc.number_line())
{
  for(int i = 0; i < Igc.number_line(); ++i) {
    tm(i) = boost::make_shared<Time>(Igc.pixel_time(ImageCoordinate(i,0)));
    pos(i) = Igc.cf_look_vector_pos(ImageCoordinate(i,0));
    for(int j = 0; j < gc.cols(); ++j) {
      gc(i,j) = boost::make_shared<Geodetic>(Latitude(i,j),
					     Longitude(i,j), Height(i,j));
    }
  }
}
