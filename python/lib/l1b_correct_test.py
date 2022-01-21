from .l1b_correct import *
from .l1b_geo_generate import L1bGeoGenerate
import geocal
import glob
import sys
from test_support import *

def test_l1b_correct(isolated_dir, test_data):
    # Rather than creating the igccol_initial our self, we just
    # use L1bGeoGenerate. It create a l1b_correct
    sys.path.append(test_data + "l1_osp_dir")
    import l1b_geo_config
    l1a_att = glob.glob(f"{test_data}/*l1a_att_*.nc")[0]
    line_time = glob.glob(f"{test_data}/*_l1a_line_time*.nc")
    l1b_rad = glob.glob(f"{test_data}/*_l1b_rdn_*.img")
    t = L1bGeoGenerate(l1b_geo_config, l1a_att, line_time, l1b_rad)
    l1b_correct = t.l1b_correct
    l1b_correct.run()
    
