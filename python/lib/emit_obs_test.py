from .emit_obs import *
import geocal
from test_support import *
from pytest import approx

def p_view_angle(igc, ic):
    '''Independent calculation of view angles, using pyorbital. Not
    identical to our calculation, but shoule be pretty close.'''
    import datetime
    import pyorbital.orbital
    gp = igc.ground_coordinate(ic)
    pos = igc.cf_look_vector_pos(ic)
    # Couple of notes here. This takes an array only, so we pass one value
    # through. The height is in km, not meter, so scale here.
    # The datetime is a required argument, although it isn't actually used
    # for anything. We just pass "now" as a convenient date time object
    az,alt= pyorbital.orbital.get_observer_look([pos.longitude], [pos.latitude],
                      [pos.height_reference_surface / 1000],
                      datetime.datetime.now(), [gp.longitude], [gp.latitude],
                      [gp.height_reference_surface/1000])
    return 90-alt[0], az[0]

def p_solar(igc, ic):
    import pyorbital.astronomy
    import datetime
    # Time of line 5 is 2020-06-10T01:50:51.790238Z. We don't really
    # need to write a geocal.Time to datetime conversion, so just hard
    # code this. The solar angles aren't super accurate anyways since
    # pyorbital doesn't include all the stuff JPL spice does.
    t = datetime.datetime(2020, 6, 10, 1, 50, 51, 790238)
    gp = igc.ground_coordinate(ic)
    alt,az = pyorbital.astronomy.get_alt_az(t, [gp.longitude], [gp.latitude])
    z = 90 - alt[0] * geocal.rad_to_deg
    az = az[0] * geocal.rad_to_deg
    if(az < 0):
        az += 360
    return z,az 
    
# This is kind of long for a unit test, and we already test this
# at the end-to-end-check level. So normally skip this, although we
# can turn this back on to debug some kind of problem
@slow
def test_generate_obs(igc, isolated_dir, emit_loc):
    # Subset the igc, just so this goes quicker
    tt = igc.ipi.time_table
    ttsub = geocal.MeasuredTimeTable([tt.time_list(i) for i in range(10)])
    igc.ipi.time_table = ttsub
    t = EmitObs("test_obs.img", igc=igc, loc=emit_loc)
    t.run()
    g = EmitObs("test_obs.img")
    ln = 5
    for smp in range(0, igc.number_sample, 100):
        ic = geocal.ImageCoordinate(ln, smp)
        p_zen, p_azm = p_view_angle(igc, ic)
        p_szen, p_saz = p_solar(igc, ic)
        assert g.view_zenith[ln,smp] == approx(p_zen,abs=0.1)
        assert g.view_azimuth[ln,smp] == approx(p_azm,abs=3.0)
        assert g.solar_zenith[ln,smp] == approx(p_szen,abs=0.01)
        assert g.solar_azimuth[ln,smp] == approx(p_saz,abs=0.01)
        # Don't have an independent test of solar phase, cosine_i or
        # path length.

        # slope and aspect are direct calls to geocal,
        # which already tested slope/aspect against gdal_dem
    
    
