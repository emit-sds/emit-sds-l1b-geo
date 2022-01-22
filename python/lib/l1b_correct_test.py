from .l1b_correct import *
from .l1b_geo_generate import L1bGeoGenerate
import geocal
import glob
import sys
from test_support import *

def test_l1b_correct(isolated_dir, l1b_geo_config, emit_igccol):
    t = L1bCorrect(emit_igccol, l1b_geo_config, None)
    t.run()
    
