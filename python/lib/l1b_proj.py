import subprocess
import geocal
import os
import logging
import re

logger = logging.getLogger('l1b_geo_process.l1b_proj')

class L1bProj(object):
    '''This handles projection the Igc to the surface, forming a vicar file
    that we can match against.'''
    def __init__(self, igccol, l1_osp_dir, geo_qa,
                 img_type="initial"):
        self.igccol = igccol
        self.geo_qa = geo_qa
        self.l1_osp_dir = l1_osp_dir
        self.img_type = img_type
        if(not os.path.exists("extra_python_init.py")):
            with open("extra_python_init.py", "w") as fh:
                print("from emit import *\n", file=fh)

    def proj_scene(self, i):
        '''Project data for a scene.'''
        igc = self.igccol.image_ground_connection(i)
        mi = self.l1_osp_dir.match_mapinfo(igc)
        mi_fname = "map_info_%s_%03d.xml" % (self.img_type, i+1)
        igc_fname = "igc_%s_%03d.xml" % (self.img_type, i+1)
        proj_fname = "proj_%s_%03d.img" % (self.img_type, i+1)
        ref_fname = "ref_%s_%03d.img" % (self.img_type, i+1)
        logger.info("Creating %s", proj_fname)
        geocal.write_shelve(mi_fname, mi)
        geocal.write_shelve(igc_fname, igc)
        try:
            self.l1_osp_dir.write_ortho_base_subset(ref_fname, mi)
        except RuntimeError as e:
            if(not re.search("RasterImage doesn't cover any of the area", str(e))):
                raise
            logger.info("Don't have reference data for scene %03d, skipping", i+1)
            return None
        subprocess.run(["igc_raycast_project", f"--map-info={mi_fname}",
                        igc_fname, proj_fname + ".tmp"], check=True)
        subprocess.run(f"gdal_calc.py --quiet -A {proj_fname}.tmp --outfile={proj_fname}.tif --type=Float32 --calc=\"A*(A>0)\" --NoDataValue=0", shell=True,
                       check=True)
        subprocess.run(["gdal_translate", "-of", "VICAR", "-q",
                        "-ot", "Int16",
                        proj_fname+".tif",
                        proj_fname], check=True)
        subprocess.run(["rm", proj_fname + ".tmp", proj_fname + ".tif"])
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
