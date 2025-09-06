from emit import *
from geocal import *
from tp_pair_col import TpPairCol
from aviris_ng_util import *
import os
import math
from multiprocessing import Pool
import pandas as pd
from pptx import Presentation

# This uses tie-points between a couple of lines and a
# cross "tie" line

# Two roughly parallel lines, with a cross "tie" line
# Upper image, sample 0 is south of sample 598
igc1 = create_igc("ang20220224t204803_output")
# Lower image, sample 0 is south of sample 598
igc2 = create_igc("ang20220224t211618_output")
# Tie line, sample 0 is west of sample 598
igc3 = create_igc("ang20220224t223027_output")

# Save IGC, just for reference
write_shelve("camera_model_fitted/igc1.xml",
             create_igc("ang20220224t204803_output", with_rad=False))
write_shelve("camera_model_fitted/igc2.xml",
             create_igc("ang20220224t211618_output", with_rad=False))
write_shelve("camera_model_fitted/igc3.xml",
             create_igc("ang20220224t223027_output", with_rad=False))

# Determine overlap area and use for creating two sets
# of tiepoints
s1 = igc1.loc.ogr_shape()
s2 = igc2.loc.ogr_shape()
s3 = igc3.loc.ogr_shape()

s2_3 = s2.Intersection(s3)
lon1, lon2, lat1, lat2 = s2_3.GetEnvelope()
ln = [igc3.image_coordinate(Geodetic(lat1,lon1)).line,
      igc3.image_coordinate(Geodetic(lat1,lon2)).line,
      igc3.image_coordinate(Geodetic(lat2,lon1)).line,
      igc3.image_coordinate(Geodetic(lat2,lon2)).line]
lnstart_3_2 = math.floor(min(ln))
lnend_3_2 = math.ceil(max(ln))
s1_3 = s1.Intersection(s3)
lon1, lon2, lat1, lat2 = s1_3.GetEnvelope()
ln = [igc3.image_coordinate(Geodetic(lat1,lon1)).line,
      igc3.image_coordinate(Geodetic(lat1,lon2)).line,
      igc3.image_coordinate(Geodetic(lat2,lon1)).line,
      igc3.image_coordinate(Geodetic(lat2,lon2)).line]
lnstart_3_1 = math.floor(min(ln))
lnend_3_1 = math.ceil(max(ln))
igccol3_2 = IgcArray([igc3, igc2])
igccol3_1 = IgcArray([igc3, igc1])
# Tighter matching with a smaller area. We demand much strong correlation
# an variance, since data is acquired at nearly the same time. May have
# a bit more blunders
min_corr = 0.9
min_var = 50.0
m = CcorrLsmMatcher(CcorrMatcher(15, 15, 9, 9,min_corr,min_var),
                    LsmMatcher(11, 11))
if False:
    tcol = TpPairCol(igccol3_1, rot_mi(igc3), matcher=m)
    pool = Pool(20)
    tpcol = tcol.tpcol(pool=pool, llist=range(lnstart_3_1,lnend_3_1,10))
    write_shelve("camera_model_fitted/tpcol_3_1.xml", tpcol)
    pool.close()
if False:
    tcol = TpPairCol(igccol3_2, rot_mi(igc3), matcher=m)
    pool = Pool(20)
    tpcol = tcol.tpcol(pool=pool, llist=range(lnstart_3_2,lnend_3_2,10))
    write_shelve("camera_model_fitted/tpcol_3_2.xml", tpcol)
    pool.close()
tpcol_3_2 = read_shelve("camera_model_fitted/tpcol_3_2.xml")
tpcol_3_1 = read_shelve("camera_model_fitted/tpcol_3_1.xml")


# Residual before we recreate the camera
df_bfit_3_1 = TpPairCol.tp_to_df(tpcol_3_1, igc3, igc1)
df_bfit_3_2 = TpPairCol.tp_to_df(tpcol_3_2, igc3, igc2)

# Get camera_field_alignment data for both sets, and combine into
# one overall fit
cfa1 = TpPairCol.camera_field_alignment(tpcol_3_1, igc3, igc1)
cfa2 = TpPairCol.camera_field_alignment(tpcol_3_2, igc3, igc2)
cfa = np.vstack([cfa1,cfa2])

# Smooth by fitting a Chebyshev polynomial to the data
cp_x = np.polynomial.chebyshev.Chebyshev.fit(cfa[:,0], cfa[:,1],5, [0,598])
cp_y = np.polynomial.chebyshev.Chebyshev.fit(cfa[:,0], cfa[:,2],5, [0,598])

cam = GlasGfmCamera(1,598)
cam.sample_number_first = 0
cam.delta_sample_pair = 1
cam.focal_length = 27.5
fa = np.empty((598,4))
fa[:,0] = cp_x(np.array(list(range(598)),dtype=np.float64))
fa[:,1] = cp_y(np.array(list(range(598)),dtype=np.float64))
fa[:,2] = cp_x(np.array(list(range(1,599)),dtype=np.float64))
fa[:,3] = cp_y(np.array(list(range(1,599)),dtype=np.float64))
cam.field_alignment = fa
write_shelve("camera_model_fitted/cam_cal_2022_04_11_glas.xml", cam)
ppt = Presentation()        
plot_camera_data(cam, f"Calibrated 4/11/2022 Field Alignment")
ppt_save(ppt)
ppt.save("camera_model_fitted/camera_model.ppt")


