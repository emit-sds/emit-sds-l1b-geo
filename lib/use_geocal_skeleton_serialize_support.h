#include "geocal/geocal_serialize_support.h"

#define USE_GEOCAL_SKELETON_IMPLEMENT(NAME) \
BOOST_CLASS_EXPORT_IMPLEMENT(UseGeoCalSkeleton::NAME); \
template void NAME::serialize(boost::archive::polymorphic_oarchive& ar, \
				    const unsigned int version); \
template void NAME::serialize(boost::archive::polymorphic_iarchive& ar, \
				    const unsigned int version);
#define USE_GEOCAL_SKELETON_SPLIT_IMPLEMENT(NAME) \
BOOST_CLASS_EXPORT_IMPLEMENT(UseGeoCalSkeleton::NAME); \
template void NAME::save(boost::archive::polymorphic_oarchive& ar, \
				    const unsigned int version) const; \
template void NAME::load(boost::archive::polymorphic_iarchive& ar, \
				    const unsigned int version);

#define USE_GEOCAL_SKELETON_BASE(NAME,BASE) boost::serialization::void_cast_register<UseGeoCalSkeleton::NAME, UseGeoCalSkeleton::BASE>();
#define USE_GEOCAL_SKELETON_GENERIC_BASE(NAME) boost::serialization::void_cast_register<UseGeoCalSkeleton::NAME, GeoCal::GenericObject>();
