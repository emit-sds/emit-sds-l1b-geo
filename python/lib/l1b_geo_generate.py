from .envi_file import EnviFile
from .emit_igc import EmitIgc
from .emit_loc import EmitLoc
from .emit_glt import EmitGlt
from .emit_kmz_and_quicklook import EmitKmzAndQuicklook
from .misc import orb_and_scene_from_file_name, emit_file_name
from .standard_metadata import StandardMetadata
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

    def run_scene(self, scene):
        logger.info("Processing scene %s", scene)
        igc = EmitIgc(self.l1a_att_fname, *self.scene_to_fname[scene])
        igc.title = "Scene %s" % scene
        standard_metadata = StandardMetadata(igc=igc)
        loc_fname = emit_file_name("l1b_loc", igc.ipi.time_table.min_time,
                                   int(self.orbit_number),
                                   int(scene),
                                   int(self.l1b_geo_config.build_version),
                                   int(self.l1b_geo_config.product_version),
                                   ".img")
        glt_fname = emit_file_name("l1b_glt", igc.ipi.time_table.min_time,
                                   int(self.orbit_number),
                                   int(scene),
                                   int(self.l1b_geo_config.build_version),
                                   int(self.l1b_geo_config.product_version),
                                   ".img")
        # KMZ and quicklook name based on l1b_rad_fname.
        _, rad_fname = self.scene_to_fname[scene]
        kmz_base_fname, _ = os.path.splitext(os.path.basename(rad_fname))
        loc = EmitLoc(loc_fname, igc=igc, standard_metadata=standard_metadata)
        glt = EmitGlt(glt_fname, emit_loc=loc,
                      standard_metadata=standard_metadata)
        kmz = None
        if(self.l1b_geo_config.generate_kmz or
           self.l1b_geo_config.generate_quicklook):
            kmz = EmitKmzAndQuicklook(kmz_base_fname, loc, rad_fname,
                   band_list = self.l1b_geo_config.map_band_list,
                   use_jpeg = self.l1b_geo_config.kmz_use_jpeg,
                   resolution = self.l1b_geo_config.map_resolution,
                   number_subpixel = self.l1b_geo_config.map_number_subpixel,
                   generate_kmz = self.l1b_geo_config.generate_kmz,
                   generate_quicklook = self.l1b_geo_config.generate_quicklook)
        loc.run()
        glt.run()
        if(kmz):
            kmz.run()
        # obs file

    def run(self):
        logger.info("Starting L1bGeoGenerate")
        # TODO SBA correction
        # TODO Write out corrected ephemeris data
        # TODO Write out QA data
        for scene in sorted(self.scene_to_fname.keys()):
            self.run_scene(scene)
                
__all__ = ["L1bGeoGenerate",]
