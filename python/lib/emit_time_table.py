import geocal
import h5netcdf
import numpy as np

class EmitTimeTable(geocal.MeasuredTimeTable):
    '''This is the EMIT time table. Right now this is just a wrapper
    around a generic GeoCal MeasuredTimeTable. We can extend this to a
    full C++ class if there is any need.
    '''
    def __init__(self, tt_fname):
        f = h5netcdf.File(tt_fname, "r")
        tm = f["line_time_j2000"][:]
        super().__init__([geocal.Time.time_j2000(t) for t in tm])

    @classmethod
    def write_file(cls, tt_fname, tt):
        '''Write a file. This is really meant for generating test data.'''
        fout = h5netcdf.File(tt_fname, "w")
        tm = np.array([tt.time(geocal.ImageCoordinate(i, 0))[0].j2000
                       for i in range(tt.max_line+1)])
        t = fout.create_variable("line_time_j2000", ('t',), data=tm)
        t.attrs["units"] = "s"
        t.attrs["description"] = "J2000 time for each line in the spectral radiance image"
        fout.close()
        
__all__ = ["EmitTimeTable",]
