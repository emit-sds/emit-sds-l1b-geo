from .aviris_ng_loc import AvirisNgLoc
from .aviris_ng_igm import AvirisNgIgm
from .aviris_ng_obs import AvirisNgObs
from .aviris_ng_orbit import AvirisNgOrbit
from .aviris_ng_time_table import AvirisNgTimeTable
from .aviris_ng_standard_metadata import AvirisNgStandardMetadata
import geocal
import logging
import re
import os
from multiprocessing import Pool

logger = logging.getLogger('l1b_geo_process.aviris_ng_geo_generate')

class AvirisNgGeoGenerate:
    '''This is the overall l1b geo process for AVIRIS NG. This is very
    similar to L1bGeoGenerate for EMIT, but we have this as a separate class
    so we can handle all the differences between AVIRIS NG and EMIT.'''
    def __init__(self, l1_osp_dir, orb_fname, tt_fname, rad_fname):
        self.orb_fname = orb_fname
        self.tt_fname = tt_fname
        self.rad_fname = rad_fname
        self.l1_osp_dir = l1_osp_dir
        self.basename = re.sub(r'_att.nc$', '', os.path.basename(self.orb_fname) )
        # TODO Change DEM, possibly from config file
        dem = geocal.SrtmDem()
        self.orb = AvirisNgOrbit(self.orb_fname)
        self.tt = AvirisNgTimeTable(self.tt_fname)
        self.rad = geocal.GdalRasterImage(rad_fname,
                            l1_osp_dir.l1b_geo_config.match_rad_band)
        self.cam = l1_osp_dir.camera()
        self.ipi = geocal.Ipi(self.orb,self.cam,0,self.tt.min_time,
                              self.tt.max_time,self.tt)
        self.igc = geocal.IpiImageGroundConnection(self.ipi, dem, None)
  
    def run(self):
        logger.info("Starting AvirisNgGeoGenerate")
        standard_metadata = AvirisNgStandardMetadata(line_averaging=self.tt.line_average)
        if(self.l1_osp_dir.l1b_geo_config.number_process > 1):
            logger.info("Using %d processors", self.l1_osp_dir.l1b_geo_config.number_process)
            pool = Pool(self.l1_osp_dir.l1b_geo_config.number_process)
        else:
            logger.info("Using 1 processor")
            pool = None
        # TODO: Tiepoint/correction goes here. We'll need to add this
        # TODO: Write corrected orbit
        loc_fname = self.basename + "_loc"
        igm_fname = self.basename + "_igm"
        obs_fname = self.basename + "_obs"
        loc = AvirisNgLoc(loc_fname, igc=self.igc,
                          standard_metadata=standard_metadata)
        igm = AvirisNgIgm(igm_fname, igc=self.igc, loc=loc,
                          standard_metadata=standard_metadata)
        obs = AvirisNgObs(obs_fname, igc=self.igc, loc=loc,
                          standard_metadata=standard_metadata)
        # GLT
        loc.run(pool=pool)
        igm.run(pool=pool)
        obs.run(pool=pool)
        logger.info("Skipping GLT, we don't yet work with UTM")
        
__all__ = ["AvirisNgGeoGenerate", ]
