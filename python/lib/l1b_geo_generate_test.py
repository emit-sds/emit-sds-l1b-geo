from .l1b_geo_generate import *
import geocal
import glob
import sys
from test_support import *

def test_l1b_geo_generate(isolated_dir, test_data):
    sys.path.append(test_data + "l1_osp_dir")
    import l1b_geo_config
    l1a_att = glob.glob(f"{test_data}/*l1a_att_*.nc")[0]
    line_time = glob.glob(f"{test_data}/*_l1a_line_time*.nc")
    l1b_rad = glob.glob(f"{test_data}/*_l1b_rdn_*.img")
    t = L1bGeoGenerate(l1b_geo_config, l1a_att, line_time, l1b_rad)
    t.run()
    
