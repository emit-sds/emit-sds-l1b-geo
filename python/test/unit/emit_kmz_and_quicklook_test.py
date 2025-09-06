from emit import EmitLoc, EmitKmzAndQuicklook
import pytest


def test_generate_loc(isolated_dir, test_data, emit_loc, l1b_rdn_fname):
    t = EmitKmzAndQuicklook("test", emit_loc, l1b_rdn_fname)
    t.run()


# TODO Have a test for handling the date line correctly
@pytest.mark.skip
def test_cross_date_line(test_data):
    loc_cross_date_line = EmitLoc(test_data + "sample_cross_dateline_loc.img")
    print(loc_cross_date_line)
