# Fixtures that don't really fit in one of the other files.
import pytest
import os
import pickle


@pytest.fixture(scope="function")
def isolated_dir(tmpdir):
    """This is a fixture that creates a temporary directory, and uses this
    while running a unit tests. Useful for tests that write out a test file
    and then try to read it.

    This fixture changes into the temporary directory, and at the end of
    the test it changes back to the current directory.

    Note that this uses the fixture tmpdir, which keeps around the last few
    temporary directories (cleaning up after a fixed number are generated).
    So if a test fails, you can look at the output at the location of tmpdir,
    e.g. /tmp/pytest-of-smyth
    """
    curdir = os.getcwd()
    try:
        tmpdir.chdir()
        yield curdir
    finally:
        os.chdir(curdir)


@pytest.fixture(scope="function")
def aviris_gps_table(test_data):
    """AVIRIS NG GPS data."""
    # The "bytes" here is needed because we pickled using python 2.7. See
    # https://groups.google.com/g/sage-devel/c/nLG8zMSKSD0
    return pickle.load(
        open(test_data / "aviris_ng_old/input_afids_ng/gps_table_raw.pkl", "rb"),
        encoding="bytes",
    )


@pytest.fixture(scope="function")
def aviris_pps_table(test_data):
    """AVIRIS NG PPS data."""
    # The "bytes" here is needed because we pickled using python 2.7. See
    # https://groups.google.com/g/sage-devel/c/nLG8zMSKSD0
    return pickle.load(
        open(test_data / "aviris_ng_old/input_afids_ng/pps_table_raw.pkl", "rb"),
        encoding="bytes",
    )


@pytest.fixture(scope="function")
def l1_osp_dir(test_data):
    from emit.l1_osp_dir import L1OspDir

    return L1OspDir(test_data / "l1_osp_dir")


@pytest.fixture(scope="function")
def l1b_geo_config(l1_osp_dir):
    return l1_osp_dir.l1b_geo_config


@pytest.fixture(scope="function")
def aviris_frame_meta(test_data):
    """This returns pickled data we saved from the original pyortho
    program, which we can compare against to make sure we get the same
    results."""
    frame_meta, gpstime, filedate, zone_alpha = pickle.load(
        open(
            test_data / "aviris_ng_old/input_afids_ng/pyortho_20170328t202059.pkl", "rb"
        ),
        encoding="bytes",
    )
    return frame_meta
