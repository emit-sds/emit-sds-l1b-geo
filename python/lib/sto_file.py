import geocal
import pandas as pd
import numpy as np

class StoFile:
    '''This class reads a BAD sto file, and presents the data as
    a list of geocal.QuaternionOrbitData. This is a bit low level, it
    is a building piece for making a orbit file from the sto file.
    '''
    def __init__(self, fname):
        t = pd.read_csv(fname, sep=None, engine='python')
        # Pull out actual data
        t = t[t["#Header"] == "#Data"]
        # Time is in GPS seconds, and is made up of
        # LADP06MD2378W (USGNC_PS_Pointing_Coarse_Time_Tag) and
        # and LADP06MD2380W (USGNC_PS_PD_Fine_Pointing_Fine_Time_Tag)
        # Note the corrections (USGNC_GCM_Time_Error_Seconds) does *not*
        # need to be applied to this data. That is for the broadcast time,
        # the PS_Pointing is a different time tag and doesn't need to be
        # corrected

        # Position is LADP06MD2395H, LADP06MD2396H, LADP06MD2397H
        # Velocity is LADP06MD2399R, LADP06MD2400R LADP06MD2401R
        # Attitude quaternion is LADP06MD2382U, LADP06MD2383U,
        # LADP06MD2384U, LADP06MD2385U

        tm = t[["LADP06MD2378W", "LADP06MD2380W"]]
        pos = t[["LADP06MD2395H", "LADP06MD2396H", "LADP06MD2397H"]]
        vel = t[["LADP06MD2399R", "LADP06MD2400R", "LADP06MD2401R"]]
        att_q = t[["LADP06MD2382U", "LADP06MD2383U", "LADP06MD2384U",
                   "LADP06MD2385U"]]

        # Convert to numpy arrays, which are easier to work with to
        # pull everything together
        tm = tm.to_numpy(dtype=np.float64)
        pos = pos.to_numpy(dtype=np.float64)
        vel = vel.to_numpy(dtype=np.float64)
        att_q = att_q.to_numpy(dtype=np.float64)

        self.orbit_data = []
        for i in range(tm.shape[0]):
            t = geocal.Time.time_gps(tm[i,0] + tm[i,1])
            p = geocal.Eci(*pos[i,:])
            v = vel[i,:]
            att = geocal.Quaternion_double(*att_q[i,:])
            self.orbit_data.append(geocal.QuaternionOrbitData(t,p,v,att))

    @staticmethod
    def create_orbit(flist, tmin, tmax):
        qlist = []
        for fname in flist:
            qlist_file = StoFile(fname).orbit_data
            qlist.extend([q for q in qlist_file
                          if (q.time >= tmin and q.time <= tmax)])
        return geocal.OrbitQuaternionList(qlist)
