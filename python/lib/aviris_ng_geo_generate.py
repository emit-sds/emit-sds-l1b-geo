from .aviris_ng_loc import AvirisNgLoc
from .aviris_ng_igm import AvirisNgIgm
from .aviris_ng_obs import AvirisNgObs
from .aviris_ng_orbit import AvirisNgOrbit
from .aviris_ng_time_table import AvirisNgTimeTable
from .aviris_ng_standard_metadata import AvirisNgStandardMetadata
from .geo_qa import GeoQa
from .l1b_correct import L1bCorrect
from .l1b_proj import L1bProj
import geocal
import logging
import re
import os
from multiprocessing import Pool

logger = logging.getLogger('l1b_geo_process.aviris_ng_geo_generate')

class AvirisNgGeoGenerate:
    '''This is the overall l1b geo process for AVIRIS NG. This is very
    similar to L1bGeoGenerate for EMIT, but we have this as a separate class
    so we can handle all the differences between AVIRIS NG and EMIT.'''
    def __init__(self, l1_osp_dir, orb_fname, tt_fname, rad_fname):
        self.orb_fname = orb_fname
        self.tt_fname = tt_fname
        self.rad_fname = rad_fname
        self.l1_osp_dir = l1_osp_dir
        self.basename = re.sub(r'_att.nc$', '', os.path.basename(self.orb_fname) )
        # TODO Change DEM, possibly from config file
        self.dem = geocal.SrtmDem()
        self.orb = AvirisNgOrbit(self.orb_fname)
        self.tt = AvirisNgTimeTable(self.tt_fname)
        self.rad = geocal.GdalRasterImage(rad_fname,
                            l1_osp_dir.match_rad_band)
        # The range of the data is small as DNs, since this is in radiance
        # units. Scale so we get a wider range to match on.
        # TODO Number should be calculated, or passed in as a configuration
        # option
        rad_scale = 100.0
        self.rad = geocal.ScaleImage(self.rad, rad_scale)
        self.cam = l1_osp_dir.camera()
        self.ipi = geocal.Ipi(self.orb,self.cam,0,self.tt.min_time,
                              self.tt.max_time,self.tt)
        self.igc = geocal.IpiImageGroundConnection(self.ipi, self.dem,
                                                   self.rad)
        self.geo_qa = GeoQa(self.basename + "_geoqa.nc", "aviris_ng_geo.log")

    def create_scene(self):
        # For tiepointing, we want to break the data up into roughly square
        # scenes, because image matching works better
        nline_per_scene = self.l1_osp_dir.number_line_per_scene
        rset = []
        for i in range(0,
                       self.tt.max_line // nline_per_scene * nline_per_scene,
                       nline_per_scene):
            if(i + 2 * nline_per_scene < self.tt.max_line):
                rset.append(range(i,i+nline_per_scene))
            else:
                # Special handling for last scene, we add in the extra
                # lines so we don't have a small runt at the end
                rset.append(range(i,self.tt.max_line))

        tline = [self.tt.time_list(i) for i in range(self.tt.size_time_list)]
        # Extra pad added by MeasuredTimeTable, we just want the actual times
        # so strip these off
        tline = tline[1:-1]
        
        # Create subsetted ImageGroundConnection, and put into an
        # overall IgcArray
        self.igccol_initial = geocal.IgcArray([])
        for i,r in enumerate(rset):
            # OffsetImageGroundConnection is simpler to subset, but
            # our ray tracing code actually assumes we have a
            # IpiImageGroundConnection. Can probably generalize that
            # a some point, but for now we'll just do the slightly more
            # complicated thing of directly creating the
            # IpiImageGroundConnection
            #igcsub = geocal.OffsetImageGroundConnection(self.igc, r.start,
            #                   0, len(r), self.igc.number_sample)
            ttsub = geocal.MeasuredTimeTable(tline[r.start:r.stop])
            radsub = geocal.SubRasterImage(self.rad, r.start, 0,
                                    len(r), self.rad.number_sample)
            ipisub = geocal.Ipi(self.orb,self.cam,0,ttsub.min_time,
                                ttsub.max_time,ttsub)
            igcsub = geocal.IpiImageGroundConnection(ipisub, self.dem,
                                                     radsub, f"Scene {i+1}")
            self.igccol_initial.add_igc(igcsub)
        self.igccol_initial.add_object(self.cam)
        self.igccol_initial.add_object(self.orb)
        self.igccol_initial.add_object(self.tt)
  
    def run(self):
        logger.info("Starting AvirisNgGeoGenerate")
        standard_metadata = AvirisNgStandardMetadata(line_averaging=self.tt.line_average)
        if(self.l1_osp_dir.number_process > 1):
            logger.info("Using %d processors", self.l1_osp_dir.number_process)
            pool = Pool(self.l1_osp_dir.number_process)
        else:
            logger.info("Using 1 processor")
            pool = None
        self.create_scene()
        l1b_correct = L1bCorrect(self.igccol_initial,
                                 self.l1_osp_dir,
                                 self.geo_qa)
        self.igccol_corrected = l1b_correct.igccol_corrected(pool=pool)
        self.cam.parameter = self.igccol_corrected.image_ground_connection(0).ipi.camera.parameter
        # TODO Put in copy orbit parameter when we have an orbit model that
        # gets updated.
        
        if(self.l1_osp_dir.do_final_projection):
            proj = L1bProj(self.igccol_corrected, self.l1_osp_dir,
                           self.geo_qa, img_type="final")
            proj.proj(pool=pool)
        # TODO: Write corrected orbit
        geocal.write_shelve(self.basename + "_camera.xml", self.cam)
        loc_fname = self.basename + "_loc"
        igm_fname = self.basename + "_igm"
        obs_fname = self.basename + "_obs"
        loc = AvirisNgLoc(loc_fname, igc=self.igc,
                          standard_metadata=standard_metadata)
        igm = AvirisNgIgm(igm_fname, igc=self.igc, loc=loc,
                          standard_metadata=standard_metadata)
        obs = AvirisNgObs(obs_fname, igc=self.igc, loc=loc,
                          standard_metadata=standard_metadata)
        # GLT
        loc.run(pool=pool)
        igm.run(pool=pool)
        obs.run(pool=pool)
        logger.info("Skipping GLT, we don't yet work with UTM")
        if(self.geo_qa is not None):
            # TODO Any flushing of log file needed?
            self.geo_qa.close()
        
__all__ = ["AvirisNgGeoGenerate", ]
