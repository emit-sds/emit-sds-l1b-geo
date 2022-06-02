# Short script to import the spreadsheet into a GlasGfmCamera
import pandas as pd
import geocal
import numpy as np

# Camera we used in initial testing. Keep around just so we have a copy
# of this for use with old test data.
focal_length = 193.5e-3
line_pitch = 30e-6
sample_pitch = 30e-6
nsamp = 1280
spectral_channel = 324
cam = geocal.SimpleCamera(0,0,0,focal_length, line_pitch, sample_pitch,
                   1, nsamp)
geocal.write_shelve("camera_initial_testdata.xml", cam)

# Focal length is from an Email from Christine Bradley (2/18/2022). This
# was measured in TVAC. We'll look at fitting this on orbit, it isn't
# atypical for this to change slightly in orbit from gravity unloading/thermal
# changes (at the < 1% level). But start with the TVAC measured data.

focal_length_mm = 193.3
focal_length_time = geocal.Time.parse_time("2022-02-18T00:00:00Z")

# These are in mm. CCD pitch is 30 micron, so we should see a spacing
# in the x direction of about 0.03
#
# In this file, the pixel sample number (the index column) is 0 or 1 based
# (see comment below, 0 based is current best guess).
# This is for the full camera, including shielded pixels.
field_x = pd.read_excel("EMIT_Camera_Model_FieldAngles_20220402.xlsx",
                        sheet_name = "field_x", index_col=0)
field_y = pd.read_excel("EMIT_Camera_Model_FieldAngles_20220402.xlsx",
                        sheet_name = "field_y", index_col=0)

# There is a pretty small keystone and smile (keystone ~10% of a pixel,
# smile ~2% of a pixel, from Email from Christine Bradley, 2/17/2022).
#
# We ignore this in the camera model, and just
# have one band that is applied to all the bands.
# The spectral pixel in the spreadsheet goes from 312 to 32, we just pick
# the middle one of 172 for reading our field angles. We could look at
# the spectral pixel dependency of this if needed, but for now we just
# ignore this.
#
# Note we don't know the actual wavelength for this, we could probably figure this
# out from but it isn't actually important. This only gets used if we are doing a
# wavelength dependent refraction correction. We won't do this for EMIT, the effect is too small.
# So we use the default wavelength here.

field_x = field_x[172]
field_y = field_y[172]

# Data actually goes from pixel 25 to 1265. Not surprisingly there was
# no measurements where the pixels are shielded. We fit Chebyshev polynomial
# to the full data, just so we have reasonable values for the full camera.
# We'll ultimately want a "clipped" camera covering where we actually have
# radiance data, but right now we are importing the full camera.
#
# Note I'm not sure if the sample number in the spreadsheet is 0 or 1 based.
# The GLAS model is 0 based. Christine Bradley thought the data was 0 based,
# but the numbers reported looked like they were 1 based. I'm not sure how
# much we could tell the difference here. We'll assume Christine is right

is_one_based = False
if is_one_based:
    sample = np.array(field_x.index) - 1
else:
    sample = np.array(field_x.index)
    
cp_x = np.polynomial.chebyshev.Chebyshev.fit(sample, np.array(field_x), 5,
                                             [0,1280])
cp_y = np.polynomial.chebyshev.Chebyshev.fit(sample, np.array(field_y), 5,
                                             [0,1280])
fa_x = np.empty((1280 // 4 + 1,))
fa_y = np.empty((1280 // 4 + 1,))

if is_one_based:
    smplist = list(range(0,1284,4))
else:
    smplist = list(range(1,1285,4))
    
for i,smp in enumerate(smplist):
    try:
        f_ind = list(sample).index(smp)
        fa_x[i] = np.array(field_x)[f_ind]
        fa_y[i] = np.array(field_y)[f_ind]
    except ValueError:
        fa_x[i] = cp_x(smp)
        fa_y[i] = cp_y(smp)

cam = geocal.GlasGfmCamera(1,1280)
if is_one_based:
    cam.sample_number_first = 0
else:
    # We want as close to the raw data as possible. The spreadsheet
    # has numbers like 25 with every 4th pixel. So to fit the data,
    # we need to start with 1
    cam.sample_number_first = 1
cam.delta_sample_pair = 4
cam.focal_length = focal_length_mm
cam.focal_length_time = focal_length_time
fa = np.empty((1280//4,4))
fa[:,0] = fa_x[:-1]
fa[:,1] = fa_y[:-1]
fa[:,2] = fa_x[1:]
fa[:,3] = fa_y[1:]
cam.field_alignment = fa
geocal.write_shelve("camera_full_2022_04_02_glas.xml", cam)

# From an email from David Thompson (5/12/2022), we'll be using
# pixels 24 to 1265 inclusive (0 based pixel) for our images.
# This may end up being tweaked by a pixel or two when we get
# real data, but for now use the values from David Thompson
cam2 = geocal.SubCamera(cam, 0, 24, 1, 1265+1-24)
geocal.write_shelve("camera_active_2022_04_02.xml", cam2)



        
