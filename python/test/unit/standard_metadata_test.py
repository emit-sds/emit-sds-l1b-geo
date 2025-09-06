from emit import EnviFile, StandardMetadata


def test_standard_metadata(igc, isolated_dir):
    f = EnviFile("test_file.img", shape=(2, 10, 10), mode="w")
    s = StandardMetadata(igc=igc)
    s.write_metadata(f)
