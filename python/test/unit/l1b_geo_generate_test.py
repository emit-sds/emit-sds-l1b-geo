from .l1b_geo_generate import *
import geocal
import glob
import sys
from test_support import *

# This is kind of long for a unit test, and we already test this
# at the end-to-end-check level. So normally skip this, although we
# can turn this back on to debug some kind of problem
@slow
def test_l1b_geo_generate(isolated_dir, test_data, l1_osp_dir):
    l1a_att = glob.glob(f"{test_data}/*_o80000_l1a_att_*.nc")[0]
    line_time = glob.glob(f"{test_data}/*_o80000_*_l1a_line_time*.nc")
    l1b_rad = glob.glob(f"{test_data}/*_o80000_*_l1b_rdn_*.img")
    t = L1bGeoGenerate(l1_osp_dir, l1a_att, line_time, l1b_rad)
    t.run()
    
