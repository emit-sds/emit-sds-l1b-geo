#ifndef EMIT_IGC_COLLECTION_H
#define EMIT_IGC_COLLECTION_H
#include "geocal/ipi_image_ground_connection.h"
#include "igc_array.h"

namespace Emit {
/****************************************************************//**
  This is a collection of EmitImageGroundConnection. This is just
  a IgcArray, with a few convenience functions put in. 
*******************************************************************/

class EmitIgcCollection : public virtual GeoCal::IgcArray {
public:
  EmitIgcCollection()
  { assume_igc_independent_ = false; }
  virtual ~EmitIgcCollection() {}
  virtual void add_igc
  (const boost::shared_ptr<GeoCal::IpiImageGroundConnection>& Igc)
  { igc_list.push_back(Igc);
    if((int) igc_list.size() == 1) {
      add_object(Igc->ipi_ptr()->camera_ptr());
      add_object(Igc->ipi_ptr()->orbit_ptr());
      add_object(Igc->ipi_ptr()->time_table_ptr());
    }
  }
  void nearest_attitude_time_point(const boost::shared_ptr<GeoCal::Time>& T,
				   boost::shared_ptr<GeoCal::Time>& Tbefore,
				   boost::shared_ptr<GeoCal::Time>& Tafter) const;
  virtual void print(std::ostream& Os) const;
private:
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};
}

BOOST_CLASS_EXPORT_KEY(Emit::EmitIgcCollection);
  
#endif
