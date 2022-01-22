from .emit_orbit_extension import EmitOrbit
from .emit_time_table import EmitTimeTable
from .emit_camera import EmitCamera
from .misc import create_dem, orb_and_scene_from_file_name
from emit_swig import EmitIgcCollection
import geocal

class EmitIgc(geocal.IpiImageGroundConnection):
    '''EMIT ImageGroundConnection. Right now this is just a wrapper around 
    a generic GeoCal IpiImageGroundConnection. We can extend
    this to a full C++ class if there is any need.'''
    def __init__(self, orbit_fname, tt_fname, l1b_rdn_fname = None,
                 l1b_band = 1):
        '''Create a EmitIgc. We can either include the raster image data
        or not. If desired, supplied l1b_rdn_fname and the band of the
        L1B radiance file to use.'''

        orb = EmitOrbit(orbit_fname)
        cam = EmitCamera()
        dem = create_dem(None)
        tt = EmitTimeTable(tt_fname)
        ipi = geocal.Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
        if(l1b_rdn_fname is not None):
            img = geocal.GdalRasterImage(l1b_rdn_fname, l1b_band)
        else:
            img = None
        # Put in raster image
        super().__init__(ipi, dem, img)

def _create(cls, orbit_fname, tt_and_rdn_fname, l1b_band):
    '''Create a EmitIgcCollection. This takes an orbit file name,
    a list of time table and radiance file name pairs, and the band to
    set. We get the scene number from the radiance file name, and set EmitIgc
    title based on it. If the files happen to be out of order, we sort
    the data. We also attach the list of scenes as "scene_list", the orbit
    number as "orbit_number" and the uncorrected orbit 
    as "uncorrected_orbit".'''
    orb = EmitOrbit(orbit_fname)
    cam = EmitCamera()
    dem = create_dem(None)
    scene_to_igc = {}
    for tt_fname, rdn_fname in tt_and_rdn_fname:
        orbit_number, scene = orb_and_scene_from_file_name(rdn_fname)
        tt = EmitTimeTable(tt_fname)
        ipi = geocal.Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
        img = geocal.GdalRasterImage(rdn_fname, l1b_band)
        igc = geocal.IpiImageGroundConnection(ipi, dem, img)
        scene_to_igc[scene] = igc
        igc.title = f"Scene {scene}"
    igccol = EmitIgcCollection()
    igccol.orbit_number = orbit_number
    igccol.scene_list = sorted(scene_to_igc.keys())
    for scene in igccol.scene_list:
        igccol.add_igc(scene_to_igc[scene])
    igccol.uncorrected_orbit = orb
    return igccol

EmitIgcCollection.create = classmethod(_create)

__all__ = ["EmitIgc", ]    
