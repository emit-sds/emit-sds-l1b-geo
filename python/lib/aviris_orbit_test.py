from .aviris_orbit import *
from .aviris_time_table import AvirisTimeTable
from .aviris_igm import AvirisIgm
from .misc import create_dem
import geocal
from test_support import *
import scipy.optimize

def test_aviris_orbit(isolated_dir):
    tt = AvirisTimeTable(aviris_test_data + "f180522t01p00r07rdn_e_obs")
    orb = AvirisOrbit(aviris_test_data + "f180522t01p00r07rdn_e_lonlat_eph", tt)
    print(orb)

    
def test_aviris_igc(isolated_dir):
    '''AVIRIS is actually a push whisk broom, so the EMIT style push
    broom isn't really right. But since we are just using this as 
    test data, we can pretend that AVIRIS test data is a push broom. But
    we need to be somewhat accurate on the location on the ground, so
    make sure the IGC is close to the supplied IGM file. If needed, 
    we can do a more realistic simulation. However we can separately test
    all the geolocation stuff, and Phil can use AVIRIS for the L2/L3 
    testing.'''
    tt = AvirisTimeTable(aviris_test_data + "f180522t01p00r07rdn_e_obs")
    orb = AvirisOrbit(aviris_test_data + "f180522t01p00r07rdn_e_lonlat_eph", tt)
    # Not sure what AVIRIS pitch is. AVIRIS-NG is 27 micrometer x 27 micrometer
    line_pitch=27e-6
    sample_pitch=27e-6
    nsamp = 677
    spectral_channel = 224
    focal_length = 193.5e-3
    cam = geocal.SimpleCamera(0,0,0,focal_length, line_pitch, sample_pitch,
                              1, nsamp)
    dem = create_dem(None)
    ipi = geocal.Ipi(orb, cam, 0, tt.min_time, tt.max_time, tt)
    igc = geocal.IpiImageGroundConnection(ipi, dem, None)
    igm = AvirisIgm(aviris_test_data + "f180522t01p00r07rdn_e_ort_igm")
    #cconv = LocalRcConverter(LocalRcParameter(igc))
    def f(x):
        igc.ipi.camera = geocal.SimpleCamera(0,0,0,x[0],
                                             line_pitch, -sample_pitch,
                                             1, nsamp)
        res = []
        for ln in range(0, igm.shape[0], 100):
            for smp in range(0, igm.shape[1], 100):
                res.append(geocal.distance(igc.ground_coordinate(geocal.ImageCoordinate(ln, smp)), igm[ln,smp]))
        return res
    print(f([193.5e-3 / 6.7,]))
    res = scipy.optimize.least_squares(f, [193.5e-3 / 6.7,], bounds=([0,],[0.04,]))
    print(res)
    geocal.write_shelve("igc.xml", igc)
    
