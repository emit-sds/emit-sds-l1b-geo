from .l1b_tp_collect import L1bTpCollect
import geocal
import logging
import os

logger = logging.getLogger('l1b_geo_process.l1b_correct')

class L1bCorrect:
    '''This takes an in initial IgcCollection, collects tie-points, does
    image image matching, and runs the SBA to generate a corrected image 
    ground connection.'''
    def __init__(self, igccol_initial, l1b_geo_config, geo_qa):
        self.igccol_initial = igccol_initial
        self.l1b_geo_config = l1b_geo_config
        self.geo_qa = geo_qa
        self.l1b_tp_collect = L1bTpCollect(igccol_initial, l1b_geo_config,
                                           geo_qa)
        if(not os.path.exists("extra_python_init.py")):
            with open("extra_python_init.py", "w") as fh:
                print("from emit import *\n", file=fh)

    def igccol_corrected(self, pool=None):
        if(self.l1b_geo_config.skip_sba):
            logger.info("Skipping SBA correction, using uncorrected ephemeris and attitude")
            return self.igccol_initial
        self.tpcol = self.l1b_tp_collect.tpcol(pool)
        geocal.write_shelve("igccol_initial.xml", self.igccol_initial)
        # TODO Put in actual SBA here    
        self.igccolcorr = self.igccol_initial
        return self.igccolcorr

__all__ = ["L1bCorrect",]        
