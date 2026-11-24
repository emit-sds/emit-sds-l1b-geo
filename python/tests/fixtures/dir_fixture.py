# This defines fixtures that gives the paths to various directories with
# test data

import os
import pytest
from pathlib import Path


@pytest.fixture(scope="function")
def unit_test_data():
    """Return the unit test directory"""
    yield Path(os.path.dirname(__file__)).parent.parent.parent / "unit_test_data"


@pytest.fixture(scope="function")
def aviris_test_data(unit_test_data):
    """Return the AVIRIS test directory"""
    yield unit_test_data / "AVIRIS_data"


@pytest.fixture(scope="function")
def aviris_ng_test_data(unit_test_data):
    """Return the AVIRIS_NG test directory"""
    yield unit_test_data / "AVIRIS_NG_data"


@pytest.fixture(scope="function")
def aviris_ng_full_test_data():
    """We have some AVIRIS NG test data in the source tree, but there is
    a more full set in a directory Phil put together. This is too large
    to include in our source tree, so look for this and if found run tests
    that depend on this."""
    # Location on eco-scf
    tdata = Path("/beegfs/store/brodrick/emit/pushbroom_demo/l1b")
    if not tdata.exists():
        # Location on rifle
        tdata = Path("/bigdata/smyth/EmitTestData/aviris-ng")
    if tdata.exists():
        yield tdata
    else:
        pytest.skip("Don't have aviris-ng test data, so skipping test")


# Changed test data in 6.00. For backwards testing, just use the 5.00
# version of these files, it is sufficient for testing
@pytest.fixture(scope="function")
def test_data():
    """Determine the directory with the test data."""
    if "EMIT_TEST_DATA" in os.environ:
        tdata = Path(os.environ["EMIT_TEST_DATA"]) / "latest"
    else:
        # Location on eco-scf
        tdata = Path("/beegfs/store/shared/emit-test-data/latest")
        if not tdata.exists():
            # Location on rifle
            tdata = Path("/ldata/smyth/emit-test-data/latest")
    if tdata.exists():
        return tdata
    else:
        pytest.skip("Don't have emit-test-data, so skipping test")


@pytest.fixture(scope="function")
def orbit_fname(test_data):
    """Test orbit"""
    return test_data / "emit20200610t014911_o80000_l1a_att_b001_v01.nc"


@pytest.fixture(scope="function")
def time_table_fname(test_data):
    """Test time table"""
    return test_data / "emit20200610t015051_o80000_s001_l1a_line_time_b001_v01.txt"


@pytest.fixture(scope="function")
def l1b_rdn_fname(test_data):
    """L1B Radiance file to use"""
    return test_data / "emit20200610t015051_o80000_s001_l1b_rdn_b001_v01.img"


@pytest.fixture(scope="function")
def aviris_orbit_fname(test_data):
    """AVIRIS NG Orbit name"""
    # We currently just use the EMIT one. This is in a netCDF file format,
    # but we use this as a place holder. Can replace with a more direct
    # aviris GPS file when ready.
    return test_data / "aviris_ng_old/emit20170328t202050_o90000_l1a_att_b001_v01.nc"


@pytest.fixture(scope="function")
def aviris_time_table_fname(test_data):
    """AVIRIS NG Test time table. This is in netCDF file format. Can
    replace with real AVIRIS NG time table when ready."""
    return (
        test_data
        / "aviris_ng_old/emit20170328t202050_o90000_l1a_line_time_full_b001_v01.nc"
    )


@pytest.fixture(scope="function")
def aviris_l1b_rdn_fname(test_data):
    """AVIRIS NG L1B Radiance file to use. This is actually resampled to
    EMIT wavelengths, we might want to replace this data set"""
    return test_data / "aviris_ng_old/input_afids_ng/ang20170328t202059_rdn_emit_syn"


@pytest.fixture(scope="function")
def aviris_gps_fname(test_data):
    """AVIRIS NG GPS data."""
    return test_data / "aviris_ng_old/input_afids_ng/ang20170328t202059_gps"


@pytest.fixture(scope="function")
def aviris_raw_fname(test_data):
    """AVIRIS NG raw data."""
    return test_data / "aviris_ng_old/input_afids_ng/ang20170328t202059_raw"


@pytest.fixture(scope="function")
def aviris_pps_fname(test_data):
    """AVIRIS NG PPS data."""
    return test_data / "aviris_ng_old/input_afids_ng/ang20170328t202059_pps"


@pytest.fixture(scope="function")
def emit_loc(test_data):
    """EmitLoc that can be used with the igc for testing"""
    from emit.emit_loc import EmitLoc

    loc = EmitLoc(
        test_data / "expected/emit20200610t015051_o80000_s001_l1b_loc_b001_v01.img"
    )
    return loc


@pytest.fixture(scope="function")
def l1b_loc(unit_test_data):
    """L1B LOC file that can be used with the igc for testing"""
    return unit_test_data / "l1b_loc.img"
