from .emit_camera import *
from test_support import *
import geocal

def test_emit_camera(orbit_fname):
    cam = EmitCamera()
    assert cam.number_sample(0) == 1280
    
    
    
    



