from .emit_kmz_and_quicklook import *
from .emit_loc import EmitLoc
from test_support import *

def test_generate_loc(isolated_dir, test_data, emit_loc, l1b_rdn_fname):
    t = EmitKmzAndQuicklook("test", emit_loc, l1b_rdn_fname)
    t.run()


# TODO Have a test for handling the date line correctly
@skip
def test_cross_date_line(test_data):
    loc_cross_date_line = EmitLoc(test_data + "sample_cross_dateline_loc.img")
    
    
