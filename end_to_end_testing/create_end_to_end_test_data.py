# This creates test data for EMIT. Note that the data is simulated from
# ASTER, and really isn't any good for science processing. But start with
# this. The test data that we have for science is based on aircraft data
# that isn't easily mapped to what we need for geolocation

from geocal import *
from emit import *
import h5py
import subprocess

# While developing we run this multiple times. Skip things we already
# have
CREATE_IGC_SIM = False
CREATE_ENVI = False
CREATE_ORBIT = False
CREATE_TT = True

# We only bother simulating one band for this test. We can't realistically
# generate science data from the few ASTER bands available, so we only
# generate one. AVIRIS HG goes from 0.38 micrometer - 2.51. Not sure about
# EMIT, we'll need to dig that up. Not exactly sure which band we will want
# to match for LANDSAT, but we'll start with the red band - landsat 7 band
# 3 (0.63-0.69) abd ASTER band 2 (also 0.63 - 0.69).
aster_band = 2
sdata = VicarLiteRasterImage(f"{aster_mosaic_dir()}/calnorm_b{aster_band}.img",
                             1, VicarLiteFile.READ, 10000, 10000)
# Scale factor to convert DN to radiance
sfactor = aster_radiance_scale_factor()[aster_band-1]

# Orbit data. This has nadir attitude, which is probably fine for testing
# We can perhaps see if we can dig up actual BAD data for our orbit time if
# needed.
orb = SpiceOrbit(SpiceOrbit.ISS_ID, "iss_spice/iss_2020.bsp")

# Time was determined by looking as iss_orbit_determine.py along with
# http://www.isstracker.com/historical to view the
# actual orbits, and select the one that passes through our data the best.
tstart = Time.parse_time("2020-06-10T01:51:31.753198Z")
tstart = tstart - 40
# Nominal time spacing
tspace = 9.26e-3
nline = 10000
tt = ConstantSpacingTimeTable(tstart, tstart + nline * tspace, tspace)

# Simple pinhole camera, we'll replace with the calibrated camera
focal_length = 193.5e-3
line_pitch = 30e-6
sample_pitch = 30e-6
nsamp = 1280
spectral_channel = 324
cam = SimpleCamera(0,0,0,focal_length, line_pitch, sample_pitch,
                   1, nsamp)

# DEM
dem = create_dem(None)

# IGC
ipi = Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
igc = IpiImageGroundConnection(ipi, dem, None)

# Simulate data
igc_sim = IgcSimulatedRayCaster(igc, sdata)

# Create projected data
if CREATE_IGC_SIM:
    write_shelve("igc_sim.xml", igc_sim)
    subprocess.run(["write_image", "--number-process=40", "--process-number-line=100", "--process-number-sample=1240", "--vicar-type=REAL", f"--scale={sfactor}", "--verbose", "igc_sim.xml", "igc_sim.img"])

if CREATE_ENVI:
    fin = VicarLiteRasterImage("igc_sim.img")
    d = fin.read_all_double()
    # We have 324 bands. But in make believe simulation just create 2 bands
    # so the file size is smaller. We can generate the full size if
    # we want to look at performance etc.
    nband = 2
    t = GdalMultiBand("igc_sim_envi.img", "ENVI", fin.number_line,
                      fin.number_sample, nband, GdalRasterImage.Float32,
                      "INTERLEAVE=BIL")
    for b in range(t.number_band):
        t.gdal_raster_image(b).write(0,0,d)
    # Extra metadata
    t.gdal_raster_image(0)["ENVI","emit acquisition start time"] = "foo"
    # etc.
if CREATE_ORBIT:
    t = L1aRawAttSimulate(orb, tt.min_time - 100, tt.max_time + 100)
    t.create_file("orbit_l1a_sim.nc")
if CREATE_TT:
    t = EmitTimeTable()
    t.write_time_table(tt, "line_time_sim.nc")
    
    
    



