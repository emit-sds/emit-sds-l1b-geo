from .aviris_ng_orbit import *
import math
import geocal
from test_support import *

def test_aviris_ng_orbit():
    gps_week = math.floor(geocal.Time.parse_time("2017-03-23T00:00:00Z").gps /
                          (7 * 24 * 60 * 60))
    orb = AvirisNgOrbit(aviris_ng_test_data + "ang20170323t202244_eph_att",
                        gps_week)
    print(orb)

    
    
