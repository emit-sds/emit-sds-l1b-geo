import geocal
from emit_swig import EmitTimeTableBase
import h5netcdf
import pandas as pd
from packaging import version
import numpy as np
import os

class EmitTimeTable(EmitTimeTableBase):
    '''This is the EMIT time table. 
    '''
    def __init__(self, tt_fname, number_sample=1242, reverse_image=False,
                 trim_pad=None):
        '''Read the time table. Our AVIRIS test data has a small amount
        amount of garbage at the start and end, so you can optionally
        add a trim_pad amount to chop off at the start and end of the 
        time table'''
        # Newer version of h5netcdf needs decode_vlen_strings, but this
        # keyword isn't in older versions
        if os.path.splitext(tt_fname)[1] == ".nc":
            if version.parse(h5netcdf.__version__) >= version.parse("0.13.0"):
                f = h5netcdf.File(tt_fname, "r", decode_vlen_strings=False)
            else:
                f = h5netcdf.File(tt_fname, "r")
            if trim_pad:
                tm = f["line_time_j2000"][trim_pad:-trim_pad]
            else:
                tm = f["line_time_j2000"][:]
            tm2 = geocal.Vector_Time()
            for t in tm:
                tm2.append(geocal.Time.time_j2000(t))
            super().__init__(tm2,
                             number_sample, reverse_image)
        else:
            t = pd.read_csv(tt_fname, header=None, sep=' ')
            # First column is line number. Should just be sequential lines
            # Check for sanity
            if(not (t[0] == list(range(len(t[0])))).all()):
                raise RuntimeError(f"For file {tt_fname} first column should be sequential line numnbers")
            # Second column is GPS time in nanoseconds
            if trim_pad:
                tm = t[1][trim_pad:-trim_pad]
            else:
                tm = t[1][:]
            tm2 = geocal.Vector_Time()
            for t in tm:
                tm2.append(geocal.Time.time_gps(t*1e-9))
            super().__init__(tm2, number_sample, reverse_image)

    @classmethod
    def write_file_txt(cls, tt_fname, tt):
        '''Write a file. This is really meant for generating test data.'''
        tm = np.array([int(tt.time(geocal.ImageCoordinate(i, 0))[0].gps * 1e9)
                       for i in range(tt.max_line+1)])
        with open(tt_fname, "w") as fh:
            for i,t in enumerate(tm):
                print("%06d %d %s -1 -1" %
                      (i, t, str(geocal.Time.time_gps(t*1e-9))),
                      file=fh)
        
    @classmethod
    def write_file_netcdf(cls, tt_fname, tt):
        '''Write a file. This is really meant for generating test data.'''
        if version.parse(h5netcdf.__version__) >= version.parse("0.13.0"):
            fout = h5netcdf.File(tt_fname, "w", decode_vlen_strings=False)
        else:
            fout = h5netcdf.File(tt_fname, "w")
        tm = np.array([tt.time(geocal.ImageCoordinate(i, 0))[0].j2000
                       for i in range(tt.max_line+1)])
        t = fout.create_variable("line_time_j2000", ('t',), data=tm)
        t.attrs["units"] = "s"
        t.attrs["description"] = "J2000 time for each line in the spectral radiance image"
        fout.close()
        
__all__ = ["EmitTimeTable",]
