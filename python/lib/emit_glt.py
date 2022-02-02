import geocal
import scipy
import numpy as np
from emit_swig import *
from .envi_file import EnviFile
import subprocess
import logging
import cv2
import math

logger = logging.getLogger('l1b_geo_process.emit_loc')

class EmitGlt(EnviFile):
    '''This generate the l1b_geo GLT file. 
    
    Note that we don't actually create the data until you run "run" function.
    The EmitLoc should also have been generate (so either you are reading
    an existing file or you have done EmitLoc.run to generate the data).
    '''
    def __init__(self, fname, emit_loc = None,
                 standard_metadata = None,
                 resolution = 60, number_subpixel = 3,
                 rotated_map = False):
        self.fname = fname
        self.emit_loc = emit_loc
        self.resolution = resolution
        self.standard_metadata = standard_metadata
        self.number_subpixel = number_subpixel
        self.rotated_map = rotated_map
        # Note that if we are writing the file, then we actually need to
        # wait on calling __init__ because we don't know the size yet.
        if(self.emit_loc is None):
            super().__init__(fname, mode="r")
        
    def map_info_not_rotated(self):
        mi = geocal.cib01_mapinfo(self.resolution)
        # We only need the edges pixels, this defines the full
        # range of data here
        lat = self.emit_loc.latitude
        lon = self.emit_loc.longitude
        pt = [geocal.Geodetic(lat[0,i], lon[0, i]) for
              i in range(self.emit_loc.shape[2])]
        pt.extend(geocal.Geodetic(lat[-1,i], lon[-1, i]) for
                  i in range(self.emit_loc.shape[2]))
        pt.extend(geocal.Geodetic(lat[i,0], lon[i,0]) for
                  i in range(self.emit_loc.shape[2]))
        pt.extend(geocal.Geodetic(lat[i,-1], lon[i,-1]) for
                  i in range(self.emit_loc.shape[2]))
        mi = mi.cover(pt)
        return mi
    
    def map_info_rotated(self):
        mi = geocal.cib01_mapinfo(self.resolution)
        # We only need the edges pixels, this defines the full
        # range of data here
        f = mi.coordinate_converter.convert_to_coordinate
        lat = self.emit_loc.latitude
        lon = self.emit_loc.longitude
        pt = [f(geocal.Geodetic(lat[0,i], lon[0, i])) for
              i in range(self.emit_loc.shape[2])]
        pt.extend(f(geocal.Geodetic(lat[-1,i], lon[-1, i]))
                  for i in range(self.emit_loc.shape[2]))
        pt.extend(f(geocal.Geodetic(lat[i,0], lon[i, 0]))
                   for i in range(self.emit_loc.shape[1]))
        pt.extend(f(geocal.Geodetic(lat[i,-1], lon[i, -1]))
                   for i in range(self.emit_loc.shape[1]))
        # Note cv2 convexhull can't work with noncontigous array. The
        # error message returned is very confusing, it complains that the
        # type isn't float32 - even though it is. But we just make sure
        # to make a contiguous array and this works ok.
        pt = np.ascontiguousarray(np.array(pt)[:,0:2], dtype=np.float32)
        rect = cv2.minAreaRect(pt)
        t = cv2.boxPoints(rect)
        a = math.atan2(t[0,0] - t[-1,0], t[0,1] - t[-1,1])
        logger.info("Rotated minimum area rectangle is angle %f",
                    a * geocal.rad_to_deg)
        rot = np.array([[math.cos(a), -math.sin(a)],[math.sin(a),math.cos(a)]])
        p = mi.transform
        pm = np.array([[p[1], p[2]],[p[4], p[5]]])
        pm2 = np.matmul(rot,pm)
        mi2 = geocal.MapInfo(mi.coordinate_converter,
                             np.array([p[0],pm2[0,0],pm2[0,1],p[3],pm2[1,0],pm2[1,1]]),
                             mi.number_x_pixel, mi.number_y_pixel, mi.is_point)
        # In general, mi2 will cover invalid lat/lon. Just pull in to a
        # reasonable area, we handling the actual cover later
        mi2 = mi2.cover([geocal.Geodetic(10,10),geocal.Geodetic(20,20)])
        s = mi.resolution_meter / mi2.resolution_meter
        mi2 = mi2.scale(s, s)
        return mi2

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
        lat = scipy.ndimage.interpolation.zoom(self.emit_loc.latitude,
                                               self.number_subpixel, order=2)
        lon = scipy.ndimage.interpolation.zoom(self.emit_loc.longitude,
                                               self.number_subpixel, order=2)
        res = Resampler(lat, lon, mi, self.number_subpixel, False)
        super().__init__(self.fname, map_info = mi,
                         shape=(2,res.map_info.number_y_pixel,
                                res.map_info.number_x_pixel),
                         dtype=np.int32, mode="w",
                         description="Emit L1B geographic lookup table file",
                         band_description = ["GLT Sample Lookup", "GLT Line Lookup"])
        # TODO We are using the smallest line/sample here. We should change
        # this to instead use the nearest
        ln_d = np.broadcast_to(np.arange(0,self.emit_loc.shape[1])[:,np.newaxis],
                               self.emit_loc.latitude.shape)
        smp_d = np.broadcast_to(np.arange(0,self.emit_loc.shape[2])[np.newaxis,:],
                               self.emit_loc.latitude.shape)
        ln = geocal.MemoryRasterImage(ln_d.shape[0], ln_d.shape[1])
        ln.write(0,0,ln_d.astype(np.int))
        smp = geocal.MemoryRasterImage(smp_d.shape[0], smp_d.shape[1])
        smp.write(0,0,smp_d.astype(np.int))
        self.glt_line[:,:] = res.resample_field(ln, 1.0, False, -999.0, True)
        self.glt_sample[:,:] = res.resample_field(smp, 1.0, False, -999.0, True)
        if(self.standard_metadata):
            self.standard_metadata.write_metadata(self)
        
__all__ = ["EmitGlt",]
