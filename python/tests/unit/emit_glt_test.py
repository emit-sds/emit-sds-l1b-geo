from emit import EmitGlt, EmitLoc
import geocal
import pytest


def test_generate_glt(isolated_dir, emit_loc, igc, test_data):
    t = EmitGlt("test_glt.img", emit_loc)
    print(t.map_info_rotated())
    print(t.map_info_rotated().transform)
    t.run()
    g = EmitGlt("test_glt.img")
    f = geocal.GdalRasterImage("test_glt.img")
    ln = 1000
    for smp in range(0, t.shape[2], 100):
        if g.glt_line[ln, smp] != -999:
            ic = geocal.ImageCoordinate(
                float(g.glt_line[ln, smp] - 1), float(g.glt_sample[ln, smp] - 1)
            )
            if ic.line >= 0 and ic.sample >= 0:
                gc = f.ground_coordinate(geocal.ImageCoordinate(ln, smp), igc.dem)
                ic2 = igc.image_coordinate(gc)
                # TODO
                # We are currently using the smallest int in our resampling.
                # Should change to nearest neighbor at some point instead,
                # We can then perhaps compare to with 0.5. Right now we can
                # have a difference of 1 pixel of so.
                assert ic.line == pytest.approx(ic2.line, abs=1.0)
                assert ic.sample == pytest.approx(ic2.sample, abs=1.0)


# TODO Have a test for handling the date line correctly
@pytest.mark.skip
def test_cross_date_line(test_data):
    loc_cross_date_line = EmitLoc(test_data + "sample_cross_dateline_loc.img")
    print(loc_cross_date_line.map_info_rotated())
