# Short script to import the spreadsheet into a GlasGfmCamera
import pandas as pd
import geocal
import numpy as np
import scipy

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

# These are in degrees
#
# In this file, the pixel sample number (the index column) is 0 or 1 based
# (see comment below, 0 based is current best guess).
# This is for the full camera, including shielded pixels.
field_x = pd.read_excel("EMIT_Camera_Model_FieldAngles_20220402.xlsx",
                        sheet_name = "field_x", index_col=0)
field_y = pd.read_excel("EMIT_Camera_Model_FieldAngles_20220402.xlsx",
                        sheet_name = "field_y", index_col=0)

# Note that the orbit data from BAD uses a different direction convention
# then Christine's camera model. Using the language of the QuaternionCamera
# she has LINE_IS_Y, INCREASE_IS_POSITIVE for both line and sample.
# The BAD data uses a convention of LINE_IS_X, INCREASE_IS_POSITIVE for
# both line and sample. So we need to swap field_x and field_y when
# assigning to glas model
glas_x = field_y
glas_y = field_x

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

glas_x = glas_x[172]
glas_y = glas_y[172]

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
    sample = np.array(glas_x.index) - 1
else:
    sample = np.array(glas_x.index)
    
cp_x = np.polynomial.chebyshev.Chebyshev.fit(sample, np.array(glas_x), 5,
                                             [0,1280])
cp_y = np.polynomial.chebyshev.Chebyshev.fit(sample, np.array(glas_y), 5,
                                             [0,1280])
# We go ahead an fill in all the rest of the data using interpolation
interp_x = scipy.interpolate.interp1d(sample, np.array(glas_x),
                                      kind="cubic", bounds_error=True)
interp_y = scipy.interpolate.interp1d(sample, np.array(glas_y),
                                      kind="cubic", bounds_error=True)

fa_x = np.empty((1280 + 1,))
fa_y = np.empty((1280 + 1,))

for i,smp in enumerate(range(0,1280+1)):
    try:
        fa_x[i] = interp_x(smp)
        fa_y[i] = interp_y(smp)
    except ValueError:
        fa_x[i] = cp_x(smp)
        fa_y[i] = cp_y(smp)

print(fa_x[-1])
print(fa_y[-1])

cam = geocal.GlasGfmCamera(1,1280)

cam = geocal.GlasGfmCamera.create_glas_from_field_angle(fa_x, fa_y,
              focal_length = focal_length_mm*1e-3,
              focal_length_time = focal_length_time)
geocal.write_shelve("camera_full_2022_04_02_glas.xml", cam)

# From an email from David Thompson (5/12/2022), we'll be using
# pixels 24 to 1265 inclusive (0 based pixel) for our images.
# This may end up being tweaked by a pixel or two when we get
# real data, but for now use the values from David Thompson
cam2 = geocal.SubCamera(cam, 0, 24, 1, 1265+1-24)
geocal.write_shelve("camera_active_2022_04_02.xml", cam2)

# Do some basic checks on the camera
fa_diff = 0
for smp in glas_x.index:
    fa_x, fa_y = cam.sc_look_vector(geocal.FrameCoordinate(0,smp),0).field_angle()
    fa_diff = max(abs(glas_x[smp] - fa_x), abs(glas_y[smp] - fa_y), fa_diff)
    if False:
        print(smp, abs(glas_x[smp] - fa_x), abs(glas_y[smp] - fa_y))
print(f"Max fa_diff: {fa_diff}")
print(f"Max fa_diff scaled to pixel: {(fa_diff * geocal.deg_to_rad) / 155e-6}")

# Check the spacing in microradians, and compare to value for Christine's
# powerpoint
print("Cross Track IFOV (should be close to 155 micro-radians)",
      (cam.sc_look_vector(geocal.FrameCoordinate(0,630),0).field_angle()[1]-
       cam.sc_look_vector(geocal.FrameCoordinate(0,629),0).field_angle()[1]) *
      geocal.deg_to_rad*1e6)

# Check sample pitch, should be close to 30 micron
print("Sample pitch (should be close to 30 micron)",
      (cam.frame_coordinate_to_xy(geocal.FrameCoordinate(0,630),0)[1]-cam.frame_coordinate_to_xy(geocal.FrameCoordinate(0,629),0)[1]) * 1e6)

# Check that curve goes the right way in the camera
print("X diff for 100 pixel in microns (should be positive)",
      (cam.frame_coordinate_to_xy(geocal.FrameCoordinate(0,25),0)[0]-
       cam.frame_coordinate_to_xy(geocal.FrameCoordinate(0,25+100),0)[0])*1e6)



        
