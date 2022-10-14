#include "emit_time_table_base.h"
#include "emit_serialize_support.h"
#include <boost/make_shared.hpp>
using namespace Emit;
using namespace GeoCal;

template<class Archive>
void EmitTimeTableBase::serialize(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(MeasuredTimeTable)
    & GEOCAL_NVP(nsamp) & GEOCAL_NVP(rimage);
}

EMIT_IMPLEMENT(EmitTimeTableBase);

/// See base class for description
void EmitTimeTableBase::print(std::ostream& Os) const
{
  Os << "EmitTimeTableBase\n"
     << "  Number sample: " << number_sample() << "\n"
     << "  Reverse image: " << reverse_image() << "\n"
     << "  Min line:      " << min_line() << "\n"
     << "  Max line:      " << max_line() << "\n"
     << "  Min time:      " << min_time() << "\n"
     << "  Max time:      " << max_time() << "\n";
}

ImageCoordinate EmitTimeTableBase::image_coordinate
(Time T, const FrameCoordinate& F) const
{
  ImageCoordinate ic = MeasuredTimeTable::image_coordinate(T, F);
  if(rimage)
    ic.sample = (nsamp - 1) - ic.sample;
  return ic;
}

ImageCoordinateWithDerivative 
EmitTimeTableBase::image_coordinate_with_derivative
(const TimeWithDerivative& T, 
 const FrameCoordinateWithDerivative& F) const
{
  ImageCoordinateWithDerivative ic =
    MeasuredTimeTable::image_coordinate_with_derivative(T, F);
  if(rimage)
    ic.sample = (nsamp - 1) - ic.sample;
  return ic;
}

void EmitTimeTableBase::time(const ImageCoordinate& Ic, Time& T,
			     FrameCoordinate& F) const
{
  ImageCoordinate ic2(Ic);
  if(rimage)
    ic2.sample = (nsamp - 1) - ic2.sample;
  MeasuredTimeTable::time(ic2, T, F);
}

void EmitTimeTableBase::time_with_derivative
(const ImageCoordinateWithDerivative& Ic, 
 TimeWithDerivative& T, 
 FrameCoordinateWithDerivative& F) const
{
  ImageCoordinateWithDerivative ic2(Ic);
  if(rimage)
    ic2.sample = (nsamp - 1) - ic2.sample;
  MeasuredTimeTable::time_with_derivative(ic2, T, F);
}
