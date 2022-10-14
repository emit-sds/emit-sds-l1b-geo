#include "polynomial_paraxial_transform.h"
#include "emit_serialize_support.h"
using namespace Emit;

template<int D1, int D2> template<class Archive>
void PolynomialParaxialTransform<D1, D2>::serialize
(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(ParaxialTransform)
    & GEOCAL_NVP_(par_to_real) & GEOCAL_NVP_(real_to_par)
    & GEOCAL_NVP_(min_x_real) & GEOCAL_NVP_(max_x_real)
    & GEOCAL_NVP_(min_y_real) & GEOCAL_NVP_(max_y_real)
    & GEOCAL_NVP_(min_x_pred) & GEOCAL_NVP_(max_x_pred)
    & GEOCAL_NVP_(min_y_pred) & GEOCAL_NVP_(max_y_pred);
}

EMIT_IMPLEMENT(PolynomialParaxialTransform_3d_3d);
EMIT_IMPLEMENT(PolynomialParaxialTransform_5d_3d);
EMIT_IMPLEMENT(PolynomialParaxialTransform_3d_5d);
EMIT_IMPLEMENT(PolynomialParaxialTransform_5d_5d);

