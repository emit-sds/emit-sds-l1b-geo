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
		    int Min_line = 0)
    : GeoCal::MeasuredTimeTable(Time_list, Min_line)
  {
  }

  virtual void print(std::ostream& Os) const;
private:
  EmitTimeTableBase() {}
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
}

BOOST_CLASS_EXPORT_KEY(Emit::EmitTimeTableBase);
#endif

