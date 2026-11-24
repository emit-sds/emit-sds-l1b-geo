from emit import EnviFile
import geocal


def test_envi_file(isolated_dir):
    d = EnviFile("test.img", (3, 1000, 1200), mode="w")
    d[0, 0, 0] = 1
    d[0, 0, 1] = 2
    d[0, 1, 0] = 3
    d[1, 1, 0] = 4
    d.flush()
    d = None
    dread = EnviFile("test.img")
    assert dread[0, 0, 0] == 1
    assert dread[0, 0, 1] == 2
    assert dread[0, 1, 0] == 3
    assert dread[1, 1, 0] == 4
    # Check that we have the metadata and BIL stuff correct
    gread = geocal.GdalMultiBand("test.img")
    assert gread.raster_image(0).read(0, 0) == 1
    assert gread.raster_image(0).read(0, 1) == 2
    assert gread.raster_image(0).read(1, 0) == 3
    assert gread.raster_image(1).read(1, 0) == 4
