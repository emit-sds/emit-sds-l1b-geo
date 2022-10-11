#ifndef EMIT_TIME_TABLE_BASE_H
#define EMIT_TIME_TABLE_BASE_H
#include "geocal/time_table.h"

namespace Emit {
/****************************************************************//**
  This is a MeasuredTimeTable, where we also add support for
  reversing the image data. We separate this out from EmitTimeTable
  just to have the interface a little simpler - we already have python
  EmitTimeTable.
*******************************************************************/

class EmitTimeTableBase : public GeoCal::MeasuredTimeTable {
public:
//-------------------------------------------------------------------------
/// Constructor.
//-------------------------------------------------------------------------
  EmitTimeTableBase(const std::vector<GeoCal::Time>& Time_list,
		    int Number_sample, bool Reverse_image,
		    int Min_line = 0)
    : GeoCal::MeasuredTimeTable(Time_list, Min_line),
      nsamp(Number_sample), rimage(Reverse_image)
  {
  }

  virtual GeoCal::ImageCoordinate
  image_coordinate(GeoCal::Time T,
		   const GeoCal::FrameCoordinate& F) const;
  virtual GeoCal::ImageCoordinateWithDerivative 
  image_coordinate_with_derivative(const GeoCal::TimeWithDerivative& T, 
	   const GeoCal::FrameCoordinateWithDerivative& F) const;
  virtual void time(const GeoCal::ImageCoordinate& Ic, GeoCal::Time& T,
		    GeoCal::FrameCoordinate& F) const;
  virtual void time_with_derivative
  (const GeoCal::ImageCoordinateWithDerivative& Ic, 
   GeoCal::TimeWithDerivative& T, 
   GeoCal::FrameCoordinateWithDerivative& F) const;
  int number_sample() const { return nsamp;}
  bool reverse_image() const { return rimage; }
  virtual void print(std::ostream& Os) const;
private:
  int nsamp;
  bool rimage;
  EmitTimeTableBase() {}
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
}

BOOST_CLASS_EXPORT_KEY(Emit::EmitTimeTableBase);
#endif

