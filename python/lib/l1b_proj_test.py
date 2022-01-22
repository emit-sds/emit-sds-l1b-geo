from .l1b_proj import *
import geocal
import glob
import sys
from test_support import *
from multiprocessing import Pool

@slow
def test_l1b_proj(isolated_dir, l1b_geo_config, emit_igccol):
    p = L1bProj(emit_igccol, l1b_geo_config, emit_igccol)
    pool = Pool(10)
    res = p.proj(pool=pool)
    print(res)
    
