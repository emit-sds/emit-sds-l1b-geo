from .envi_file import EnviFile
from .emit_igc import EmitIgc
from .emit_loc import EmitLoc
from .emit_obs import EmitObs
from .emit_glt import EmitGlt
from .geo_qa import GeoQa
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
from multiprocessing import Pool

logger = logging.getLogger('l1b_geo_process.l1b_geo_generate')

class L1bGeoGenerate:
    '''This is the overall l1b_geo process. This class writes output
    and temporary files to the current directory, and processes all
    the scenes.'''
    def __init__(self, l1_osp_dir, l1a_att_fname, line_time_fname_list,
                 l1b_rad_fname_list):
        self.l1_osp_dir = l1_osp_dir
        self.l1a_att_fname = l1a_att_fname
        self.tt_and_rdn_fname = zip(line_time_fname_list, l1b_rad_fname_list)
        self.igccol_initial = EmitIgcCollection.create(self.l1a_att_fname,
                                  self.tt_and_rdn_fname,
                                  self.l1_osp_dir.match_rad_band,
                                  l1_osp_dir = self.l1_osp_dir)
        tstart = self.igccol_initial.image_ground_connection(0).ipi.time_table.min_time
        self.build_version = self.l1_osp_dir.build_version
        self.product_version = self.l1_osp_dir.product_version
        self.orbit_number = self.igccol_initial.orbit_number
        qa_fname = emit_file_name("l1b_geoqa", tstart,
                                   int(self.orbit_number),
                                   None,
                                   int(self.build_version),
                                   int(self.product_version),
                                   ".nc")
        self.geo_qa = GeoQa(qa_fname, "l1b_geo.log")

    @property
    def uncorrected_orbit(self):
        return self.igccol_initial.uncorrected_orbit

    @property
    def corrected_orbit(self):
        return self.igccol_corrected.image_ground_connection(0).ipi.orbit
    
    def run_scene(self, i):
        igc = self.igccol_corrected.image_ground_connection(i)
        scene = self.scene_list[i]
        logger.info("Processing %s", igc.title)
        standard_metadata = StandardMetadata(igc=igc)
        loc_fname = emit_file_name("l1b_loc", igc.ipi.time_table.min_time,
                                   int(self.orbit_number),
                                   int(scene),
                                   int(self.build_version),
                                   int(self.product_version),
                                   ".img")
        obs_fname = emit_file_name("l1b_obs", igc.ipi.time_table.min_time,
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
        kmz_base_fname = re.sub(r'_rdn_', '_rdnrgb_', kmz_base_fname)
        loc = EmitLoc(loc_fname, igc=igc, standard_metadata=standard_metadata)
        obs = EmitObs(obs_fname, igc=igc, standard_metadata=standard_metadata,
                      loc=loc)
        glt = EmitGlt(glt_fname, loc=loc,
                      standard_metadata=standard_metadata,
                      rotated_map=self.glt_rotated)
        kmz = None
        if(self.generate_kmz or
           self.generate_quicklook):
            kmz = EmitKmzAndQuicklook(kmz_base_fname, loc, rad_fname,
                   scene = int(scene),
                   band_list = self.map_band_list,
                   use_jpeg = self.kmz_use_jpeg,
                   resolution = self.map_resolution,
                   number_subpixel = self.map_number_subpixel,
                   generate_kmz = self.generate_kmz,
                   generate_quicklook = self.generate_quicklook)
        loc.run()
        obs.run()
        glt.run()
        if(kmz):
            kmz.run()
        # obs file

    def run(self):
        logger.info("Starting L1bGeoGenerate")
        if(self.l1_osp_dir.number_process > 1):
            logger.info("Using %d processors", self.l1_osp_dir.number_process)
            pool = Pool(self.l1_osp_dir.number_process)
        else:
            logger.info("Using 1 processor")
            pool = None
        l1b_correct = L1bCorrect(self.igccol_initial, self.l1_osp_dir,
                                 self.geo_qa)
        self.igccol_corrected = l1b_correct.igccol_corrected(pool=pool)
        tstart = self.igccol_initial.image_ground_connection(0).ipi.time_table.min_time
        orb_fname = emit_file_name("l1b_att", tstart,
                                   int(self.orbit_number),
                                   None,
                                   int(self.build_version),
                                   int(self.product_version),
                                   ".nc")
        self.uncorrected_orbit.write_corrected_orbit(orb_fname,
                                                     self.corrected_orbit)
        # For convenience, grab data for l1b_geo_config, just so we don't
        # have lots of long strings
        self.scene_list = self.igccol_initial.scene_list
        self.generate_kmz = self.l1_osp_dir.generate_kmz
        self.generate_quicklook = self.l1_osp_dir.generate_quicklook
        self.map_band_list = self.l1_osp_dir.map_band_list
        self.kmz_use_jpeg = self.l1_osp_dir.kmz_use_jpeg
        self.map_resolution = self.l1_osp_dir.map_resolution
        self.map_number_subpixel = self.l1_osp_dir.map_number_subpixel
        self.glt_rotated = self.l1_osp_dir.glt_rotated
        if(pool is None):
            res = list(map(self.run_scene,
                           list(range(self.igccol_corrected.number_image))))
        else:
            res = pool.map(self.run_scene,
                           list(range(self.igccol_corrected.number_image)))
        if(self.geo_qa is not None):
            # TODO Any flushing of log file needed?
            self.geo_qa.close()
                
__all__ = ["L1bGeoGenerate",]
