from .emit_igc import *
import geocal
from test_support import *

def test_emit_igc(orbit_fname, scene_start):
    igc = emit_igc(orbit_fname, scene_start)
    # Pixel resolution should be ~60m, and roughly square
    print("Line resolution: ", geocal.distance(
        igc.ground_coordinate(geocal.ImageCoordinate(500,igc.number_sample/2)),
        igc.ground_coordinate(geocal.ImageCoordinate(500+1,igc.number_sample/2))))
    print("Sample resolution: ", geocal.distance(
        igc.ground_coordinate(geocal.ImageCoordinate(500,igc.number_sample/2)),
        igc.ground_coordinate(geocal.ImageCoordinate(500,igc.number_sample/2+1))))
