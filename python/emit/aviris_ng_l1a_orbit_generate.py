from .aviris_ng_orbit import AvirisNgOrbit
from .aviris_ng_raw import AvirisNgRaw
from .aviris_ng_time_table import AvirisNgTimeTable
import geocal
from loguru import logger
import re
import numpy as np
import os


class AvirisNgL1aOrbitGenerate:
    """This is the overall l1a orbit process for AVIRIS NG. This
    creates the initial orbit, time table, and line averaging files"""

    def __init__(
        self, raw_fname, gps_fname, pps_fname, l1_osp_dir, raw_binfac_fname=None
    ):
        self.raw_fname = raw_fname
        self.gps_fname = gps_fname
        self.pps_fname = pps_fname
        self.raw_binfac_fname = raw_binfac_fname
        self.l1_osp_dir = l1_osp_dir
        self.l1_osp_dir.setup_spice()
        self.basename = re.sub(r"_raw$", "", os.path.basename(self.raw_fname))
        logger.info(f"Raw file:   {self.raw_fname}")
        logger.info(f"GPS file:   {self.gps_fname}")
        logger.info(f"PPS file:   {self.pps_fname}")
        logger.info(f"L1 OSP dir: {self.l1_osp_dir.l1_osp_dir}")

    def calc_line_average(self):
        """AVIRIS-NG is oversampled in the downtrack direction, with the
        raw data. We determine a line averaging that gives a roughly square
        pixel. We do this by looking at the middle sample, and determining
        the spacing on the ground in the along track and cross track directions.
        We then take the median of all the ratios that gives us a squarish
        pixel.

        This is almost the same as what the pyortho program did, but there
        are minor differences in the details. It is possible pyortho might
        calculate a value off by 1 or 2 from what we calculate here."""
        # Allow the line average to be overridden, for backwards compatibility
        # with pyortho
        if self.raw_binfac_fname:
            return int(open(self.raw_binfac_fname).read())
        cam = self.l1_osp_dir.camera()
        dem = self.l1_osp_dir.dem
        # Full resolution time table, no line averaging
        tt = AvirisNgTimeTable(self.pps_fname, raw=self.r)
        ipi = geocal.Ipi(self.orb, cam, 0, tt.min_time, tt.max_time, tt)
        igc = geocal.IpiImageGroundConnection(ipi, dem, None)
        last_point = None
        smp = igc.number_sample / 2
        bin_factor = []
        for ln in range(0, igc.number_line):
            if ln % 1000 == 0 and len(bin_factor) > 1:
                logger.info(
                    f"Doing line {ln} of {igc.number_line} bin factor {int(np.median(np.array(bin_factor)))}"
                )
            try:
                pt1 = igc.ground_coordinate(geocal.ImageCoordinate(ln, smp))
                pt2 = igc.ground_coordinate(geocal.ImageCoordinate(ln, smp + 1))
                if last_point:
                    dt = geocal.distance(pt1, last_point)
                    at = geocal.distance(pt1, pt2)
                    bin_factor.append(int(round(at / dt)))
                last_point = pt1
            except RuntimeError:
                # Just skip any problems with calculating ground coordinate,
                # we just go on to the next line
                last_point = None
        line_average = int(np.median(np.array(bin_factor)))
        return line_average

    def run(self):
        logger.info("Starting AvirisNgL1aOrbitGenerate")
        self.orb = AvirisNgOrbit(self.gps_fname)
        self.orb.write_orbit(self.basename + "_att.nc")
        self.r = AvirisNgRaw(self.raw_fname)
        line_average = self.calc_line_average()
        self.tt = AvirisNgTimeTable(
            self.pps_fname, raw=self.r, line_average=line_average
        )
        self.tt.write(self.basename + "_line_time.nc")
        with open(self.basename + "_raw.binfac", "w") as fh:
            print(line_average, file=fh)


__all__ = [
    "AvirisNgL1aOrbitGenerate",
]
