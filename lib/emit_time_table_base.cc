#include "emit_time_table_base.h"
#include "emit_serialize_support.h"
#include <boost/make_shared.hpp>
using namespace Emit;
using namespace GeoCal;

template<class Archive>
void EmitTimeTableBase::serialize(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(MeasuredTimeTable);
}

EMIT_IMPLEMENT(EmitTimeTableBase);

/// See base class for description
void EmitTimeTableBase::print(std::ostream& Os) const
{
  Os << "EmitTimeTableBase\n"
     << "  Min line:     " << min_line() << "\n"
     << "  Max line:     " << max_line() << "\n"
     << "  Min time:     " << min_time() << "\n"
     << "  Max time:     " << max_time() << "\n";
}

