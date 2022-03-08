from .l1b_tp_collect import L1bTpCollect
import geocal
import logging
import os
import pickle
import pandas as pd
import scipy.optimize
import numpy as np
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
        self.igccolcorr.parameter_subset = parm
        res = []
        for i, tp in enumerate(self.tpcol):
            gp = tp.ground_location
            for j in range(tp.number_image):
                if(tp.image_coordinate(j)):
                    res.extend(self.igccolcorr.collinearity_residual(j, gp, tp.image_coordinate(j)))
        return res

    def summarize_residual(self, parm, desc=""):
        '''Just print out a summary of the collinearity_residual. This is
        just a human readable summary of the data.'''
        res = self.collinearity_residual(parm)
        logger.info("%s Line residual summary: %s", desc,
                    pd.DataFrame(np.abs(res[0::2])).describe())
        logger.info("%s Sample residual summary: %s", desc,
                    pd.DataFrame(np.abs(res[1::2])).describe())

    def fit_camera(self):
        '''Sample of fitting the camera exterior orientation (the euler
        angles). This is a basic sample of how to do this. There is
        the full sba program which can be used if desired, but
        probably things are small enough to just do something like
        this.
        '''
        # Grab the camera object. Probably should put nearer the top,
        # but for now we just go through the object structure
        cam = self.igccolcorr.image_ground_connection(0).ipi.camera
        # Set the variables we will fit
        cam.fit_epsilon = True
        cam.fit_beta = True
        cam.fit_delta = True
        # Not sure if we want to fit focal length or not. In general
        # it can change over time a small amount (e.g., 1%). For now,
        # include this
        cam.fit_focal_length = True
        cam.fit_sample_pitch = False
        cam.fit_line_pitch = False
        cam.fit_principal_point_sample(False,0)
        cam.fit_principal_point_line(False,0)
        logger.info("Initial camera value:")
        for v, desc in zip(cam.parameter_subset,cam.parameter_name_subset):
            logger.info(f"{desc}: {v}")
        x0 = cam.parameter_subset.copy()
        self.summarize_residual(x0, desc= "Initial")
        # Now fit the data. Can play with this, but for right now
        # just use the default scipy least squares optimization
        r = scipy.optimize.least_squares(self.collinearity_residual, x0)
        logger.info("Fitting results: %s", r)
        logger.info("Fitted camera value:")
        for v, desc in zip(cam.parameter_subset,cam.parameter_name_subset):
            logger.info(f"{desc}: {v}")
        self.summarize_residual(r.x, desc= "Fitted")

    def igccol_corrected(self, pool=None):
        if(self.l1_osp_dir.l1b_geo_config.skip_sba):
            logger.info("Skipping SBA correction, using uncorrected ephemeris and attitude")
            return self.igccol_initial
        self.tpcol, self.time_range_tp = self.l1b_tp_collect.tpcol(pool)
        # Useful to save out, just so we have this
        geocal.write_shelve("tpcol.xml", self.tpcol)
        geocal.write_shelve("igccol_initial.xml", self.igccol_initial)
        self.igccolcorr = geocal.read_shelve("igccol_initial.xml")
        # Can also save this whole object, if you want to be able to
        # play with fitting data.
        pickle.dump(self, open("l1b_correct.pkl", "wb"))
        self.fit_camera()
        return self.igccolcorr

__all__ = ["L1bCorrect",]        
