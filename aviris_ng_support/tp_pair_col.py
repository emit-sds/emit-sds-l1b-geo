import geocal
import multiprocessing
import os
import glob
import pandas as pd
import numpy as np

class TpPairCol(object):
    def __init__(self, igccol, mi, sample_spacing=10, matcher=None):
        self.igccol = igccol
        self.ri = geocal.RayIntersect2(igccol, max_ground_covariance = 100*100)
        self.igc1 = self.igccol.image_ground_connection(0)
        self.igc2 = self.igccol.image_ground_connection(1)
        self.mi = mi
        self.sample_spacing = sample_spacing
        if(not matcher):
            matcher = geocal.CcorrLsmMatcher()
        self.mtch = geocal.SurfaceImageToImageMatch(self.igc1, self.igc2,
                                                    mi, matcher)

    def tp_ln(self, ln):
        print(f"Starting {ln}")
        res = []
        for smp in range(0,self.igc1.number_sample,self.sample_spacing):
            ic = geocal.ImageCoordinate(ln, smp)
            ic2, lsigma, ssigma, success, diagnostic = self.mtch.match(ic)
            if(success):
                tp = geocal.TiePoint(2)
                tp.image_coordinate(0, ic, 0.05, 0.05)
                tp.image_coordinate(1, ic2, lsigma, ssigma)
                tp2 = self.ri.ray_intersect(tp)
                res.append(tp2)
                ic2_guess = self.igc2.image_coordinate(self.igc1.ground_coordinate(ic))
                print(ic, ic2_guess, ic2, ic2.line-ic2_guess.line,
                      ic2.sample-ic2_guess.sample,
                      geocal.distance(self.igc1.ground_coordinate(ic),
                               self.igc2.ground_coordinate(ic2)))
        return res

    def tpcol(self, llist=None, pool=None):
        if(not llist):
            llist = list(range(0, self.igc1.number_line, 100))
        if(pool):
            res = pool.map(self.tp_ln, llist,
                           max(len(llist) // multiprocessing.cpu_count(), 1))
        else:
            res = list(map(self.tp_ln, llist))
        res2 = geocal.TiePointCollection()
        for t in res:
            res2.extend([tp for tp in t if tp is not None])
        return res2

    @classmethod
    def tp_to_dist(cls, tpcol, igc1, igc2):
        '''Return distance that the tie-points would be on the ground given
        the two igcs'''
        res = []
        for tp in tpcol:
            gp1 = igc1.ground_coordinate(tp.image_coordinate(0))
            gp2 = igc2.ground_coordinate(tp.image_coordinate(1))
            # Project to surface, so we don't include the DEM difference
            # in the distance
            gp1 = geocal.SimpleDem().surface_point(gp1)
            gp2 = geocal.SimpleDem().surface_point(gp2)
            res.append(distance(gp1, gp2))
        return res

    @classmethod
    def camera_field_alignment(cls, tpcol, igc1, igc2,
                               min_ic1_sample = 100, max_ic1_sample=500,
                               focal_length = 27.5,
                           frame_to_sc = geocal.Quaternion_double(1,0,0,0)):
        '''Return an array with sample, field alignment x and y
        for the given set of tie-points. The field alignment values are
        redundant with the focal_length and frame_to_sc (e.g., if you change
        the focal_length you can just return different field alignment values
        that give the same pointing). You can supply the pointing and focal 
        length that you would like.'''
        res = []
        for tp in tpcol:
            ic1 = tp.image_coordinate(0)
            # Restrict to middle of camera, which seems to be reasonable
            # accurate with ground truth. This is because we are bootstrapping
            # here, we want to use data that we are reasonable sure is
            # accurate to begin with
            if(ic1.sample >= min_ic1_sample and ic1.sample <= max_ic1_sample):
                gp1 = igc1.ground_coordinate(ic1)
                ic2 = tp.image_coordinate(1)
                tm,_ = igc2.ipi.time_table.time(ic2)
                slv = igc2.ipi.orbit.sc_look_vector(tm,gp1)
                dcs = frame_to_sc.conj() * slv.look_quaternion * frame_to_sc
                x = focal_length * dcs.R_component_2 / dcs.R_component_4
                y = focal_length * dcs.R_component_3 / dcs.R_component_4
                res.append([ic2.sample, x, y])
        return(np.array(res))

    @classmethod
    def tp_to_df(cls, tpcol, igc1, igc2):
        '''Return a pandas data frame that contains a summary of
        The data in the tpcol and the residuals.'''
        data = []
        for tp in tpcol:
            ic1 = tp.image_coordinate(0)
            gp1 = igc1.ground_coordinate(ic1)
            ic2_pred = igc2.image_coordinate(gp1)
            ic2 = tp.image_coordinate(1)
            gp2 = igc2.ground_coordinate(ic2)
            gp1=geocal.SimpleDem().surface_point(gp1)
            gp2=geocal.SimpleDem().surface_point(gp2)
            data.append([ic1.line, ic1.sample, ic2.line, ic2.sample,
                         ic2.line-ic2_pred.line, ic2.sample-ic2_pred.sample,
                         geocal.distance(gp1,gp2)])
        data = np.array(data)
        df = pd.DataFrame(data, columns=["line 1", "sample 1",
                                         "line 2", "sample 2",
                                         "line residual", "sample residual",
                                         "dist"])
        return df
        
