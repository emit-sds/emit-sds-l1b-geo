import geocal

# We may well need to implement this in C++ for performance, but for now
# just do a simple ImageGroundConnection.

def emit_igc(orbit_fname, tstart):
    # As a placeholder, we use and ECOSTRESS orbit data file. We'll replace
    # this with a real EMIT orbit later
    orb = geocal.HdfOrbit_Eci_TimeJ2000(orbit_fname, "", "Ephemeris/time_j2000",
         "Ephemeris/eci_position", "Ephemeris/eci_velocity",
         "Attitude/time_j2000", "Attitude/quaternion")
    # We should get the time directly from an EMIT file, but for now
    # just use fixed time spacing
    tspace = 9.26e-3
    nline = 1000
    tt = geocal.ConstantSpacingTimeTable(tstart, tstart + nline * tspace, tspace)
    # Simple pinhole camera, we'll replace with the calibrated camera
    focal_length = 193.5e-3
    line_pitch = 30e-6
    sample_pitch = 30e-6
    nsamp = 1240
    spectral_channel = 480
    cam = geocal.SimpleCamera(0,0,0,focal_length, line_pitch, sample_pitch,
                              1, nsamp)
    # Probably should get the directory through some kind of configuration, but
    # for now just use the default through environment variables. Also, for
    # now allow 0 height where we don't have DEM data (e.g. over ocean). We
    # might actually want to consider this an error, since we don't expect
    # EMIT to be over water. But for now allow it
    dem = geocal.SrtmDem("", False)
    ipi = geocal.Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
    igc = geocal.IpiImageGroundConnection(ipi, dem, None)
    return igc

__all__ = ["emit_igc", ]    
