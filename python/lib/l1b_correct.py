from .l1b_tp_collect import L1bTpCollect
import geocal
import logging
import os
import pickle

logger = logging.getLogger('l1b_geo_process.l1b_correct')

class L1bCorrect:
    '''This takes an in initial IgcCollection, collects tie-points, does
    image image matching, and runs the SBA to generate a corrected image 
    ground connection.'''
    def __init__(self, igccol_initial, l1_osp_dir, geo_qa):
        self.igccol_initial = igccol_initial
        self.l1_osp_dir = l1_osp_dir
        self.geo_qa = geo_qa
        self.l1b_tp_collect = L1bTpCollect(igccol_initial, l1_osp_dir,
                                           geo_qa)
        if(not os.path.exists("extra_python_init.py")):
            with open("extra_python_init.py", "w") as fh:
                print("from emit import *\n", file=fh)

    def collinearity_residual(self, parm):
        '''Simple calculation of collinearity residual. This is a simpler
        interface than doing a full SBA, and should be good for doing an
        initial camera exterior orientation calculation.'''
        self.igccol_corrected.parameter_subset = parm
        res = []
        for i, tp in enumerate(self.tpcol):
            gp = tp.ground_location
            for j in range(tp.number_image):
                if(tp.image_coordinate(j)):
                    res.extend(self.igccol_corrected.collinearity_residual(j, gp, tp.image_coordinate(j)))
        return res

    def igccol_corrected(self, pool=None):
        if(self.l1_osp_dir.l1b_geo_config.skip_sba):
            logger.info("Skipping SBA correction, using uncorrected ephemeris and attitude")
            return self.igccol_initial
        self.tpcol, self.time_range_tp = self.l1b_tp_collect.tpcol(pool)
        geocal.write_shelve("tpcol.xml", self.tpcol)
        pickle.dump(self, open("l1b_correct.pkl", "wb"))
        geocal.write_shelve("igccol_initial.xml", self.igccol_initial)
        # TODO Put in actual SBA here    
        self.igccolcorr = self.igccol_initial
        return self.igccolcorr

__all__ = ["L1bCorrect",]        
