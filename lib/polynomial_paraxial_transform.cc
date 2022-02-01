#include "polynomial_paraxial_transform.h"
#include "emit_serialize_support.h"
using namespace Emit;

template<int D1, int D2> template<class Archive>
void PolynomialParaxialTransform<D1, D2>::serialize
(Archive & ar, const unsigned int version)
{
  ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(ParaxialTransform)
    & GEOCAL_NVP_(par_to_real) & GEOCAL_NVP_(real_to_par);
}

EMIT_IMPLEMENT(PolynomialParaxialTransform_3d_3d);
EMIT_IMPLEMENT(PolynomialParaxialTransform_5d_5d);

