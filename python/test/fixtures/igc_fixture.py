import pytest
import geocal
import emit


@pytest.fixture(scope="function")
def aviris_camera(test_data):
    """This was a camera model fitted in a quick and dirty way in
    our end_to_end_testing. We'll want to replace this is a more careful
    camera model."""
    return geocal.read_shelve(str(test_data / "l1_osp_aviris_ng_dir" / "camera.xml"))


@pytest.fixture(scope="function")
def aviris_igc_full(
    aviris_camera, aviris_orbit_fname, aviris_time_table_fname, aviris_l1b_rdn_fname
):
    """ImageGroundConnection that we can use for testing"""
    # Band here is the band in the camera model. Our camera only has 1 band,
    # so this is 0 even if we are using a difference radiance band
    camera_band = 0
    # Band to use for image matching
    l1b_band = 39  # This is red band of the simulated data.
    # We have some values outside the orbit range at the start and end.
    # We just trim this off, since this is test data. "Real" data will
    # need to figure out how to handle this.
    trim_pad = 5
    tt = emit.EmitTimeTable(str(aviris_time_table_fname), trim_pad=trim_pad)
    orb = emit.EmitOrbit(str(aviris_orbit_fname))
    ipi = geocal.Ipi(orb, aviris_camera, camera_band, tt.min_time, tt.max_time, tt)
    dem = geocal.SrtmDem()
    img = geocal.GdalRasterImage(str(aviris_l1b_rdn_fname), l1b_band)
    img = geocal.SubRasterImage(img, trim_pad, 0, tt.max_line, img.number_sample)
    igc = geocal.IpiImageGroundConnection(ipi, dem, img)
    return igc


@pytest.fixture(scope="function")
def igc(orbit_fname, time_table_fname, l1b_rdn_fname, l1_osp_dir):
    """ImageGroundConnection that we can use for testing"""
    res = emit.EmitIgc(
        orbit_fname, time_table_fname, l1b_rdn_fname, l1_osp_dir=l1_osp_dir
    )
    res.title = "Scene 1"
    return res


@pytest.fixture(scope="function")
def emit_igccol(test_data, l1_osp_dir):
    l1a_att = next(test_data.glob("*_o80000_l1a_att_*.nc"))
    line_time = test_data.glob("*_o80000_*_l1a_line_time*.txt")
    l1b_rad = test_data.glob("*_o80000_*_l1b_rdn_*.img")
    rad_band = 1
    igccol = emit.EmitIgcCollection.create(
        l1a_att, zip(line_time, l1b_rad), rad_band, l1_osp_dir
    )
    return igccol


@pytest.fixture(scope="function")
def emit_dateline_igccol(test_data, l1_osp_dir):
    l1a_att = test_data / "emit20240101t231526_o00116_l1a_att_b0106_v01.nc"
    line_time = [
        test_data
        / "emit20240102t001521_o00116_s001_l1a_raw_b0106_v01_line_timestamps.txt",
    ]
    l1b_rad = [
        test_data / "emit20240102t001521_o00116_s001_l1b_rdn_b0106_v01.img",
    ]
    # Red band for matching
    rad_band = 38
    igccol = emit.EmitIgcCollection.create(
        l1a_att, zip(line_time, l1b_rad), rad_band, l1_osp_dir
    )
    return igccol


@pytest.fixture(scope="function")
def emit_loc(test_data):
    # Sample_loc is created in emit_loc_test.py, in a test that is normally skipped.
    # You can rerun that to generate data if needed.
    return emit.EmitLoc(test_data / "sample_loc.img")
