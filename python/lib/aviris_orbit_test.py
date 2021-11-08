from .aviris_orbit import *
from .aviris_time_table import AvirisTimeTable
import geocal
from test_support import *

def test_aviris_orbit(isolated_dir):
    tt = AvirisTimeTable(aviris_test_data + "f180522t01p00r07rdn_e_obs")
    orb = AvirisOrbit(aviris_test_data + "f180522t01p00r07rdn_e_lonlat_eph", tt)
    print(orb)
