from .envi_file import *
from .standard_metadata import *
import logging
import numpy as np
import geocal

logger = logging.getLogger('l1b_geo_process.emit_loc')

class EmitLoc(EnviFile):
    '''Generate or read the LOC file for EMIT.'''
    def __init__(self, fname, igc = None, standard_metadata = None):
        '''Open a file. As a convention if the IGC is supplied we just
        assume we are creating a file. Otherwise, we read an existing one.

        Note that we don't actually create the data until you run the 
        "run" function, so it will initially just be unintialized data.

        Note that the shape is (3, number_line, number_sample)
        '''
        self.igc = igc
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
                         description = "EMIT L1B pixel location file",
                         band_description = ["Longitude (WGS-84)", "Latitude (WGS-84)", "Elevation (m)"])
        

    def run(self):
        '''Actually generate the output data.'''
        logger.info("Generating LOC data for %s", self.igc.title)
        # We could run this in parallel if needed. However our
        # scene size is fairly small (1280 lines) so that it probably isn't
        # worth worry about this, at least initially. We can probably handle
        # the parallelization at the scene level if performance is an issue.
        #
        # We pick a large resolution here to force the subpixels to be 1.
        rcast = geocal.IgcRayCaster(self.igc,0,-1,1,10000)
        while(not rcast.last_position):
            gpos = rcast.next_position()
            for i in range(gpos.shape[1]):
                gp = geocal.Geodetic(geocal.Ecr(gpos[0,i,0,0,0,0],
                                                gpos[0,i,0,0,0,1],
                                                gpos[0,i,0,0,0,2]))
                self[0,rcast.current_position, i] = gp.longitude
                self[1,rcast.current_position, i] = gp.latitude
                self[2,rcast.current_position, i] = gp.height_reference_surface
        self.standard_metadata.write_metadata(self)
        
__all__ = ["EmitLoc", ]
