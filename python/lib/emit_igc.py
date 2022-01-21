from .emit_orbit_extension import EmitOrbit
from .emit_time_table import EmitTimeTable
from .emit_camera import EmitCamera
from .misc import create_dem
import geocal

class EmitIgc(geocal.IpiImageGroundConnection):
    '''EMIT ImageGroundConnection. Right now this is just a wrapper around 
    a generic GeoCal IpiImageGroundConnection. We can extend
    this to a full C++ class if there is any need.'''
    def __init__(self, orbit_fname, tt_fname, l1b_rdn_fname = None,
                 l1b_band = 1, igc = None):
        '''Create a EmitIgc. We can either include the raster image data
        or not. If desired, supplied l1b_rdn_fname and the band of the
        L1B radiance file to use.

        Since we want to share some of the files between Igc for different 
        scenes, you can optionally supply a igc, and we take shared object 
        out of that'''

        if(igc is None):
            orb = EmitOrbit(orbit_fname)
            cam = EmitCamera()
            dem = create_dem(None)
        else:
            orb = igc.ipi.orbit
            cam = igc.ipi.camera
            dem = igc.dem
        tt = EmitTimeTable(tt_fname)
        ipi = geocal.Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
        if(l1b_rdn_fname is not None):
            img = geocal.GdalRasterImage(l1b_rdn_fname, l1b_band)
        else:
            img = None
        # Put in raster image
        super().__init__(ipi, dem, img)

__all__ = ["EmitIgc", ]    
