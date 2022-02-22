from .aviris_ng_igm import *
import math
import geocal
from test_support import *

def test_aviris_ng_obs(aviris_ng_full_test_data):
    igm = AvirisNgIgm(aviris_ng_full_test_data + "ang20170323t202244_igm")
    print(igm.shape)
    print(igm.ground_coordinate(0,igm.shape[2]//2))
    print(geocal.Geodetic(igm.ground_coordinate(0,igm.shape[2]//2)))


    

    
    
