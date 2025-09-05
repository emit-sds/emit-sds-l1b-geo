import struct
import geocal


class AvirisOrbit(geocal.OrbitQuaternionList):
    """This reads the AVIRIS orbit data. Note that there are two versions
    of this, a "eph" which is in terms of UTM and a "lonlat_eph" in terms
    of latitude and longitude. This class takes the second format. We could
    read the UTM data if needed, but 1) we can't easily know the UTM zone number
    and 2) the lonlat version gets generated whenever the UTM version does.

    The orbit data doesn't contain any timing information. So we also require
    that the AvirisTimeTable that goes with this data also."""

    def __init__(self, fname, aviris_tt):
        fh = open(fname, "rb")
        sz_to_read = struct.calcsize("<6d")
        tm_arr = []
        pos_arr = []
        rph_arr = []
        datum = geocal.DatumGeoid96()
        for i in range(aviris_tt.max_line):
            tm, _ = aviris_tt.time(geocal.ImageCoordinate(i, 0))
            tm_arr.append(tm)
            # Data is binary, float data in intel/little-endian format
            # Data is lon, lat, elv and roll/pitch/heading.
            # Pretty sure this is in degrees and meters
            (lon, lat, elv, roll, pitch, heading) = struct.unpack(
                "<6d", fh.read(sz_to_read)
            )
            # The elevation is above the datum, not WGS 84. So we need
            # to add the datum undulation to get the correct elevation
            elv += datum.undulation(geocal.Geodetic(lat, lon))
            pos_arr.append(geocal.Geodetic(lat, lon, elv))
            rph_arr.append([roll, pitch, heading])
        od = []
        for i in range(aviris_tt.max_line - 1):
            i2 = i + 1
            # Special handling for the last point, we get the
            # velocity by looking at the previous point
            if i2 >= aviris_tt.max_line:
                i2 = i - 1
            od.append(
                geocal.AircraftOrbitData(
                    tm_arr[i],
                    pos_arr[i],
                    tm_arr[i2],
                    pos_arr[i2],
                    rph_arr[i][0],
                    rph_arr[i][1],
                    rph_arr[i][2],
                )
            )
        super().__init__(od)


__all__ = [
    "AvirisOrbit",
]
