from .aviris_ng_loc import *
import geocal
from test_support import *
from multiprocessing import Pool

# Only need to run if we have to regenerate the test data
@skip
def test_create_loc(igc, test_data):
    '''Create a LOC file for use with unit tests. We create
    both a normal one, and one that crosses the dateline (for
    testing handling of that.

    We put this in the test_data directory because of it's size'''
    g = AvirisNgLoc(test_data + "sample_loc.img", igc=igc)
    g.run()

@slow
def test_generate_avris_loc(aviris_igc_full, isolated_dir):
    print(aviris_igc_full.ipi.time_table)
    print(aviris_igc_full.image)
    geocal.write_shelve("igc.xml", aviris_igc_full)
    g = AvirisNgLoc("test_loc.img", igc=aviris_igc_full)
    pool = Pool(20)
    g.run(pool=pool)
    
    
    
