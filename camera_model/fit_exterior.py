# One off script to fit the camera exterior orientation.
# We save this so we have a record of how we did this.

from geocal import *
from emit import *
import numpy as np
import scipy
import pandas as pd
import glob

#qa_list = glob.glob("*")
qa_list = ["/home/smyth/LocalFast/Emit/orbit_22204/output/emit20220810t051018_o22204_l1b_geoqa_b001_v01.nc", "/home/smyth/LocalFast/Emit/orbit_21501/output/emit20220803t104303_o21501_l1b_geoqa_b001_v01.nc"]
cam = None
igctpcol_list = []
for fname in qa_list:
    df = GeoQa.dataframe(fname)
    if(df["Number Tiepoint"].max() == 0):
        continue
    ibest = int(df["Number Tiepoint"].argmax())
    igccol = GeoQa.igccol_initial(fname, include_img = False)
    igc = igccol.image_ground_connection(ibest)
    # Have one common camera shared
    if(cam is None):
        cam = igc.ipi.camera
    else:
        igc.ipi.camera = cam
    tpcol = GeoQa.tpcol_single(fname, ibest)
    igctpcol_list.append((igc, tpcol))

def collinearity_residual(parm):
    '''Simple calculation of collinearity residual. This is a simpler
       interface than doing a full SBA, and should be good for doing
       an initial camera exterior orientation calculation.
    '''
    cam.full_camera.parameter_subset = parm
    res = []
    for igc, tpcol in igctpcol_list:
        for i, tp in enumerate(tpcol):
            gp = tp.ground_location
            if(tp.image_coordinate(0)):
                res.extend(igc.collinearity_residual(gp, tp.image_coordinate(0)))
    return res

def summarize_residual(parm, desc=""):
    '''Just print out a summary of the collinearity_residual. This is
      just a human readable summary of the data.'''
    res = collinearity_residual(parm)
    print("%s Line residual summary: %s" %
          (desc,
           pd.DataFrame(np.abs(res[0::2])).describe()))
    print("%s Sample residual summary: %s" %
          (desc,
           pd.DataFrame(np.abs(res[1::2])).describe()))

cfull = cam.full_camera
cfull.fit_epsilon = True
cfull.fit_beta = True
cfull.fit_delta = True
cfull.fit_focal_length = False

x0 = cfull.parameter_subset.copy()
summarize_residual(x0, "Initial")
r = scipy.optimize.least_squares(collinearity_residual, x0, loss = "huber")
print(r)
summarize_residual(r.x, "Fitted")

print("orbit, initial accuracy, updated accuracy")
for fname in qa_list:
    df = GeoQa.dataframe(fname)
    igccol = GeoQa.igccol_initial(fname, include_img = False)
    tpcol = GeoQa.tpcol(fname)
    igccol.camera = cam
    df2 = pd.DataFrame(np.array([tpcol.data_frame(igccol, i).ground_2d_distance.quantile(.68)
                                 for i in range(igccol.number_image)]),
                       columns=["Updated Accuracy",])
    if not np.isnan(df["Initial Accuracy"].min()):
        print("%s %0.1lf (%0.1lf - %0.1lf) %0.1lf (%0.1lf - %0.1lf)"
              % (extended_orb_from_file_name(fname),
                 df['Initial Accuracy'].median(),
                 df["Initial Accuracy"].min(), df["Initial Accuracy"].max(),
                 df2['Updated Accuracy'].median(),
                 df2["Updated Accuracy"].min(), df2["Updated Accuracy"].max(),
                 ))


           
