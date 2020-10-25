// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

%include "use_geocal_skeleton_common.i"

%{
#include "ecostress_scan_mirror.h"
%}

%base_import(generic_object)
%import "image_coordinate.i"

%use_geocal_skeleton_shared_ptr(UseGeoCalSkeleton::EcostressScanMirror);
namespace UseGeoCalSkeleton {
class EcostressScanMirror : public GeoCal::GenericObject {
public:
  EcostressScanMirror(double Scan_start = -25.5, double Scan_end = 25.5,
		      int Number_sample = 5400);
  double scan_mirror_angle(double Ic_sample) const;
  boost::math::quaternion<double>
    rotation_quaterion(double Ic_sample) const;
  %python_attribute(scan_start, double);
  %python_attribute(scan_end, double);
  %python_attribute(number_sample, int);
  std::string print_to_string() const;
  %pickle_serialization();
};
}

