from .envi_file import EnviFile
from .standard_metadata import StandardMetadata
from loguru import logger
import numpy as np
import re
import math
import geocal


class AvirisNgIgm(EnviFile):
    """Generate or read the IGM file for AVIRIS-NG."""

    def __init__(
        self,
        fname,
        igc=None,
        loc=None,
        standard_metadata=None,
        number_line_process=1000,
        l1_osp_dir=None,
    ):
        self.igc = igc
        self.loc = loc
        self.l1_osp_dir = l1_osp_dir
        self.number_line_process = number_line_process
        if self.igc is None:
            mode = "r"
            shape = None
            fh = geocal.GdalRasterImage(str(fname))
            m = re.search(r"UTM zone (\d+) (North|South)", fh["ENVI", "description"])
            if not m:
                raise RuntimeError(f"Don't recognize UTM zone in {fname}")
            self.utm_zone = int(m[1]) * (1 if m[2] == "North" else -1)
            fh.close()
        else:
            mode = "w"
            self.standard_metadata = standard_metadata
            if self.standard_metadata is None:
                self.standard_metadata = StandardMetadata(igc=igc)
            shape = (3, self.igc.number_line, self.igc.number_sample)
            gp = igc.ground_coordinate(
                geocal.ImageCoordinate(igc.number_line / 2.0, igc.number_sample / 2.0)
            )
            self.utm_zone = int(math.floor(((gp.longitude + 180.0) / 6.0) + 1.0))
            if gp.latitude < 0:
                self.utm_zone *= -1
        super().__init__(
            fname,
            shape=shape,
            dtype=np.float64,
            mode=mode,
            description="ANG AIG VSWIR RT-Ortho IGM (easting, northing, elevation)\nUTM zone %d %s"
            % (abs(self.utm_zone), "North" if self.utm_zone > 0 else "South"),
            band_description=["Easting (m)", "Northing (m)", "Elevation (m)"],
        )
        if self.utm_zone < 0:
            self.ogrw = geocal.OgrWrapper.from_epsg(32700 + abs(self.utm_zone))
        else:
            self.ogrw = geocal.OgrWrapper.from_epsg(32600 + abs(self.utm_zone))

    @property
    def east(self):
        """Return the UTM east field"""
        return self[0, :, :]

    @property
    def north(self):
        """Return the UTM north field"""
        return self[1, :, :]

    @property
    def height(self):
        """Return the height field."""
        return self[2, :, :]

    def ground_coordinate(self, ln, smp):
        """Return the UTM point for the given line/sample"""
        east, north, elv = self.data[:, ln, smp]
        return geocal.OgrCoordinate(self.ogrw, east, north, elv)

    def run_scene(self, i):
        nline = min(self.number_line_process, self.igc.number_line - i)
        logger.info(f"Generating IGM data for {self.igc.title} ({i}, {i + nline})")
        with self.multiprocess_data():
            for ln in range(i, i + nline):
                for smp in range(self.shape[2]):
                    g = geocal.OgrCoordinate(
                        self.ogrw, self.loc.ground_coordinate(ln, smp)
                    )
                    self[0, ln, smp] = g.x
                    self[1, ln, smp] = g.y
                    self[2, ln, smp] = g.z

    def run(self, pool=None):
        """Actually generate the output data."""
        logger.info(f"Generating IGM data for {self.igc.title}")
        ilist = list(range(0, self.igc.number_line, self.number_line_process))
        if pool is None:
            _ = list(map(self.run_scene, ilist))
        else:
            _ = pool.map(self.run_scene, ilist)
        self.standard_metadata.write_metadata(self)


__all__ = ["AvirisNgIgm"]
