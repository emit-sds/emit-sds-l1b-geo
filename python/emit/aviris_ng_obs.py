from .envi_file import EnviFile
from .standard_metadata import StandardMetadata
from loguru import logger
import numpy as np
import geocal
import re
from math import acos, sin, cos

class AvirisNgObs(EnviFile):
    """This reads the AVIRIS NG obs data."""

    def __init__(
        self,
        fname,
        loc=None,
        igc=None,
        standard_metadata=None,
        number_line_process=1000,
        l1_osp_dir=None,
    ):
        """Open a file. As a convention if the IGC is supplied we just
        assume we are creating a file. Otherwise, we read an existing one.

        Note that we don't actually create the data until you run the
        "run" function, so it will initially just be unintialized data.

        Note that the shape is (3, number_line, number_sample)
        """
        self.igc = igc
        self.loc = loc
        self.l1_osp_dir = l1_osp_dir
        self.number_line_process = number_line_process
        if self.igc is None:
            mode = "r"
            shape = None
        else:
            mode = "w"
            self.standard_metadata = standard_metadata
            if self.standard_metadata is None:
                self.standard_metadata = StandardMetadata(igc=self.igc)
            shape = (11, self.igc.number_line, self.igc.number_sample)
        super().__init__(
            fname,
            shape=shape,
            dtype=np.float64,
            mode=mode,
            description="ANG AIG VSWIR RT-Ortho OBS",
            band_description=[
                "Path length (sensor-to-ground in meters)",
                "To-sensor azimuth (0 to 360 degrees CW from N)",
                "To-sensor zenith (0 to 90 degrees from zenith)",
                "To-sun azimuth (0 to 360 degrees CW from N)",
                "To-sun zenith (0 to 90 degrees from zenith)",
                "Solar phase (degrees between to-sensor and to-sun vectors in principal plane)",
                "Slope (local surface slope as derived from DEM in degrees) ",
                "Aspect (local surface aspect 0 to 360 degrees clockwise from N)",
                "Cosine(i) (apparent local illumination factor based on DEM slope and aspect and to sun vector)",
                "UTC Time (decimal hours for mid-line pixels)",
                "Earth-sun distance (AU)",
            ],
        )

    @property
    def path_length(self):
        """Return the path length field"""
        return self[0, :, :]

    @property
    def view_azimuth(self):
        """Return the view azimuth field"""
        return self[1, :, :]

    @property
    def view_zenith(self):
        """Return the view zenith field"""
        return self[2, :, :]

    @property
    def solar_azimuth(self):
        """Return the solar azimuth field"""
        return self[3, :, :]

    @property
    def solar_zenith(self):
        """Return the solar zenith field"""
        return self[4, :, :]

    @property
    def solar_phase(self):
        """Return the solar phase field"""
        return self[5, :, :]

    @property
    def slope(self):
        """Return the slope field"""
        return self[6, :, :]

    @property
    def aspect(self):
        """Return the aspect field"""
        return self[7, :, :]

    @property
    def cosine_i(self):
        """Return the cosine(i) field"""
        return self[8, :, :]

    @property
    def utc_time(self):
        """Return the UTC Time field"""
        return self[9, :, :]

    @property
    def earth_sun_distance(self):
        """Return the earth-sun distance field"""
        return self[10, :, :]

    def run_scene(self, i):
        nline = min(self.number_line_process, self.igc.number_line - i)
        logger.info(f"Generating OBS data for {self.igc.title} ({i}, {i+nline})")
        with self.multiprocess_data():
            for ln in range(i, i + nline):
                pos = self.igc.cf_look_vector_pos(geocal.ImageCoordinate(ln, 0))
                tm = self.igc.pixel_time(geocal.ImageCoordinate(ln, 0))
                self.earth_sun_distance[ln, :] = geocal.Ecr.solar_distance(tm)
                seconds_in_day = tm - geocal.Time.parse_time(
                    re.split("T", str(tm))[0] + "T00:00:00Z"
                )
                self.utc_time[ln, :] = seconds_in_day / (60 * 60)
                for smp in range(self.igc.number_sample):
                    gp = self.loc.ground_coordinate(ln, smp)
                    # This is to sensor direction, opposite of what we
                    # sometimes use
                    clv = geocal.CartesianFixedLookVector(gp, pos)
                    lv = geocal.LnLookVector(clv, gp)
                    slv = geocal.LnLookVector.solar_look_vector(tm, gp)
                    self.path_length[ln, smp] = geocal.distance(gp, pos)
                    # Convention is different for LookVector, subtract 180
                    # to get AVIRIS convention
                    t = lv.view_azimuth - 180
                    if t < 0:
                        t += 360
                    self.view_azimuth[ln, smp] = t
                    self.view_zenith[ln, smp] = lv.view_zenith
                    t = slv.view_azimuth - 180
                    if t < 0:
                        t += 360
                    self.solar_azimuth[ln, smp] = t
                    self.solar_zenith[ln, smp] = slv.view_zenith
                    d = (
                        lv.direction[0] * slv.direction[0]
                        + lv.direction[1] * slv.direction[1]
                        + lv.direction[2] * slv.direction[2]
                    )
                    self.solar_phase[ln, smp] = acos(d) * geocal.rad_to_deg
                    self.slope[ln, smp], self.aspect[ln, smp] = (
                        self.igc.dem.slope_and_aspect(gp)
                    )
                    slope_dir = [
                        sin(self.slope[ln, smp]) * sin(self.aspect[ln, smp]),
                        sin(self.slope[ln, smp]) * cos(self.aspect[ln, smp]),
                        cos(self.slope[ln, smp]),
                    ]
                    self.cosine_i[ln, smp] = (
                        slope_dir[0] * slv.direction[0]
                        + slope_dir[1] * slv.direction[1]
                        + slope_dir[2] * slv.direction[2]
                    )

    def run(self, pool=None):
        """Actually generate the output data."""
        logger.info(f"Generating OBS data for {self.igc.title}")
        ilist = list(range(0, self.igc.number_line, self.number_line_process))
        if pool is None:
            _ = list(map(self.run_scene, ilist))
        else:
            _ = pool.map(self.run_scene, ilist)
        self.standard_metadata.write_metadata(self)


__all__ = [
    "AvirisNgObs",
]
