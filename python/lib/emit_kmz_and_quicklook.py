from .gaussian_stretch import gaussian_stretch
import geocal
import scipy
import numpy as np
from emit_swig import *
import subprocess
import logging

logger = logging.getLogger('l1b_geo_process.emit_loc')

class EmitKmzAndQuicklook(object):
    '''This generate the l1b_geo KMZ file. This is almost the same work
    needed to produce the quick look file, so we fold this in to one
    calculation. We could separate this if there ever a reason.
    
    Note that we don't actually create the data until you run "run" function.
    The EmitLoc should also have been generate (so either you are reading
    an existing file or you have done EmitLoc.run to generate the data).
    '''
    def __init__(self, file_base_name, emit_loc,
                 rad_fname, band_list = [1,1,1],
                 use_jpeg = False,
                 resolution = 60, number_subpixel = 3):
        self.file_base_name = file_base_name
        self.emit_loc = emit_loc
        self.band_list = band_list
        self.use_jpeg = use_jpeg
        self.resolution = resolution
        self.number_subpixel = number_subpixel
        self.rad_fname = rad_fname

    def run(self):
        logger.info("Generating KMZ and quicklook")
        mi = geocal.cib01_mapinfo(self.resolution)
        lat = scipy.ndimage.interpolation.zoom(self.emit_loc.latitude,
                                               self.number_subpixel, order=2)
        lon = scipy.ndimage.interpolation.zoom(self.emit_loc.longitude,
                                               self.number_subpixel, order=2)
        res = Resampler(lat, lon, mi, self.number_subpixel, False)
        cmd_merge = ["gdalbuildvrt", "-q", "-separate", "map_scaled.vrt"]
        for b in self.band_list:
            ras = geocal.GdalRasterImage(self.rad_fname, b)
            data = res.resample_field(ras)
            data_scaled = gaussian_stretch(data)
            fname = "map_b%d_scaled.img" % b
            d = geocal.mmap_file(fname, res.map_info, nodata=0.0,
                                 dtype=np.uint8)
            d[:] = data_scaled
            d = None
            cmd_merge.append(fname)
        subprocess.run(cmd_merge)
        cmd = ["gdal_translate", "-of", "KMLSUPEROVERLAY", "map_scaled.vrt",
               self.file_base_name + ".kmz"]
        if(not self.use_jpeg):
            cmd.extend(["-co", "FORMAT=PNG"])
        subprocess.run(cmd, check=True)
        cmd = ["gdal_translate", "-of", "PNG", "-a_nodata", "none",
               "map_scaled.vrt", self.file_base_name + ".png"]        
        subprocess.run(cmd, check=True)
    
__all__ = ["EmitKmzAndQuicklook",]
