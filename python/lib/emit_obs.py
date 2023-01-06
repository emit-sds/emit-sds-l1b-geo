from .envi_file import *
from .standard_metadata import *
from emit_swig import EmitObsCalc
import logging
import numpy as np
import geocal
import re
from math import acos, sin, cos
import pandas as pd

logger = logging.getLogger('l1b_geo_process.emit_loc')

class EmitObs(EnviFile):
    '''Generate or read the OBS file for EMIT.'''
    def __init__(self, fname, loc = None, igc = None,
                 standard_metadata = None):
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
            self.loc = loc
            if(self.standard_metadata is None):
                self.standard_metadata = StandardMetadata(igc=igc)
            shape = (11, igc.number_line, igc.number_sample)
        super().__init__(fname, shape=shape, dtype=np.float64, mode=mode,
                         description = "EMIT L1B pixel location file",
                         band_description = ["Path length (m)", "To-sensor azimuth (0 to 360 degrees CW from N)", "To-sensor zenith (0 to 90 degrees from zenith)", "To-sun azimuth (0 to 360 degrees CW from N)", "To-sun zenith (0 to 90 degrees from zenith)", "Solar phase", "Slope", "Aspect", "Cosine(i)", "UTC Time", "Earth-sun distance (AU)"])

    @property
    def path_length(self):
        '''Return the path length field'''
        return self[0,:,:]

    @property
    def view_azimuth(self):
        '''Return the view azimuth field'''
        return self[1,:,:]

    @property
    def view_zenith(self):
        '''Return the view zenith field'''
        return self[2,:,:]

    @property
    def solar_azimuth(self):
        '''Return the solar azimuth field'''
        return self[3,:,:]

    @property
    def solar_zenith(self):
        '''Return the solar zenith field'''
        return self[4,:,:]

    @property
    def solar_phase(self):
        '''Return the solar phase field'''
        return self[5,:,:]

    @property
    def slope(self):
        '''Return the slope field'''
        return self[6,:,:]

    @property
    def aspect(self):
        '''Return the aspect field'''
        return self[7,:,:]
    
    @property
    def cosine_i(self):
        '''Return the cosine(i) field'''
        return self[8,:,:]

    @property
    def utc_time(self):
        '''Return the UTC Time field'''
        return self[9,:,:]

    @property
    def earth_sun_distance(self):
        '''Return the earth-sun distance field'''
        return self[10,:,:]
    
    def run(self):
        '''Actually generate the output data.'''
        logger.info("Generating OBS data for %s", self.igc.title)
        latsubpixel, lonsubpixel = self.loc.scaled_lat_lon_grid(2)
        ocalc = EmitObsCalc(self.igc, self.loc.latitude, self.loc.longitude,
                            self.loc.height, latsubpixel, lonsubpixel)
        self.view_azimuth[:],self.view_zenith[:] = ocalc.view_angle();
        self.solar_azimuth[:],self.solar_zenith[:] = ocalc.solar_angle();
        self.path_length[:] = ocalc.path_length()
        self.earth_sun_distance[:] = ocalc.earth_sun_distance()
        self.utc_time[:] = ocalc.seconds_in_day() / (60 * 60)
        self.solar_phase[:] = ocalc.solar_phase()
        self.slope[:], self.aspect[:], self.cosine_i[:] = ocalc.slope_angle();
        self.standard_metadata.write_metadata(self)
        

    def compare(self, f2):
        '''Compare with another file, returning True if the same,
        False otherwise. 

        Note the compare is done with a tolerance. We report
        the differences'''
        print("Comparing OBS files")
        same = self.metadata_compare(f2)
        print("   Path length Difference (meters)")
        diff = np.abs(self.path_length - f2.path_length)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   View Azimuth Difference (degree)")
        diff = np.abs(self.view_azimuth - f2.view_azimuth)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   View Zenith Difference (degree)")
        diff = np.abs(self.view_zenith - f2.view_zenith)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   Solar Azimuth Difference (degree)")
        diff = np.abs(self.solar_azimuth - f2.solar_azimuth)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   Solar Zenith Difference (degree)")
        diff = np.abs(self.solar_zenith - f2.solar_zenith)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   Solar Phase Difference")
        diff = np.abs(self.solar_phase - f2.solar_phase)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   Slope Difference (degree)")
        diff = np.abs(self.slope - f2.slope)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   Aspect Difference (degree)")
        diff = np.abs(self.aspect - f2.aspect)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   Cosine(I) Difference")
        diff = np.abs(self.cosine_i - f2.cosine_i)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   UTC Time Difference")
        diff = np.abs(self.utc_time - f2.utc_time)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        print("   Earth-Sun distance Difference")
        diff = np.abs(self.earth_sun_distance - f2.earth_sun_distance)
        print(pd.DataFrame(diff.flatten()).describe())
        if(diff.max() > 1e-2):
            same = False
        if same:
            print("   Files are considered the same")
        else:
            print("   Files are considered different")
        return same
        
__all__ = ["EmitObs", ]
