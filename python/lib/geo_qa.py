import h5netcdf
from packaging import version

class GeoQa:
    '''This handles the Geo QA file.'''
    def __init__(self, fname, log_fname):
        self.fname = fname
        self.log_fname = log_fname
        self.scene_name = None
        self.tp_stat = None
        self.encountered_exception = False

    def add_tp_log(self, scene_name, tplogfname):
        pass

    def add_tp_single_scene(self, image_index, igccol, tpcol, ntpoint_initial,
                            ntpoint_removed, ntpoint_final, number_match_try):
        pass

    def close(self):
        # This is a placeholder
        # Newer version of h5netcdf needs decode_vlen_strings, but this
        # keyword isn't in older versions
        if version.parse(h5netcdf.__version__) >= version.parse("0.13.0"):
            fout = h5netcdf.File(self.fname, "w", decode_vlen_strings=False)
        else:
            fout = h5netcdf.File(self.fname, "w")
        g = fout.create_group("Placeholder")
        t = g.create_variable("placeholder", ('p',), data = [1,2,3])
        fout.close()
        
        
    

__all__ = ["GeoQa",]    
