from .l1b_geo_generate import *
import geocal
from test_support import *

def test_generate_loc(igc, isolated_dir):
    g = L1bGeoGenerate(igc)
    g.generate_loc("test_loc.img")
