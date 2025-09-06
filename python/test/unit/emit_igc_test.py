from emit import EmitIgc, EmitIgcCollection
import geocal
import glob


def test_emit_igc(isolated_dir, orbit_fname, time_table_fname, l1b_rdn_fname):
    igc = EmitIgc(orbit_fname, time_table_fname, l1b_rdn_fname)
    # Pixel resolution should be ~60m, and roughly square
    print(
        "Line resolution: ",
        geocal.distance(
            igc.ground_coordinate(geocal.ImageCoordinate(500, igc.number_sample / 2)),
            igc.ground_coordinate(
                geocal.ImageCoordinate(500 + 1, igc.number_sample / 2)
            ),
        ),
    )
    print(
        "Sample resolution: ",
        geocal.distance(
            igc.ground_coordinate(geocal.ImageCoordinate(500, igc.number_sample / 2)),
            igc.ground_coordinate(
                geocal.ImageCoordinate(500, igc.number_sample / 2 + 1)
            ),
        ),
    )
    # Test that we can save a reload this. Note that the python layer
    # gets stripped off, but for our purposes I don't think that matters.
    # We can make these full C++ classes instead of python classes if it
    # matters.
    geocal.write_shelve("igc.xml", igc)
    igc2 = geocal.read_shelve("igc.xml")
    print(igc2)


def test_create_igccollection(isolated_dir, test_data, l1_osp_dir):
    l1a_att = next(test_data.glob("*_o80000_l1a_att_*.nc"))
    line_time = [
        next(test_data.glob("*_o80000_s001_l1a_line_time*.txt")),
        next(test_data.glob("*_o80000_s002_l1a_line_time*.txt")),
        next(test_data.glob("*_o80000_s003_l1a_line_time*.txt")),
    ]
    l1b_rad = [
        next(test_data.glob("*_o80000_s001_l1b_rdn_*.img")),
        next(test_data.glob("*_o80000_s002_l1b_rdn_*.img")),
        next(test_data.glob("*_o80000_s003_l1b_rdn_*.img")),
    ]
    rad_band = 1
    print(l1_osp_dir)
    print(l1_osp_dir.spice_data_dir)
    igccol = EmitIgcCollection.create(
        l1a_att, zip(line_time, l1b_rad), rad_band, l1_osp_dir=l1_osp_dir
    )
    assert igccol.orbit_number == "80000"
    assert igccol.scene_list == ["001", "002", "003"]
    assert igccol.number_image == 3
    assert igccol.image_ground_connection(0).title == "20200610t015051"
    assert igccol.image_ground_connection(1).title == "20200610t015103"
    assert igccol.image_ground_connection(2).title == "20200610t015115"
    assert (
        igccol.image_ground_connection(0).ipi.time_table.min_time
        < igccol.image_ground_connection(1).ipi.time_table.min_time
    )
    print(glob.glob(f"{test_data}/*_l1a_line_time*.nc"))
    print(glob.glob(f"{test_data}/*_l1b_rdn_*.img"))
    print(igccol.image_ground_connection(1).ipi.time_table.min_time)
    print(igccol.image_ground_connection(2).ipi.time_table.min_time)
    assert (
        igccol.image_ground_connection(1).ipi.time_table.min_time
        < igccol.image_ground_connection(2).ipi.time_table.min_time
    )
