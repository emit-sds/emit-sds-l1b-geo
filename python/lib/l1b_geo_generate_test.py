from .l1b_geo_generate import *
import geocal
from test_support import *

def test_generate_loc(igc, isolated_dir):
    g = L1bGeoGenerate(igc, ".")
    g.generate_loc("test_loc.img")

def test_generate_obs(igc, isolated_dir, l1b_loc):
    g = L1bGeoGenerate(igc, ".")
    g.generate_obs("test_obs.img", l1b_loc)

def test_emit_file_name(igc):
    g = L1bGeoGenerate(igc, ".")
    print(g.emit_file_name("l1b_loc"))
    
