from .emit_loc import EmitLoc
from .emit_obs import EmitObs
from .emit_glt import EmitGlt
from .geo_qa import GeoQa
from .l1b_correct import L1bCorrect
from .emit_kmz_and_quicklook import EmitKmzAndQuicklook
from .misc import emit_file_name
from .standard_metadata import StandardMetadata
from emit_swig import EmitIgcCollection
from loguru import logger
import subprocess
from multiprocessing import Pool


class L1bGeoGenerate:
    """This is the overall l1b_geo process. This class writes output
    and temporary files to the current directory, and processes all
    the scenes."""

    def __init__(
        self, l1_osp_dir, l1a_att_fname, line_time_fname_list, l1b_rad_fname_list
    ):
        self.l1_osp_dir = l1_osp_dir
        self.l1a_att_fname = l1a_att_fname
        self.tt_and_rdn_fname = list(zip(line_time_fname_list, l1b_rad_fname_list))
        self.igccol_initial = EmitIgcCollection.create(
            self.l1a_att_fname,
            self.tt_and_rdn_fname,
            self.l1_osp_dir.match_rad_band,
            l1_osp_dir=self.l1_osp_dir,
        )
        tstart = self.igccol_initial.image_ground_connection(0).ipi.time_table.min_time
        self.build_version = self.l1_osp_dir.build_version
        self.product_version = self.l1_osp_dir.product_version
        self.orbit_number = self.igccol_initial.orbit_number
        qa_fname = emit_file_name(
            "l1b_geoqa",
            tstart,
            int(self.orbit_number),
            None,
            int(self.build_version),
            int(self.product_version),
            ".nc",
        )
        self.geo_qa = GeoQa(
            qa_fname,
            "l1b_geo.log",
            self.l1a_att_fname,
            self.tt_and_rdn_fname,
            self.l1_osp_dir,
        )

    @property
    def uncorrected_orbit(self):
        return self.igccol_initial.uncorrected_orbit

    @property
    def corrected_orbit(self):
        return self.igccol_corrected.image_ground_connection(0).ipi.orbit

    def run_scene(self, i):
        igc = self.igccol_corrected.image_ground_connection(i)
        if(igc.crosses_dateline):
            raise RuntimeError("Add handler here")
        scene = self.scene_list[i]
        scene_time = self.scene_time_list[i]
        rdn_fname = self.rdn_fname_list[i]
        scene_index = self.scene_index_list[i]
        logger.info(f"Processing {igc.title}")
        # TODO Create actual QA value here.
        if self.geo_qa and self.geo_qa.qa_flag:
            qa_value = self.geo_qa.qa_flag[i]
        else:
            # If we don't have qa_flag, then there was problem in
            # correcting the data. So the qa_value is poor
            qa_value = "Poor"
        standard_metadata = StandardMetadata(igc=igc, geolocation_accuracy_qa=qa_value)
        loc_fname = emit_file_name(
            "l1b_loc",
            scene_time,
            int(self.orbit_number),
            int(scene),
            int(self.build_version),
            int(self.product_version),
            ".img",
        )
        obs_fname = emit_file_name(
            "l1b_obs",
            scene_time,
            int(self.orbit_number),
            int(scene),
            int(self.build_version),
            int(self.product_version),
            ".img",
        )
        glt_fname = emit_file_name(
            "l1b_glt",
            scene_time,
            int(self.orbit_number),
            int(scene),
            int(self.build_version),
            int(self.product_version),
            ".img",
        )
        kmz_base_fname = emit_file_name(
            "l1b_rdnrgb",
            scene_time,
            int(self.orbit_number),
            int(scene),
            int(self.build_version),
            int(self.product_version),
            "",
        )
        loc = EmitLoc(loc_fname, igc=igc, standard_metadata=standard_metadata)
        obs = EmitObs(obs_fname, igc=igc, standard_metadata=standard_metadata, loc=loc)
        glt = EmitGlt(
            glt_fname,
            loc=loc,
            standard_metadata=standard_metadata,
            rotated_map=self.glt_rotated,
        )
        kmz = None
        if self.generate_kmz or self.generate_quicklook or self.generate_erdas:
            kmz = EmitKmzAndQuicklook(
                kmz_base_fname,
                loc,
                rdn_fname,
                igc_index=i,
                scene_index=scene_index,
                band_list=self.map_band_list,
                use_jpeg=self.kmz_use_jpeg,
                resolution=self.map_resolution,
                number_subpixel=self.map_number_subpixel,
                generate_kmz=self.generate_kmz,
                generate_erdas=self.generate_erdas,
                generate_quicklook=self.generate_quicklook,
                l1_osp_dir=self.l1_osp_dir,
            )
        loc.run()
        obs.run()
        glt.run()
        if kmz:
            try:
                with logger.catch(reraise=True):
                    kmz.run()
            except (RuntimeError, subprocess.SubprocessError):
                logger.warn(
                    f"KMZ failed for {i + 1}. Skipping generation of KMZ and quicklook"
                )
                logger.warn("Continuing with processing")

    def run(self):
        try:
            logger.info("Starting L1bGeoGenerate")
            self._run()
        finally:
            self.geo_qa.close()

    def _run(self):
        """Internal run function. Just pulled out so we can wrap the
        call with a try/finally block w/o being deeply nested"""
        if self.l1_osp_dir.number_process > 1:
            logger.info(f"Using {self.l1_osp_dir.number_process} processors")
            pool = Pool(self.l1_osp_dir.number_process)
        else:
            logger.info("Using 1 processor")
            pool = None
        l1b_correct = L1bCorrect(self.igccol_initial, self.l1_osp_dir, self.geo_qa)
        self.igccol_corrected = l1b_correct.igccol_corrected(pool=pool)
        tstart = self.igccol_initial.image_ground_connection(0).ipi.time_table.min_time
        orb_fname = emit_file_name(
            "l1b_att",
            tstart,
            int(self.orbit_number),
            None,
            int(self.build_version),
            int(self.product_version),
            ".nc",
        )
        self.uncorrected_orbit.write_corrected_orbit(orb_fname, self.corrected_orbit)
        # For convenience, grab data for l1b_geo_config, just so we don't
        # have lots of long strings
        self.scene_list = self.igccol_initial.scene_list
        self.scene_time_list = self.igccol_initial.scene_time_list
        self.rdn_fname_list = self.igccol_initial.rdn_fname_list
        self.scene_index_list = self.igccol_initial.scene_index_list
        self.generate_kmz = self.l1_osp_dir.generate_kmz
        self.generate_erdas = self.l1_osp_dir.generate_erdas
        self.generate_quicklook = self.l1_osp_dir.generate_quicklook
        self.map_band_list = self.l1_osp_dir.map_band_list
        self.kmz_use_jpeg = self.l1_osp_dir.kmz_use_jpeg
        self.map_resolution = self.l1_osp_dir.map_resolution
        self.map_number_subpixel = self.l1_osp_dir.map_number_subpixel
        self.glt_rotated = self.l1_osp_dir.glt_rotated
        if pool is None:
            _ = list(
                map(self.run_scene, list(range(self.igccol_corrected.number_image)))
            )
        else:
            _ = pool.map(
                self.run_scene, list(range(self.igccol_corrected.number_image))
            )


__all__ = [
    "L1bGeoGenerate",
]
