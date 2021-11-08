# This contains support routines for doing unit tests.
import pytest
import geocal
import os
try:
    from emit_swig import *
    have_swig = True
except ImportError:
    have_swig = False

unit_test_data = os.path.abspath(os.path.dirname(__file__) + "/../../unit_test_data") + "/"
aviris_test_data = unit_test_data + "AVIRIS_data/"

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
def orbit_fname(test_data):
    '''Test orbit'''
    return test_data + "orbit_l1a_sim.nc"

@pytest.fixture(scope="function")
def time_table_fname(test_data):
    '''Test time table'''
    return test_data + "line_time_sim.nc"

@pytest.fixture(scope="function")
def l1b_rdn_fname(test_data):
    '''L1B Radiance file to use'''
    return test_data + "igc_sim_envi.img"

@pytest.fixture(scope="function")
def igc(orbit_fname, time_table_fname, l1b_rdn_fname):
    '''ImageGroundConnection that we can use for testing'''
    from emit.emit_igc import EmitIgc
    return EmitIgc(orbit_fname, time_table_fname, l1b_rdn_fname)

@pytest.fixture(scope="function")
def l1b_loc():
    '''L1B LOC file that can be used with the igc for testing'''
    return unit_test_data + "l1b_loc.img"




