from .geo_qa import *
from test_support import *
import geocal
import os

@skip
def test_geo_qa(isolated_dir, l1_osp_dir, test_data):
    # Since this runs at the end of processing, it isn't too easy to
    # test this isolation. This test uses data from our end to
    # end run. It can't be run as a normal unit test, but we can
    # turn this on if we need to change or test something about the
    # the QA file. Otherwise it is best tested in the end to end check
    # we run.
    run_dir = "/home/smyth/Local/emit-build/build/l1b_geo_run"
    os.environ["EMIT_END_TO_END_TEST"] = "t"
    
    geo_qa = GeoQa("geoqa.nc", "l1b_geo.log",
                   f"{test_data}/emit20200610t014911_o80000_l1a_att_b001_v01.nc",
                   [(f"{test_data}/emit20200610t015051_o80000_s001_l1a_line_time_b001_v01.txt",
                     f"{test_data}/emit20200610t015051_o80000_s001_l1b_rdn_b001_v01.img"),
                    (f"{test_data}/emit20200610t015103_o80000_s002_l1a_line_time_b001_v01.txt",
                     f"{test_data}/emit20200610t015103_o80000_s002_l1b_rdn_b001_v01.img"),
                    
                    (f"{test_data}/emit20200610t015115_o80000_s003_l1a_line_time_b001_v01.txt",
                     f"{test_data}/emit20200610t015115_o80000_s003_l1b_rdn_b001_v01.img")],
                   l1_osp_dir)
    igccol = geocal.read_shelve(f"{run_dir}/igccol_initial.xml")
    igccol_corrected = geocal.read_shelve(f"{run_dir}/igccol_sba.xml")
    tpcol = geocal.read_shelve(f"{run_dir}/tpcol.xml")
    for i in range(3):
        tplist = geocal.TiePointCollection([tp for tp in tpcol
                                            if(tp.image_coordinate(i))])
        # These values are nonsense, just so we can test
        ntpoint_final = len(tplist)
        ntpoint_removed = 10 * (i+1)
        ntpoint_initial = ntpoint_final + ntpoint_removed
        number_match_try = (i+1)
        geo_qa.add_tp_log(f"Image Index {i+1} 0", f"{run_dir}/tpmatch_00{i+1}.log_0")
        geo_qa.add_tp_single_scene(i, igccol, tplist, ntpoint_initial,
                                   ntpoint_removed, ntpoint_final,
                                   number_match_try)
    geo_qa.add_final_accuracy(igccol_corrected, tpcol)
    geo_qa.close()
    igccol = GeoQa.igccol_initial("geoqa.nc")
    tpcol = GeoQa.tpcol("geoqa.nc")
    igccol_corrected = GeoQa.igccol_corrected("geoqa.nc")
    print(igccol)
    print(tpcol)
    print(igccol_corrected)
