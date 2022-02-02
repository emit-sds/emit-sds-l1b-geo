from .envi_file import *
from .standard_metadata import *
import logging
import numpy as np
import geocal
import re
import math

logger = logging.getLogger('l1b_geo_process.emit_loc')

class EmitObs(EnviFile):
    '''Generate or read the OBS file for EMIT.'''
    def __init__(self, fname, emit_loc = None, igc = None,
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
            self.emit_loc = emit_loc
            if(self.standard_metadata is None):
                self.standard_metadata = StandardMetadata(igc=igc)
            shape = (11, igc.number_line, igc.number_sample)
        super().__init__(fname, shape=shape, dtype=np.float64, mode=mode,
                         description = "EMIT L1B pixel location file",
                         band_description = ["Path length (m)", "To-sensor azimuth (0 to 360 degrees CW from N)", "To-sensor zenith (0 to 90 degrees from zenith)", "To-sun azimuth (0 to 360 degrees CW from N)", "To-sun zenith (0 to 90 degrees from zenith)", "Solar phase", "Slope", "Aspect", "Cosine(i)", "UTC Time", "Earth-sun distance (AU]"])

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
        # TODO This is fairly slow, we should probably move most of this
        # to C++ level for performance
        for ln in range(self.igc.number_line):
            if(ln % 100 == 0):
                logger.info("Doing line %d" % ln)
            pos = self.igc.cf_look_vector_pos(geocal.ImageCoordinate(ln,0))
            tm = self.igc.pixel_time(geocal.ImageCoordinate(ln,0))
            self.earth_sun_distance[ln,:] = geocal.Ecr.solar_distance(tm)
            seconds_in_day = tm - geocal.Time.parse_time(re.split('T', str(tm))[0] + "T00:00:00Z")
            self.utc_time[ln,:] = seconds_in_day / (60 * 60)
            for smp in range(self.igc.number_sample):
                gp = geocal.Geodetic(self.emit_loc.latitude[ln,smp],
                                     self.emit_loc.longitude[ln,smp],
                                     self.emit_loc.height[ln,smp])
                clv = geocal.CartesianFixedLookVector(pos, gp)
                lv = geocal.LnLookVector(clv, gp)
                slv = geocal.LnLookVector.solar_look_vector(tm, gp)
                self.path_length[ln, smp] = geocal.distance(gp, pos)
                self.view_azimuth[ln,smp] = lv.view_azimuth
                self.view_zenith[ln,smp] = lv.view_zenith
                self.solar_azimuth[ln,smp] = slv.view_azimuth
                self.solar_zenith[ln,smp] = slv.view_zenith
                d = (lv.direction[0] * slv.direction[0] +
                     lv.direction[1] * slv.direction[1] +
                     lv.direction[2] * slv.direction[2])
                self.solar_phase[ln,smp] = math.acos(d) * geocal.rad_to_deg
                self.slope[ln,smp] = -9999
                self.aspect[ln,smp] = -9999
                self.cosine_i[ln,smp] = -9999
        self.standard_metadata.write_metadata(self)
        
__all__ = ["EmitObs", ]
