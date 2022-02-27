from .aviris_ng_raw import *
from test_support import *
import pickle
import numpy as np
import numpy.testing as npt

# This actually runs pretty quick if the file is in memory already.
# But it can be a bit slow (as in ~1 minute) if the whole file needs to
# be read.
@slow
def test_aviris_ng_raw(aviris_raw_fname, aviris_frame_meta):
    r = AvirisNgRaw(aviris_raw_fname)
    if False:
        pickle.dump(r, open("aviris_raw.pkl", "wb"))
    # Compare against data that pyortho calculated
    frame_meta_clock = np.array([f[0] for f in aviris_frame_meta])
    clock_avg = r.clock_average(line_average=9)
    npt.assert_allclose(clock_avg, frame_meta_clock)

def test_aviris_ng_gps_table(aviris_gps_fname, aviris_gps_table):
    f = AvirisNgGpsTable(aviris_gps_fname)
    # Check that we read the same data as we read using pyortho, and
    # then saved as a pickle file
    npt.assert_allclose(f.gps_table, aviris_gps_table)

def test_aviris_ng_pps_table(aviris_pps_fname, aviris_pps_table):
    f = AvirisNgPpsTable(aviris_pps_fname)
    # Check that we read the same data as we read using pyortho, and
    # then saved as a pickle file
    npt.assert_allclose(f.pps_table, aviris_pps_table)
    
    
    
    
