from emit import AvirisNgRaw, AvirisNgTimeTable
import geocal
import pytest


@pytest.mark.long_test
def test_aviris_ng_time_table(aviris_pps_fname, aviris_raw_fname, isolated_dir):
    r = AvirisNgRaw(aviris_raw_fname)
    tt = AvirisNgTimeTable(aviris_pps_fname, raw=r, line_average=9)
    # A couple of times that we happened to grab the "clock2location"
    # data from
    assert (
        abs(
            tt.pps_table.clock_to_time(1777609046)
            - geocal.Time.parse_time("2017-03-28T20:21:02.095971Z")
        )
        < 1e-6
    )
    assert (
        abs(
            tt.pps_table.clock_to_time(1786609377)
            - geocal.Time.parse_time("2017-03-28T20:22:32.099810Z")
        )
        < 1e-6
    )
    tm, _ = tt.time(geocal.ImageCoordinate(0, 0))
    assert abs(tm - geocal.Time.parse_time("2017-03-28T20:21:02.095971Z")) < 1e-6
    tm, _ = tt.time(geocal.ImageCoordinate(1000, 0))
    assert abs(tm - geocal.Time.parse_time("2017-03-28T20:22:32.099810Z")) < 1e-6
    tt.write("time_table.nc")
    tt2 = AvirisNgTimeTable("time_table.nc")
    tm, _ = tt2.time(geocal.ImageCoordinate(0, 0))
    assert abs(tm - geocal.Time.parse_time("2017-03-28T20:21:02.095971Z")) < 1e-6
    tm, _ = tt2.time(geocal.ImageCoordinate(1000, 0))
    assert abs(tm - geocal.Time.parse_time("2017-03-28T20:22:32.099810Z")) < 1e-6
