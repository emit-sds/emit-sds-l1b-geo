from .emit_loc import *
import geocal
from test_support import *

def test_generate_loc(igc, isolated_dir):
    g = EmitLoc("test_loc.img", igc=igc)
    g.run()
    

