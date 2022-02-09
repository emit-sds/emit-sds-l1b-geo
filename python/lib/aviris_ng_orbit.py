import struct
import geocal
from .misc import create_dem

class AvirisNgOrbit(geocal.OrbitQuaternionList):
    '''This reads the AVIRIS NG orbit data. Note that the time is given
    as GPS time for a the GPS week, but we don't independently have the
    week number.

    We could probably write something that keys off the file name, but we
    don't actually have all that much data so it doesn't seem worth it. 
    A quick way to calculate this is something like:

    math.floor(Time.parse_time("2017-03-23T00:00:00Z").gps / (7 * 24 * 60 * 60))

    I'm *pretty* sure the height is relative to WGS-84 rather than the
    datum. Error is small, and since this is pretend test data perhaps
    it doesn't matter so much
    '''
    def __init__(self, fname, gps_week):
        # We use a GdalMultiBand here just for convenience. It just
        # figures out the shape etc. for us from the hdr file
        d = geocal.GdalMultiBand(fname).read_all_double()
        # GPS time
        tm_arr = [geocal.Time.time_gps(gps_week, gps_offset) for
                  gps_offset in d[0,:,0]]
        # Lat, lon, height
        pos_arr = d[1:4,:,0].transpose()
        # Pitch, roll, heading
        prh_arr = d[4:7,:,0].transpose()
        od = []
        for i in range(pos_arr.shape[0]):
            i2 = i + 1
            # Special handling for the last point, we get the
            # velocity by looking at the previous point
            if(i2 >= pos_arr.shape[0]):
                i2 = i - 1
            # Temp, this might actually be switched
            od.append(geocal.AircraftOrbitData(tm_arr[i],
                geocal.Geodetic(*pos_arr[i]),
                tm_arr[i2], geocal.Geodetic(*pos_arr[i2]),
                prh_arr[i][1], prh_arr[i][0], prh_arr[i][2]))
        super().__init__(od)
        
__all__ = ["AvirisNgOrbit",]    
