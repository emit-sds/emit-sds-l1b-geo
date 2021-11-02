from .emit_igc import *
import geocal
from test_support import *

def test_emit_igc(isolated_dir, orbit_fname, time_table_fname,
                  l1b_rdn_fname):
    igc = EmitIgc(orbit_fname, time_table_fname, l1b_rdn_fname)
    # Pixel resolution should be ~60m, and roughly square
    print("Line resolution: ", geocal.distance(
        igc.ground_coordinate(geocal.ImageCoordinate(500,igc.number_sample/2)),
        igc.ground_coordinate(geocal.ImageCoordinate(500+1,igc.number_sample/2))))
    print("Sample resolution: ", geocal.distance(
        igc.ground_coordinate(geocal.ImageCoordinate(500,igc.number_sample/2)),
        igc.ground_coordinate(geocal.ImageCoordinate(500,igc.number_sample/2+1))))
    # Test that we can save a reload this. Note that the python layer
    # gets stripped off, but for our purposes I don't think that matters.
    # We can make these full C++ classes instead of python classes if it
    # matters.
    geocal.write_shelve("igc.xml", igc)
    igc2 = geocal.read_shelve("igc.xml")
    print(igc2)
