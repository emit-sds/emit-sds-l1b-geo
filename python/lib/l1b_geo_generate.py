from .envi_file import EnviFile
import geocal
import numpy as np

# Not sure if we really want this to be a class or not, but I think there
# may be enough overlap between calculations that we want to keep these
# together.
#
# Also, we'll probably want to run some of this in parallel and/or move to
# C++. I imagine this will be a bit slow.
class L1bGeoGenerate:
    def __init__(self, igc):
        self.igc = igc

    def generate_loc(self, loc_fname):
        '''Generate the Level 1B Pixel Location (LOC) File'''
        # This will likely be a bit on the slow side
        d = EnviFile(loc_fname,
                     shape=(3, self.igc.number_line, self.igc.number_sample),
                     dtype = np.float64, mode="w")
        # We pick a large resolution here to force the subpixels to be 1.
        rcast = geocal.IgcRayCaster(self.igc,0,-1,1,10000)
        while(not rcast.last_position):
            gpos = rcast.next_position()
            for i in range(gpos.shape[1]):
                gp = geocal.Geodetic(geocal.Ecr(gpos[0,i,0,0,0,0],
                                                gpos[0,i,0,0,0,1],
                                                gpos[0,i,0,0,0,2]))
                d[0,rcast.current_position, i] = gp.longitude
                d[1,rcast.current_position, i] = gp.latitude
                d[2,rcast.current_position, i] = gp.height_reference_surface
                
                
__all__ = ["L1bGeoGenerate",]
