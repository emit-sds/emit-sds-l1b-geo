from .aviris_ng_obs import *
import math
import geocal
from test_support import *

def test_aviris_ng_obs(aviris_ng_full_test_data):
    obs = AvirisNgObs(aviris_ng_full_test_data + "ang20170323t202244_obs")
    print(obs.utc_time[0,0])

    
    
