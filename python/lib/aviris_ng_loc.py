from .envi_file import *
from .standard_metadata import *
import logging
import numpy as np
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
