from .aviris_ng_raw_orbit import *
import math
import geocal
from test_support import *
import numpy.testing as npt
import numpy as np

def test_aviris_ng_raw_orbit(aviris_gps_fname, aviris_gps_table):
    orb = AvirisNgRawOrbit(aviris_gps_fname)
    print(orb)
    if False:
        geocal.write_shelve("temp_orb.xml", orb)
    # Check that we read the same data as we read using pyortho, and
    # then saved as a pickle file
    npt.assert_allclose(orb.gps_table, aviris_gps_table)
    # A few values we captured from clock2location in the original
    # pyortho.
    # Results of clock2location(1777609046, pps_table, gps_table)
    d = np.array([   31.409547770006476, -114.48458679929081 ,
                     19777.57181145388, 0.055194396664021,
                     3.394098701485017, -16.606637934005672])
    # Time corresponding to this
    tm = geocal.Time.parse_time("2017-03-28T20:21:02.095971Z")
    od = orb.orbit_data(tm)
    # Convert to AircraftOrbitData so we can compare easier
    od = geocal.AircraftOrbitData(od)
    print(od)
    print(geocal.distance(od.position_geodetic, geocal.Geodetic(*d[:3])))
    assert geocal.distance(od.position_geodetic, geocal.Geodetic(*d[:3])) < 2e-2
    # We don't expect these to be exact. clock2location does a linear
    # interpolation, we use slerp. But these should be pretty close
    prh = np.array([od.pitch, od.roll, od.heading])
    npt.assert_allclose(prh, d[-3:], rtol=1e-5)
    # Repeat with a second point
    # Results of clock2location(1777609377, pps_table, gps_table)
    d = np.array([   31.571806306701045, -114.52789763272177 ,
                     19769.21363372091 , 0.170461972130597,
                     -0.056784217571797, -15.337669705285139])
    tm = geocal.Time.parse_time("2017-03-28T20:22:32.099810Z")
    od = orb.orbit_data(tm)
    od = geocal.AircraftOrbitData(od)
    print(od)
    print(geocal.distance(od.position_geodetic, geocal.Geodetic(*d[:3])))
    assert geocal.distance(od.position_geodetic, geocal.Geodetic(*d[:3])) < 2e-2
    prh = np.array([od.pitch, od.roll, od.heading])
    npt.assert_allclose(prh, d[-3:], rtol=1e-5)
    
    
