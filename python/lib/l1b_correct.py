import geocal
import logging

logger = logging.getLogger('l1b_geo_process.l1b_geo_generate')

class L1bCorrect:
    '''This takes an in initial IgcCollection, collects tie-points, does
    image image matching, and runs the SBA to generate a corrected image 
    ground connection.'''
    def __init__(self, igccol_initial, l1b_geo_config, geo_qa):
        self.igccol_initial = igccol_initial
        self.l1b_geo_config = l1b_geo_config
        self.geo_qa = geo_qa

    def run(self):
        # Save file so downstream programs know to import emit
        with open("extra_python_init.py", "w") as fh:
            print("from emit import *\n", file=fh)
        geocal.write_shelve("igccol_initial.xml", self.igccol_initial)
            
        self.igccol_corrected = self.igccol_initial

__all__ = ["L1bCorrect",]        
