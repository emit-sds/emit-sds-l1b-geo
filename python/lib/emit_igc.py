from .emit_orbit_extension import EmitOrbit
from .emit_time_table import EmitTimeTable
from .emit_camera import EmitCamera
from .misc import orb_and_scene_from_file_name
from emit_swig import EmitIgcCollection
import logging
import geocal
import os

logger = logging.getLogger('l1b_geo_process.emit_igc')

class EmitIgc(geocal.IpiImageGroundConnection):
    '''EMIT ImageGroundConnection. Right now this is just a wrapper around 
    a generic GeoCal IpiImageGroundConnection. We can extend
    this to a full C++ class if there is any need.'''
    def __init__(self, orbit_fname, tt_fname, l1b_rdn_fname = None,
                 l1b_band = 1, l1_osp_dir = None):
        '''Create a EmitIgc. We can either include the raster image data
        or not. If desired, supplied l1b_rdn_fname and the band of the
        L1B radiance file to use.'''

        orb = EmitOrbit(orbit_fname)
        cam = EmitCamera()
        if(l1_osp_dir):
            dem = l1_osp_dir.dem
        else:
            dem = geocal.SrtmDem()
        tt = EmitTimeTable(tt_fname)
        ipi = geocal.Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
        if(l1b_rdn_fname is not None):
            img = geocal.GdalRasterImage(l1b_rdn_fname, l1b_band)
        else:
            img = None
        # Put in raster image
        super().__init__(ipi, dem, img)

# We assume here that the same orbit and camera is used for each of the
# ImageGroundConnection in EmitIgcCollection. This is mostly just a
# convenience, if we end up needing to relax this it shouldn't be a big deal
# and we'd just need to work through the code to figure out where we have
# assumed this.
#
# Note the time table is not the same for each ImageGroundConnection, this
# varies for each one.
def _orbit(self):
    '''Return orbit for a EmitIgcCollection'''
    return self.image_ground_connection(0).ipi.orbit

def _set_orbit(self, orb):
    for i in range(self.number_image):
        self.image_ground_connection(i).ipi.orbit = orb

def _camera(self):
    '''Return camera for a EmitIgcCollection'''
    return self.image_ground_connection(0).ipi.camera

def _set_camera(self, cam):
    for i in range(self.number_image):
        self.image_ground_connection(i).ipi.camera = cam

def _create(cls, orbit_fname, tt_and_rdn_fname, l1b_band,
            l1_osp_dir):
    '''Create a EmitIgcCollection. This takes an orbit file name,
    a list of time table and radiance file name pairs, and the band to
    set. We get the scene number from the radiance file name, and set EmitIgc
    title based on it. If the files happen to be out of order, we sort
    the data. We also attach the list of scenes as "scene_list", the orbit
    number as "orbit_number" and the uncorrected orbit 
    as "uncorrected_orbit".'''
    if(l1_osp_dir):
        l1_osp_dir.setup_spice()
    logger.info("SPICE data dir: %s", os.environ["SPICEDATA"])
    orb = EmitOrbit(orbit_fname)
    cam = l1_osp_dir.camera()
    dem = l1_osp_dir.dem
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
EmitIgcCollection.orbit = property(_orbit, _set_orbit,
                                   doc="The orbit used by EmitIgcCollection")
EmitIgcCollection.camera = property(_camera, _set_camera,
                                   doc="The camera used by EmitIgcCollection")
__all__ = ["EmitIgc", ]    
