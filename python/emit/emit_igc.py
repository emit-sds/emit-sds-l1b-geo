from .emit_orbit_extension import EmitOrbit
from .emit_time_table import EmitTimeTable
from .emit_camera import EmitCamera
from .envi_file import EnviFile
from .misc import orb_and_scene_from_file_name
from emit_swig import EmitIgcCollection, EmitL1bImage, ReverseCamera
import logging
import geocal
import os

logger = logging.getLogger("l1b_geo_process.emit_igc")


class EmitIgc(geocal.IpiImageGroundConnection):
    """EMIT ImageGroundConnection. Right now this is just a wrapper around
    a generic GeoCal IpiImageGroundConnection. We can extend
    this to a full C++ class if there is any need."""

    def __init__(
        self,
        orbit_fname,
        tt_fname,
        l1b_rdn_fname=None,
        l1b_band=1,
        l1_osp_dir=None,
        rad_match_scale=1.0,
    ):
        """Create a EmitIgc. We can either include the raster image data
        or not. If desired, supplied l1b_rdn_fname and the band of the
        L1B radiance file to use."""

        orb = EmitOrbit(orbit_fname)
        if l1_osp_dir:
            dem = l1_osp_dir.dem
            cam = l1_osp_dir.camera()
        else:
            dem = geocal.SrtmDem()
            cam = EmitCamera()
        reverse_image = False
        if l1b_rdn_fname is not None:
            img = EmitL1bImage(l1b_rdn_fname, l1b_band, rad_match_scale)
            f = EnviFile(l1b_rdn_fname, mode="r")
            if "flip_horizontal" in f.metadata:
                reverse_image = bool(f.metadata["flip_horizontal"])
        else:
            img = None
        if reverse_image:
            logger.info("Reversing image data")
        # reverse_image for time table isn't correctly supported by
        # IgcRayCaster in GeoCal. We should fix that, but in the short
        # term use our ReverseCamera instead
        tt = EmitTimeTable(
            tt_fname, number_sample=cam.number_sample(0), reverse_image=False
        )
        if reverse_image:
            ipicam = ReverseCamera(cam)
        else:
            ipicam = cam
        ipi = geocal.Ipi(orb, ipicam, 0, tt.min_time, tt.max_time, tt)
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
    """Return orbit for a EmitIgcCollection"""
    return self.image_ground_connection(0).ipi.orbit


def _set_orbit(self, orb):
    for i in range(self.number_image):
        self.image_ground_connection(i).ipi.orbit = orb


def _camera(self):
    """Return camera for a EmitIgcCollection"""
    return self.image_ground_connection(0).ipi.camera


def _set_camera(self, cam):
    for i in range(self.number_image):
        self.image_ground_connection(i).ipi.camera = cam


def _create(cls, orbit_fname, tt_and_rdn_fname, l1b_band, l1_osp_dir, include_img=True):
    """Create a EmitIgcCollection. This takes an orbit file name,
    a list of time table and radiance file name pairs, and the band to
    set. We get the scene number from the radiance file name, and set EmitIgc
    title based on it. If the files happen to be out of order, we sort
    the data. We also attach the list of scenes as "scene_list", the orbit
    number as "orbit_number" and the uncorrected orbit
    as "uncorrected_orbit"."""
    if l1_osp_dir:
        l1_osp_dir.setup_spice()
    logger.info("SPICE data dir: %s", os.environ["SPICEDATA"])
    orb = EmitOrbit(orbit_fname)
    cam = l1_osp_dir.camera()
    dem = l1_osp_dir.dem
    index_to_igc = {}
    index_to_scene = {}
    index_to_scene_time = {}
    index_to_rdn_fname = {}
    for tt_fname, rdn_fname in tt_and_rdn_fname:
        orbit_number, scene, stime = orb_and_scene_from_file_name(rdn_fname)
        reverse_image = False
        if include_img:
            img = EmitL1bImage(rdn_fname, l1b_band, l1_osp_dir.rad_match_scale)
            f = EnviFile(rdn_fname, mode="r")
            if "flip_horizontal" in f.metadata:
                reverse_image = bool(f.metadata["flip_horizontal"])
        else:
            img = None
        if reverse_image:
            logger.info("Reversing image data for %s", stime)
        else:
            logger.info("Not reversing image data for %s", stime)
        # reverse_image for time table isn't correctly supported by
        # IgcRayCaster in GeoCal. We should fix that, but in the short
        # term use our ReverseCamera instead
        tt = EmitTimeTable(
            tt_fname, number_sample=cam.number_sample(0), reverse_image=False
        )
        if reverse_image:
            ipicam = ReverseCamera(cam)
        else:
            ipicam = cam
        ipi = geocal.Ipi(orb, ipicam, 0, tt.min_time, tt.max_time, tt)
        igc = geocal.IpiImageGroundConnection(ipi, dem, img)
        if l1_osp_dir.use_scene_index:
            index_to_igc[scene] = igc
            index_to_scene[scene] = scene
            index_to_scene_time[scene] = stime
            index_to_rdn_fname[scene] = rdn_fname
            igc.title = f"Scene {scene}"
        else:
            index_to_igc[stime] = igc
            index_to_scene[stime] = scene
            index_to_scene_time[stime] = stime
            index_to_rdn_fname[stime] = rdn_fname
            igc.title = f"{stime}"
    igccol = EmitIgcCollection()
    igccol.orbit_number = orbit_number
    index_list = sorted(index_to_igc.keys())
    igccol.scene_list = [index_to_scene[i] for i in index_list]
    igccol.scene_time_list = [index_to_scene_time[i] for i in index_list]
    igccol.scene_index_list = index_list
    igccol.rdn_fname_list = [index_to_rdn_fname[i] for i in index_list]
    for i in index_list:
        igccol.add_igc(index_to_igc[i])
    igccol.uncorrected_orbit = orb
    return igccol


EmitIgcCollection.create = classmethod(_create)
EmitIgcCollection.orbit = property(
    _orbit, _set_orbit, doc="The orbit used by EmitIgcCollection"
)
EmitIgcCollection.camera = property(
    _camera, _set_camera, doc="The camera used by EmitIgcCollection"
)
__all__ = [
    "EmitIgc",
]
