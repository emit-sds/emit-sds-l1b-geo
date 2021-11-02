import geocal
import numpy as np
import h5netcdf

class EmitOrbit(geocal.HdfOrbit_Eci_TimeJ2000):
    '''EMIT orbit. Right now this is just a wrapper around a generic
    GeoCal HDF Orbit (since netcdf is basically the same). We can extend
    this to a full C++ class if there is any need.'''
    def __init__(self, orbit_fname):
        super().__init__(orbit_fname, "", "Ephemeris/time_j2000",
         "Ephemeris/eci_position", "Ephemeris/eci_velocity",
         "Attitude/time_j2000", "Attitude/quaternion")

    @classmethod
    def write_file(cls, orbit_fname, orb, min_time, max_time):
        '''Write a file. This is really meant for generating test data.'''
        fout = h5netcdf.File(orbit_fname, "w")
        # For now, we have both ephemeris and attitude with same time spacing.
        # We could change that in the future if needed.
        tspace = 1.0
        tm = np.arange(min_time.j2000 - tspace,
                       max_time.j2000 + tspace,
                       tspace)
        pos = np.zeros((tm.shape[0], 3))
        vel = np.zeros((tm.shape[0], 3))
        quat = np.zeros((tm.shape[0], 4))
        for i, t in enumerate(tm):
            od = orb.orbit_data(geocal.Time.time_j2000(t))
            pos[i, :] = od.position_ci.position
            vel[i, :] = od.velocity_ci
            quat[i, :] = geocal.quaternion_to_array(od.sc_to_ci)
        g = fout.create_group("Ephemeris")
        t = g.create_variable("time_j2000", ('t',), data = tm)
        t.attrs["units"] = "s"
        t = g.create_variable("eci_position", ('t', 'position'), data=pos)
        t.attrs["description"] = "ECI position"
        t.attrs["units"] = "m"
        t = g.create_variable("eci_velocity", ('t', 'velocity'), data=vel)
        t.attrs["description"] = "ECI velocity"
        t.attrs["units"] = "m/s"
        
        g = fout.create_group("Attitude")
        t = g.create_variable("time_j2000", ('t',), data=tm)
        t.attrs["units"] = "s"
        t = g.create_variable("quaternion", ('t', 'quaternion'), data=quat)
        t.attrs["description"] = "Attitude quaternion, goes from spacecraft to ECI. The coefficient convention used has the real part in the first column."
        t.attrs["units"] = "dimensionless"
        fout.close()
        

__all__ = ["EmitOrbit", ]
