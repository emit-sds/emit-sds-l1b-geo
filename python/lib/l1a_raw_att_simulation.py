import numpy as np
import h5netcdf
from geocal import Time, quaternion_to_array

class L1aRawAttSimulate(object):
    '''This is used to generate L1A raw simulated simulated data.'''
    def __init__(self, orb, min_time, max_time):
        '''Create a L1ARawAttSimulate to process the given orbit.'''
        self.orb = orb
        self.min_time = min_time
        self.max_time = max_time
        
    def create_file(self, l1a_raw_att_fname):
        fout = h5netcdf.File(l1a_raw_att_fname, "w")
        # For now, we have both ephemeris and attitude with same time spacing.
        # We could change that in the future if needed.
        tspace = 1.0
        tm = np.arange(self.min_time.j2000 - tspace,
                       self.max_time.j2000 + tspace,
                       tspace)
        pos = np.zeros((tm.shape[0], 3))
        vel = np.zeros((tm.shape[0], 3))
        quat = np.zeros((tm.shape[0], 4))
        for i, t in enumerate(tm):
            od = self.orb.orbit_data(Time.time_j2000(t))
            pos[i, :] = od.position_ci.position
            vel[i, :] = od.velocity_ci
            quat[i, :] = quaternion_to_array(od.sc_to_ci)
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

__all__ = ["L1aRawAttSimulate"]
