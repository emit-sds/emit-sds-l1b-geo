from .envi_file import EnviFile
from .emit_igc import EmitIgc
from .emit_loc import EmitLoc
from .emit_glt import EmitGlt
from .l1b_correct import L1bCorrect
from .emit_kmz_and_quicklook import EmitKmzAndQuicklook
from .misc import orb_and_scene_from_file_name, emit_file_name
from .standard_metadata import StandardMetadata
from emit_swig import EmitIgcCollection
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
        self.tt_and_rdn_fname = zip(line_time_fname_list, l1b_rad_fname_list)
        self.igccol_initial = EmitIgcCollection.create(self.l1a_att_fname,
                                  self.tt_and_rdn_fname,
                                  self.l1b_geo_config.match_rad_band,
                                  l1b_geo_config = self.l1b_geo_config)
        # TODO Add this in
        self.geo_qa = None
        self.l1b_correct = L1bCorrect(self.igccol_initial, self.l1b_geo_config,
                                      self.geo_qa)

    @property
    def orbit_number(self):
        return self.igccol_initial.orbit_number

    @property
    def build_version(self):
        return self.l1b_geo_config.build_version

    @property
    def product_version(self):
        return self.l1b_geo_config.product_version

    @property
    def uncorrected_orbit(self):
        return self.igccol_initial.uncorrected_orbit

    @property
    def corrected_orbit(self):
        return self.igccol_corrected.image_ground_connection(0).ipi.orbit
    
    def run_scene(self, igc, scene):
        logger.info("Processing %s", igc.title)
        standard_metadata = StandardMetadata(igc=igc)
        loc_fname = emit_file_name("l1b_loc", igc.ipi.time_table.min_time,
                                   int(self.orbit_number),
                                   int(scene),
                                   int(self.build_version),
                                   int(self.product_version),
                                   ".img")
        glt_fname = emit_file_name("l1b_glt", igc.ipi.time_table.min_time,
                                   int(self.orbit_number),
                                   int(scene),
                                   int(self.build_version),
                                   int(self.product_version),
                                   ".img")
        # KMZ and quicklook name based on l1b_rad_fname.
        rad_fname = igc.image.file_names[0]
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
        self.l1b_correct.run()
        self.igccol_corrected = self.l1b_correct.igccol_corrected
        tstart = self.igccol_initial.image_ground_connection(0).ipi.time_table.min_time
        orb_fname = emit_file_name("l1b_att", tstart,
                                   int(self.orbit_number),
                                   None,
                                   int(self.build_version),
                                   int(self.product_version),
                                   ".nc")
        self.uncorrected_orbit.write_corrected_orbit(orb_fname,
                                                     self.corrected_orbit)
        for i in range(self.igccol_corrected.number_image):
            self.run_scene(self.igccol_corrected.image_ground_connection(i),
                           self.igccol_initial.scene_list[i])
        if(self.geo_qa is not None):
            geo_qa.write()
                
__all__ = ["L1bGeoGenerate",]
