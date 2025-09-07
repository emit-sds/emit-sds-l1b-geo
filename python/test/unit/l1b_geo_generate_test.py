from emit import L1bGeoGenerate
import pytest


# This is kind of long for a unit test, and we already test this
# at the end-to-end-check level. So normally skip this, although we
# can turn this back on to debug some kind of problem
@pytest.mark.long_test
def test_l1b_geo_generate(isolated_dir, test_data, l1_osp_dir):
    l1a_att = next(test_data.glob("*_o80000_l1a_att_*.nc"))
    line_time = list(test_data.glob("*_o80000_*_l1a_line_time*.txt"))
    l1b_rad = list(test_data.glob("*_o80000_*_l1b_rdn_*.img"))
    t = L1bGeoGenerate(l1_osp_dir, l1a_att, line_time, l1b_rad)
    t.run()

    
@pytest.mark.long_test
def test_dateline_l1b_geo_generate(isolated_dir, test_data, l1_osp_dir):
    '''Test data that crosses the dateline'''
    l1a_att = test_data / "emit20240101t231526_o00116_l1a_att_b0106_v01.nc"
    line_time = [test_data / "emit20240102t001521_o00116_s001_l1a_raw_b0106_v01_line_timestamps.txt",]
    l1b_rad = [test_data / "emit20240102t001521_o00116_s001_l1b_rdn_b0106_v01.img",]
    t = L1bGeoGenerate(l1_osp_dir, l1a_att, line_time, l1b_rad)
    t.run()
    
