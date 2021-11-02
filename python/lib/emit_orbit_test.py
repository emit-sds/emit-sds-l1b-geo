from .emit_orbit import *
from test_support import *
import geocal

def test_emit_orbit(orbit_fname):
    orb = EmitOrbit(orbit_fname)
    #print(orb)
    # Trivial test, we are just making sure we can access the orbit
    assert orb.max_time - orb.min_time > 10.0

def test_write_emit_orbit(isolated_dir):
    t = geocal.Time.parse_time("2020-10-01T12:01:02.00Z");
    orb = geocal.KeplerOrbit(t, t + 1000)
    EmitOrbit.write_file("orbit.nc", orb, t+1, t+900)
    orb = EmitOrbit("orbit.nc")
    # We add 1 second padding at the beginning of the orbit to allow
    # for interpolation
    assert abs(orb.min_time - t) < 0.01
    assert abs(orb.max_time - (t+900)) < 0.01
    
    
    
    



