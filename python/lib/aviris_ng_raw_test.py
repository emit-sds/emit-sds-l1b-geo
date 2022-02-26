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
    
    
    
