from .aviris_ng_orbit import AvirisNgOrbit
from .aviris_ng_raw import AvirisNgRaw
from .aviris_ng_time_table import AvirisNgTimeTable
import logging
import re
import os

logger = logging.getLogger('l1b_geo_process.aviris_ng_l1a_orbit_generate')

class AvirisNgL1aOrbitGenerate:
    '''This is the overall l1a orbit process for AVIRIS NG. This
    creates the initial orbit, time table, and line averaging files'''
    def __init__(self, raw_fname, gps_fname, pps_fname, l1_osp_dir):
        self.raw_fname = raw_fname
        self.gps_fname = gps_fname
        self.pps_fname = pps_fname
        self.l1_osp_dir = l1_osp_dir
        self.basename = re.sub(r'_raw$', '', os.path.basename(self.raw_fname) )
        logger.info("Raw file:   %s", self.raw_fname)
        logger.info("GPS file:   %s", self.gps_fname)
        logger.info("PPS file:   %s", self.pps_fname)
        logger.info("L1 OSP dir: %s", self.l1_osp_dir.l1_osp_dir)
    def run(self):
        logger.info("Starting AvirisNgL1aOrbitGenerate")
        orb = AvirisNgOrbit(self.gps_fname)
        orb.write_orbit(self.basename + "_att.nc")
        r = AvirisNgRaw(self.raw_fname)
        # TODO calculate this
        line_average = 9
        tt = AvirisNgTimeTable(self.pps_fname, raw=r,
                               line_average=line_average)
        tt.write(self.basename + "_line_time.nc")
        with open(self.basename + "_raw.binfac", "w") as fh:
            print(line_average, file=fh)
            
        
__all__ = ["AvirisNgL1aOrbitGenerate", ]
