from .geo_qa import *
from test_support import *

def test_geo_qa(isolated_dir):
    geo_qa = GeoQa("geoqa.nc", "l1b_geo.log")
    geo_qa.close()
    
