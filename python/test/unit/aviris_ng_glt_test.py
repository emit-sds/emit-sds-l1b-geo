from emit import AvirisNgLoc, AvirisNgIgm, AvirisNgGlt
import pytest


@pytest.mark.long_test
def test_generate_avris_glt(aviris_igc_full, isolated_dir, test_data):
    loc = AvirisNgLoc(test_data / "aviris_ng_old" / "aviris_ng_full_loc")
    igm = AvirisNgIgm("test_igm", igc=aviris_igc_full, loc=loc)
    glt = AvirisNgGlt("test_glt", igc=aviris_igc_full, loc=loc, igm=igm, resolution=20)
    print(glt.map_info_rotated())
    glt.run()
