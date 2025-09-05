import geocal
import scipy
import numpy as np
from emit_swig import *
from .envi_file import EnviFile
import subprocess
import logging
import cv2
import math

logger = logging.getLogger('l1b_geo_process.aviris_ng_glt')

class AvirisNgGlt(EnviFile):
    '''This generate the aviris_glt_geo GLT file. 
    
    1. Integer rather than a float that you would normally use for resampling.
    2. 1 based rather than the 0 based you might expect
    3. Has a fill value of 0

    We don't actually do anything with the GLT, instead use the LOC for
    resampling (which is a better thing to do). So we just match what the
    historical data used.

    Note that we don't actually create the data until you run "run" function.
    The EmitLoc should also have been generate (so either you are reading
    an existing file or you have done EmitLoc.run to generate the data).
    '''
    def __init__(self, fname, loc = None, igm = None, igc=None,
                 standard_metadata = None,
                 resolution = 20, number_subpixel = 3,
                 rotated_map = True):
        self.fname = fname
        self.loc = loc
        self.igm = igm
        self.resolution = resolution
        self.standard_metadata = standard_metadata
        self.number_subpixel = number_subpixel
        self.rotated_map = rotated_map
        # Note that if we are writing the file, then we actually need to
        # wait on calling __init__ because we don't know the size yet.
        if(self.loc is None):
            super().__init__(fname, mode="r")
        
    def map_info_not_rotated(self):
        mi = geocal.cib01_mapinfo(self.resolution)
        # We only need the edges pixels, this defines the full
        # range of data here
        lat = self.loc.latitude
        lon = self.loc.longitude
        pt = [geocal.Geodetic(lat[0,i], lon[0, i]) for
              i in range(self.loc.shape[2])]
        pt.extend(geocal.Geodetic(lat[-1,i], lon[-1, i]) for
                  i in range(self.loc.shape[2]))
        pt.extend(geocal.Geodetic(lat[i,0], lon[i,0]) for
                  i in range(self.loc.shape[2]))
        pt.extend(geocal.Geodetic(lat[i,-1], lon[i,-1]) for
                  i in range(self.loc.shape[2]))
        mi = mi.cover(pt)
        return mi

    def map_info_rotated(self):
        cconv = geocal.OgrCoordinateConverter(self.igm.ogrw)
        mi = geocal.MapInfo(cconv, 0,0,self.resolution,self.resolution,1,1)
        mi = geocal.cib01_mapinfo(self.resolution)
        return self.loc.map_info_rotated(mi)

    @property
    def glt_line(self):
        return self[1,:,:]

    @property
    def glt_sample(self):
        return self[0,:,:]
    
    def run(self):
        logger.info("Generating GLT")
        if(self.rotated_map):
            mi = self.map_info_rotated()
        else:
            mi = self.map_info_not_rotated()
        lat, lon = self.loc.scaled_lat_lon_grid(self.number_subpixel)
        res = Resampler(lat, lon, mi, self.number_subpixel, False)
        super().__init__(self.fname, map_info = res.map_info,
                         shape=(2,res.map_info.number_y_pixel,
                                res.map_info.number_x_pixel),
                         dtype=np.int32, mode="w",
                         description="ANG AIG VSWIR RT-Ortho GLT (IGM sample, IGM line",
                         band_description = ["GLT Sample Lookup", "GLT Line Lookup"])
        # TODO We are using the smallest line/sample here. We should change
        # this to instead use the nearest
        ln_d = np.broadcast_to(np.arange(0,self.loc.shape[1])[:,np.newaxis],
                               self.loc.latitude.shape)
        smp_d = np.broadcast_to(np.arange(0,self.loc.shape[2])[np.newaxis,:],
                               self.loc.latitude.shape)
        ln_d = np.ascontiguousarray(ln_d)
        smp_d = np.ascontiguousarray(smp_d)
        ln = geocal.MemoryRasterImage(ln_d.shape[0], ln_d.shape[1])
        ln.write(0,0,ln_d.astype(np.int))
        smp = geocal.MemoryRasterImage(smp_d.shape[0], smp_d.shape[1])
        smp.write(0,0,smp_d.astype(np.int))
        self.glt_line[:,:] = res.resample_field(ln, 1.0, False, -999.0, True)
        self.glt_sample[:,:] = res.resample_field(smp, 1.0, False, -999.0, True)
        # Correct for the odd 1 based definition of GLT, and change fill
        # value to 0
        self.glt_line[:,:] += 1
        self.glt_sample[:,:] += 1
        self.glt_line[self.glt_line < 0] = 0
        self.glt_sample[self.glt_sample < 0] = 0
        if(self.standard_metadata):
            self.standard_metadata.write_metadata(self)
        
__all__ = ["AvirisNgGlt",]
