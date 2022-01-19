from .envi_file import EnviFile
from .misc import orb_and_scene_from_file_name
import geocal
import numpy as np
import os
import shutil
import logging
import re

logger = logging.getLogger('l1b_geo_process.l1b_geo_generate')

class L1bGeoGenerate:
    '''This is the overall l1b_geo process. This class writes output
    and temporary files to the current directory, and processes all
    the scenes.'''
    def __init__(self, l1b_geo_config, l1a_att_fname, line_time_fname_list,
                 l1b_rad_fname_list):
        self.l1b_geo_config = l1b_geo_config
        self.l1a_att_fname = l1a_att_fname
        self.orbit_number, _ = orb_and_scene_from_file_name(l1b_rad_fname_list[0])
        self.scene_to_fname = {}
        self.l1b_rad_fname = {}
        for i in range(len(l1b_rad_fname_list)):
            _, scene = orb_and_scene_from_file_name(l1b_rad_fname_list[i])
            self.scene_to_fname[scene] = (line_time_fname_list[i],
                                          l1b_rad_fname_list[i])

    def run(self):
        logger.info("Starting L1bGeoGenerate")
        # TODO SBA correction
        for scene in sorted(self.scene_to_fname.keys()):
            logger.info("Processing scene %s", scene)

                
__all__ = ["L1bGeoGenerate",]
