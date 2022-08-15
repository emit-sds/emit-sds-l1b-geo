# One off script to fit the camera exterior orientation.
# We save this so we have a record of how we did this.

from geocal import *
from emit import *
import numpy as np
import scipy
import glob

#qa_list = glob.glob("*")
qa_list = ["/home/smyth/LocalFast/Emit/orbit_22204/output/emit20220810t051018_o22204_l1b_geoqa_b001_v01.nc", "/home/smyth/LocalFast/Emit/orbit_21501/output/emit20220803t104303_o21501_l1b_geoqa_b001_v01.nc"]
print(GeoQa.dataframe(qa_list[0]))
print(GeoQa.dataframe(qa_list[1]))

           
