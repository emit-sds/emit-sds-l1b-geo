import struct
import geocal
from .misc import create_dem

class AvirisNgObs:
    '''This reads the AVIRIS NG obs data.

    Note that the time is relative to day. We could parse this from the
    file name, but since we don't have a lot of data this doesn't seem
    to be worth it. Instead, we just take the time in.

    Time_day would be something like 

    Time.parse_time("2017-03-23T00:00:00Z")

    I'm *pretty* sure the height is relative to WGS-84 rather than the
    datum. Error is small, and since this is pretend test data perhaps
    it doesn't matter so much
    '''
    def __init__(self, fname, time_day):
        # We use a GdalMultiBand here just for convenience. It just
        # figures out the shape etc. for us from the hdr file
        self.data = geocal.GdalMultiBand(fname).read_all_double()
        self._time = [time_day + 60 * 60 * v for v in self.data[9,:,0]]
                    

    @property
    def path_length(self):
        '''Path length (m)'''
        return self.data[0,:,:]

    @property
    def view_azimuth(self):
        '''To-sensor azimuth (0 to 360 degrees cw from N)'''
        return self.data[1,:,:]

    @property
    def view_zenith(self):
        '''To-sensor zenith (0 to 90 degrees from zenith)'''
        return self.data[2,:,:]

    @property
    def view_azimuth(self):
        '''To-sun azimuth (0 to 360 degrees cw from N)'''
        return self.data[3,:,:]

    @property
    def view_zenith(self):
        '''To-sun zenith (0 to 90 degrees from zenith)'''
        return self.data[4,:,:]

    @property
    def solar_phase(self):
        '''Solar Phase'''
        return self.data[5,:,:]

    @property
    def slope(self):
        '''Solar Phase'''
        return self.data[6,:,:]
    
    @property
    def aspect(self):
        '''Solar Phase'''
        return self.data[7,:,:]

    @property
    def cosine_i(self):
        '''Cosine(i)'''
        return self.data[8,:,:]

    @property
    def time(self):
        '''Time of each line'''
        return self._time

    @property
    def earth_sun_distance(self):
        '''Earth-sun distance (AU)'''
        return self.data[10,:,:]
    
    
    
        
__all__ = ["AvirisNgObs",]    
