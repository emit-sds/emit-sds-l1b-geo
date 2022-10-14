from .gaussian_stretch import gaussian_stretch
import geocal
import scipy
import numpy as np
from emit_swig import *
import subprocess
import logging
import pickle

logger = logging.getLogger('l1b_geo_process.loc')

class EmitKmzAndQuicklook(object):
    '''This generate the l1b_geo KMZ file. This is almost the same work
    needed to produce the quick look file, so we fold this in to one
    calculation. We could separate this if there ever a reason.
    
    Note that we don't actually create the data until you run "run" function.
    The EmitLoc should also have been generate (so either you are reading
    an existing file or you have done EmitLoc.run to generate the data).
    '''
    def __init__(self, file_base_name, loc,
                 rad_fname, band_list = [1,1,1],
                 scene_index = 1,
                 igc_index = 0,
                 use_jpeg = False,
                 resolution = 60, number_subpixel = 3,
                 generate_kmz = True,
                 l1_osp_dir = None,
                 generate_quicklook = True, generate_erdas = False):
        self.file_base_name = file_base_name
        self.loc = loc
        self.band_list = band_list
        self.use_jpeg = use_jpeg
        self.resolution = resolution
        self.number_subpixel = number_subpixel
        self.rad_fname = rad_fname
        self.generate_quicklook = generate_quicklook
        self.generate_kmz = generate_kmz
        self.generate_erdas = generate_erdas
        self.scene_index = scene_index
        self.igc_index = igc_index
        self.l1_osp_dir = l1_osp_dir

    def run(self):
        logger.info("Generating KMZ and quicklook")
        mi = geocal.cib01_mapinfo(self.resolution)
        lat, lon = self.loc.scaled_lat_lon_grid(self.number_subpixel)
        res = Resampler(lat, lon, mi, self.number_subpixel, False)
        vrt_fname = "map_scaled_%s.vrt" % self.scene_index
        cmd_merge = ["gdalbuildvrt", "-q", "-separate", vrt_fname]
        if(res.map_info.number_y_pixel > 10000 or
           res.map_info.number_x_pixel > 10000):
            raise RuntimeError(f"Funny map, ending process. File name: {self.file_base_name} Map info: {res.map_info}")
        for b in self.band_list:
            ras = EmitL1bImage(self.rad_fname, b, 1.0)
            data = res.resample_field(ras).copy()
            # Set bad values to 0
            data[np.not_equal(np.isfinite(data), True)] = 0
            # Set fill values to 0
            data[data < -100] = 0
            data_scaled = gaussian_stretch(data)
            fname = "map_b%d_%s_scaled.img" % (b, self.scene_index)
            d = geocal.mmap_file(fname, res.map_info, nodata=0.0,
                                 dtype=np.uint8)
            d[:] = data_scaled
            d = None
            cmd_merge.append(fname)
        subprocess.run(cmd_merge)
        if(self.generate_erdas):
            ref_fname = "ref_final_%03d.img" % (self.igc_index+1)
            self.l1_osp_dir.write_ortho_base_subset(ref_fname, res.map_info)
            # Allow to fail. The pyramid building sometimes fails, and in
            # any case this is just diagnostic check so we don't want to
            # trigger an error just because erdas fails
            subprocess.run(["gdal_to_erdas", vrt_fname,
                            "proj_erdas_%03d.img" % (self.igc_index+1)],
                           check=False)
            subprocess.run(["gdal_to_erdas", ref_fname,
                            "ref_erdas_%03d.img" % (self.igc_index+1)],
                           check=False)
        cmd = ["gdal_translate", "-q", "-of", "KMLSUPEROVERLAY",
               vrt_fname,
               self.file_base_name + ".kmz"]
        if(not self.use_jpeg):
            cmd.extend(["-co", "FORMAT=PNG"])
        if(self.generate_kmz):
            subprocess.run(cmd, check=True)
        cmd = ["gdal_translate", "-q", "-of", "PNG", "-a_nodata", "none",
               vrt_fname, self.file_base_name + ".png"]
        if(self.generate_quicklook):
            subprocess.run(cmd, check=True)
        # Remove the .aux.xml file GDAL generates
        try:
            os.unlink(self.file_base_name + ".kmz" + ".aux.xml")
        except FileNotFoundError:
            pass
        try:
            os.unlink(self.file_base_name + ".png" + ".aux.xml")
        except FileNotFoundError:
            pass
        
    
__all__ = ["EmitKmzAndQuicklook",]
