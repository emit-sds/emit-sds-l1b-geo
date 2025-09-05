from .aviris_ng_orbit import *
import math
import geocal
from test_support import *
import numpy.testing as npt
import numpy as np

def test_aviris_ng_orbit(aviris_gps_fname, isolated_dir):
    orb = AvirisNgOrbit(aviris_gps_fname)
    # A few values we captured from clock2location in the original
    # pyortho.
    # Results of clock2location(1777609046, pps_table, gps_table)
    d1 = np.array([   31.409547770006476, -114.48458679929081 ,
                     19777.57181145388, 0.055194396664021,
                     3.394098701485017, -16.606637934005672])
    # Time corresponding to this
    tm1 = geocal.Time.parse_time("2017-03-28T20:21:02.095971Z")
    od = orb.orbit_data(tm1)
    # Convert to AircraftOrbitData so we can compare easier
    od = geocal.AircraftOrbitData(od)
    print(od)
    print(geocal.distance(od.position_geodetic, geocal.Geodetic(*d1[:3])))
    assert geocal.distance(od.position_geodetic, geocal.Geodetic(*d1[:3])) < 2e-2
    # We don't expect these to be exact. clock2location does a linear
    # interpolation, we use slerp. But these should be pretty close
    prh1 = np.array([od.pitch, od.roll, od.heading])
    npt.assert_allclose(prh1, d1[-3:], rtol=1e-5)
    # Repeat with a second point
    # Results of clock2location(1777609377, pps_table, gps_table)
    d2 = np.array([   31.571806306701045, -114.52789763272177 ,
                     19769.21363372091 , 0.170461972130597,
                     -0.056784217571797, -15.337669705285139])
    tm2 = geocal.Time.parse_time("2017-03-28T20:22:32.099810Z")
    od = orb.orbit_data(tm2)
    od = geocal.AircraftOrbitData(od)
    print(od)
    print(geocal.distance(od.position_geodetic, geocal.Geodetic(*d2[:3])))
    assert geocal.distance(od.position_geodetic, geocal.Geodetic(*d2[:3])) < 2e-2
    prh2 = np.array([od.pitch, od.roll, od.heading])
    npt.assert_allclose(prh2, d2[-3:], rtol=1e-5)
    orb.write_orbit("orb.nc")
    orb2 = AvirisNgOrbit("orb.nc")
    
    od = orb2.orbit_data(tm1)
    od = geocal.AircraftOrbitData(od)
    assert geocal.distance(od.position_geodetic, geocal.Geodetic(*d1[:3])) < 2e-2
    prh1 = np.array([od.pitch, od.roll, od.heading])
    npt.assert_allclose(prh1, d1[-3:], rtol=1e-5)
    od = orb.orbit_data(tm2)
    od = geocal.AircraftOrbitData(od)
    assert geocal.distance(od.position_geodetic, geocal.Geodetic(*d2[:3])) < 2e-2
    prh2 = np.array([od.pitch, od.roll, od.heading])
    npt.assert_allclose(prh2, d2[-3:], rtol=1e-5)
    
    
    
