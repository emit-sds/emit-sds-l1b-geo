from .aviris_ng_raw import AvirisNgPpsTable
import os
import numpy as np
import math
import re
import geocal
import h5py
from packaging import version
import h5netcdf

class AvirisNgTimeTable(geocal.MeasuredTimeTable):
    def __init__(self, fname, gps_week=None, line_average=None,
                 msg_words=13, img_sl=800, raw = None):
        '''Read the given raw pps file for AVIRIS-NG, or the given netCDF
        file. For the PPS file, we use the given line_average and create
        a time table for every science packet.

        The GPS week can be passed in explicitly, or we extract this
        from the file name.'''
        self.line_average = line_average
        if(h5py.is_hdf5(fname)):
            f = h5py.File(fname, "r")
            self.line_average = f["TimeTable"].attrs["line_average"]
            self.gps_week = f["TimeTable"].attrs["gps_week"]
            tline = f["TimeTable/line_time_gps"][:]
            tline = [geocal.Time.time_gps(t) for t in tline]
            self.pps_table = None
        else:
            if(not raw):
                raise RuntimeError("Need to supply AvirisNgRaw object raw if we are creating table from the pps file")
            self.pps_table = AvirisNgPpsTable(fname, msg_words=msg_words)
            self.gps_week = self.pps_table.gps_week
            if(line_average):
                tline = self.pps_table.clock_to_time(
                    raw.clock_average(img_sl=img_sl,line_average=line_average))
            else:
                tline = self.pps_table.clock_to_time(
                    raw.clock_science(img_sl=img_sl))
        
        super().__init__(tline)
        
    def write(self, tt_fname):
        '''Write the data to a netCDF file'''
        if version.parse(h5netcdf.__version__) >= version.parse("0.13.0"):
            fout = h5netcdf.File(tt_fname, "w", decode_vlen_strings=False)
        else:
            fout = h5netcdf.File(tt_fname, "w")
        g = fout.create_group("TimeTable")
        g.attrs["gps_week"] = self.gps_week
        g.attrs["line_average"] = self.line_average
        tm = [self.time_list(i).gps for i in range(self.size_time_list)]
        # MeasuredTimeTable adds a extra entry at the start and end of the
        # table for padding. Strip this off.
        tm = tm[1:-1]
        t = g.create_variable("line_time_gps", ('t',),
                              data = np.array(tm, dtype=np.float64))
        t.attrs["units"] = "s"
        t.attrs["description"] = "Time in seconds from GPS epoch for each line"
        
