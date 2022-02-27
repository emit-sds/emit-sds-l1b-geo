from .aviris_ng_raw_time_table import *
import math
import geocal
from test_support import *
import numpy.testing as npt

def test_aviris_ng_raw_time_table(aviris_pps_fname):
    t = AvirisNgRawTimeTable(aviris_pps_fname)
    # A couple of times that we happened to grab the "clock2location"
    # data from
    assert abs(t.pps_table.clock_to_time(1777609046) - geocal.Time.parse_time("2017-03-28T20:21:02.095971Z")) < 1e-6
    assert abs(t.pps_table.clock_to_time(1786609377) - geocal.Time.parse_time("2017-03-28T20:22:32.099810Z")) < 1e-6
    
    
