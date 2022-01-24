from .l1b_correct import *
from .geo_qa import GeoQa
import geocal
import glob
import sys
from test_support import *
from multiprocessing import Pool

@slow
def test_l1b_correct(isolated_dir, l1b_geo_config, emit_igccol):
    geo_qa = GeoQa("geoqa.nc", "l1b_geo.log")
    t = L1bCorrect(emit_igccol, l1b_geo_config, geo_qa)
    pool = Pool(10)
    igccol_corrected = t.igccol_corrected(pool=pool)
    
