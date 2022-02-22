from .aviris_ng_loc import AvirisNgLoc
from .aviris_ng_igm import AvirisNgIgm
from .aviris_ng_obs import AvirisNgObs
from .aviris_ng_standard_metadata import AvirisNgStandardMetadata
import logging
import re
from multiprocessing import Pool

logger = logging.getLogger('l1b_geo_process.aviris_ng_geo_generate')

class AvirisNgGeoGenerate:
    '''This is the overall l1b geo process for AVIRIS NG. This is very
    similar to L1bGeoGenerate for EMIT, but we have this as a separate class
    so we can handle all the differences between AVIRIS NG and EMIT.'''
    def __init__(self, igc, l1_osp_dir):
        self.igc = igc
        self.l1_osp_dir = l1_osp_dir
        start_time = self.igc.ipi.time_table.min_time
        dstring = re.sub(r'T', 't', re.sub(r'[-:]', '',
                                           re.split(r'\.', str(start_time))[0]))
        self.basename = f"ang{dstring}_rdn_"
  
    def run(self):
        logger.info("Starting AvirisNgGeoGenerate")
        line_averaging = 9      # TODO: Where does this come from?
        standard_metadata = AvirisNgStandardMetadata(line_averaging=line_averaging)
        if(self.l1_osp_dir.l1b_geo_config.number_process > 1):
            logger.info("Using %d processors", self.l1_osp_dir.l1b_geo_config.number_process)
            pool = Pool(self.l1_osp_dir.l1b_geo_config.number_process)
        else:
            logger.info("Using 1 processor")
            pool = None
        # TODO: Tiepoint/correction goes here. We'll need to add this
        # TODO: Write corrected orbit
        loc_fname = self.basename + "loc"
        igm_fname = self.basename + "igm"
        obs_fname = self.basename + "obs"
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
