# This creates test data for EMIT. Note that the data is simulated from
# ASTER, and really isn't any good for science processing. But start with
# this. The test data that we have for science is based on aircraft data
# that isn't easily mapped to what we need for geolocation

from geocal import *
from emit import *
import h5py
import subprocess
import re

# While developing we run this multiple times. Skip things we already
# have
CREATE_IGC_SIM = False
CREATE_ENVI = True
CREATE_ORBIT = False
CREATE_TT = False

# We only bother simulating one band for this test. We can't realistically
# generate science data from the few ASTER bands available, so we only
# generate one. AVIRIS NG goes from 0.38 micrometer - 2.51. Not sure about
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

# Time was determined by looking as iss_orbit_determine.py along with
# http://www.isstracker.com/historical to view the
# actual orbits, and select the one that passes through our data the best.
tstart = Time.parse_time("2020-06-10T01:51:31.753198Z")
tstart = tstart - 40
# Nominal time spacing
tspace = 9.26e-3
nline = 1280
nscene = 3
orbit = 80000
end_fname = "b001_v01"
for scene in range(nscene):
    tt = ConstantSpacingTimeTable(tstart + scene * nline * tspace,
                                  tstart + ((scene+1) * nline - 1) * tspace,
                                  tspace)

    # IGC
    ipi = Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
    igc = IpiImageGroundConnection(ipi, dem, None)

    # Start of file name
    tm = igc.pixel_time(ImageCoordinate(0,0))
    dstring = re.sub(r'T', 't', re.sub(r'[-:]', '',
                                       re.split(r'\.', str(tm))[0]))
    dstring_end = re.sub(r'[-:]', '', re.split(r'\.', str(tt.max_time))[0])
    start_fname = "emit%s_o%05d_s%03d" % (dstring, orbit, scene+1)
    
    # Simulate data
    igc_sim = IgcSimulatedRayCaster(igc, sdata)

    # Create projected data
    if CREATE_IGC_SIM:
        write_shelve("igc_sim_%03d.xml" % (scene+1), igc_sim)
        subprocess.run(["write_image", "--number-process=40", "--process-number-line=100", "--process-number-sample=1240", "--vicar-type=REAL", f"--scale={sfactor}", "--verbose", "igc_sim_%03d.xml" % (scene+1), "igc_sim_%03d.img" % (scene+1)])

    if CREATE_ENVI:
        fin = VicarLiteRasterImage("igc_sim_%03d.img" % (scene+1))
        d = fin.read_all_double()
        # We have 324 bands. But in make believe simulation just create 2 bands
        # so the file size is smaller. We can generate the full size if
        # we want to look at performance etc.
        nband = 2
        fname = f"{start_fname}_l1b_rdn_{end_fname}.img"
        t = GdalMultiBand(fname, "ENVI", fin.number_line,
        fin.number_sample, nband, GdalRasterImage.Float32,
                          "INTERLEAVE=BIL")
        for b in range(t.number_band):
            t.gdal_raster_image(b).write(0,0,d)
            # Extra metadata
            t2 = t.gdal_raster_image(0)
            set_file_description(t2, "EMIT L1B calibrated spectral radiance (units: uW nm-1 cm-2 sr-1)")
            t2["ENVI","wavelength units"] = "Nanometers"
            t2["ENVI", "emit acquisition stop time"] = dstring_end
            t2["ENVI", "emit acquisition start time"] = dstring.replace("t","T")
            t2["ENVI", "emit pge name"] = "create_end_to_end_test_data.py"
            t2["ENVI", "emit pge version"] = "1.0.0"
            t2["ENVI", "emit pge input files"] = "{ made_up_input }"
            t2["ENVI", "emit software build version"] = "b001"
            t2["ENVI", "emit documentation version"] = "Initial Release"
            t2["ENVI", "emit data product creation time"] = "20010101T000000"
            t2["ENVI", "emit data product version"] = "v01"
            wavelength = []
            fwhm = []
            for i in range(2):
                wavelength.append(str((630+690) / 2))
                fwhm.append(str((690 - 630) / 2))
                set_band_description(t.gdal_raster_image(i),
                                     f"630-690 band {i+1}")
            t2["ENVI", "wavelength"] = "{ " + ", ".join(wavelength) + " }"
            t2["ENVI", "fwhm"] = "{ " + ", ".join(fwhm) + " }"
            
    if CREATE_ORBIT and scene == 0:
        tm = tt.min_time - 100
        dstring2 = re.sub(r'T', 't', re.sub(r'[-:]', '',
                                           re.split(r'\.', str(tm))[0]))
        
        fname = "emit%s_o%05d_l1a_att_%s.nc" % (dstring2, orbit, end_fname)
        EmitOrbit.write_file(fname, orb, tm,
                             tt.min_time + nscene * nline * tspace + 100)
    if CREATE_TT:
        fname = f"{start_fname}_l1a_line_time_{end_fname}.nc"
        EmitTimeTable.write_file(fname, tt)
    
    
    



