from emit import GeoQa, L1bTpCollect
from multiprocessing import Pool
import pytest


@pytest.mark.long_test
def test_l1b_tp_collect(isolated_dir, l1_osp_dir, emit_igccol, test_data):
    geo_qa = GeoQa(
        "geoqa.nc",
        "l1b_geo.log",
        test_data / "emit20200610t014911_o80000_l1a_att_b001_v01.nc",
        [
            (
                test_data
                / "emit20200610t015051_o80000_s001_l1a_line_time_b001_v01.txt",
                test_data / "emit20200610t015051_o80000_s001_l1b_rdn_b001_v01.img",
            ),
            (
                test_data
                / "emit20200610t015103_o80000_s002_l1a_line_time_b001_v01.txt",
                test_data / "emit20200610t015103_o80000_s002_l1b_rdn_b001_v01.img",
            ),
            (
                test_data
                / "emit20200610t015115_o80000_s003_l1a_line_time_b001_v01.txt",
                test_data / "emit20200610t015115_o80000_s003_l1b_rdn_b001_v01.img",
            ),
        ],
        l1_osp_dir,
    )
    t = L1bTpCollect(emit_igccol, l1_osp_dir, geo_qa)
    pool = Pool(10)
    res = t.tpcol(pool=pool)
    print(res)
