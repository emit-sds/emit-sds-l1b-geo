from .envi_file import EnviFile
from .standard_metadata import StandardMetadata
import logging
import numpy as np
import geocal
import pandas as pd
import scipy
from packaging.version import parse as parse_version

logger = logging.getLogger("l1b_geo_process.emit_loc")


class EmitLoc(EnviFile):
    """Generate or read the LOC file for EMIT."""

    def __init__(self, fname, igc=None, standard_metadata=None):
        """Open a file. As a convention if the IGC is supplied we just
        assume we are creating a file. Otherwise, we read an existing one.

        Note that we don't actually create the data until you run the
        "run" function, so it will initially just be unintialized data.

        Note that the shape is (3, number_line, number_sample)
        """
        self.igc = igc
        if self.igc is None:
            mode = "r"
            shape = None
        else:
            mode = "w"
            self.standard_metadata = standard_metadata
            if self.standard_metadata is None:
                self.standard_metadata = StandardMetadata(igc=igc)
            shape = (3, igc.number_line, igc.number_sample)
        super().__init__(
            fname,
            shape=shape,
            dtype=np.float64,
            mode=mode,
            description="EMIT L1B pixel location file",
            band_description=[
                "Longitude (WGS-84)",
                "Latitude (WGS-84)",
                "Elevation (m)",
            ],
        )

    @property
    def latitude(self):
        """Return the latitude field"""
        return self[1, :, :]

    @property
    def longitude(self):
        """Return the longitude field"""
        return self[0, :, :]

    @property
    def height(self):
        """Return the height field."""
        return self[2, :, :]

    def scaled_lat_lon_grid(self, scale):
        """Scale the latitude longitude grid for doing subsampling. This
        divides each pixel in scale x scale, and returns the lat/lon for
        each point in the scaled grid (e.g., for 2, we return (-0.25,-0.25)
        through (0.25,0.25)"""
        lat = self.latitude[:]
        lon = self.longitude[:]
        # TODO Put in handling for crossing dateline
        if self.crosses_date_line:
            raise RuntimeError("Don't yet work when we cross the dateline")
        latf = scipy.interpolate.RectBivariateSpline(
            np.arange(lat.shape[0]),
            np.arange(lat.shape[1]),
            lat,
            bbox=[-0.5, lat.shape[0] - 0.5, -0.5, lat.shape[1] - 0.5],
            kx=2,
            ky=2,
        )
        lonf = scipy.interpolate.RectBivariateSpline(
            np.arange(lon.shape[0]),
            np.arange(lon.shape[1]),
            lon,
            bbox=[-0.5, lon.shape[0] - 0.5, -0.5, lon.shape[1] - 0.5],
            kx=2,
            ky=2,
        )
        xi = np.arange(-0.5 + (1.0 / scale) / 2, lat.shape[0] - 0.5, 1.0 / scale)
        yi = np.arange(-0.5 + (1.0 / scale) / 2, lat.shape[1] - 0.5, 1.0 / scale)
        latscale = latf(xi, yi, grid=True)
        lonscale = lonf(xi, yi, grid=True)
        return latscale, lonscale

    def ground_coordinate(self, ln, smp):
        """Return the Geodetic point for the given line/sample"""
        lon, lat, elv = self[:, ln, smp]
        return geocal.Geodetic(lat, lon, elv)

    @property
    def crosses_date_line(self):
        """Returns true if we cross the dateline"""
        return self.longitude.min() < -170 and self.longitude.max() > 160

    def run(self):
        """Actually generate the output data."""
        logger.info("Generating LOC data for %s", self.igc.title)
        # We could run this in parallel if needed. However our
        # scene size is fairly small (1280 lines) so that it probably isn't
        # worth worry about this, at least initially. We can probably handle
        # the parallelization at the scene level if performance is an issue.
        # We added a number_framelet in 1.28. For now check for an older
        # version, eventually this will go away and we'll just assume we have
        # the newer version
        if parse_version(geocal.__version__) > parse_version("1.27"):
            rcast = geocal.IgcRayCaster(self.igc, 1, 0, -1, 1, 30)
        else:
            rcast = geocal.IgcRayCaster(self.igc, 0, -1, 1, 30)
        rcast.number_sub_line = 1
        rcast.number_sub_sample = 1
        while not rcast.last_position:
            gpos = rcast.next_position()
            for i in range(gpos.shape[1]):
                gp = geocal.Geodetic(
                    geocal.Ecr(
                        gpos[0, i, 0, 0, 0, 0],
                        gpos[0, i, 0, 0, 0, 1],
                        gpos[0, i, 0, 0, 0, 2],
                    )
                )
                self[0, rcast.current_position, i] = gp.longitude
                self[1, rcast.current_position, i] = gp.latitude
                self[2, rcast.current_position, i] = gp.height_reference_surface
        self.standard_metadata.write_metadata(self)

    def compare(self, f2):
        """Compare with another file, returning True if the same,
        False otherwise.

        Note the compare is done with a tolerance. We allow +-1 pixel in
        the location due to small round off differences. We report
        the differences"""
        print("Comparing LOC files")
        same = self.metadata_compare(f2)
        distance = np.array(
            [
                [
                    geocal.distance(
                        self.ground_coordinate(i, j), f2.ground_coordinate(i, j)
                    )
                    for j in range(self.shape[2])
                ]
                for i in range(self.shape[1])
            ]
        )
        print("   Difference (meters)")
        r = pd.DataFrame(distance.flatten()).describe()
        print(r)
        if distance.max() >= 60.0:
            same = False
        if same:
            print("   Files are considered the same")
        else:
            print("   Files are considered different")
        return same


__all__ = [
    "EmitLoc",
]
