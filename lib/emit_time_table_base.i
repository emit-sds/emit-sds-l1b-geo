// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "emit_time_table_base.h"
%}

%geocal_base_import(time_table)
%base_import(geocal_time)
%include "geocal_time_include.i"

%emit_shared_ptr(Emit::EmitTimeTableBase);
namespace Emit {
class EmitTimeTableBase : public GeoCal::MeasuredTimeTable {
public:
  EmitTimeTableBase(const std::vector<GeoCal::Time>& Time_list,
		    int Number_sample, bool Reverse_image,
		    int Min_line = 0);
  %python_attribute(number_sample, int);
  %python_attribute(reverse_image, bool);
  %pickle_serialization();
};
}

// List of things "import *" will include
%python_export("EmitTimeTableBase")
