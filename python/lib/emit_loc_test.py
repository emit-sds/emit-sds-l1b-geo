from .emit_loc import *
import geocal
from test_support import *

# Only need to run if we have to regenerate the test data
@skip
def test_create_loc(igc, test_data):
    '''Create a LOC file for use with unit tests. We create
    both a normal one, and one that crosses the dateline (for
    testing handling of that.

    We put this in the test_data directory because of it's size'''
    g = EmitLoc(test_data + "sample_loc.img", igc=igc)
    g.run()
    g = EmitLoc(test_data + "sample_cross_dateline_loc.img", igc=igc)
    g.run()
    t = g.longitude + (-180 - (g.longitude.max() + g.longitude.min()) / 2)
    t[t< -180] = t[t < -180] + 360
    g.longitude[:,:] = t
    

# This is kind of long for a unit test, and we already test this
# at the end-to-end-check level. So normally skip this, although we
# can turn this back on to debug some kind of problem
@slow
def test_generate_loc(igc, isolated_dir):
    # Subset the igc, just so this goes quicker
    tt = igc.ipi.time_table
    ttsub = geocal.MeasuredTimeTable([tt.time_list(i) for i in range(10)])
    igc.ipi.time_table = ttsub
    t = EmitLoc("test_loc.img", igc=igc)
    t.run()
    g = EmitLoc("test_loc.img")
    for ln in range(igc.number_line):
        for smp in range(0, igc.number_sample, 100):
            ic = geocal.ImageCoordinate(ln, smp)
            pt = igc.ground_coordinate(ic)
            assert(geocal.distance(pt, g.ground_coordinate(ln, smp)) < 0.1)
    
def test_cross_date_line(test_data):
    loc = EmitLoc(test_data + "sample_loc.img")
    loc_cross_date_line = EmitLoc(test_data + "sample_cross_dateline_loc.img")
    assert not loc.crosses_date_line
    assert loc_cross_date_line.crosses_date_line
    
    
