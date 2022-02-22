from .aviris_ng_igm import *
from .aviris_ng_loc import *
import math
import geocal
from test_support import *
from multiprocessing import Pool

def test_aviris_ng_igm(aviris_ng_full_test_data):
    igm = AvirisNgIgm(aviris_ng_full_test_data + "ang20170323t202244_igm")
    print(igm.shape)
    print(igm.ground_coordinate(0,igm.shape[2]//2))
    print(geocal.Geodetic(igm.ground_coordinate(0,igm.shape[2]//2)))

@slow    
def test_generate_avris_igm(aviris_igc_full, isolated_dir, test_data):
    loc = AvirisNgLoc(test_data + "aviris_ng_full_loc")
    igm = AvirisNgIgm("test_igm", igc=aviris_igc_full,
                      loc = loc)
    pool = Pool(20)
    igm.run(pool=pool)
    print(igm.ground_coordinate(0,igm.shape[2]//2))
    print(geocal.Geodetic(igm.ground_coordinate(0,igm.shape[2]//2)))
    

    

    
    
