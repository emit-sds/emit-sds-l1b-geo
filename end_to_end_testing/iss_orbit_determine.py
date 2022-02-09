#! /usr/bin/env python
#
# This program is used to determine the best ISS paths to cover a set of points.

from geocal import *
import re
import scipy

version = "1.0"
usage = '''Usage:
  iss_orbit_determine.py [options]
  iss_orbit_determine.py -h | --help
  iss_orbit_determine.py -v | --version
   
This program is used to determine the best ISS paths to cover a set 
of points.
Options:
  -h --help         
       Print this message

  -v --version      
       Print program version
'''

args = docopt_simple(usage, version=version)

orb = SpiceOrbit(SpiceOrbit.ISS_ID, "iss_spice/iss_2020.bsp")
tstart = Time.parse_time("2020-01-01T00:00:00Z")
tend = Time.parse_time("2021-01-01T00:00:00Z")

def latitude_diff(toffset, lat):
    return orb.position_cf(tstart + toffset).latitude - lat

def longitude_diff(toffset, lon):
    return orb.position_cf(tstart + toffset).longitude - lon

# Probably something more efficient, but this isn't something we will 
# run often. This takes a few minutes to run, so we save the results.

# These points are latitude, longitude of four points that cover the 
# California ASTER data we have, selected by hand.

pts = [(39.5, -122), (38, -121), (36, -118), (34, -116)]
if(not os.path.exists("iss_time.json")):
    step_size = 100.0
    threshold = 1.0
    allres = {}
    for pt in pts:
        res = []
        gp = Geodetic(pt[0], pt[1])
        for ts in np.arange(0.0, tend - tstart - 100.0, step_size):
            if(latitude_diff(ts, pt[0]) * latitude_diff(ts + step_size, pt[0]) 
               <= 0):
                t = scipy.optimize.brentq(latitude_diff, ts, ts + step_size, 
                                          args=(pt[0],))
                if(abs(longitude_diff(t, pt[1])) < threshold):
                    # Check that we are on the day side, we don't want
                    # night side data
                    slv = LnLookVector.solar_look_vector(tstart + t, gp)
                    if(slv.view_zenith < 90):
                        res.append(t)
        print(pt, ":")
        print(res)
        allres[str(pt)] = res
    write_shelve("iss_time.json", allres)

near_time = read_shelve("iss_time.json")
cam_nadir = SimpleCamera(0,0,0)
fc_nadir = FrameCoordinate(cam_nadir.number_line(0) / 2.0, 
                           cam_nadir.number_sample(0) / 2.0)

pindex = 1
pt = Geodetic(pts[pindex][0], pts[pindex][1])
for t in near_time[str(pts[pindex])]:
    spt = orb.reference_surface_intersect_approximate(tstart + t, cam_nadir, 
                                                      fc_nadir)
    # This is the format needed by http://www.isstracker.com/historical
    # which can be used to generate plots
    s = str(tstart + t)
    s = re.sub(r'T', ' ', s)
    s = re.sub(r'\.\d+Z', '+0000', s)
    print(tstart + t, "   ", s, " : ", distance(pt, spt) / 1e3, " km")


