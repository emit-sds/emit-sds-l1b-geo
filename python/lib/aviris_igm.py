from .envi_file import EnviFile
from .misc import create_dem
import geocal

class AvirisIgm:
    '''Small helper class that handles reading the AVIRIS IGM
    and returning the ground location from this file.'''
    def __init__(self, igm_fname):
        self.f = EnviFile(igm_fname)
        self.datum = create_dem(None).datum

    @property 
    def shape(self):
        return (self.f.shape[1], self.f.shape[2])

    def __getitem__(self, key):
        lon, lat, elv = self.f[:,key[0],key[1]]
        # Elevation is relative to datum, so we need to add undulation
        # to get height above WGS 84.
        elv += self.datum.undulation(geocal.Geodetic(lat, lon))
        return geocal.Geodetic(lat, lon, elv)
        
__all__ = ["AvirisIgm"]
