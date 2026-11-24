from emit import StoFile, EmitOrbit
import geocal
import h5py
import numpy as np


def test_sto_file(unit_test_data):
    """Read a sto file"""
    f = StoFile(
        unit_test_data / "oco3_issbad_210930000000_210930020000_211005113331_hsc.sto"
    )
    print(len(f.orbit_data))


def test_create_orbit(isolated_dir, unit_test_data):
    """Create a netCDF file containing sto data between two times"""
    # Somehow we need to know what the min and max time is, and what the
    # sto file list is that we need.
    tmin = geocal.Time.parse_time("2021-09-30T00:53:21.241Z")
    tmax = geocal.Time.parse_time("2021-09-30T02:26:38.337Z")
    f1 = unit_test_data / "oco3_issbad_210930000000_210930020000_211005113331_hsc.sto"
    f2 = unit_test_data / "oco3_issbad_210930020000_210930040000_211005113331_hsc.sto"
    orb = StoFile.create_orbit([f1, f2], tmin, tmax)
    print(orb)
    EmitOrbit.write_file2("test_orb.nc", orb)

    # Compare with what OCO-3 put into its file, just to make sure we
    # are consistent.
    f = h5py.File(
        unit_test_data / "oco3_L0AEP_13628_210930_B10305r_211124062049.h5", "r"
    )
    att1 = f["/STOISSBAD/sto_bad_att1"][:]
    att2 = f["/STOISSBAD/sto_bad_att2"][:]
    att3 = f["/STOISSBAD/sto_bad_att3"][:]
    att4 = f["/STOISSBAD/sto_bad_att4"][:]
    pos1 = f["/STOISSBAD/sto_bad_iss_pos1"][:]
    pos2 = f["/STOISSBAD/sto_bad_iss_pos2"][:]
    pos3 = f["/STOISSBAD/sto_bad_iss_pos3"][:]
    tm = [geocal.Time.time_pgs(t) for t in f["/STOISSBAD/sto_bad_iss_time_tai93"][:]]
    v1 = f["/STOISSBAD/sto_bad_iss_vel1"][:]
    v2 = f["/STOISSBAD/sto_bad_iss_vel2"][:]
    v3 = f["/STOISSBAD/sto_bad_iss_vel3"][:]
    qlist2 = []
    for i in range(att1.shape[0]):
        t = tm[i]
        p = geocal.Eci(pos1[i], pos2[i], pos3[i])
        v = np.array([v1[i], v2[i], v3[i]])
        att_q = geocal.Quaternion_double(att1[i], att2[i], att3[i], att4[i])
        if i == 1000:
            print(att_q)
        qlist2.append(geocal.QuaternionOrbitData(t, p, v, att_q))
    oco_orb = geocal.OrbitQuaternionList(qlist2)
    print(
        "Note that the quaternion will be different. OCO converts this to is SRU frame. But time and position match"
    )
    print(orb.orbit_data(tm[1000]))
    print(oco_orb.orbit_data(tm[1000]))
