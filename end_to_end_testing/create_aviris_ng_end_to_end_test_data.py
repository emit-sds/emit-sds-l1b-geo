# This create the AVIRIS-NG end to end test data.
# See the README.md file for how we captured the data that we generated as the
# input to this.

from geocal import *
from emit import *
import pickle
import math
import re

# While developing we run this multiple times. Skip things we already
# have
CREATE_ORBIT = True

emit_test_data = "/home/smyth/Local/emit-test-data/latest"
input_test_data = f"{emit_test_data}/input_afids_ng"

orbit = 90000
end_fname = "b001_v01"

# This is zone_alpha, but with "S" changed to "N" - I think the data
# is actually wrong here
utm_zone = 11

if CREATE_ORBIT:
    fname = f"{input_test_data}/pyortho_20170328t202059.pkl"
    # The "bytes" here is needed because we pickled using python 2.7. See
    # https://groups.google.com/g/sage-devel/c/nLG8zMSKSD0
    frame_meta, gpstime, filedate, zone_alpha = pickle.load(open(fname, "rb"), encoding="bytes")
    filedate = Time.parse_time(filedate.decode('utf-8'))
    gps_week = math.floor(filedate.gps / (7 * 24 * 60 * 60))
    line_time = [Time.time_gps(gps_week,t) for t in gpstime]
    if(utm_zone < 0):
        ogrw = OgrWrapper.from_epsg(32700 + abs(utm_zone))
    else:
        ogrw = OgrWrapper.from_epsg(32600 + abs(utm_zone))
    pos = [OgrCoordinate(ogrw,*frame_meta[i,1:4]) for i in range(frame_meta.shape[0])]
    # This is pitch, roll, and heading in degrees
    prh = frame_meta[:,-3:] * rad_to_deg
    od = []
    for i in range(len(pos)):
        isecond = i+1
        if(isecond >= len(pos)):
            isecond = i-1
        od.append(AircraftOrbitData(line_time[i],pos[i],
                                    line_time[isecond],pos[isecond],
                                    prh[i,1],prh[i,0],prh[i,2]))
    orb = OrbitQuaternionList(od)
    write_shelve("orb_aviris.xml", orb)
    tm = orb.min_time
    dstring2 = re.sub(r'T', 't', re.sub(r'[-:]', '',
                                        re.split(r'\.', str(tm))[0]))
    fname = "emit%s_o%05d_l1a_att_%s.nc" % (dstring2, orbit, end_fname)
    EmitOrbit.write_file2(f"{emit_test_data}/{fname}", orb)
    tt = MeasuredTimeTable(line_time)
    fname = "emit%s_o%05d_l1a_line_time_full_%s.nc" % (dstring2, orbit, end_fname)
    EmitTimeTable.write_file(f"{emit_test_data}/{fname}", tt)
    
    
