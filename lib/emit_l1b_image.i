// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "emit_common.i"

%{
#include "emit_l1b_image.h"
%}
%geocal_base_import(scale_image)
%emit_shared_ptr(Emit::EmitL1bImage);
namespace Emit {
class EmitL1bImage : public GeoCal::ScaleImage {
public:
  EmitL1bImage(const std::string& Fname, int Band, double Scale_factor);
  %pickle_serialization();
};
}

// List of things "import *" will include
%python_export("EmitL1bImage")

