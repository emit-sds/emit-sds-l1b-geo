from .aviris_ng_glt import *
from .aviris_ng_loc import *
from .aviris_ng_igm import *
import math
import geocal
from test_support import *
from multiprocessing import Pool

@slow    
def test_generate_avris_glt(aviris_igc_full, isolated_dir, test_data):
    loc = AvirisNgLoc(test_data + "aviris_ng_full_loc")
    igm = AvirisNgIgm("test_igm", igc=aviris_igc_full,
                      loc = loc)
    glt = AvirisNgGlt("test_glt", igc=aviris_igc_full,
                      loc = loc, igm = igm, resolution=20)
    print(glt.map_info_rotated())
    glt.run()
    

    

    
    
