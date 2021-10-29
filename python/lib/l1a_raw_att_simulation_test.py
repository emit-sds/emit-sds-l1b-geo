from .l1a_raw_att_simulation import *
from test_support import *
import geocal

def test_l1a_raw_att_simulate(isolated_dir):
    t = geocal.Time.parse_time("2020-10-01T12:01:02.00Z");
    orb = geocal.KeplerOrbit(t, t + 1000)
    l1a_raw_att_sim = L1aRawAttSimulate(orb, t+1, t + 900)
    l1a_raw_att_sim.create_file("orbit.nc")
    
    
    
    



