from .aviris_ng_raw_orbit import *
import math
import geocal
from test_support import *
import numpy.testing as npt

def test_aviris_ng_raw_orbit(aviris_gps_fname, aviris_gps_table):
    orb = AvirisNgRawOrbit(aviris_gps_fname)
    print(orb)
    if False:
        geocal.write_shelve("temp_orb.xml", orb)
    # Check that we read the same data as we read using pyortho, and
    # then saved as a pickle file
    npt.assert_allclose(orb.gps_table, aviris_gps_table)
    
    
