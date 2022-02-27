from .misc import file_name_to_gps_week
from .aviris_ng_raw import AvirisNgGpsTable
import geocal
import numpy as np
import os
import re
import math
import struct

class AvirisNgRawOrbit(geocal.OrbitQuaternionList):
    '''This reads the raw gps data
    '''
    def __init__(self, fname, gps_week=None):
        '''Read the given raw gps file for AVIRIS-NG.

        The GPS week can be passed in explicitly, or we extract this
        from the file name.'''
        self.gps_table = AvirisNgGpsTable(fname)
        self.gps_week = gps_week
        if(not self.gps_week):
            self.gps_week = file_name_to_gps_week(fname)
        gtable = self.gps_table.gps_table
        tm = [geocal.Time.time_gps(self.gps_week, gtable[i, 0])
              for i in range(gtable.shape[0])]
        pos = [geocal.Geodetic(gtable[i,1],gtable[i,2],
                               gtable[i,3])
               for i in range(gtable.shape[0])]
        # This is pitch, roll, and heading in degrees
        prh = gtable[:,-3:] 
        od = []
        for i in range(len(pos)):
            isecond = i+1
            if(isecond >= len(pos)):
                isecond = i-1
            od.append(geocal.AircraftOrbitData(tm[i],pos[i],
                                               tm[isecond],pos[isecond],
                                               prh[i,1],prh[i,0],prh[i,2]))
        super().__init__(od)

__all__ = ["AvirisNgRawOrbit",]    
