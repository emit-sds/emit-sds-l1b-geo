from .aviris_ng_raw_time_table import *
import math
import geocal
from test_support import *
import numpy.testing as npt

def test_aviris_ng_raw_time_table(aviris_pps_fname, aviris_pps_table):
    t = AvirisNgRawTimeTable(aviris_pps_fname)
    # Check that we read the same data as we read using pyortho, and
    # then saved as a pickle file
    npt.assert_allclose(t.pps_table, aviris_pps_table)
    # A couple of times that we happened to grab the "clock2location"
    # data from
    assert abs(t.clock_to_time(1777609046) - geocal.Time.parse_time("2017-03-28T20:21:02.095971Z")) < 1e-6
    assert abs(t.clock_to_time(1786609377) - geocal.Time.parse_time("2017-03-28T20:22:32.099810Z")) < 1e-6
    
    
