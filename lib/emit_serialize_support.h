#include "geocal/geocal_serialize_support.h"

#define EMIT_IMPLEMENT(NAME) \
BOOST_CLASS_EXPORT_IMPLEMENT(Emit::NAME); \
template void NAME::serialize(boost::archive::polymorphic_oarchive& ar, \
				    const unsigned int version); \
template void NAME::serialize(boost::archive::polymorphic_iarchive& ar, \
				    const unsigned int version);
#define EMIT_SPLIT_IMPLEMENT(NAME) \
BOOST_CLASS_EXPORT_IMPLEMENT(Emit::NAME); \
template void NAME::save(boost::archive::polymorphic_oarchive& ar, \
				    const unsigned int version) const; \
template void NAME::load(boost::archive::polymorphic_iarchive& ar, \
				    const unsigned int version);

#define EMIT_BASE(NAME,BASE) boost::serialization::void_cast_register<Emit::NAME, Emit::BASE>();
#define EMIT_GENERIC_BASE(NAME) boost::serialization::void_cast_register<Emit::NAME, GeoCal::GenericObject>();
