import geocal
import h5netcdf
import numpy as np

class EmitTimeTable:
    '''This is the EMIT time table. We'll likely make this a C++ class
    to more tightly integrate in with GeoCal, but right now the exact
    way we will want this isn't clear. A better name for this current class
    might be "EMIT TimeTable reader and writer"'''
    def __init__(self):
        self.tt = None
    def write_time_table(self, tt, fname):
        self.tt = tt
        with h5netcdf.File(fname, "w") as fout:
            tm = np.array([tt.time(geocal.ImageCoordinate(i, 0))[0].j2000
                           for i in range(tt.max_line+1)])
            t = fout.create_variable("line_time_j2000", ('t',), data=tm)
            t.attrs["units"] = "s"
            t.attrs["description"] = "J2000 time for each line in the spectral radiance image"

    def read_time_table(self, fname):
        f = h5netcdf.File(fname, "r")
        tm = f["line_time_j2000"][:]
        self.tt = geocal.MeasuredTimeTable([geocal.Time.time_j2000(t) for t in tm])
        
        
