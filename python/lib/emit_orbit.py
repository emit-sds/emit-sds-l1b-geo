import geocal
import numpy as np
import h5netcdf
import h5py

class EmitOrbit(geocal.HdfOrbit_Eci_TimeJ2000):
    '''EMIT orbit. Right now this is just a wrapper around a generic
    GeoCal HDF Orbit (since netcdf is basically the same). We can extend
    this to a full C++ class if there is any need.'''
    def __init__(self, orbit_fname):
        super().__init__(orbit_fname, "", "Ephemeris/time_j2000",
         "Ephemeris/eci_position", "Ephemeris/eci_velocity",
         "Attitude/time_j2000", "Attitude/quaternion")

    def write_corrected_orbit(self, orbit_fname, orb_corrected):
        '''This copies the existing data in this orbit to a new file
        as "Uncorrected" data, as well as writing out corrected orbit 
        data.'''
        fout = h5netcdf.File(orbit_fname, "w")
        fin = h5py.File(self.file_name, "r")
        eph_tm_uncorr = fin["Ephemeris/time_j2000"][:]
        pos_uncorr = fin["Ephemeris/eci_position"][:]
        vel_uncorr = fin["Ephemeris/eci_velocity"][:]
        att_tm_uncorr = fin["Attitude/time_j2000"][:]
        quat_uncorr = fin["Attitude/quaternion"][:]
        
        # Add times, being careful not to past the edge of the orbit (since
        # this depends on both ephemeris and attitude we may have points in
        # one or the other that is outside the time range.
        have_min_time = False
        have_max_time = False
        att_tm = []
        for t in [geocal.Time.time_j2000(t) for t in att_tm_uncorr]:
            if(not have_min_time and t <= orb_corrected.min_time) :
                t = orb_corrected.min_time
                have_min_time = True
            if(not have_max_time and t >= orb_corrected.max_time):
                t = orb_corrected.max_time
                have_max_time = True
            if(t >= orb_corrected.min_time and t <= orb_corrected.max_time):
                att_tm.append(t)
        have_min_time = False
        have_max_time = False
        eph_tm = []
        for t in [geocal.Time.time_j2000(t) for t in eph_tm_uncorr]:
            if(not have_min_time and t <= orb_corrected.min_time) :
                t = orb_corrected.min_time
                have_min_time = True
            if(not have_max_time and t >= orb_corrected.max_time):
                t = orb_corrected.max_time
                have_max_time = True
            if(t >= orb_corrected.min_time and t <= orb_corrected.max_time):
                eph_tm.append(t)
        quat = np.zeros((len(att_tm), 4))
        for i, t in enumerate(att_tm):
            od = orb_corrected.orbit_data(t)
            quat[i, :] = geocal.quaternion_to_array(od.sc_to_ci)
        pos = np.zeros((len(eph_tm), 3))
        vel = np.zeros((len(eph_tm), 3))
        for i, t in enumerate(eph_tm):
            od = orb_corrected.orbit_data(t)
            pos[i, :] = od.position_ci.position
            vel[i, :] = od.velocity_ci
        
        g = fout.create_group("Uncorrected Ephemeris")
        g2 = fout.create_group("Ephemeris")
        t = g.create_variable("time_j2000", ('t',), data = eph_tm_uncorr)
        t.attrs["units"] = "s"
        t = g2.create_variable("time_j2000", ('t',),
                               data = np.array([t.j2000 for t in eph_tm]))
        t.attrs["units"] = "s"

        t = g.create_variable("eci_position", ('t', 'position'),
                              data=pos_uncorr)
        t.attrs["description"] = "ECI position"
        t.attrs["units"] = "m"
        t = g2.create_variable("eci_position", ('t', 'position'),
                              data=pos)
        t.attrs["description"] = "ECI position"
        t.attrs["units"] = "m"
        t = g.create_variable("eci_velocity", ('t', 'velocity'),
                              data=vel_uncorr)
        t.attrs["description"] = "ECI velocity"
        t.attrs["units"] = "m/s"
        t = g2.create_variable("eci_velocity", ('t', 'velocity'),
                               data=vel)
        t.attrs["description"] = "ECI velocity"
        t.attrs["units"] = "m/s"
        
        g = fout.create_group("Uncorrected Attitude")
        g2 = fout.create_group("Attitude")
        t = g.create_variable("time_j2000", ('t',), data=att_tm_uncorr)
        t.attrs["units"] = "s"
        t = g2.create_variable("time_j2000", ('t',),
                               data = np.array([t.j2000 for t in att_tm]))
        t.attrs["units"] = "s"

        t = g.create_variable("quaternion", ('t', 'quat'), data=quat_uncorr)
        t.attrs["description"] = "Attitude quaternion, goes from spacecraft to ECI. The coefficient convention used has the real part in the first column."
        t.attrs["units"] = "dimensionless"
        t = g2.create_variable("quaternion", ('t', 'quat'), data=quat)
        t.attrs["description"] = "Attitude quaternion, goes from spacecraft to ECI. The coefficient convention used has the real part in the first column."
        t.attrs["units"] = "dimensionless"

        fout.close()
        

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
        t = g.create_variable("quaternion", ('t', 'quat'), data=quat)
        t.attrs["description"] = "Attitude quaternion, goes from spacecraft to ECI. The coefficient convention used has the real part in the first column."
        t.attrs["units"] = "dimensionless"
        fout.close()
        

__all__ = ["EmitOrbit", ]
