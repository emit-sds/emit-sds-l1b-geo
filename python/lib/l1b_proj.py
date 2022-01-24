from .misc import band_to_landsat_band
import subprocess
import geocal
import os
import logging

logger = logging.getLogger('l1b_geo_process.l1b_proj')

class L1bProj(object):
    '''This handles projection the Igc to the surface, forming a vicar file
    that we can match against.'''
    def __init__(self, igccol, l1b_geo_config, geo_qa):
        self.igccol = igccol
        self.geo_qa = geo_qa
        self.l1b_geo_config = l1b_geo_config
        logger.info("OrthoBase dir: %s", l1b_geo_config.ortho_base_dir)
        logger.info("Landsat band: %d", l1b_geo_config.landsat_band)
        self.ortho = geocal.Landsat7Global(l1b_geo_config.ortho_base_dir,
                          band_to_landsat_band(l1b_geo_config.landsat_band))
        # Want to scale to roughly 60 meters. Much of the landsat data
        # is at a higher resolution, but emit is roughly 60 meter, so
        # we want to data to roughly match
        self.ortho_scale = round(l1b_geo_config.match_resolution /
                                 self.ortho.map_info.resolution_meter)
        if(not os.path.exists("extra_python_init.py")):
            with open("extra_python_init.py", "w") as fh:
                print("from emit import *\n", file=fh)

    def proj_scene(self, i):
        '''Project data for a scene.'''
        igc = self.igccol.image_ground_connection(i)
        mibase = self.ortho.map_info.scale(self.ortho_scale, self.ortho_scale)
        mi = igc.cover(mibase)
        mi_fname = "map_info_%03d.xml" % (i+1)
        igc_fname = "igc_initial_%03d.xml" % (i+1)
        proj_fname = "proj_initial_%03d.img" % (i+1)
        ref_fname = "ref_%03d.img" % (i+i)
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
        # Can't pickle this with the pool, so just set to None for now.
        # We don't actually need this for anything in proj_scene.
        l1b_geo_config = self.l1b_geo_config
        try:
            self.l1b_geo_config = None
            if(pool is None):
                res = list(map(self.proj_scene,
                           list(range(self.igccol.number_image))))
            else:
                res = pool.map(self.proj_scene,
                               list(range(self.igccol.number_image)))
        finally:
            self.l1b_geo_config = l1b_geo_config
        return res
        

__all__ = ["L1bProj",]
