from .misc import band_to_landsat_band
import subprocess
import geocal
import os
import logging

logger = logging.getLogger('l1b_geo_process.l1b_proj')

# Temp, this should probably get moved into geocal. But for now place here
# This should also get expanded, right now this doesn't handle resizing etc.
def _create_subset_file(self, fname, driver, Desired_map_info = None,
                        Translate_arg = None):
    r = geocal.SubRasterImage(self, Desired_map_info)
    geocal.GdalRasterImage.save(fname, driver, r, geocal.GdalRasterImage.Int16)

geocal.GdalRasterImage.create_subset_file = _create_subset_file    

class L1bProj(object):
    '''This handles projection the Igc to the surface, forming a vicar file
    that we can match against.'''
    def __init__(self, igccol, l1_osp_dir, geo_qa,
                 img_type="initial"):
        self.igccol = igccol
        self.geo_qa = geo_qa
        self.l1_osp_dir = l1_osp_dir
        self.img_type = img_type
        logger.info("OrthoBase dir: %s", l1_osp_dir.ortho_base_dir)
        logger.info("Landsat band: %d", l1_osp_dir.landsat_band)
        #self.ortho = geocal.Landsat7Global(l1_osp_dir.ortho_base_dir,
        #                  band_to_landsat_band(l1_osp_dir.landsat_band))
        self.ortho = geocal.GdalRasterImage("/beegfs/scratch/brodrick/shift/pre_campaign_analyses/ancillary_data/sentinel_2_20220307.tif", 1)        

        # Want to scale to the reference resolution:
        #self.ortho_scale = round(l1_osp_dir.match_resolution /
        #                         self.ortho.map_info.resolution_meter)
        # Use full resolution of aviris-ng
        self.ortho_scale = 1
        if(not os.path.exists("extra_python_init.py")):
            with open("extra_python_init.py", "w") as fh:
                print("from emit import *\n", file=fh)

    def proj_scene(self, i):
        '''Project data for a scene.'''
        igc = self.igccol.image_ground_connection(i)
        mibase = self.ortho.map_info.scale(self.ortho_scale, self.ortho_scale)
        mi = igc.cover(mibase)
        mi_fname = "map_info_%s_%03d.xml" % (self.img_type, i+1)
        igc_fname = "igc_%s_%03d.xml" % (self.img_type, i+1)
        proj_fname = "proj_%s_%03d.img" % (self.img_type, i+1)
        ref_fname = "ref_%s_%03d.img" % (self.img_type, i+1)
        logger.info("Creating %s", proj_fname)
        geocal.write_shelve(mi_fname, mi)
        geocal.write_shelve(igc_fname, igc)
        subprocess.run(["igc_raycast_project", f"--map-info={mi_fname}",
                        igc_fname, proj_fname], check=True)
        self.ortho.create_subset_file(ref_fname,
                                      "VICAR",
                                      Desired_map_info = mi,
                                      Translate_arg = "-ot Int16")
        return (proj_fname, ref_fname)

    def proj(self, pool=None):
        '''Project all the scenes, using the given multiprocessing pool
        if supplied.'''
        if(pool is None):
            res = list(map(self.proj_scene,
                           list(range(self.igccol.number_image))))
        else:
            res = pool.map(self.proj_scene,
                           list(range(self.igccol.number_image)))
        return res
        

__all__ = ["L1bProj",]
