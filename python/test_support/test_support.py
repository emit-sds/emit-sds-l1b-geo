# This contains support routines for doing unit tests.
import pytest
import geocal
import glob
import os
import sys
import pickle
try:
    from emit_swig import *
    have_swig = True
except ImportError:
    have_swig = False

unit_test_data = os.path.abspath(os.path.dirname(__file__) + "/../../unit_test_data") + "/"
aviris_test_data = unit_test_data + "AVIRIS_data/"
aviris_ng_test_data = unit_test_data + "AVIRIS_NG_data/"

@pytest.fixture(scope="function")
def isolated_dir(tmpdir):
    '''This is a fixture that creates a temporary directory, and uses this
    while running a unit tests. Useful for tests that write out a test file
    and then try to read it.

    This fixture changes into the temporary directory, and at the end of
    the test it changes back to the current directory.

    Note that this uses the fixture tmpdir, which keeps around the last few
    temporary directories (cleaning up after a fixed number are generated).
    So if a test fails, you can look at the output at the location of tmpdir, 
    e.g. /tmp/pytest-of-smyth
    '''
    curdir = os.getcwd()
    try:
        tmpdir.chdir()
        yield curdir
    finally:
        os.chdir(curdir)

slow = pytest.mark.slow

# Short hand for marking as unconditional skipping. Good for tests we
# don't normally run, but might want to comment out for a specific debugging
# reason.
skip = pytest.mark.skip

@pytest.fixture(scope="function")
def test_data():
    '''Determine the directory with the test data.'''
    if("EMIT_TEST_DATA" in os.environ):
        tdata = os.environ["EMIT_TEST_DATA"] + "/latest/"
    else:
        # Location on eco-scf
        tdata = "/beegfs/store/emit-test-data/latest/"
        if(not os.path.exists(tdata)):
            # Location on rifle
            tdata="/ldata/smyth/emit-test-data/latest/"
        if(not os.path.exists(tdata)):
            pytest.skip("Don't have emit-test-data, so skipping test")
    if(os.path.exists(tdata)):
        yield tdata
    else:
        pytest.skip("Don't have emit-test-data, so skipping test")

@pytest.fixture(scope="function")
def aviris_ng_full_test_data():
    '''We have some AVIRIS NG test data in the source tree, but there is
    a more full set in a directory Phil put together. This is too large
    to include in our source tree, so look for this and if found run tests
    that depend on this.'''
    # Location on eco-scf
    tdata = "/beegfs/store/brodrick/emit/pushbroom_demo/l1b/"
    if(not os.path.exists(tdata)):
        # Location on rifle
        tdata="/bigdata/smyth/EmitTestData/aviris-ng/"
    if(os.path.exists(tdata)):
        yield tdata
    else:
        pytest.skip("Don't have aviris-ng test data, so skipping test")
    
@pytest.fixture(scope="function")
def orbit_fname(test_data):
    '''Test orbit'''
    return test_data + "emit20200610t014911_o80000_l1a_att_b001_v01.nc"

@pytest.fixture(scope="function")
def time_table_fname(test_data):
    '''Test time table'''
    return test_data + "emit20200610t015051_o80000_s001_l1a_line_time_b001_v01.nc"

@pytest.fixture(scope="function")
def l1b_rdn_fname(test_data):
    '''L1B Radiance file to use'''
    return test_data + "emit20200610t015051_o80000_s001_l1b_rdn_b001_v01.img"

@pytest.fixture(scope="function")
def aviris_orbit_fname(test_data):
    '''AVIRIS NG Orbit name'''
    # We currently just use the EMIT one. This is in a netCDF file format,
    # but we use this as a place holder. Can replace with a more direct
    # aviris GPS file when ready.
    return test_data + "emit20170328t202050_o90000_l1a_att_b001_v01.nc"

@pytest.fixture(scope="function")
def aviris_time_table_fname(test_data):
    '''AVIRIS NG Test time table. This is in netCDF file format. Can
    replace with real AVIRIS NG time table when ready.'''
    return test_data + "emit20170328t202050_o90000_l1a_line_time_full_b001_v01.nc"

@pytest.fixture(scope="function")
def aviris_l1b_rdn_fname(test_data):
    '''AVIRIS NG L1B Radiance file to use. This is actually resampled to
    EMIT wavelengths, we might want to replace this data set'''
    return test_data + "input_afids_ng/ang20170328t202059_rdn_emit_syn"

@pytest.fixture(scope="function")
def aviris_gps_fname(test_data):
    '''AVIRIS NG GPS data.''' 
    return test_data + "input_afids_ng/ang20170328t202059_gps"

@pytest.fixture(scope="function")
def aviris_raw_fname(test_data):
    '''AVIRIS NG raw data.''' 
    return test_data + "input_afids_ng/ang20170328t202059_raw"

@pytest.fixture(scope="function")
def aviris_pps_fname(test_data):
    '''AVIRIS NG PPS data.''' 
    return test_data + "input_afids_ng/ang20170328t202059_pps"

@pytest.fixture(scope="function")
def aviris_frame_meta(test_data):
    '''This returns pickled data we saved from the original pyortho
    program, which we can compare against to make sure we get the same
    results.'''
    frame_meta, gpstime, filedate, zone_alpha = pickle.load(open(test_data + "input_afids_ng/pyortho_20170328t202059.pkl", "rb"), encoding="bytes")
    return frame_meta

@pytest.fixture(scope="function")
def aviris_gps_table(test_data):
    '''AVIRIS NG GPS data.'''
    # The "bytes" here is needed because we pickled using python 2.7. See
    # https://groups.google.com/g/sage-devel/c/nLG8zMSKSD0
    return pickle.load(open(test_data + "input_afids_ng/gps_table_raw.pkl", "rb"),encoding="bytes")

@pytest.fixture(scope="function")
def aviris_pps_table(test_data):
    '''AVIRIS NG PPS data.'''
    # The "bytes" here is needed because we pickled using python 2.7. See
    # https://groups.google.com/g/sage-devel/c/nLG8zMSKSD0
    return pickle.load(open(test_data + "input_afids_ng/pps_table_raw.pkl", "rb"),encoding="bytes")

@pytest.fixture(scope="function")
def aviris_camera(test_data):
    '''This was a camera model fitted in a quick and dirty way in
    our end_to_end_testing. We'll want to replace this is a more careful
    camera model.'''
    return geocal.read_shelve(test_data + "l1_osp_aviris_ng_dir/camera.xml")

@pytest.fixture(scope="function")
def aviris_igc_full(aviris_camera, aviris_orbit_fname, aviris_time_table_fname,
                    aviris_l1b_rdn_fname):
    '''ImageGroundConnection that we can use for testing'''
    from emit.emit_time_table import EmitTimeTable
    from emit.emit_orbit_extension import EmitOrbit
    # Band here is the band in the camera model. Our camera only has 1 band,
    # so this is 0 even if we are using a difference radiance band
    camera_band = 0
    # Band to use for image matching
    l1b_band = 39               # This is red band of the simulated data.
    # We have some values outside the orbit range at the start and end.
    # We just trim this off, since this is test data. "Real" data will
    # need to figure out how to handle this.
    trim_pad = 5
    tt = EmitTimeTable(aviris_time_table_fname, trim_pad = trim_pad)
    orb = EmitOrbit(aviris_orbit_fname)
    ipi = geocal.Ipi(orb, aviris_camera, camera_band, tt.min_time,
                     tt.max_time, tt)
    dem = geocal.SrtmDem()
    img = geocal.GdalRasterImage(aviris_l1b_rdn_fname, l1b_band)
    img = geocal.SubRasterImage(img, trim_pad, 0, tt.max_line,
                                img.number_sample)
    igc = geocal.IpiImageGroundConnection(ipi, dem, img)
    return igc


@pytest.fixture(scope="function")
def igc(orbit_fname, time_table_fname, l1b_rdn_fname):
    '''ImageGroundConnection that we can use for testing'''
    from emit.emit_igc import EmitIgc
    res = EmitIgc(orbit_fname, time_table_fname, l1b_rdn_fname)
    res.title = "Scene 1"
    return res

@pytest.fixture(scope="function")
def emit_loc(test_data):
    '''EmitLoc that can be used with the igc for testing'''
    from emit.emit_loc import EmitLoc
    loc = EmitLoc(test_data + "sample_loc.img")
    return loc

@pytest.fixture(scope="function")
def l1b_loc():
    '''L1B LOC file that can be used with the igc for testing'''
    return unit_test_data + "l1b_loc.img"

@pytest.fixture(scope="function")
def l1_osp_dir(test_data):
    from emit.l1_osp_dir import L1OspDir
    return L1OspDir(test_data + "l1_osp_dir")

@pytest.fixture(scope="function")
def l1b_geo_config(l1_osp_dir):
    return l1_osp_dir.l1b_geo_config

@pytest.fixture(scope="function")
def emit_igccol(test_data, l1_osp_dir):
    import emit.emit_igc
    l1a_att = glob.glob(f"{test_data}/*_o80000_l1a_att_*.nc")[0]
    line_time = glob.glob(f"{test_data}/*_o80000_*_l1a_line_time*.nc")
    l1b_rad = glob.glob(f"{test_data}/*_o80000_*_l1b_rdn_*.img")
    rad_band = 1
    igccol = EmitIgcCollection.create(l1a_att, zip(line_time, l1b_rad),
                                      rad_band, l1_osp_dir)
    return igccol

    



