from .l1b_tp_collect import *
import geocal
import glob
import sys
from test_support import *

def test_l1b_tp_collect(isolated_dir, l1b_geo_config, emit_igccol):
    t = L1bTpCollect(emit_igccol, l1b_geo_config, emit_igccol)
    
