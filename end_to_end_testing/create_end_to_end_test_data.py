# This creates test data for EMIT. Note that the data is simulated from
# ASTER, and really isn't any good for science processing. But start with
# this. The test data that we have for science is based on aircraft data
# that isn't easily mapped to what we need for geolocation

from geocal import *
from emit import *
import h5py

# We only bother simulation one band for this test. We can't realistically
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

