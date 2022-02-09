from .aviris_ng_igm import *
import math
import geocal
from test_support import *

def test_aviris_ng_obs(aviris_ng_full_test_data):
    igm = AvirisNgIgm(aviris_ng_full_test_data + "ang20170323t202244_igm", 11)
    print(igm.shape)
    print(igm[0,igm.shape[1]//2])

    
    
