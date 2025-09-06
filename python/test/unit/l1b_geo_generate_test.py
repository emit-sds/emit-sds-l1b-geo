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
