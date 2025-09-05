from .misc import file_name_to_gps_week
from .aviris_ng_raw import AvirisNgGpsTable
import geocal
import numpy as np
import h5py
from packaging import version
import h5netcdf


class AvirisNgOrbit(geocal.OrbitQuaternionList):
    """This reads the raw gps data"""

    def __init__(self, fname, gps_week=None):
        """Read the given raw gps file for AVIRIS-NG, or the given netCDF
        file.

        The GPS week can be passed in explicitly, or we extract this
        from the file name."""
        if h5py.is_hdf5(fname):
            f = h5py.File(fname, "r")
            self.gps_table = None
            self.gps_week = f["Orbit"].attrs["gps_week"]
            tm = f["Orbit/time_gps"][:]
            tm = [geocal.Time.time_gps(t) for t in tm]
            lat = f["Orbit/latitude"][:]
            lon = f["Orbit/longitude"][:]
            altitude = f["Orbit/altitude"][:]
            pos = [
                geocal.Geodetic(lat[i], lon[i], altitude[i]) for i in range(len(lat))
            ]
            roll = f["Orbit/roll"][:]
            pitch = f["Orbit/pitch"][:]
            heading = f["Orbit/heading"][:]
            od = []
            for i in range(len(pos)):
                isecond = i + 1
                if isecond >= len(pos):
                    isecond = i - 1
                od.append(
                    geocal.AircraftOrbitData(
                        tm[i],
                        pos[i],
                        tm[isecond],
                        pos[isecond],
                        roll[i],
                        pitch[i],
                        heading[i],
                    )
                )
        else:
            self.gps_table = AvirisNgGpsTable(fname)
            self.gps_week = gps_week
            if not self.gps_week:
                self.gps_week = file_name_to_gps_week(fname)
            gtable = self.gps_table.gps_table
            tm = [
                geocal.Time.time_gps(self.gps_week, gtable[i, 0])
                for i in range(gtable.shape[0])
            ]
            pos = [
                geocal.Geodetic(gtable[i, 1], gtable[i, 2], gtable[i, 3])
                for i in range(gtable.shape[0])
            ]
            # This is pitch, roll, and heading in degrees
            prh = gtable[:, -3:]
            od = []
            for i in range(len(pos)):
                isecond = i + 1
                if isecond >= len(pos):
                    isecond = i - 1
                od.append(
                    geocal.AircraftOrbitData(
                        tm[i],
                        pos[i],
                        tm[isecond],
                        pos[isecond],
                        prh[i, 1],
                        prh[i, 0],
                        prh[i, 2],
                    )
                )
        super().__init__(od)

    def write_orbit(self, orbit_fname):
        """This write the data to a netCDF file."""
        if version.parse(h5netcdf.__version__) >= version.parse("0.13.0"):
            fout = h5netcdf.File(orbit_fname, "w", decode_vlen_strings=False)
        else:
            fout = h5netcdf.File(orbit_fname, "w")
        tm = []
        lat = []
        lon = []
        alt = []
        roll = []
        pitch = []
        heading = []
        for od in self.quaternion_orbit_data:
            aod = geocal.AircraftOrbitData(od)
            tm.append(aod.time.gps)
            lat.append(aod.position_geodetic.latitude)
            lon.append(aod.position_geodetic.longitude)
            alt.append(aod.position_geodetic.height_reference_surface)
            roll.append(aod.roll)
            pitch.append(aod.pitch)
            heading.append(aod.heading)
        g = fout.create_group("Orbit")
        g.attrs["gps_week"] = self.gps_week
        t = g.create_variable("time_gps", ("t",), data=np.array(tm, dtype=np.float64))
        t.attrs["units"] = "s"
        t.attrs["description"] = "Time in seconds from GPS epoch"
        t = g.create_variable("latitude", ("t",), data=np.array(lat, dtype=np.float64))
        t.attrs["units"] = "degrees"
        t = g.create_variable("longitude", ("t",), data=np.array(lon, dtype=np.float64))
        t.attrs["units"] = "degrees"
        t = g.create_variable("altitude", ("t",), data=np.array(alt, dtype=np.float64))
        t.attrs["units"] = "m"
        t.attrs["description"] = "Altitude in meters above WGS-84 ellipsoid"
        t = g.create_variable("roll", ("t",), data=np.array(roll, dtype=np.float64))
        t.attrs["units"] = "degrees"
        t = g.create_variable("pitch", ("t",), data=np.array(pitch, dtype=np.float64))
        t.attrs["units"] = "degrees"
        t = g.create_variable(
            "heading", ("t",), data=np.array(heading, dtype=np.float64)
        )
        t.attrs["units"] = "degrees"


__all__ = [
    "AvirisNgOrbit",
]
