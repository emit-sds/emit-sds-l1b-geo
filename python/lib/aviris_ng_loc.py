from .envi_file import *
from .standard_metadata import *
import logging
import numpy as np
import geocal
import cv2
import math
import geocal

logger = logging.getLogger('l1b_geo_process.avirs_ng_loc')

class AvirisNgLoc(EnviFile):
    '''Generate or read the LOC file for AVIRIS-NG.

    Note this is almost identical to EmitLoc. For right now we leave this
    as separate, just so we have a place to put in any differences we
    end up having.

    But I think shortly after working through the SHIFT campaign we can
    join this together with the EmitLoc, either as just a set of options
    or perhaps a derived class.'''
    def __init__(self, fname, igc = None, standard_metadata = None,
                 number_line_process = 1000):
        '''Open a file. As a convention if the IGC is supplied we just
        assume we are creating a file. Otherwise, we read an existing one.

        Note that we don't actually create the data until you run the 
        "run" function, so it will initially just be unintialized data.

        Note that the shape is (3, number_line, number_sample)
        '''
        self.igc = igc
        self.number_line_process = number_line_process
        if(self.igc is None):
            mode = 'r'
            shape = None
        else:
            mode = 'w'
            self.standard_metadata = standard_metadata
            if(self.standard_metadata is None):
                self.standard_metadata = StandardMetadata(igc=igc)
            shape = (3, igc.number_line, igc.number_sample)
        super().__init__(fname, shape=shape, dtype=np.float64, mode=mode,
                         description = "ANG AIG VSWIR RT-Ortho LOC",
                         band_description = ["Longitude (WGS-84)", "Latitude (WGS-84)", "Elevation (m)"])

    @property
    def latitude(self):
        '''Return the latitude field'''
        return self[1,:,:]

    @property
    def longitude(self):
        '''Return the longitude field'''
        return self[0,:,:]

    @property
    def height(self):
        '''Return the height field.'''
        return self[2,:,:]

    def map_info_rotated(self, mi):
        '''Calculate the rotated map info'''
        # We only need the edges pixels, this defines the full
        # range of data here
        f = mi.coordinate_converter.convert_to_coordinate
        lat = self.latitude
        lon = self.longitude
        pt = [f(geocal.Geodetic(lat[0,i], lon[0, i])) for
              i in range(self.shape[2])]
        pt.extend(f(geocal.Geodetic(lat[-1,i], lon[-1, i]))
                  for i in range(self.shape[2]))
        pt.extend(f(geocal.Geodetic(lat[i,0], lon[i, 0]))
                   for i in range(self.shape[1]))
        pt.extend(f(geocal.Geodetic(lat[i,-1], lon[i, -1]))
                   for i in range(self.shape[1]))
        # Note cv2 convexhull can't work with noncontigous array. The
        # error message returned is very confusing, it complains that the
        # type isn't float32 - even though it is. But we just make sure
        # to make a contiguous array and this works ok.
        pt = np.ascontiguousarray(np.array(pt)[:,0:2], dtype=np.float32)
        rect = cv2.minAreaRect(pt)
        t = cv2.boxPoints(rect)
        a = -math.atan2(t[0,0] - t[-1,0], t[0,1] - t[-1,1])
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

    def ogr_shape(self, spacing = 100):
        '''Create a Polygon describing the outside edge of the data.
        This is approximate, we include every 100th line just to get
        a reasonable size estimate.'''
        lat = self.latitude
        lon = self.longitude
        border = []
        for i in range(0, self.shape[1], spacing):
           border.append([lat[i,0],lon[i,0]])
        border.append([lat[-1,0],lon[-1,0]])
        for i in range(1, self.shape[1], spacing):
            border.append([lat[-i,-1],lon[-i,-1]])
        border.append([lat[0,-1],lon[0,-1]])
        return geocal.ShapeLayer.polygon_2d(border)
                       
    @property
    def crosses_date_line(self):
        '''Returns true if we cross the dateline'''
        return self.longitude.min() < -170 and self.longitude.max() > 160

    def ground_coordinate(self, ln, smp):
        '''Return the Geodetic point for the given line/sample''' 
        lon, lat, elv = self.data[:,ln, smp]
        return geocal.Geodetic(lat, lon, elv)
    

    def run_scene(self, i):
        nline = min(self.number_line_process, self.igc.number_line-i)
        logger.info("Generating LOC data for %s (%d, %d)", self.igc.title,
                    i, i+nline)
        with self.multiprocess_data():
            # We pick a large resolution here to force the subpixels to be 1.
            rcast = geocal.IgcRayCaster(self.igc,i,nline,1,10000)
            while(not rcast.last_position):
                gpos = rcast.next_position()
                for j in range(gpos.shape[1]):
                    gp = geocal.Geodetic(geocal.Ecr(gpos[0,j,0,0,0,0],
                                                    gpos[0,j,0,0,0,1],
                                                    gpos[0,j,0,0,0,2]))
                    self[0,rcast.current_position, j] = gp.longitude
                    self[1,rcast.current_position, j] = gp.latitude
                    self[2,rcast.current_position, j] = gp.height_reference_surface
        return None

    def run(self, pool=None):
        '''Actually generate the output data.'''
        logger.info("Generating LOC data for %s", self.igc.title)
        ilist = list(range(0, self.igc.number_line, self.number_line_process))
        if(pool is None):
            res = list(map(self.run_scene, ilist))
        else:
            res = pool.map(self.run_scene, ilist)
        self.standard_metadata.write_metadata(self)
        
__all__ = ["AvirisNgLoc", ]
