#include "emit_obs_calc.h"
#include "geocal/ecr.h"
#include "geocal/constant.h"
#include "geocal/geocal_matrix.h"

using namespace Emit;
using namespace GeoCal;

EmitObsCalc::EmitObsCalc
(const ImageGroundConnection& Igc,
 const blitz::Array<double, 2>& Latitude,
 const blitz::Array<double, 2>& Longitude,
 const blitz::Array<double, 2>& Height,
 const blitz::Array<double, 2>& Latitude_subpixel,
 const blitz::Array<double, 2>& Longitude_subpixel)
  : gc(Igc.number_line(), Igc.number_sample()),
    pos(Igc.number_line()),
    tm(Igc.number_line()),
    lv(Igc.number_line(), Igc.number_sample()),
    slv(Igc.number_line(), Igc.number_sample())
{
  dem = boost::dynamic_pointer_cast<DemMapInfo>(Igc.dem_ptr());
  if(!dem)
    throw Exception("Only support DemMapInfo");
  for(int i = 0; i < Igc.number_line(); ++i) {
    tm(i) = Time(Igc.pixel_time(ImageCoordinate(i,0)));
    pos(i) = Igc.cf_look_vector_pos(ImageCoordinate(i,0));
    for(int j = 0; j < gc.cols(); ++j) {
      if(Longitude(i,j) >= 180.0)
	gc(i,j) = boost::make_shared<Geodetic360>(Latitude(i,j),
						  Longitude(i,j), Height(i,j));
      else
	gc(i,j) = boost::make_shared<Geodetic>(Latitude(i,j),
					       Longitude(i,j), Height(i,j));
      CartesianFixedLookVector clv(*gc(i,j), *pos(i));
      lv(i,j) = LnLookVector(clv, *gc(i,j));
      slv(i,j) = LnLookVector::solar_look_vector(tm(i), *gc(i,j));
    }
  }
  int scale = Latitude_subpixel.rows() / Latitude.rows();
  gcsubpixel.resize(Igc.number_line()*scale, Igc.number_sample()*scale);
  for(int i = 0; i < gcsubpixel.rows(); ++i) {
    for(int j = 0; j < gcsubpixel.cols(); ++j) {
      if(Longitude_subpixel(i,j) >= 180.0)
	gcsubpixel(i,j) = boost::make_shared<Geodetic360>(Latitude_subpixel(i,j),
							  Longitude_subpixel(i,j));
      else
	gcsubpixel(i,j) = boost::make_shared<Geodetic>(Latitude_subpixel(i,j),
						       Longitude_subpixel(i,j));
    }
  }
}

//-------------------------------------------------------------------------
/// Calculate view angles. This has been compared to pyorbital, and
/// gives close to the same results.
/// This is from the local north coordinates. Zenith is relative to
/// the local tangent plane. Azimuth is relative to local north. Both
/// are given in degrees. Azimuth is 0 to 360 degrees.
//-------------------------------------------------------------------------

void EmitObsCalc::view_angle
(blitz::Array<double, 2>& View_azimuth,
 blitz::Array<double, 2>& View_zenith) const
{
  View_azimuth.resize(gc.shape());
  View_zenith.resize(gc.shape());
  for(int i = 0; i < View_azimuth.rows(); ++i)
    for(int j = 0; j < View_azimuth.cols(); ++j) {
      View_azimuth(i,j) = atan2(lv(i,j).look_vector[0],
				lv(i,j).look_vector[1]) *
	Constant::rad_to_deg;
      if(View_azimuth(i, j) < 0)
	View_azimuth(i,j) += 360;
      View_zenith(i,j) = acos(lv(i,j).direction()[2]) * Constant::rad_to_deg;
    }
}

//-------------------------------------------------------------------------
/// Calculate solar view angles. This has been compared to pyorbital, and
/// gives close to the same results.
/// This is from the local north coordinates. Zenith is relative to
/// the local tangent plane. Azimuth is relative to local north. Both
/// are given in degrees. Azimuth is 0 to 360 degrees.
//-------------------------------------------------------------------------

void EmitObsCalc::solar_angle
(blitz::Array<double, 2>& Solar_azimuth,
 blitz::Array<double, 2>& Solar_zenith) const
{
  Solar_azimuth.resize(gc.shape());
  Solar_zenith.resize(gc.shape());
  for(int i = 0; i < Solar_azimuth.rows(); ++i)
    for(int j = 0; j < Solar_azimuth.cols(); ++j) {
      Solar_azimuth(i,j) = atan2(slv(i,j).look_vector[0],
				 slv(i,j).look_vector[1]) *
	Constant::rad_to_deg;
      if(Solar_azimuth(i, j) < 0)
	Solar_azimuth(i,j) += 360;
      Solar_zenith(i,j) = acos(slv(i,j).direction()[2]) * Constant::rad_to_deg;
    }
}

//-------------------------------------------------------------------------
/// Calculate path length. This is in meters.
//-------------------------------------------------------------------------

blitz::Array<double, 2> EmitObsCalc::path_length() const
{
  blitz::Array<double, 2> plength(gc.shape());
  for(int i = 0; i < plength.rows(); ++i)
    for(int j = 0; j < plength.cols(); ++j) {
      plength(i,j) = distance(*gc(i,j), *pos(i));
    }
  return plength;
}

//-------------------------------------------------------------------------
/// Calculate earth sun distance
//-------------------------------------------------------------------------

blitz::Array<double, 2> EmitObsCalc::earth_sun_distance() const
{
  blitz::Range ra = blitz::Range::all();
  blitz::Array<double, 2> edist(gc.shape());
  for(int i = 0; i < edist.rows(); ++i)
    edist(i,ra) = Ecr::solar_distance(tm(i));
  return edist;
}

//-------------------------------------------------------------------------
/// Calculate seconds in the day for the time the data was
/// acquired. Kind of an odd thing to calculate, but the utc_time is
/// one of the fields in the OBS file.
//-------------------------------------------------------------------------

blitz::Array<double, 2> EmitObsCalc::seconds_in_day() const
{
  blitz::Range ra = blitz::Range::all();
  blitz::Array<double, 2> sinday(gc.shape());
  for(int i = 0; i < sinday.rows(); ++i) {
    std::string t = tm(i).to_string();
    t = t.substr(0,t.find("T")) + "T00:00:00Z";
    sinday(i,ra) = tm(i) - Time::parse_time(t);
  }
  return sinday;
}

//-------------------------------------------------------------------------
/// Calculate solar phase angle
//-------------------------------------------------------------------------

blitz::Array<double, 2> EmitObsCalc::solar_phase() const
{
  blitz::Array<double, 2> sphase(gc.shape());
  for(int i = 0; i < sphase.rows(); ++i)
    for(int j = 0; j < sphase.cols(); ++j)
      sphase(i,j) = acos(dot(lv(i,j).direction(), slv(i,j).direction())) *
	Constant::rad_to_deg;
  return sphase;
}

//-------------------------------------------------------------------------
/// Calculate slope, aspect and cosine_i angles. 
//-------------------------------------------------------------------------

void EmitObsCalc::slope_angle
(blitz::Array<double, 2>& Slope,
 blitz::Array<double, 2>& Aspect,
 blitz::Array<double, 2>& Cosine_i) const
{
  Slope.resize(gc.shape());
  Aspect.resize(gc.shape());
  Cosine_i.resize(gc.shape());
  for(int i = 0; i < Slope.rows(); ++i)
    for(int j = 0; j < Slope.cols(); ++j) {
      average_slope_aspect(i,j, Slope(i,j), Aspect(i,j));
      boost::array<double, 3> slope_dir;
      slope_dir[0] = sin(Slope(i,j) * Constant::deg_to_rad) *
	sin(Aspect(i,j) * Constant::deg_to_rad);
      slope_dir[1] = sin(Slope(i,j) * Constant::deg_to_rad) *
	cos(Aspect(i,j) * Constant::deg_to_rad);
      slope_dir[2] = cos(Slope(i,j) * Constant::deg_to_rad);
      Cosine_i(i,j) = dot(slope_dir, slv(i,j).direction());
    }
}

//-------------------------------------------------------------------------
/// Calculate slope/aspect for all the subpixel covering pixel i,j,
/// and average the values.
//-------------------------------------------------------------------------

void EmitObsCalc::average_slope_aspect(int i, int j,
				       double& slope, double& aspect) const
{
  blitz::Array<double, 2> slope_subpixel(subpixel_scale(), subpixel_scale());
  blitz::Array<double, 2> aspect_subpixel(slope_subpixel.shape());
  for(int i2 = 0; i2 < slope_subpixel.rows(); ++i2)
    for(int j2 = 0; j2 < slope_subpixel.cols(); ++j2)
      dem->slope_and_aspect(*gcsubpixel(i * subpixel_scale() + i2,
					j*subpixel_scale() + j2),
			    slope_subpixel(i2, j2), aspect_subpixel(i2,j2));
  // Handle sign change in aspect
  if(blitz::max(aspect_subpixel) - blitz::min(aspect_subpixel) > 100)
    aspect_subpixel = blitz::where(aspect_subpixel < 100, aspect_subpixel+360,
				   aspect_subpixel);
  slope = blitz::mean(slope_subpixel);
  aspect = blitz::mean(aspect_subpixel);
  if(aspect > 360)
    aspect -= 360;
}
