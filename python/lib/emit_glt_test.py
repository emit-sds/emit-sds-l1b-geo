from .emit_glt import *
from .emit_loc import EmitLoc
from test_support import *

def test_generate_glt(isolated_dir, emit_loc):
    t = EmitGlt("test_glt.img", emit_loc)
    print(t.map_info_rotated())
    print(t.map_info_rotated().transform)
    t.run()


# TODO Have a test for handling the date line correctly
@skip
def test_cross_date_line(test_data):
    loc_cross_date_line = EmitLoc(test_data + "sample_cross_dateline_loc.img")
    
    
