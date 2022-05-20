from .emit_obs import *
import geocal
from test_support import *

# This is kind of long for a unit test, and we already test this
# at the end-to-end-check level. So normally skip this, although we
# can turn this back on to debug some kind of problem
@slow
def test_generate_obs(igc, isolated_dir, emit_loc):
    g = EmitObs("test_obs.img", igc=igc, loc=emit_loc)
    g.run()
    
    
    
