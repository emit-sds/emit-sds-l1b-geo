from .l1b_tp_collect import *
from .geo_qa import GeoQa
import geocal
import glob
import sys
from test_support import *
from multiprocessing import Pool

@slow
def test_l1b_tp_collect(isolated_dir, l1_osp_dir, emit_igccol):
    geo_qa = GeoQa("geoqa.nc", "l1b_geo.log")
    t = L1bTpCollect(emit_igccol, l1_osp_dir, geo_qa)
    pool = Pool(10)
    res = t.tpcol(pool=pool)
    print(res)
    
