from .aviris_ng_obs import *
import math
import geocal
from test_support import *

def test_aviris_ng_obs(aviris_ng_full_test_data):
    obs = AvirisNgObs(aviris_ng_full_test_data + "ang20170323t202244_obs",
                      geocal.Time.parse_time("2017-03-23T00:00:00Z"))
    print(obs.time[0])

    
    
