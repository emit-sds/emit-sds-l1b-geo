from .aviris_time_table import *
import geocal
from test_support import *

def test_aviris_time_table():
    tt = AvirisTimeTable(aviris_test_data + "f180522t01p00r07rdn_e_obs")
    print(tt)
    for i in range(tt.max_line):
        print(tt.time(geocal.ImageCoordinate(i,0))[0])
        
