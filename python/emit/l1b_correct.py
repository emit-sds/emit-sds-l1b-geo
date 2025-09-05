from .l1b_tp_collect import L1bTpCollect
from .misc import process_run
import geocal
import logging
import os
import pickle
import pandas as pd
import scipy.optimize
import numpy as np

logger = logging.getLogger("l1b_geo_process.l1b_correct")


class L1bCorrect:
    """This takes an in initial IgcCollection, collects tie-points, does
    image image matching, and runs the SBA to generate a corrected image
    ground connection."""

    def __init__(self, igccol_initial, l1_osp_dir, geo_qa, fit_camera_only=False):
        self.igccol_initial = igccol_initial
        self.l1_osp_dir = l1_osp_dir
        self.geo_qa = geo_qa
        self.fit_camera_only = fit_camera_only
        self.l1b_tp_collect = L1bTpCollect(igccol_initial, l1_osp_dir, geo_qa)
        if not os.path.exists("extra_python_init.py"):
            with open("extra_python_init.py", "w") as fh:
                print("from emit import *\n", file=fh)

    def collinearity_residual(self, parm):
        """Simple calculation of collinearity residual. This is a simpler
        interface than doing a full SBA, and should be good for doing an
        initial camera exterior orientation calculation."""
        self.igccolcorr.parameter_subset = parm
        res = []
        for i, tp in enumerate(self.tpcol):
            gp = tp.ground_location
            for j in range(tp.number_image):
                if tp.image_coordinate(j):
                    res.extend(
                        self.igccolcorr.collinearity_residual(
                            j, gp, tp.image_coordinate(j)
                        )
                    )
        return res

    def summarize_residual(self, parm, desc=""):
        """Just print out a summary of the collinearity_residual. This is
        just a human readable summary of the data."""
        res = self.collinearity_residual(parm)
        logger.info(
            "%s Line residual summary: %s",
            desc,
            pd.DataFrame(np.abs(res[0::2])).describe(),
        )
        logger.info(
            "%s Sample residual summary: %s",
            desc,
            pd.DataFrame(np.abs(res[1::2])).describe(),
        )

    def fit_camera(self):
        """Sample of fitting the camera exterior orientation (the euler
        angles). This is a basic sample of how to do this. There is
        the full sba program which can be used if desired, but
        probably things are small enough to just do something like
        this.
        """
        # TODO This is hardcode for AVIRIS-NG exterior camera orientation
        # fitting only. Should instead generalize this for working
        # with EMIT also

        # Grab the camera object.
        cam = self.igccolcorr.camera
        # Set the variables we will fit
        cam.fit_epsilon = True
        cam.fit_beta = True
        cam.fit_delta = True
        # Not sure if we want to fit focal length or not. In general
        # it can change over time a small amount (e.g., 1%). For now,
        # include this
        cam.fit_focal_length = True
        # We have used both GlasGfm and CameraParaxial as a camera. They
        # have a different set of possible parameters, so determine
        # if we need to set the extra ones for CameraParaxial or not
        if hasattr(cam, "fit_principal_point_sample"):
            cam.fit_sample_pitch = False
            cam.fit_line_pitch = False
            cam.fit_principal_point_sample(False, 0)
            cam.fit_principal_point_line(False, 0)
        x0 = cam.parameter_subset.copy()
        if len(x0) == 0:
            logger.info("Nothing to fit")
            return
        logger.info("Initial camera value:")
        for v, desc in zip(cam.parameter_subset, cam.parameter_name_subset):
            logger.info(f"{desc}: {v}")
        self.summarize_residual(x0, desc="Initial")
        # Now fit the data. Can play with this, but for right now
        # just use the default scipy least squares optimization. We choose
        # a version of this that works a bit better with outliers
        r = scipy.optimize.least_squares(self.collinearity_residual, x0, loss="huber")
        logger.info("Fitting results: %s", r)
        logger.info("Fitted camera value:")
        for v, desc in zip(cam.parameter_subset, cam.parameter_name_subset):
            logger.info(f"{desc}: {v}")
        self.summarize_residual(r.x, desc="Fitted")

    def run_sba(self):
        """Run the SBA for correcting our data"""
        if len(self.tpcol) == 0:
            logger.info("No tie-points, so skipping SBA correction")
            return
        try:
            logger.info("Starting SBA")
            process_run(
                [
                    "sba",
                    "--verbose",
                    "--hold-gcp-fixed",
                    "--gcp-sigma=50",
                    "igccolcorr_initial.xml",
                    "tpcol.xml",
                    "igccol_sba.xml",
                    "tpcol_sba.xml",
                ],
                out_fh=open("sba.log", "w"),
            )
            logger.info("SBA Completed")
            self.igccolcorr = geocal.read_shelve("igccol_sba.xml")
            self.correction_done = True
            self.geo_qa.add_final_accuracy(self.igccolcorr, self.tpcol)
        except Exception:
            # TODO Put this logic in place
            # if(not l1b_geo_config.continue_on_sba_fail):
            #    raise
            raise

    # TODO Work on this error model
    def orb_corr(self, orb):
        """Determine our orbit correction model
        Not sure about the full error model. Right now we'll
        do a 1 position correction, and 1 attitude breakpoint for
        each image. Special handling if we skipped a scene. This
        is really pretty adhoc, we should probably play with this
        a bit with real data"""
        orb = geocal.OrbitOffsetCorrection(orb)
        tapprox_scene = 12.0
        tlast = None
        for tmin, tmax in self.time_range_tp:
            if tlast is None:
                orb.insert_position_time_point(tmin)
            if tlast is None or tmin - tlast > tapprox_scene:
                orb.insert_attitude_time_point(tmin)
            orb.insert_attitude_time_point(tmax)
            tlast = tmax
        if tlast is not None:
            orb.insert_position_time_point(tlast)
        return orb

    def igccol_corrected(self, pool=None):
        if self.l1_osp_dir.skip_sba:
            logger.info(
                "Skipping SBA correction, using uncorrected ephemeris and attitude"
            )
            return self.igccol_initial
        self.tpcol, self.time_range_tp = self.l1b_tp_collect.tpcol(pool)
        # Useful to save out, just so we have this
        geocal.write_shelve("tpcol.xml", self.tpcol)
        geocal.write_shelve("igccol_initial.xml", self.igccol_initial)
        self.igccolcorr = geocal.read_shelve("igccol_initial.xml")
        if not self.fit_camera_only:
            self.igccolcorr.orbit = self.orb_corr(self.igccolcorr.orbit)

        # Note we could have parameters for the time table (e.g., a
        # timing offset). But for now we'll leave this off and only
        # include the camera and orbit
        self.igccolcorr.add_object(self.igccolcorr.camera)
        self.igccolcorr.add_object(self.igccolcorr.orbit)
        geocal.write_shelve("igccolcorr_initial.xml", self.igccolcorr)
        # Can also save this whole object, if you want to be able to
        # play with fitting data.
        pickle.dump(self, open("l1b_correct.pkl", "wb"))
        if self.fit_camera_only:
            self.fit_camera()
        else:
            self.run_sba()
        return self.igccolcorr


__all__ = [
    "L1bCorrect",
]
