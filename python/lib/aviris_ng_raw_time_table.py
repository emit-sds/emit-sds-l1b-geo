from .misc import file_name_to_gps_week
from .aviris_ng_raw import AvirisNgPpsTable
import os
import numpy as np
import math
import re
import geocal

class AvirisNgRawTimeTable:
    def __init__(self, fname, gps_week=None):
        '''Read the given raw pps file for AVIRIS-NG.

        The GPS week can be passed in explicitly, or we extract this
        from the file name.'''
        # This comes from ortho_platform.py in pyortho. For AVIRIS-NG,
        # the number of message words is 13. I don't think this will change,
        # but if we get weird results perhaps this should be 14. Perhaps
        # we should move this into the l1_osp_dir files.
        msg_words = 13
        self.gps_week = gps_week
        if(not self.gps_week):
            self.gps_week = file_name_to_gps_week(fname)
        self.pps_table = AvirisNgPpsTable(fname, msg_words=msg_words)

    def clock_to_time(self, clock):
        '''Convert from the 'clock' value to a geocal time. Clock can either
        be a array/list like object, or a single value.'''
        gtime = self.pps_table.clock_to_gpstime(clock)
        if(len(gtime.shape) == 0):
            return geocal.Time.time_gps(self.gps_week, gtime[()])
        return [geocal.Time.time_gps(self.gps_week, g) for g in gtime]
    
